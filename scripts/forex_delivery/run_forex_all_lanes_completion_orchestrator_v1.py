"""CLI runner for the Forex all-lanes completion orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_all_lanes_completion_orchestrator_v1 as orchestrator_lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Forex all-lanes completion orchestrator")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def run_cli(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    result = orchestrator_lib.run_all_lanes_completion_orchestrator(
        repo_root=repo_root,
        strict=args.strict,
    )
    output = (
        json.dumps(orchestrator_lib.orchestrator_to_jsonable_dict(result), indent=2, sort_keys=True)
        if args.json
        else orchestrator_lib.orchestrator_to_markdown(result)
    )
    if args.write_report:
        orchestrator_lib.write_orchestrator_reports(result, repo_root=repo_root)
    return output


def main() -> None:
    print(run_cli())


if __name__ == "__main__":
    main()
