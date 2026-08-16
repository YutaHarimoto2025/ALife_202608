from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ParamsPaths:
    dir: Path

    @property
    def world(self) -> Path:
        return self.dir / "world.yaml"

    @property
    def physics(self) -> Path:
        return self.dir / "physics.yaml"

    @property
    def execution(self) -> Path:
        return self.dir / "execution.yaml"

    @property
    def headless(self) -> Path:
        return self.dir / "headless.yaml"

    @property
    def render(self) -> Path:
        return self.dir / "render.yaml"


@dataclass(frozen=True, slots=True)
class ResourcesPaths:
    dir: Path


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    root_path: Path

    @classmethod
    def built_absolutely(cls) -> ProjectPaths:
        return cls(root_path=_find_project_root(Path(__file__).resolve()))

    @property
    def params(self) -> ParamsPaths:
        return ParamsPaths(dir=self.root_path / "params")

    @property
    def resources(self) -> ResourcesPaths:
        return ResourcesPaths(dir=self.root_path / "resources")


def _find_project_root(start_path: Path) -> Path:
    directory = start_path if start_path.is_dir() else start_path.parent
    for candidate in (directory, *directory.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise FileNotFoundError("Could not find project root containing pyproject.toml")
