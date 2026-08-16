from pathlib import Path

import numpy as np

from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.config.schema import FrontendUiConfig, WorldConfig
from alife.runtime.factory import build_simulation
from alife.runtime.run_results import RunMetadata, RunResultsWriter, load_state
from utils.file_io.msgspec_io import MsgspecIO

_ROOT = ProjectPaths.built_absolutely()


def test_run_results_save_contains_resolved_params_and_restartable_state(
    tmp_path: Path,
) -> None:
    config = load_experiment(_ROOT.params)
    core = build_simulation(config)
    core.step()
    writer = RunResultsWriter(ProjectPaths(root_path=tmp_path), config)
    writer.start()

    state_path = writer.save(core.state)

    run_dir = state_path.parent
    assert state_path.name == "state_1.msgpack"
    assert len(run_dir.name) == 15
    assert run_dir.name[8] == "_"
    metadata = MsgspecIO.read_json(run_dir / "metadata.json", type=RunMetadata)
    assert metadata.run_id == run_dir.name
    assert metadata.git_commit_hash
    assert metadata.headless is False
    assert not hasattr(metadata, "params_dir")
    assert MsgspecIO.read_yaml(run_dir / "params/world.yaml", type=WorldConfig) == config.world
    assert (
        MsgspecIO.read_yaml(
            run_dir / "params/frontend_ui.yaml",
            type=FrontendUiConfig,
        )
        == config.frontend_ui
    )

    checkpoint = load_state(state_path)
    assert checkpoint.tick == core.state.tick
    np.testing.assert_array_equal(checkpoint.position, core.state.position)
    np.testing.assert_array_equal(checkpoint.velocity, core.state.velocity)

    resumed_core = build_simulation(config, state=checkpoint)
    core.step()
    resumed_core.step()
    np.testing.assert_array_equal(resumed_core.state.position, core.state.position)
    np.testing.assert_array_equal(resumed_core.state.velocity, core.state.velocity)
    assert resumed_core.state.tick == core.state.tick
