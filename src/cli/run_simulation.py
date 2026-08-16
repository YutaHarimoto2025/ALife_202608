from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from alife.api.server import create_app
from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.runtime.factory import build_simulation
from alife.runtime.runner import SimulationRunner


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="run-simulation")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser


def main() -> None:
    args = _parser().parse_args()
    paths = (
        ProjectPaths.built_absolutely()
        if args.root is None
        else ProjectPaths.from_root(args.root)
    )
    if not args.headless:
        uvicorn.run(create_app(paths), host=args.host, port=args.port)
        return

    config = load_experiment(paths.params)
    core = build_simulation(config)
    result = SimulationRunner(core, snapshot_hz_render=0.0).run(config.headless.ticks_simu)
    print(f"ticks={result.ticks_simu} tick={core.state.tick} particles={len(core.state.alive)}")
