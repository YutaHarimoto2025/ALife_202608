from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RenderSnapshot:
    tick: int
    width: float
    height: float
    positions: tuple[tuple[float, float], ...]
    radii: tuple[float, ...]
    species: tuple[int, ...]
    alive: tuple[bool, ...]
