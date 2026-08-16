"""環境Systemの何もしない実装。tick順序を保つためのplaceholder。"""

from alife.backends.numpy.state import NumpyWorldState


class NumpyEnvironment:
    def update(self, state: NumpyWorldState, dt: float) -> None:
        del state, dt
