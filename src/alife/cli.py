from __future__ import annotations

import argparse
from pathlib import Path

from alife.config.loader import load_experiment
from alife.runtime.factory import build_simulation
from alife.runtime.runner import SimulationRunner


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="alife")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="run a headless experiment")
    run.add_argument("experiment", type=Path)
    run.add_argument("--steps", type=int)

    server = subparsers.add_parser("server", help="serve an experiment over WebSocket")
    server.add_argument("experiment", type=Path)
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=8000)
    return parser


def _run_headless(experiment: Path, steps: int | None) -> None:
    config = load_experiment(experiment)
    core = build_simulation(config)
    result = SimulationRunner(core, snapshot_hz=0.0).run(steps or config.execution.steps)
    print(f"steps={result.steps} tick={core.state.tick} particles={len(core.state.alive)}")


def _run_server(experiment: Path, host: str, port: int) -> None:
    import uvicorn

    from alife.api.server import create_app

    uvicorn.run(create_app(experiment), host=host, port=port)


def main() -> None:
    args = _parser().parse_args()
    if args.command == "run":
        _run_headless(args.experiment, args.steps)
    else:
        _run_server(args.experiment, args.host, args.port)
