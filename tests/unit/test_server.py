import asyncio
from collections.abc import Iterator

import pytest

import alife.api.server as server_module
from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.runtime.factory import build_simulation


def test_service_sleeps_for_remaining_step_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = load_experiment(ProjectPaths.built_absolutely().params)
    service = server_module.SimulationService(
        build_simulation(config),
        snapshot_hz_render=0.0,
    )
    timestamps: Iterator[float] = iter((1.0, 1.005))
    sleep_durations: list[float] = []

    def fake_perf_counter() -> float:
        return next(timestamps)

    async def fake_sleep(delay: float) -> None:
        sleep_durations.append(delay)
        await service.stop()

    monkeypatch.setattr(server_module.time, "perf_counter", fake_perf_counter)
    monkeypatch.setattr(server_module.asyncio, "sleep", fake_sleep)

    asyncio.run(service.run())

    assert sleep_durations == [pytest.approx(0.005)]
