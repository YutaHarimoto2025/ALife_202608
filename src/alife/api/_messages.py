"""frontendと交わすWebSocket messageのschemaと、stateからの変換。"""

from __future__ import annotations

from dataclasses import dataclass

from alife.backends.numpy.state import NumpyWorldState


@dataclass(frozen=True, slots=True)
class _ParticleMessage:
    x: float
    y: float
    radius: float
    species: int
    alive: bool


@dataclass(frozen=True, slots=True)
class SnapshotMessage:
    tick: int
    width: float
    height: float
    particles: tuple[_ParticleMessage, ...]
    type: str = "snapshot"


@dataclass(frozen=True, slots=True)
class StatusMessage:
    paused: bool
    compute_backend: str
    speed_multiplier: float
    speed_multiplier_min: float
    speed_multiplier_max: float
    speed_multiplier_step: float
    tick: int
    dt_simu: float
    dt_required: float
    elapsed_average: float
    snapshot_hz_render: float
    snapshot_hz_render_real: float
    performance: str
    run_results_enabled: bool
    run_started: bool
    type: str = "status"


@dataclass(frozen=True, slots=True)
class SaveResultMessage:
    tick: int
    path: str
    type: str = "save_result"


@dataclass(frozen=True, slots=True)
class ErrorMessage:
    message: str
    type: str = "error"


@dataclass(frozen=True, slots=True)
class CommandMessage:
    type: str
    speed_multiplier: float | None = None


def snapshot_to_message(state: NumpyWorldState) -> SnapshotMessage:
    return SnapshotMessage(
        tick=state.tick,
        width=state.width_simu,
        height=state.height_simu,
        particles=tuple(
            _ParticleMessage(
                x=float(position[0]),
                y=float(position[1]),
                radius=float(radius),
                species=int(species),
                alive=bool(alive),
            )
            for position, radius, species, alive in zip(
                state.position,
                state.radius,
                state.species,
                state.alive,
                strict=True,
            )
        ),
    )
