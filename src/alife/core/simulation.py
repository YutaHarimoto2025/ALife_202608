"""semanticなtick順序を制御する SimulationCore を定義する。

1 tickの処理順序は environment更新 → spatial更新 → physics更新 → tick加算。
具体的なbackendを知らず、Systemはすべてconstructorから注入される。
"""

from __future__ import annotations

from typing import Protocol, TypeVar

from alife.core.interfaces import EnvironmentSystem, PhysicsSystem, SpatialSystem


class TickState(Protocol):
    tick: int


_StateT = TypeVar("_StateT", bound=TickState)


class SimulationCore[_StateT: TickState]:  # noqa: UP049
    """Owns semantic tick order without knowing the concrete backend."""

    def __init__(
        self,
        state: _StateT,
        environment: EnvironmentSystem[_StateT],
        spatial: SpatialSystem[_StateT],
        physics: PhysicsSystem[_StateT],
        dt_simu: float,
    ) -> None:
        self.state = state
        self._environment = environment
        self._spatial = spatial
        self._physics = physics
        self.dt_simu = dt_simu

    def step(self) -> None:
        self._environment.update(self.state, self.dt_simu)
        self._spatial.update(self.state)
        self._physics.step(self.state, self._spatial, self.dt_simu)
        self._increment_tick()

    def _increment_tick(self) -> None:
        self.state.tick += 1
