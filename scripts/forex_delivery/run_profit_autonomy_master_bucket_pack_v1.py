"""CLI runner for the local-only Forex Profit Autonomy Master Bucket Pack V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.profit_autonomy_master_bucket_pack_v1 import (  # noqa: E402
    bucket_to_markdown,
    build_current_state_demo_review_path_ready,
    build_current_state_no_selector,
    build_current_state_selector_landed,
    build_current_state_selector_local_only,
    evaluate_master_bucket,
    next_stage_to_operator_packet_text,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the local-only AIOS Forex Profit Autonomy Master Bucket Pack V1."
    )
    state_group = parser.add_mutually_exclusive_group()
    state_group.add_argument(
        "--selector-local-only",
        action="store_true",
        help="Evaluate the current selector local-only dependency state.",
    )
    state_group.add_argument(
        "--selector-missing",
        action="store_true",
        help="Evaluate a state where the review-ready selector is missing.",
    )
    state_group.add_argument(
        "--selector-landed",
        action="store_true",
        help="Evaluate a state where the selector is landed but proof ledger is missing.",
    )
    state_group.add_argument(
        "--demo-review-path-ready",
        action="store_true",
        help="Evaluate a state where the governed demo review path is defined.",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON.",
    )
    output_group.add_argument(
        "--markdown",
        action="store_true",
        help="Print the readable bucket markdown artifact.",
    )
    output_group.add_argument(
        "--next-packet",
        action="store_true",
        help="Print a non-executable next-packet intent report.",
    )
    args = parser.parse_args(argv)

    out = stdout if stdout is not None else sys.stdout
    result = evaluate_master_bucket(_state_from_args(args))

    if args.json:
        print(json.dumps(result_to_jsonable_dict(result), indent=2, sort_keys=True), file=out)
    elif args.markdown:
        print(bucket_to_markdown(result), end="", file=out)
    elif args.next_packet:
        print(next_stage_to_operator_packet_text(result), end="", file=out)
    else:
        print(result_to_operator_text(result), end="", file=out)
    return 0


def _state_from_args(args: argparse.Namespace):
    if args.selector_missing:
        return build_current_state_no_selector()
    if args.selector_landed:
        return build_current_state_selector_landed()
    if args.demo_review_path_ready:
        return build_current_state_demo_review_path_ready()
    return build_current_state_selector_local_only()


if __name__ == "__main__":
    raise SystemExit(main())
