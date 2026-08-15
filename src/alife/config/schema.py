from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorldConfig:
    width: float
    height: float
    particle_count: int
    particle_radius: float
    initial_speed: float


@dataclass(frozen=True, slots=True)
class PhysicsConfig:
    dt: float
    max_speed: float
    drag: float
    repulsion_strength: float
    interaction_radius: float
    restitution: float


@dataclass(frozen=True, slots=True)
class ExecutionConfig:
    seed: int
    steps: int
    snapshot_hz: float
    compute_backend: str
    renderer: str


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    world: WorldConfig
    physics: PhysicsConfig
    execution: ExecutionConfig
