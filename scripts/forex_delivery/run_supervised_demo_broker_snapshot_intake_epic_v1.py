from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.supervised_demo_broker_snapshot_intake_epic_v1 import (
    build_sample_supervised_demo_snapshot_intake_blocked_input,
    build_sample_supervised_demo_snapshot_intake_ready_input,
    run_supervised_demo_broker_snapshot_intake_epic,
    supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict,
    supervised_demo_broker_snapshot_intake_epic_to_markdown,
    supervised_demo_broker_snapshot_intake_epic_to_operator_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local supervised demo broker snapshot intake epic sample.")
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument("--sample-ready", action="store_true", help="Use the deterministic review-ready sample.")
    sample.add_argument("--sample-blocked", action="store_true", help="Use the deterministic blocked sample.")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Emit JSON.")
    output.add_argument("--markdown", action="store_true", help="Emit markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sample_input = (
        build_sample_supervised_demo_snapshot_intake_blocked_input()
        if args.sample_blocked
        else build_sample_supervised_demo_snapshot_intake_ready_input()
    )
    result = run_supervised_demo_broker_snapshot_intake_epic(sample_input)
    if args.json:
        print(json.dumps(supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(result), indent=2, sort_keys=True))
    elif args.markdown:
        print(supervised_demo_broker_snapshot_intake_epic_to_markdown(result))
    else:
        print(supervised_demo_broker_snapshot_intake_epic_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
