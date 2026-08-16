"""environment、spatial、physics各Systemの抽象契約(Protocol)を定義する。

backend実装はこれらの契約に依存し、逆方向の依存は持たない。
"""

from __future__ import annotations

from typing import Protocol, TypeVar

_EnvironmentStateT = TypeVar("_EnvironmentStateT", contravariant=True)
_SpatialStateT = TypeVar("_SpatialStateT", contravariant=True)
_PhysicsStateT = TypeVar("_PhysicsStateT")


class EnvironmentSystem(Protocol[_EnvironmentStateT]):
    def update(self, state: _EnvironmentStateT, dt: float) -> None: ...


class SpatialSystem(Protocol[_SpatialStateT]):
    def update(self, state: _SpatialStateT) -> None: ...

    def pairs(self, state: _SpatialStateT) -> tuple[tuple[int, int], ...]: ...


class PhysicsSystem(Protocol[_PhysicsStateT]):
    def step(
        self,
        state: _PhysicsStateT,
        spatial: SpatialSystem[_PhysicsStateT],
        dt: float,
    ) -> None: ...
