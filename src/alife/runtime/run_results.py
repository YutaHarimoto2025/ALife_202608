"""run_results/ へのrun単位の保存を担う。

runディレクトリの作成、解決済みparamsとmetadataの書き出し、
stateのmsgpack保存(checkpoint)を行う。
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from alife.backends.numpy.state import NumpyWorldState
from alife.config.paths import ProjectPaths
from alife.config.schema import ExperimentConfig
from utils.file_io.msgspec_io import MsgspecIO

_RUN_METADATA_SCHEMA_VERSION = 2


@dataclass(frozen=True, slots=True)
class RunMetadata:
    run_id: str
    created_at: str
    git_commit_hash: str
    headless: bool
    description: str | None
    schema_version: int = _RUN_METADATA_SCHEMA_VERSION


class RunResultsWriter:
    def __init__(
        self,
        project_paths: ProjectPaths,
        config: ExperimentConfig,
        *,
        headless: bool = False,
        description: str | None = None,
    ) -> None:
        self._project_paths = project_paths
        self._config = config
        self._headless = headless
        self._description = description
        self._git_commit_hash = _read_git_commit_hash(project_paths.root_path)
        self._run_dir: Path | None = None

    @property
    def started(self) -> bool:
        return self._run_dir is not None

    def start(self) -> Path:
        if self._run_dir is None:
            self._run_dir = self._create_run_dir()
        return self._run_dir

    def start_new(self) -> Path:
        self._run_dir = self._create_run_dir()
        return self._run_dir

    def save(self, state: NumpyWorldState) -> Path:
        if self._run_dir is None:
            raise RuntimeError("run results are not started")
        return MsgspecIO.write_msgpack(
            self._run_dir / f"state_{state.tick}.msgpack",
            state,
        )

    def _create_run_dir(self) -> Path:
        created_at = datetime.now()
        run_id = created_at.strftime("%Y%m%d_%H%M%S")
        run_dir = _create_unique_directory(self._project_paths.run_results.dir, run_id)
        params_dir = run_dir / "params"
        params_dir.mkdir()
        for filename, value in (
            ("world.yaml", self._config.world),
            ("physics.yaml", self._config.physics),
            ("execution.yaml", self._config.execution),
            ("headless.yaml", self._config.headless),
            ("frontend_ui.yaml", self._config.frontend_ui),
            ("render.yaml", self._config.render),
        ):
            MsgspecIO.write_yaml(params_dir / filename, value)
        MsgspecIO.write_json(
            run_dir / "metadata.json",
            RunMetadata(
                run_id=run_dir.name,
                created_at=created_at.isoformat(timespec="seconds"),
                git_commit_hash=self._git_commit_hash,
                headless=self._headless,
                description=self._description,
            ),
        )
        return run_dir


def load_state(path: Path) -> NumpyWorldState:
    return MsgspecIO.read_msgpack(path, type=NumpyWorldState)


def _create_unique_directory(parent_dir: Path, base_name: str) -> Path:
    parent_dir.mkdir(parents=True, exist_ok=True)
    for suffix in range(1, 10_001):
        directory_name = base_name if suffix == 1 else f"{base_name}_{suffix}"
        candidate = parent_dir / directory_name
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError(f"could not allocate run directory for {base_name!r}")


def _read_git_commit_hash(root_path: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root_path,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
