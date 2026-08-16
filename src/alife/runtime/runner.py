from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from alife.core.simulation import SimulationCore, TickState
from alife.core.snapshot import RenderSnapshot

StateT = TypeVar("StateT", bound=TickState)


@dataclass(frozen=True, slots=True)
class RunResult:
    ticks_simu: int
    snapshots: int


class SimulationRunner[StateT: TickState]:
    def __init__(self, core: SimulationCore[StateT], snapshot_hz_render: float) -> None:
        self._core = core
        self._snapshot_interval = self._interval(core.dt_simu, snapshot_hz_render)

    @staticmethod
    def _interval(dt_simu: float, snapshot_hz_render: float) -> int | None:
        if snapshot_hz_render <= 0.0:
            return None
        return max(1, round(1.0 / (dt_simu * snapshot_hz_render)))

    def run(
        self,
        ticks_simu: int,
        on_snapshot: Callable[[RenderSnapshot], None] | None = None,
    ) -> RunResult:
        snapshots = 0
        for _ in range(ticks_simu):
            self._core.step()
            if (
                on_snapshot is not None
                and self._snapshot_interval is not None
                and self._core.state.tick % self._snapshot_interval == 0
            ):
                on_snapshot(self._core.snapshot())
                snapshots += 1
        return RunResult(ticks_simu=ticks_simu, snapshots=snapshots)
