"""run-simulation command。--headless でheadless実行、既定でserverを起動する。"""

from __future__ import annotations

import argparse

import uvicorn

from alife.api.server import create_app
from alife.backends.numpy.state import NumpyWorldState
from alife.config.loader import load_experiment
from alife.config.paths import ProjectPaths
from alife.runtime.factory import build_simulation
from alife.runtime.run_results import RunResultsWriter
from alife.runtime.runner import SimulationRunner


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="run-simulation")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--description", default=None)
    parser.add_argument(
        "--no-run-results",
        action="store_true",
        help="disable run_results directory creation and state saving",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    paths = ProjectPaths.built_absolutely()
    if not args.headless:
        uvicorn.run(
            create_app(
                paths,
                run_results_enabled=not args.no_run_results,
                description=args.description,
            ),
            host=args.host,
            port=args.port,
        )
        return

    _run_headless(
        paths,
        no_run_results=args.no_run_results,
        description=args.description,
    )


def _run_headless(
    paths: ProjectPaths,
    *,
    no_run_results: bool,
    description: str | None = None,
) -> None:
    config = load_experiment(paths.params)
    core = build_simulation(config)
    run_results = (
        None
        if no_run_results
        else RunResultsWriter(
            paths,
            config,
            headless=True,
            description=description,
        )
    )
    if run_results is not None:
        run_results.start()
        if config.headless.save_ticks_simu is not None and 0 in config.headless.save_ticks_simu:
            run_results.save(core.state)

    save_ticks = set(config.headless.save_ticks_simu or ())

    def _save_tick(state: NumpyWorldState) -> None:
        if run_results is not None and state.tick in save_ticks:
            run_results.save(state)

    result = SimulationRunner(core).run(
        config.headless.ticks_simu,
        on_tick=_save_tick if run_results is not None else None,
    )
    print(f"ticks={result.ticks_simu} tick={core.state.tick} particles={len(core.state.alive)}")
