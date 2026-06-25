"""CLI runner for the local-only AIOS Forex profit validation loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.profit_validation_loop_v1 import (  # noqa: E402
    build_sample_trade_334_input,
    evaluate_profit_validation_loop,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local-only AIOS Forex profit validation gate."
    )
    parser.add_argument(
        "--sample-trade-334",
        action="store_true",
        help="Evaluate built-in local evidence for trade 334.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print deterministic JSON instead of operator text.",
    )
    args = parser.parse_args(argv)

    out = stdout if stdout is not None else sys.stdout
    validation_input = build_sample_trade_334_input() if args.sample_trade_334 else None
    result = evaluate_profit_validation_loop(validation_input)

    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
