"""CLI runner for the local-only AIOS Forex review-ready candidate selector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.review_ready_candidate_selector_v1 import (  # noqa: E402
    build_sample_all_blocked_selector_input,
    build_sample_mixed_selector_input,
    result_to_jsonable_dict,
    result_to_operator_text,
    select_review_ready_candidate,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local-only AIOS Forex review-ready candidate selector."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument(
        "--sample-mixed",
        action="store_true",
        help="Evaluate the built-in mixed candidate selector sample.",
    )
    sample_group.add_argument(
        "--sample-all-blocked",
        action="store_true",
        help="Evaluate the built-in all-blocked candidate selector sample.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of operator text.",
    )
    args = parser.parse_args(argv)

    out = stdout if stdout is not None else sys.stdout
    selector_input = (
        build_sample_mixed_selector_input()
        if args.sample_mixed
        else build_sample_all_blocked_selector_input()
    )
    result = select_review_ready_candidate(selector_input)

    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
