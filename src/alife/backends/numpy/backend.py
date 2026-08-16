"""設定から NumpyWorldState と各Systemを組み立て、SimulationCore を生成する。"""

from alife.backends.numpy._environment import NumpyEnvironment
from alife.backends.numpy._physics import NumpyParticlePhysics
from alife.backends.numpy._spatial import NumpySpatialIndex
from alife.backends.numpy.state import NumpyWorldState, create_state
from alife.config.schema import ExperimentConfig
from alife.core.simulation import SimulationCore


class NumpyBackend:
    def build(
        self,
        config: ExperimentConfig,
        state: NumpyWorldState | None = None,
    ) -> SimulationCore[NumpyWorldState]:
        state = create_state(config) if state is None else state
        spatial = NumpySpatialIndex(config.physics.interaction_radius_simu)
        return SimulationCore(
            state=state,
            environment=NumpyEnvironment(),
            spatial=spatial,
            physics=NumpyParticlePhysics(config.physics),
            dt_simu=config.physics.dt_simu,
        )
