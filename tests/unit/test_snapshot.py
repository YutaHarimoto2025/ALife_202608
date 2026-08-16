from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.api.server import snapshot_to_json
from alife.runtime.factory import build_simulation


def test_web_snapshot_contains_render_fields_only() -> None:
    config = load_experiment(ProjectPaths.built_absolutely().params)
    core = build_simulation(config)

    payload = snapshot_to_json(core.snapshot())

    assert set(payload) == {"tick", "width", "height", "particles"}
    assert len(payload["particles"]) == config.world.particle_count
