import asyncio
from pathlib import Path

import alife.api.server as server_module
from alife.api._messages import StatusMessage
from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.runtime.factory import build_simulation
from utils.file_io.msgspec_io import MsgspecIO


def test_service_dt_required_uses_speed_multiplier() -> None:
    config = load_experiment(ProjectPaths.built_absolutely().params)
    service = server_module.SimulationService(
        build_simulation(config),
        config,
        ProjectPaths.built_absolutely(),
    )
    assert service._dt_required() == config.physics.dt_simu

    queue = service.subscribe()
    service.handle_command(
        MsgspecIO.encode_json(
            {"type": "set_speed", "speed_multiplier": 2.0},
        ),
        queue,
    )

    assert service._dt_required() == config.physics.dt_simu / 2.0


def test_service_starts_paused_and_allocates_run_on_resume(tmp_path: Path) -> None:
    project_paths = ProjectPaths(root_path=tmp_path)
    config = load_experiment(ProjectPaths.built_absolutely().params)
    service = server_module.SimulationService(
        build_simulation(config),
        config,
        project_paths,
    )

    initial_status = MsgspecIO.decode_json(service.current_status(), type=StatusMessage)
    assert initial_status.paused is True
    assert initial_status.run_started is False
    assert initial_status.snapshot_hz_render == config.render.snapshot_hz_render
    assert initial_status.snapshot_hz_render_real == 0.0

    queue = service.subscribe()
    service.handle_command(MsgspecIO.encode_json({"type": "toggle_pause"}), queue)
    resumed_status = MsgspecIO.decode_json(queue.get_nowait(), type=StatusMessage)

    assert resumed_status.paused is False
    assert resumed_status.run_started is True
    assert len(tuple((tmp_path / "run_results").iterdir())) == 1


def test_service_does_not_step_before_resume(tmp_path: Path) -> None:
    project_paths = ProjectPaths(root_path=tmp_path)
    config = load_experiment(ProjectPaths.built_absolutely().params)
    service = server_module.SimulationService(
        build_simulation(config),
        config,
        project_paths,
    )

    async def _exercise() -> None:
        task = asyncio.create_task(service.run())
        await asyncio.sleep(0)
        assert service._core.state.tick == 0
        service.handle_command(
            MsgspecIO.encode_json({"type": "toggle_pause"}),
            service.subscribe(),
        )
        await asyncio.sleep(0)
        assert service._core.state.tick >= 1
        await service.stop()
        await task

    asyncio.run(_exercise())
