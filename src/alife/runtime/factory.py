from alife.backends.numpy.backend import NumpyBackend
from alife.backends.numpy.state import NumpyWorldState
from alife.config.schema import ExperimentConfig
from alife.core.simulation import SimulationCore


def build_simulation(config: ExperimentConfig) -> SimulationCore[NumpyWorldState]:
    if config.execution.compute_backend != "numpy":
        raise ValueError("only the numpy backend is available")
    return NumpyBackend().build(config)
