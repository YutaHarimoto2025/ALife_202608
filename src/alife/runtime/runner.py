"""指定tick数だけsimulationを実行する、headless用のrunner。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from alife.core.simulation import SimulationCore, TickState

_StateT = TypeVar("_StateT", bound=TickState)


@dataclass(frozen=True, slots=True)
class _RunResult:
    ticks_simu: int


class SimulationRunner[_StateT: TickState]:  # noqa: UP049
    def __init__(self, core: SimulationCore[_StateT]) -> None:
        self._core = core

    def run(
        self,
        ticks_simu: int,
        on_tick: Callable[[_StateT], None] | None = None,
    ) -> _RunResult:
        for _ in range(ticks_simu):
            self._core.step()
            if on_tick is not None:
                on_tick(self._core.state)
        return _RunResult(ticks_simu=ticks_simu)
