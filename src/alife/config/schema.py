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


@dataclass(frozen=True, slots=True)
class RenderConfig:
    snapshot_hz_render: float


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    world: WorldConfig
    physics: PhysicsConfig
    execution: ExecutionConfig
    headless: HeadlessConfig
    render: RenderConfig
