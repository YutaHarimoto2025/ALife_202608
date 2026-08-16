"""FastAPI appの構築と、WebSocketによるsnapshotとstatusの配信。

SimulationService が実時間ペース制御とcommand処理(pause、restart、
speed、save)を行う。
"""

from __future__ import annotations

import asyncio
import math
import time
from collections import deque
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import msgspec
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from alife.api._messages import (
    CommandMessage,
    ErrorMessage,
    SaveResultMessage,
    StatusMessage,
    snapshot_to_message,
)
from alife.backends.numpy.state import NumpyWorldState
from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.config.schema import ExperimentConfig
from alife.core.simulation import SimulationCore
from alife.runtime.factory import build_simulation
from alife.runtime.run_results import RunResultsWriter
from utils.file_io.msgspec_io import MsgspecIO


class SimulationService:
    def __init__(
        self,
        core: SimulationCore[NumpyWorldState],
        config: ExperimentConfig,
        project_paths: ProjectPaths,
        run_results_enabled: bool = True,
        description: str | None = None,
    ) -> None:
        self._core = core
        self._config = config
        self._project_paths = project_paths
        self._snapshot_hz_render = config.render.snapshot_hz_render
        self._run_results = (
            RunResultsWriter(project_paths, config, description=description)
            if run_results_enabled
            else None
        )
        self._queues: set[asyncio.Queue[str]] = set()
        self._stop = asyncio.Event()
        self._wake = asyncio.Event()
        self._paused = True
        self._speed_multiplier = config.frontend_ui.speed_multiplier_default
        self._elapsed_samples: deque[float] = deque(
            maxlen=config.frontend_ui.elapsed_average_window
        )
        self._elapsed_average = 0.0
        self._render_rate_samples: deque[float] = deque(
            maxlen=config.frontend_ui.elapsed_average_window
        )
        self._render_rate_last_at: float | None = None
        self._snapshot_hz_render_real = 0.0

    def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=8)
        self._queues.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        self._queues.discard(queue)

    def current_snapshot(self) -> str:
        return MsgspecIO.encode_json(snapshot_to_message(self._core.state))

    def current_status(self) -> str:
        return MsgspecIO.encode_json(self._status_message())

    def handle_command(self, raw_message: str, queue: asyncio.Queue[str]) -> None:
        try:
            command = MsgspecIO.decode_json(raw_message, type=CommandMessage)
            self._apply_command(command, queue)
        except (msgspec.DecodeError, msgspec.ValidationError, TypeError, ValueError) as error:
            self._enqueue(queue, MsgspecIO.encode_json(ErrorMessage(message=str(error))))

    async def run(self) -> None:
        tasks = [asyncio.create_task(self._run_simulation())]
        if self._snapshot_hz_render > 0.0:
            tasks.append(asyncio.create_task(self._run_render()))
        await self._stop.wait()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self) -> None:
        self._stop.set()
        self._wake.set()

    def _apply_command(self, command: CommandMessage, queue: asyncio.Queue[str]) -> None:
        if command.type == "toggle_pause":
            if self._paused:
                self._start_run_if_needed()
            self._paused = not self._paused
            self._wake.set()
            self._publish_status()
            return

        if command.type == "restart":
            self._core = build_simulation(self._config)
            self._elapsed_samples.clear()
            self._elapsed_average = 0.0
            if self._run_results is not None:
                self._run_results.start_new()
            self._wake.set()
            self._publish_status()
            self._publish_snapshot()
            return

        if command.type == "set_speed":
            speed_multiplier = command.speed_multiplier
            if speed_multiplier is None:
                raise ValueError("speed_multiplier is required")
            if not math.isfinite(speed_multiplier) or not (
                self._config.frontend_ui.speed_multiplier_min
                <= speed_multiplier
                <= self._config.frontend_ui.speed_multiplier_max
            ):
                raise ValueError(
                    "speed_multiplier must be between "
                    f"{self._config.frontend_ui.speed_multiplier_min} and "
                    f"{self._config.frontend_ui.speed_multiplier_max}"
                )
            self._speed_multiplier = speed_multiplier
            self._wake.set()
            self._publish_status()
            return

        if command.type == "save":
            if self._run_results is None:
                self._enqueue(
                    queue,
                    MsgspecIO.encode_json(
                        ErrorMessage(message="save is disabled by --no-run-results")
                    ),
                )
                return
            if not self._run_results.started:
                self._enqueue(
                    queue,
                    MsgspecIO.encode_json(
                        ErrorMessage(message="save is unavailable before simulation starts")
                    ),
                )
                return
            try:
                path = self._run_results.save(self._core.state)
            except OSError as error:
                self._enqueue(queue, MsgspecIO.encode_json(ErrorMessage(message=str(error))))
            else:
                relative_path = path.relative_to(self._project_paths.root_path)
                self._enqueue(
                    queue,
                    MsgspecIO.encode_json(
                        SaveResultMessage(
                            tick=self._core.state.tick,
                            path=str(relative_path),
                        )
                    ),
                )
            return

        raise ValueError(f"unknown command type: {command.type!r}")

    async def _run_simulation(self) -> None:
        next_deadline = time.perf_counter()
        while not self._stop.is_set():
            if self._paused:
                self._wake.clear()
                await self._wake.wait()
                next_deadline = time.perf_counter()
                continue

            step_started = time.perf_counter()
            self._core.step()
            elapsed = time.perf_counter() - step_started
            self._elapsed_samples.append(elapsed)
            self._elapsed_average = sum(self._elapsed_samples) / len(self._elapsed_samples)

            next_deadline += self._dt_required()
            self._wake.clear()
            remaining = next_deadline - time.perf_counter()
            if remaining <= 0.0:
                await asyncio.sleep(0)
                continue
            try:
                await asyncio.wait_for(self._wake.wait(), timeout=remaining)
                next_deadline = time.perf_counter()
            except TimeoutError:
                pass

    async def _run_render(self) -> None:
        interval = 1.0 / self._snapshot_hz_render
        next_deadline = time.perf_counter()
        while not self._stop.is_set():
            now = time.perf_counter()
            if self._render_rate_last_at is not None:
                elapsed = now - self._render_rate_last_at
                if elapsed > 0.0:
                    self._render_rate_samples.append(1.0 / elapsed)
                    self._snapshot_hz_render_real = sum(self._render_rate_samples) / len(
                        self._render_rate_samples
                    )
            self._render_rate_last_at = now
            self._publish_status()
            self._publish_snapshot()
            next_deadline += interval
            remaining = next_deadline - time.perf_counter()
            if remaining <= 0.0:
                await asyncio.sleep(0)
                continue
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=remaining)
            except TimeoutError:
                pass

    def _dt_required(self) -> float:
        return self._core.dt_simu / self._speed_multiplier

    def _status_message(self) -> StatusMessage:
        performance = "normal" if self._elapsed_average <= self._dt_required() else "lagging"
        run_results_enabled = self._run_results is not None
        run_started = self._run_results.started if self._run_results is not None else False
        return StatusMessage(
            paused=self._paused,
            compute_backend=self._config.execution.compute_backend,
            speed_multiplier=self._speed_multiplier,
            speed_multiplier_min=self._config.frontend_ui.speed_multiplier_min,
            speed_multiplier_max=self._config.frontend_ui.speed_multiplier_max,
            speed_multiplier_step=self._config.frontend_ui.speed_multiplier_step,
            tick=self._core.state.tick,
            dt_simu=self._core.dt_simu,
            dt_required=self._dt_required(),
            elapsed_average=self._elapsed_average,
            snapshot_hz_render=self._snapshot_hz_render,
            snapshot_hz_render_real=self._snapshot_hz_render_real,
            performance=performance,
            run_results_enabled=run_results_enabled,
            run_started=run_started,
        )

    def _start_run_if_needed(self) -> None:
        if self._run_results is not None:
            self._run_results.start()

    def _publish_status(self) -> None:
        self._publish(MsgspecIO.encode_json(self._status_message()))

    def _publish_snapshot(self) -> None:
        self._publish(self.current_snapshot())

    def _publish(self, payload: str) -> None:
        for queue in tuple(self._queues):
            self._enqueue(queue, payload)

    @staticmethod
    def _enqueue(queue: asyncio.Queue[str], payload: str) -> None:
        if queue.full():
            queue.get_nowait()
        queue.put_nowait(payload)


def create_app(
    paths: ProjectPaths,
    run_results_enabled: bool = True,
    description: str | None = None,
) -> FastAPI:
    config = load_experiment(paths.params)
    core = build_simulation(config)
    service = SimulationService(
        core,
        config,
        paths,
        run_results_enabled=run_results_enabled,
        description=description,
    )

    @asynccontextmanager
    async def _lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        task = asyncio.create_task(service.run())
        try:
            yield
        finally:
            await service.stop()
            await task

    app = FastAPI(title="ALife simulation", lifespan=_lifespan)

    async def _health() -> dict[str, str]:
        return {"status": "ok"}

    app.add_api_route("/health", _health, methods=["GET"])

    async def _websocket(websocket: WebSocket) -> None:
        await websocket.accept()
        queue = service.subscribe()
        sender = asyncio.create_task(_send_messages(websocket, queue))
        try:
            await websocket.send_text(service.current_status())
            await websocket.send_text(service.current_snapshot())
            while True:
                service.handle_command(await websocket.receive_text(), queue)
        except WebSocketDisconnect:
            pass
        finally:
            sender.cancel()
            await asyncio.gather(sender, return_exceptions=True)
            service.unsubscribe(queue)

    app.add_api_websocket_route("/ws", _websocket)
    return app


async def _send_messages(websocket: WebSocket, queue: asyncio.Queue[str]) -> None:
    while True:
        await websocket.send_text(await queue.get())
