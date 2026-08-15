from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import cast

import yaml

from alife.config.schema import ExecutionConfig, ExperimentConfig, PhysicsConfig, WorldConfig


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return cast(Mapping[str, object], value)


def _float(data: Mapping[str, object], key: str) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be a number")
    return float(value)


def _int(data: Mapping[str, object], key: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _string(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _positive(value: float, name: str) -> None:
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")


def _validate(config: ExperimentConfig) -> None:
    _positive(config.world.width, "world.width")
    _positive(config.world.height, "world.height")
    if config.world.particle_count < 1:
        raise ValueError("world.particle_count must be positive")
    _positive(config.world.particle_radius, "world.particle_radius")
    if config.world.particle_radius * 2.0 >= min(config.world.width, config.world.height):
        raise ValueError("particle radius is too large for the world")
    if config.world.initial_speed < 0.0:
        raise ValueError("world.initial_speed must not be negative")

    _positive(config.physics.dt, "physics.dt")
    _positive(config.physics.max_speed, "physics.max_speed")
    if config.physics.drag < 0.0:
        raise ValueError("physics.drag must not be negative")
    _positive(config.physics.repulsion_strength, "physics.repulsion_strength")
    _positive(config.physics.interaction_radius, "physics.interaction_radius")
    if not 0.0 <= config.physics.restitution <= 1.0:
        raise ValueError("physics.restitution must be between 0 and 1")
    if config.execution.steps < 1:
        raise ValueError("execution.steps must be positive")
    if config.execution.snapshot_hz < 0.0:
        raise ValueError("execution.snapshot_hz must not be negative")
    if config.execution.compute_backend != "numpy":
        raise ValueError("only the numpy backend is available")
    if config.execution.renderer not in {"none", "web"}:
        raise ValueError("renderer must be none or web")


def load_experiment(path: Path) -> ExperimentConfig:
    raw_value = yaml.safe_load(path.read_text(encoding="utf-8"))
    root = _mapping(raw_value, "experiment")
    world_data = _mapping(root.get("world"), "world")
    execution_data = _mapping(root.get("execution"), "execution")

    params_reference = root.get("physics_params")
    if not isinstance(params_reference, str):
        raise ValueError("physics_params must be a relative YAML path")
    params_path = (path.parent / params_reference).resolve()
    params_root = _mapping(
        yaml.safe_load(params_path.read_text(encoding="utf-8")), "physics params"
    )

    config = ExperimentConfig(
        world=WorldConfig(
            width=_float(world_data, "width"),
            height=_float(world_data, "height"),
            particle_count=_int(world_data, "particle_count"),
            particle_radius=_float(world_data, "particle_radius"),
            initial_speed=_float(world_data, "initial_speed"),
        ),
        physics=PhysicsConfig(
            dt=_float(params_root, "dt"),
            max_speed=_float(params_root, "max_speed"),
            drag=_float(params_root, "drag"),
            repulsion_strength=_float(params_root, "repulsion_strength"),
            interaction_radius=_float(params_root, "interaction_radius"),
            restitution=_float(params_root, "restitution"),
        ),
        execution=ExecutionConfig(
            seed=_int(execution_data, "seed"),
            steps=_int(execution_data, "steps"),
            snapshot_hz=_float(execution_data, "snapshot_hz"),
            compute_backend=_string(execution_data, "compute_backend"),
            renderer=_string(execution_data, "renderer"),
        ),
    )
    _validate(config)
    return config
