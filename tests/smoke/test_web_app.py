from pathlib import Path

import pytest

from alife.api.server import create_app

ROOT = Path(__file__).parents[2]


@pytest.mark.smoke
def test_web_app_exposes_health_and_websocket_routes() -> None:
    app = create_app(ROOT / "resources/experiments/minimal.yaml")
    paths = {getattr(route, "path", None) for route in app.routes}

    assert "/health" in paths
    assert "/ws" in paths
