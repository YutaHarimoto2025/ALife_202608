"""params/ のYAML群を読み込み、検証済みの ExperimentConfig へ変換する。"""

from __future__ import annotations

from alife.config.paths import ParamsPaths
from alife.config.schema import (
    ExecutionConfig,
    ExperimentConfig,
    FrontendUiConfig,
    HeadlessConfig,
    PhysicsConfig,
    RenderConfig,
    WorldConfig,
)
from utils.file_io.msgspec_io import MsgspecIO


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
    save_ticks = config.headless.save_ticks_simu
    if save_ticks is not None:
        if any(tick < 0 or tick > config.headless.ticks_simu for tick in save_ticks):
            raise ValueError("headless.save_ticks_simu must be within ticks_simu")
        if tuple(sorted(set(save_ticks))) != save_ticks:
            raise ValueError("headless.save_ticks_simu must be sorted and unique")

    frontend_ui = config.frontend_ui
    _positive(frontend_ui.speed_multiplier_default, "frontend_ui.speed_multiplier_default")
    _positive(frontend_ui.speed_multiplier_min, "frontend_ui.speed_multiplier_min")
    _positive(frontend_ui.speed_multiplier_max, "frontend_ui.speed_multiplier_max")
    _positive(frontend_ui.speed_multiplier_step, "frontend_ui.speed_multiplier_step")
    if frontend_ui.speed_multiplier_min > frontend_ui.speed_multiplier_default:
        raise ValueError("frontend_ui.speed_multiplier_default must not be below min")
    if frontend_ui.speed_multiplier_default > frontend_ui.speed_multiplier_max:
        raise ValueError("frontend_ui.speed_multiplier_default must not exceed max")
    if frontend_ui.speed_multiplier_step > (
        frontend_ui.speed_multiplier_max - frontend_ui.speed_multiplier_min
    ):
        raise ValueError("frontend_ui.speed_multiplier_step is too large")
    if frontend_ui.elapsed_average_window < 1:
        raise ValueError("frontend_ui.elapsed_average_window must be positive")
    _positive(frontend_ui.camera.min_scale, "frontend_ui.camera.min_scale")
    _positive(frontend_ui.camera.max_scale, "frontend_ui.camera.max_scale")
    if frontend_ui.camera.min_scale > frontend_ui.camera.max_scale:
        raise ValueError("frontend_ui.camera.min_scale must not exceed max_scale")
    _positive(frontend_ui.camera.pan_step, "frontend_ui.camera.pan_step")
    _positive(frontend_ui.wall.thickness, "frontend_ui.wall.thickness")
    if frontend_ui.max_particle_footprint_points < 1:
        raise ValueError("frontend_ui.max_particle_footprint_points must be positive")
    if config.render.snapshot_hz_render < 0.0:
        raise ValueError("render.snapshot_hz_render must not be negative")
    if config.execution.compute_backend != "numpy":
        raise ValueError("only the numpy backend is available")


def load_experiment(params: ParamsPaths) -> ExperimentConfig:
    config = ExperimentConfig(
        world=MsgspecIO.read_yaml(params.world, type=WorldConfig),
        physics=MsgspecIO.read_yaml(params.physics, type=PhysicsConfig),
        execution=MsgspecIO.read_yaml(params.execution, type=ExecutionConfig),
        headless=MsgspecIO.read_yaml(params.headless, type=HeadlessConfig),
        frontend_ui=MsgspecIO.read_yaml(
            params.frontend_ui,
            type=FrontendUiConfig,
        ),
        render=MsgspecIO.read_yaml(params.render, type=RenderConfig),
    )
    _validate(config)
    return config
