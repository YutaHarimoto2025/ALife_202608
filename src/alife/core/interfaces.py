from __future__ import annotations

from typing import Protocol, TypeVar

from alife.core.snapshot import RenderSnapshot

EnvironmentStateT = TypeVar("EnvironmentStateT", contravariant=True)
SpatialStateT = TypeVar("SpatialStateT", contravariant=True)
PhysicsStateT = TypeVar("PhysicsStateT")
SnapshotStateT = TypeVar("SnapshotStateT", contravariant=True)


class EnvironmentSystem(Protocol[EnvironmentStateT]):
    def update(self, state: EnvironmentStateT, dt: float) -> None: ...


class SpatialSystem(Protocol[SpatialStateT]):
    def update(self, state: SpatialStateT) -> None: ...

    def pairs(self, state: SpatialStateT) -> tuple[tuple[int, int], ...]: ...


class PhysicsSystem(Protocol[PhysicsStateT]):
    def step(
        self,
        state: PhysicsStateT,
        spatial: SpatialSystem[PhysicsStateT],
        dt: float,
    ) -> None: ...


class Snapshotter(Protocol[SnapshotStateT]):
    def snapshot(self, state: SnapshotStateT) -> RenderSnapshot: ...
