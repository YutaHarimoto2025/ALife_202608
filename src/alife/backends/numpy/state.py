"""NumPy配列によるSoA形式の NumpyWorldState と初期stateの生成。

seedは execution.yaml の共通乱数管理のものを使用する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt

from alife.config.schema import ExperimentConfig
from alife.core.state import WorldState

_NumpyArray = npt.NDArray[Any]


@dataclass(slots=True)
class NumpyWorldState(WorldState[_NumpyArray]):
    position: _NumpyArray
    velocity: _NumpyArray
    radius: _NumpyArray
    mass: _NumpyArray
    alive: _NumpyArray
    species: _NumpyArray
    tick: int = 0


def create_state(config: ExperimentConfig) -> NumpyWorldState:
    world = config.world
    rng = np.random.default_rng(config.execution.seed)
    lower = np.array(
        [world.particle_radius_simu, world.particle_radius_simu], dtype=np.float64
    )
    upper = np.array(
        [
            world.width_simu - world.particle_radius_simu,
            world.height_simu - world.particle_radius_simu,
        ],
        dtype=np.float64,
    )
    position = rng.uniform(lower, upper, size=(world.particle_count, 2)).astype(np.float64)
    angles = rng.uniform(0.0, 2.0 * np.pi, size=world.particle_count)
    speeds = rng.uniform(
        world.initial_speed_min_ratio,
        world.initial_speed_max_ratio,
        size=world.particle_count,
    ) * world.initial_speed_simu
    velocity = np.column_stack((np.cos(angles) * speeds, np.sin(angles) * speeds)).astype(
        np.float64
    )
    radius = np.full(world.particle_count, world.particle_radius_simu, dtype=np.float64)
    mass = np.maximum(radius * radius, np.finfo(np.float64).eps)
    alive = np.ones(world.particle_count, dtype=bool)
    species = np.zeros(world.particle_count, dtype=np.uint16)
    return NumpyWorldState(
        width_simu=world.width_simu,
        height_simu=world.height_simu,
        position=position,
        velocity=velocity,
        radius=radius,
        mass=mass,
        alive=alive,
        species=species,
    )
