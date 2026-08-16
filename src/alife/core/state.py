"""backend非依存なparticle stateの抽象schema WorldState を定義する。

配列の実体(_ArrayT)はbackendごとに決まり、SoA形式で保持する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

_ArrayT = TypeVar("_ArrayT")


@dataclass(slots=True)
class WorldState[_ArrayT]:  # noqa: UP049
    """Backend-independent meaning of the particle state."""

    width_simu: float
    height_simu: float
    position: _ArrayT
    velocity: _ArrayT
    radius: _ArrayT
    mass: _ArrayT
    alive: _ArrayT
    species: _ArrayT
    tick: int = 0
