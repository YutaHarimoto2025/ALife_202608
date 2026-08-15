from pathlib import Path

import pytest

from alife.config.loader import load_experiment

ROOT = Path(__file__).parents[2]
EXPERIMENT = ROOT / "resources/experiments/minimal.yaml"


def test_minimal_experiment_is_valid() -> None:
    config = load_experiment(EXPERIMENT)

    assert config.world.particle_count == 100
    assert config.physics.dt == 0.01
    assert config.execution.compute_backend == "numpy"


def test_invalid_backend_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "experiment.yaml"
    path.write_text(
        """world:
  width: 100
  height: 100
  particle_count: 2
  particle_radius: 2
  initial_speed: 1
physics_params: params.yaml
execution:
  seed: 1
  steps: 1
  snapshot_hz: 1
  compute_backend: cuda
  renderer: none
""",
        encoding="utf-8",
    )
    (tmp_path / "params.yaml").write_text(
        "dt: 0.01\nmax_speed: 10\ndrag: 0\nrepulsion_strength: 1\n"
        "interaction_radius: 10\nrestitution: 1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="numpy"):
        load_experiment(path)
