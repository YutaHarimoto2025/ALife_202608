from pathlib import Path

import pytest

from alife.config.loader import load_experiment
from alife.runtime.factory import build_simulation
from alife.runtime.runner import SimulationRunner

ROOT = Path(__file__).parents[2]


@pytest.mark.smoke
def test_experiment_runs_headless() -> None:
    config = load_experiment(ROOT / "resources/experiments/minimal.yaml")
    core = build_simulation(config)

    result = SimulationRunner(core, config.execution.snapshot_hz).run(5)

    assert result.steps == 5
    assert core.state.tick == 5
