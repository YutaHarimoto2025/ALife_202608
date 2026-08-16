import pytest

from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.runtime.factory import build_simulation
from alife.runtime.runner import SimulationRunner


@pytest.mark.smoke
def test_experiment_runs_headless() -> None:
    config = load_experiment(ProjectPaths.built_absolutely().params)
    core = build_simulation(config)

    result = SimulationRunner(core).run(5)

    assert result.ticks_simu == 5
    assert core.state.tick == 5
