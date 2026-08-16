from pathlib import Path

import pytest

from alife.config.loader import load_experiment
from alife.config.paths import ParamsPaths, ProjectPaths

PROJECT = ProjectPaths.built_absolutely()


def test_minimal_experiment_is_valid() -> None:
    config = load_experiment(PROJECT.params)

    assert config.world.particle_count == 100
    assert config.world.initial_speed_min_ratio == 0.25
    assert config.world.initial_speed_max_ratio == 1.0
    assert config.physics.dt_simu == 0.01
    assert config.execution.compute_backend == "numpy"


def test_invalid_backend_is_rejected(tmp_path: Path) -> None:
    params = ParamsPaths(dir=tmp_path / "params")
    params.dir.mkdir()
    params.world.write_text(
        "width_simu: 100\nheight_simu: 100\nparticle_count: 2\n"
        "particle_radius_simu: 2\ninitial_speed_simu: 1\n"
        "initial_speed_min_ratio: 0.25\n"
        "initial_speed_max_ratio: 1.0\n",
        encoding="utf-8",
    )
    params.physics.write_text(
        "dt_simu: 0.01\nmax_speed_simu: 10\ndrag_simu: 0\n"
        "repulsion_strength_simu: 1\ninteraction_radius_simu: 10\n"
        "restitution_simu: 1\n",
        encoding="utf-8",
    )
    params.execution.write_text(
        "seed: 1\ncompute_backend: cuda\n",
        encoding="utf-8",
    )
    params.headless.write_text(
        "ticks_simu: 1\n",
        encoding="utf-8",
    )
    params.render.write_text(
        "snapshot_hz_render: 1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="numpy"):
        load_experiment(params)
