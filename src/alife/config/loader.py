from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import cast

import yaml

from alife.config.paths import ParamsPaths
from alife.config.schema import (
    ExecutionConfig,
    ExperimentConfig,
    HeadlessConfig,
    PhysicsConfig,
    RenderConfig,
    WorldConfig,
)


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


def _non_negative(value: float, name: str) -> None:
    if value < 0.0:
        raise ValueError(f"{name} must not be negative")


def _validate(config: ExperimentConfig) -> None:
    _positive(config.world.width_simu, "world.width_simu")
    _positive(config.world.height_simu, "world.height_simu")
    if config.world.particle_count < 1:
        raise ValueError("world.particle_count must be positive")
    _positive(config.world.particle_radius_simu, "world.particle_radius_simu")
    if config.world.particle_radius_simu * 2.0 >= min(
        config.world.width_simu, config.world.height_simu
    ):
        raise ValueError("particle radius is too large for the world")
    if config.world.initial_speed_simu < 0.0:
        raise ValueError("world.initial_speed_simu must not be negative")
    _non_negative(config.world.initial_speed_min_ratio, "world.initial_speed_min_ratio")
    _non_negative(config.world.initial_speed_max_ratio, "world.initial_speed_max_ratio")
    if config.world.initial_speed_min_ratio > config.world.initial_speed_max_ratio:
        raise ValueError("world.initial_speed_min_ratio must not exceed max ratio")

    _positive(config.physics.dt_simu, "physics.dt_simu")
    _positive(config.physics.max_speed_simu, "physics.max_speed_simu")
    if config.physics.drag_simu < 0.0:
        raise ValueError("physics.drag_simu must not be negative")
    _positive(config.physics.repulsion_strength_simu, "physics.repulsion_strength_simu")
    _positive(config.physics.interaction_radius_simu, "physics.interaction_radius_simu")
    if not 0.0 <= config.physics.restitution_simu <= 1.0:
        raise ValueError("physics.restitution_simu must be between 0 and 1")
    if config.headless.ticks_simu < 1:
        raise ValueError("headless.ticks_simu must be positive")
    if config.render.snapshot_hz_render < 0.0:
        raise ValueError("render.snapshot_hz_render must not be negative")
    if config.execution.compute_backend != "numpy":
        raise ValueError("only the numpy backend is available")


def _load_mapping(path: Path, name: str) -> Mapping[str, object]:
    return _mapping(yaml.safe_load(path.read_text(encoding="utf-8")), name)


def load_experiment(params: ParamsPaths) -> ExperimentConfig:
    world_data = _load_mapping(params.world, "world")
    physics_data = _load_mapping(params.physics, "physics")
    execution_data = _load_mapping(params.execution, "execution")
    headless_data = _load_mapping(params.headless, "headless")
    render_data = _load_mapping(params.render, "render")

    config = ExperimentConfig(
        world=WorldConfig(
            width_simu=_float(world_data, "width_simu"),
            height_simu=_float(world_data, "height_simu"),
            particle_count=_int(world_data, "particle_count"),
            particle_radius_simu=_float(world_data, "particle_radius_simu"),
            initial_speed_simu=_float(world_data, "initial_speed_simu"),
            initial_speed_min_ratio=_float(world_data, "initial_speed_min_ratio"),
            initial_speed_max_ratio=_float(world_data, "initial_speed_max_ratio"),
        ),
        physics=PhysicsConfig(
            dt_simu=_float(physics_data, "dt_simu"),
            max_speed_simu=_float(physics_data, "max_speed_simu"),
            drag_simu=_float(physics_data, "drag_simu"),
            repulsion_strength_simu=_float(physics_data, "repulsion_strength_simu"),
            interaction_radius_simu=_float(physics_data, "interaction_radius_simu"),
            restitution_simu=_float(physics_data, "restitution_simu"),
        ),
        execution=ExecutionConfig(
            seed=_int(execution_data, "seed"),
            compute_backend=_string(execution_data, "compute_backend"),
        ),
        headless=HeadlessConfig(
            ticks_simu=_int(headless_data, "ticks_simu"),
        ),
        render=RenderConfig(
            snapshot_hz_render=_float(render_data, "snapshot_hz_render"),
        ),
    )
    _validate(config)
    return config
