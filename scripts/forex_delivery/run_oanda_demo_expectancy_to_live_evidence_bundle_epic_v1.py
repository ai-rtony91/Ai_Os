from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_expectancy_to_live_evidence_bundle_epic_v1 import (  # noqa: E402
    build_sample_blocked_expectancy_epic_input,
    build_sample_missing_live_evidence_epic_input,
    build_sample_partial_live_evidence_epic_input,
    build_sample_ready_live_gap_review_epic_input,
    build_sample_unsafe_live_evidence_epic_input,
    oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict,
    oanda_demo_expectancy_to_live_evidence_bundle_epic_to_markdown,
    oanda_demo_expectancy_to_live_evidence_bundle_epic_to_operator_text,
    run_oanda_demo_expectancy_to_live_evidence_bundle_epic,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview OANDA demo expectancy to live evidence bundle gap epic."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument("--sample-missing-live-evidence", action="store_true")
    sample_group.add_argument("--sample-partial-live-evidence", action="store_true")
    sample_group.add_argument("--sample-ready-gap-review", action="store_true")
    sample_group.add_argument("--sample-blocked-expectancy", action="store_true")
    sample_group.add_argument("--sample-unsafe", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument("--markdown", action="store_true")
    return parser.parse_args()


def _select_sample(args: argparse.Namespace):
    if args.sample_partial_live_evidence:
        return build_sample_partial_live_evidence_epic_input()
    if args.sample_ready_gap_review:
        return build_sample_ready_live_gap_review_epic_input()
    if args.sample_blocked_expectancy:
        return build_sample_blocked_expectancy_epic_input()
    if args.sample_unsafe:
        return build_sample_unsafe_live_evidence_epic_input()
    return build_sample_missing_live_evidence_epic_input()


def main() -> int:
    args = parse_args()
    result = run_oanda_demo_expectancy_to_live_evidence_bundle_epic(_select_sample(args))
    if args.json:
        print(
            json.dumps(
                oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(result),
                indent=2,
            )
        )
    elif args.markdown:
        print(oanda_demo_expectancy_to_live_evidence_bundle_epic_to_markdown(result), end="")
    else:
        print(oanda_demo_expectancy_to_live_evidence_bundle_epic_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
