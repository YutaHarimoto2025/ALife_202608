from alife.backends.numpy.state import NumpyWorldState


class NumpyEnvironment:
    def update(self, state: NumpyWorldState, dt: float) -> None:
        del state, dt
