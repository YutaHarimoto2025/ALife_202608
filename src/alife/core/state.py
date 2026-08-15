from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

ArrayT = TypeVar("ArrayT")


@dataclass(slots=True)
class WorldState[ArrayT]:
    """Backend-independent meaning of the particle state."""

    width: float
    height: float
    position: ArrayT
    velocity: ArrayT
    radius: ArrayT
    mass: ArrayT
    alive: ArrayT
    species: ArrayT
    tick: int = 0
