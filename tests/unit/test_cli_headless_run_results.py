import shutil
from pathlib import Path

from alife.config.paths import ProjectPaths
from cli.run_simulation import _run_headless

_ROOT = ProjectPaths.built_absolutely()


def test_headless_run_results_are_controlled_only_by_flag(tmp_path: Path) -> None:
    enabled_root = _copy_project_params(tmp_path / "enabled")
    _run_headless(
        ProjectPaths(root_path=enabled_root),
        no_run_results=False,
        description="test run",
    )

    run_dirs = tuple((enabled_root / "run_results").iterdir())
    assert len(run_dirs) == 1
    assert {path.name for path in run_dirs[0].glob("state_*.msgpack")} == {
        "state_0.msgpack",
        "state_500.msgpack",
        "state_1000.msgpack",
    }
    metadata = (run_dirs[0] / "metadata.json").read_text()
    assert '"headless": true' in metadata
    assert '"description": "test run"' in metadata

    disabled_root = _copy_project_params(tmp_path / "disabled")
    _run_headless(ProjectPaths(root_path=disabled_root), no_run_results=True)
    assert not (disabled_root / "run_results").exists()


def _copy_project_params(root: Path) -> Path:
    root.mkdir()
    shutil.copytree(_ROOT.params.dir, root / "params")
    return root
