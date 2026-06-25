from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.sanitized_broker_snapshot_intake_v1 import (
    build_sample_blocked_snapshot_intake_input,
    build_sample_missing_fields_snapshot_intake_input,
    build_sample_sanitized_snapshot_intake_input,
    intake_sanitized_broker_snapshot,
    sanitized_snapshot_intake_to_jsonable_dict,
    sanitized_snapshot_intake_to_markdown,
    sanitized_snapshot_intake_to_operator_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local sanitized broker snapshot intake sample.")
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument("--sample-ready", action="store_true", help="Use the deterministic review-ready sample.")
    sample.add_argument("--sample-blocked", action="store_true", help="Use the deterministic blocked sample.")
    sample.add_argument(
        "--sample-missing-fields",
        action="store_true",
        help="Use the deterministic missing-fields sample.",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Emit JSON.")
    output.add_argument("--markdown", action="store_true", help="Emit markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.sample_blocked:
        sample_input = build_sample_blocked_snapshot_intake_input()
    elif args.sample_missing_fields:
        sample_input = build_sample_missing_fields_snapshot_intake_input()
    else:
        sample_input = build_sample_sanitized_snapshot_intake_input()

    result = intake_sanitized_broker_snapshot(sample_input)
    if args.json:
        print(json.dumps(sanitized_snapshot_intake_to_jsonable_dict(result), indent=2, sort_keys=True))
    elif args.markdown:
        print(sanitized_snapshot_intake_to_markdown(result))
    else:
        print(sanitized_snapshot_intake_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
