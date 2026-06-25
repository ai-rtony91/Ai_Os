"""CLI runner for the local-only Forex loss-to-candidate gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.loss_to_next_profit_candidate_gate_v1 import (  # noqa: E402
    build_sample_trade_334_input,
    evaluate_loss_to_next_profit_candidate_gate,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local-only AIOS loss-to-next-profit-candidate gate."
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
    gate_input = build_sample_trade_334_input() if args.sample_trade_334 else None
    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
