"""粒子の物理更新。drag、近接粒子間の反発、max_speed制限、壁での反射を適用する。

相互作用のpair列挙は SpatialSystem から受け取る。
"""

from __future__ import annotations

from typing import cast

import numpy as np
import numpy.typing as npt

from alife.backends.numpy.state import NumpyWorldState
from alife.config.schema import PhysicsConfig
from alife.core.interfaces import SpatialSystem


class NumpyParticlePhysics:
    def __init__(self, config: PhysicsConfig) -> None:
        self._config = config

    def step(
        self,
        state: NumpyWorldState,
        spatial: SpatialSystem[NumpyWorldState],
        dt: float,
    ) -> None:
        position = cast(npt.NDArray[np.float64], state.position)
        velocity = cast(npt.NDArray[np.float64], state.velocity)
        mass = cast(npt.NDArray[np.float64], state.mass)
        force = -self._config.drag_simu * velocity.copy()
        for first, second in spatial.pairs(state):
            delta: npt.NDArray[np.float64] = position[first] - position[second]
            distance = float(np.linalg.norm(delta))
            if distance == 0.0:
                direction: npt.NDArray[np.float64] = (
                    np.array((1.0, 0.0), dtype=np.float64)
                    if first % 2 == 0
                    else np.array((0.0, 1.0), dtype=np.float64)
                )
                distance = 1.0
            else:
                direction = delta / distance
            if distance >= self._config.interaction_radius_simu:
                continue
            strength = self._config.repulsion_strength_simu * (
                1.0 - distance / self._config.interaction_radius_simu
            )
            force[first] += direction * strength
            force[second] -= direction * strength

        velocity += dt * force / mass[:, None]
        speed = np.linalg.norm(velocity, axis=1)
        moving = speed > self._config.max_speed_simu
        velocity[moving] *= self._config.max_speed_simu / speed[moving, None]
        position += dt * velocity
        self._reflect_at_bounds(state)

    def _reflect_at_bounds(self, state: NumpyWorldState) -> None:
        position = cast(npt.NDArray[np.float64], state.position)
        velocity = cast(npt.NDArray[np.float64], state.velocity)
        radius = cast(npt.NDArray[np.float64], state.radius)
        for axis, limit in enumerate((state.width_simu, state.height_simu)):
            lower = position[:, axis] < radius
            upper = position[:, axis] > limit - radius
            position[lower, axis] = radius[lower]
            position[upper, axis] = limit - radius[upper]
            velocity[lower, axis] = (
                np.abs(velocity[lower, axis]) * self._config.restitution_simu
            )
            velocity[upper, axis] = (
                -np.abs(velocity[upper, axis]) * self._config.restitution_simu
            )
