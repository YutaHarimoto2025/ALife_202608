from __future__ import annotations

from collections import defaultdict

import numpy as np

from alife.backends.numpy.state import NumpyWorldState

Cell = tuple[int, int]


class NumpySpatialIndex:
    def __init__(self, cell_size: float) -> None:
        self._cell_size = cell_size
        self._cells: dict[Cell, list[int]] = defaultdict(list)
        self._pairs: tuple[tuple[int, int], ...] = ()

    def update(self, state: NumpyWorldState) -> None:
        self._cells.clear()
        for index in np.flatnonzero(state.alive):
            position = state.position[int(index)]
            cell = (int(position[0] // self._cell_size), int(position[1] // self._cell_size))
            self._cells[cell].append(int(index))

        pairs: set[tuple[int, int]] = set()
        for cell, indices in self._cells.items():
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    neighbor_indices = self._cells.get((cell[0] + dx, cell[1] + dy), ())
                    for first in indices:
                        for second in neighbor_indices:
                            if first < second:
                                pairs.add((first, second))
        self._pairs = tuple(sorted(pairs))

    def pairs(self, state: NumpyWorldState) -> tuple[tuple[int, int], ...]:
        del state
        return self._pairs
