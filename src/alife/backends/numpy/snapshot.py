from alife.backends.numpy.state import NumpyWorldState
from alife.core.snapshot import RenderSnapshot


class NumpySnapshotter:
    def snapshot(self, state: NumpyWorldState) -> RenderSnapshot:
        positions = tuple((float(x), float(y)) for x, y in state.position)
        radii = tuple(float(value) for value in state.radius)
        species = tuple(int(value) for value in state.species)
        alive = tuple(bool(value) for value in state.alive)
        return RenderSnapshot(
            tick=state.tick,
            width=state.width_simu,
            height=state.height_simu,
            positions=positions,
            radii=radii,
            species=species,
            alive=alive,
        )
