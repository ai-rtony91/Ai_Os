from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_owner_run_live_microtrade_result_capture_epic_v1 import (  # noqa: E402
    build_sample_breakeven_result_input,
    build_sample_loss_result_input,
    build_sample_missing_owner_result_input,
    build_sample_profit_result_input,
    build_sample_unsafe_result_input,
    run_oanda_owner_run_live_microtrade_result_capture_epic,
    to_jsonable_dict,
    to_markdown,
    to_operator_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview owner-run live microtrade result capture epic."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument("--sample-profit", action="store_true")
    sample_group.add_argument("--sample-loss", action="store_true")
    sample_group.add_argument("--sample-breakeven", action="store_true")
    sample_group.add_argument("--sample-missing", action="store_true")
    sample_group.add_argument("--sample-unsafe", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument("--markdown", action="store_true")
    return parser.parse_args()


def _select_sample(args: argparse.Namespace):
    if args.sample_loss:
        return build_sample_loss_result_input()
    if args.sample_breakeven:
        return build_sample_breakeven_result_input()
    if args.sample_missing:
        return build_sample_missing_owner_result_input()
    if args.sample_unsafe:
        return build_sample_unsafe_result_input()
    return build_sample_profit_result_input()


def main() -> int:
    args = parse_args()
    result = run_oanda_owner_run_live_microtrade_result_capture_epic(_select_sample(args))
    if args.json:
        print(json.dumps(to_jsonable_dict(result), indent=2))
    elif args.markdown:
        print(to_markdown(result), end="")
    else:
        print(to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

