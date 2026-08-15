from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from alife.backends.numpy.state import NumpyWorldState
from alife.config.loader import load_experiment
from alife.core.simulation import SimulationCore
from alife.renderers.web import snapshot_to_json
from alife.runtime.factory import build_simulation


class SimulationService:
    def __init__(self, core: SimulationCore[NumpyWorldState], snapshot_hz: float) -> None:
        self._core = core
        self._interval = max(1, round(1.0 / (core.dt * snapshot_hz))) if snapshot_hz > 0 else 0
        self._queues: set[asyncio.Queue[dict[str, Any]]] = set()
        self._stop = asyncio.Event()

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=1)
        self._queues.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self._queues.discard(queue)

    def current_snapshot(self) -> dict[str, Any]:
        return snapshot_to_json(self._core.snapshot())

    async def run(self) -> None:
        while not self._stop.is_set():
            self._core.step()
            if self._interval and self._core.state.tick % self._interval == 0:
                payload = self.current_snapshot()
                for queue in tuple(self._queues):
                    if queue.full():
                        queue.get_nowait()
                    queue.put_nowait(payload)
            await asyncio.sleep(self._core.dt)

    async def stop(self) -> None:
        self._stop.set()


def create_app(experiment_path: Path) -> FastAPI:
    config = load_experiment(experiment_path)
    core = build_simulation(config)
    service = SimulationService(core, config.execution.snapshot_hz)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        task = asyncio.create_task(service.run())
        try:
            yield
        finally:
            await service.stop()
            await task

    app = FastAPI(title="ALife simulation", lifespan=lifespan)

    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.add_api_route("/health", health, methods=["GET"])

    async def websocket(websocket: WebSocket) -> None:
        await websocket.accept()
        queue = service.subscribe()
        try:
            await websocket.send_json(service.current_snapshot())
            while True:
                await websocket.send_json(await queue.get())
        except WebSocketDisconnect:
            pass
        finally:
            service.unsubscribe(queue)

    app.add_api_websocket_route("/ws", websocket)
    return app
