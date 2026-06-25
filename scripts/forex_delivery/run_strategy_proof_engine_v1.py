"""CLI runner for local-only AIOS Forex Strategy Proof Engine V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.strategy_proof_engine_v1 import (  # noqa: E402
    build_sample_all_blocked_strategy_evidence,
    build_sample_mixed_strategy_evidence,
    evaluate_strategy_proof_engine,
    result_to_jsonable_dict,
    result_to_operator_text,
    strategy_proof_to_markdown,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local-only AIOS Forex Strategy Proof Engine V1."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument(
        "--sample-mixed",
        action="store_true",
        help="Evaluate the built-in mixed strategy proof sample.",
    )
    sample_group.add_argument(
        "--sample-all-blocked",
        action="store_true",
        help="Evaluate the built-in all-blocked strategy proof sample.",
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
        help="Print readable markdown.",
    )
    args = parser.parse_args(argv)

    evidence = (
        build_sample_all_blocked_strategy_evidence()
        if args.sample_all_blocked
        else build_sample_mixed_strategy_evidence()
    )
    result = evaluate_strategy_proof_engine(evidence)
    out = stdout if stdout is not None else sys.stdout

    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    elif args.markdown:
        out.write(strategy_proof_to_markdown(result))
    else:
        out.write(result_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
