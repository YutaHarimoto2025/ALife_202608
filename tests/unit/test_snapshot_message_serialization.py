from alife.api._messages import SnapshotMessage, snapshot_to_message
from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.runtime.factory import build_simulation
from utils.file_io.msgspec_io import MsgspecIO


def test_web_snapshot_contains_render_fields_only() -> None:
    config = load_experiment(ProjectPaths.built_absolutely().params)
    core = build_simulation(config)

    payload = MsgspecIO.decode_json(
        MsgspecIO.encode_json(snapshot_to_message(core.state)),
        type=SnapshotMessage,
    )

    assert payload.type == "snapshot"
    assert payload.tick == 0
    assert len(payload.particles) == config.world.particle_count
