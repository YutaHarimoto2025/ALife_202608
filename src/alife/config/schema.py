"""params/ の各YAMLに対応する設定schema(dataclass)を定義する。"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorldConfig:
    width_simu: float
    height_simu: float
    particle_count: int
    particle_radius_simu: float
    initial_speed_simu: float
    initial_speed_min_ratio: float
    initial_speed_max_ratio: float


@dataclass(frozen=True, slots=True)
class PhysicsConfig:
    dt_simu: float
    max_speed_simu: float
    drag_simu: float
    repulsion_strength_simu: float
    interaction_radius_simu: float
    restitution_simu: float


@dataclass(frozen=True, slots=True)
class ExecutionConfig:
    seed: int
    compute_backend: str


@dataclass(frozen=True, slots=True)
class HeadlessConfig:
    ticks_simu: int
    save_ticks_simu: tuple[int, ...] | None


@dataclass(frozen=True, slots=True)
class FrontendCameraConfig:
    min_scale: float
    max_scale: float
    pan_step: float


@dataclass(frozen=True, slots=True)
class FrontendWallConfig:
    thickness: float


@dataclass(frozen=True, slots=True)
class FrontendUiConfig:
    speed_multiplier_default: float
    speed_multiplier_min: float
    speed_multiplier_max: float
    speed_multiplier_step: float
    elapsed_average_window: int
    camera: FrontendCameraConfig
    wall: FrontendWallConfig
    show_particle_footprint: bool
    max_particle_footprint_points: int


@dataclass(frozen=True, slots=True)
class RenderConfig:
    snapshot_hz_render: float


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    world: WorldConfig
    physics: PhysicsConfig
    execution: ExecutionConfig
    headless: HeadlessConfig
    frontend_ui: FrontendUiConfig
    render: RenderConfig
