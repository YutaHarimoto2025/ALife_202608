from pathlib import Path

import pytest

from alife.config.loader import load_experiment
from alife.config.paths import ParamsPaths, ProjectPaths

_PROJECT = ProjectPaths.built_absolutely()


def test_minimal_experiment_is_valid() -> None:
    config = load_experiment(_PROJECT.params)

    assert config.world.particle_count == 100
    assert config.world.initial_speed_min_ratio == 0.25
    assert config.world.initial_speed_max_ratio == 1.0
    assert config.physics.dt_simu == 0.01
    assert config.execution.compute_backend == "numpy"
    assert config.headless.save_ticks_simu == (0, 500, 1000)
    assert config.frontend_ui.speed_multiplier_default == 1.0
    assert config.frontend_ui.max_particle_footprint_points == 24


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
        "ticks_simu: 1\nsave_ticks_simu: null\n",
        encoding="utf-8",
    )
    params.frontend_ui.write_text(
        "speed_multiplier_default: 1\n"
        "speed_multiplier_min: 0.1\n"
        "speed_multiplier_max: 10\n"
        "speed_multiplier_step: 0.1\n"
        "elapsed_average_window: 10\n"
        "camera:\n"
        "  min_scale: 0.2\n"
        "  max_scale: 8.0\n"
        "  pan_step: 30.0\n"
        "wall:\n"
        "  thickness: 8.0\n"
        "show_particle_footprint: false\n"
        "max_particle_footprint_points: 24\n",
        encoding="utf-8",
    )
    params.render.write_text(
        "snapshot_hz_render: 1\n",
        encoding="utf-8",
    )

    params.execution.write_text(
        "seed: 1\ncompute_backend: numpy\n",
        encoding="utf-8",
    )
    config = load_experiment(params)
    assert config.headless.save_ticks_simu is None

    params.execution.write_text(
        "seed: 1\ncompute_backend: cuda\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="numpy"):
        load_experiment(params)
