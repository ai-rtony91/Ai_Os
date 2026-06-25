"""CLI runner for the local-only AIOS Forex candidate evidence intake."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.candidate_evidence_intake_v1 import (  # noqa: E402
    build_sample_incomplete_candidate,
    build_sample_review_ready_candidate,
    evaluate_candidate_evidence_intake,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local-only AIOS Forex candidate evidence intake."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument(
        "--sample-incomplete",
        action="store_true",
        help="Evaluate the built-in incomplete candidate sample.",
    )
    sample_group.add_argument(
        "--sample-review-ready",
        action="store_true",
        help="Evaluate the built-in synthetic review-ready candidate sample.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of operator text.",
    )
    args = parser.parse_args(argv)

    out = stdout if stdout is not None else sys.stdout
    candidate = (
        build_sample_review_ready_candidate()
        if args.sample_review_ready
        else build_sample_incomplete_candidate()
    )
    result = evaluate_candidate_evidence_intake(candidate)

    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
