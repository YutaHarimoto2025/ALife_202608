from typing import Any

from alife.core.snapshot import RenderSnapshot


def snapshot_to_json(snapshot: RenderSnapshot) -> dict[str, Any]:
    return {
        "tick": snapshot.tick,
        "width": snapshot.width,
        "height": snapshot.height,
        "particles": [
            {
                "x": position[0],
                "y": position[1],
                "radius": radius,
                "species": species,
                "alive": alive,
            }
            for position, radius, species, alive in zip(
                snapshot.positions,
                snapshot.radii,
                snapshot.species,
                snapshot.alive,
                strict=True,
            )
        ],
    }
