from pathlib import Path

from alife.config.loader import load_experiment
from alife.renderers.web import snapshot_to_json
from alife.runtime.factory import build_simulation

ROOT = Path(__file__).parents[2]


def test_web_snapshot_contains_render_fields_only() -> None:
    config = load_experiment(ROOT / "resources/experiments/minimal.yaml")
    core = build_simulation(config)

    payload = snapshot_to_json(core.snapshot())

    assert set(payload) == {"tick", "width", "height", "particles"}
    assert len(payload["particles"]) == config.world.particle_count
