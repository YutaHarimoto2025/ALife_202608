from alife.core.snapshot import RenderSnapshot


class NullRenderer:
    def render(self, snapshot: RenderSnapshot) -> None:
        del snapshot
