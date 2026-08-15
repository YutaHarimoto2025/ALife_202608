from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from alife.config.schema import ExperimentConfig
from alife.core.state import WorldState

NumpyArray = npt.NDArray[Any]
NumpyWorldState = WorldState[NumpyArray]


def create_state(config: ExperimentConfig) -> NumpyWorldState:
    world = config.world
    rng = np.random.default_rng(config.execution.seed)
    lower = np.array([world.particle_radius, world.particle_radius], dtype=np.float64)
    upper = np.array(
        [world.width - world.particle_radius, world.height - world.particle_radius],
        dtype=np.float64,
    )
    position = rng.uniform(lower, upper, size=(world.particle_count, 2)).astype(np.float64)
    angles = rng.uniform(0.0, 2.0 * np.pi, size=world.particle_count)
    speeds = rng.uniform(0.25, 1.0, size=world.particle_count) * world.initial_speed
    velocity = np.column_stack((np.cos(angles) * speeds, np.sin(angles) * speeds)).astype(
        np.float64
    )
    radius = np.full(world.particle_count, world.particle_radius, dtype=np.float64)
    mass = np.maximum(radius * radius, np.finfo(np.float64).eps)
    alive = np.ones(world.particle_count, dtype=bool)
    species = np.zeros(world.particle_count, dtype=np.uint16)
    return WorldState[NumpyArray](
        width=world.width,
        height=world.height,
        position=position,
        velocity=velocity,
        radius=radius,
        mass=mass,
        alive=alive,
        species=species,
    )
