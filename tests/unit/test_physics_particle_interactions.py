import numpy as np

from alife.backends.numpy._physics import NumpyParticlePhysics
from alife.backends.numpy._spatial import NumpySpatialIndex
from alife.backends.numpy.state import NumpyWorldState
from alife.config.schema import PhysicsConfig


def _state() -> NumpyWorldState:
    return NumpyWorldState(
        width_simu=100.0,
        height_simu=100.0,
        position=np.array([[10.0, 50.0], [20.0, 50.0]], dtype=np.float64),
        velocity=np.array([[10.0, 0.0], [-10.0, 0.0]], dtype=np.float64),
        radius=np.array([2.0, 2.0], dtype=np.float64),
        mass=np.array([1.0, 1.0], dtype=np.float64),
        alive=np.array([True, True]),
        species=np.array([0, 0], dtype=np.uint16),
    )


def test_physics_respects_max_speed_and_updates_position() -> None:
    state = _state()
    physics = NumpyParticlePhysics(
        PhysicsConfig(
            dt_simu=0.1,
            max_speed_simu=5.0,
            drag_simu=0.0,
            repulsion_strength_simu=1.0,
            interaction_radius_simu=1.0,
            restitution_simu=1.0,
        )
    )
    spatial = NumpySpatialIndex(cell_size=10.0)
    spatial.update(state)

    physics.step(state, spatial, 0.1)

    assert np.all(np.linalg.norm(state.velocity, axis=1) <= 5.0)
    np.testing.assert_allclose(state.position, [[10.5, 50.0], [19.5, 50.0]])


def test_spatial_index_returns_only_same_or_neighbor_cells() -> None:
    state = _state()
    spatial = NumpySpatialIndex(cell_size=10.0)
    spatial.update(state)

    assert spatial.pairs(state) == ((0, 1),)
