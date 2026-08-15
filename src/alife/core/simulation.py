from __future__ import annotations

from typing import Protocol, TypeVar

from alife.core.interfaces import EnvironmentSystem, PhysicsSystem, Snapshotter, SpatialSystem
from alife.core.snapshot import RenderSnapshot


class TickState(Protocol):
    tick: int


StateT = TypeVar("StateT", bound=TickState)


class SimulationCore[StateT: TickState]:
    """Owns semantic tick order without knowing the concrete backend."""

    def __init__(
        self,
        state: StateT,
        environment: EnvironmentSystem[StateT],
        spatial: SpatialSystem[StateT],
        physics: PhysicsSystem[StateT],
        snapshotter: Snapshotter[StateT],
        dt: float,
    ) -> None:
        self.state = state
        self._environment = environment
        self._spatial = spatial
        self._physics = physics
        self._snapshotter = snapshotter
        self.dt = dt

    def step(self) -> None:
        self._environment.update(self.state, self.dt)
        self._spatial.update(self.state)
        self._physics.step(self.state, self._spatial, self.dt)
        self._increment_tick()

    def snapshot(self) -> RenderSnapshot:
        return self._snapshotter.snapshot(self.state)

    def _increment_tick(self) -> None:
        self.state.tick += 1
