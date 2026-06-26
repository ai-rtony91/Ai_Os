from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_vacation_profit_live_sample_gate_v1 import (  # noqa: E402
    build_sample_compounding_blocked_input,
    build_sample_missing_autonomy_controls_input,
    build_sample_no_live_sample_input,
    build_sample_ready_for_review_input,
    build_sample_unsafe_input,
    evaluate_oanda_vacation_profit_live_sample_gate,
    to_jsonable_dict,
    to_markdown,
    to_operator_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview OANDA vacation profit live sample gate."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument("--sample-ready-review", action="store_true")
    sample_group.add_argument("--sample-no-live-sample", action="store_true")
    sample_group.add_argument("--sample-missing-autonomy", action="store_true")
    sample_group.add_argument("--sample-compounding-blocked", action="store_true")
    sample_group.add_argument("--sample-unsafe", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument("--markdown", action="store_true")
    return parser.parse_args()


def _select_sample(args: argparse.Namespace):
    if args.sample_no_live_sample:
        return build_sample_no_live_sample_input()
    if args.sample_missing_autonomy:
        return build_sample_missing_autonomy_controls_input()
    if args.sample_compounding_blocked:
        return build_sample_compounding_blocked_input()
    if args.sample_unsafe:
        return build_sample_unsafe_input()
    return build_sample_ready_for_review_input()


def main() -> int:
    args = parse_args()
    result = evaluate_oanda_vacation_profit_live_sample_gate(_select_sample(args))
    if args.json:
        print(json.dumps(to_jsonable_dict(result), indent=2))
    elif args.markdown:
        print(to_markdown(result), end="")
    else:
        print(to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

