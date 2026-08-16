from alife.backends.numpy.environment import NumpyEnvironment
from alife.backends.numpy.physics import NumpyParticlePhysics
from alife.backends.numpy.snapshot import NumpySnapshotter
from alife.backends.numpy.spatial import NumpySpatialIndex
from alife.backends.numpy.state import NumpyWorldState, create_state
from alife.config.schema import ExperimentConfig
from alife.core.simulation import SimulationCore


class NumpyBackend:
    def build(self, config: ExperimentConfig) -> SimulationCore[NumpyWorldState]:
        state = create_state(config)
        spatial = NumpySpatialIndex(config.physics.interaction_radius_simu)
        return SimulationCore(
            state=state,
            environment=NumpyEnvironment(),
            spatial=spatial,
            physics=NumpyParticlePhysics(config.physics),
            snapshotter=NumpySnapshotter(),
            dt_simu=config.physics.dt_simu,
        )
