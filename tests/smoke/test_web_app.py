import pytest

from alife.api.server import create_app
from alife.config.paths import ProjectPaths


@pytest.mark.smoke
def test_web_app_exposes_health_and_websocket_routes() -> None:
    app = create_app(ProjectPaths.built_absolutely())
    paths = {getattr(route, "path", None) for route in app.routes}

    assert "/health" in paths
    assert "/ws" in paths
