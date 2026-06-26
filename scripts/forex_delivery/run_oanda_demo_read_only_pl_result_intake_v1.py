from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    build_sample_breakeven_pl_evidence,
    build_sample_incomplete_pl_evidence,
    build_sample_loss_pl_evidence,
    build_sample_profit_pl_evidence,
    build_sample_unsafe_pl_evidence,
    intake_oanda_demo_read_only_pl_result,
    oanda_demo_read_only_pl_result_intake_to_jsonable_dict,
    oanda_demo_read_only_pl_result_intake_to_markdown,
    oanda_demo_read_only_pl_result_intake_to_operator_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic OANDA demo read-only P/L result intake samples."
    )
    parser.add_argument("--sample-profit", action="store_true")
    parser.add_argument("--sample-loss", action="store_true")
    parser.add_argument("--sample-breakeven", action="store_true")
    parser.add_argument("--sample-incomplete", action="store_true")
    parser.add_argument("--sample-unsafe", action="store_true")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()

    result = intake_oanda_demo_read_only_pl_result(_sample_evidence(args))

    if args.emit_json:
        print(
            json.dumps(
                oanda_demo_read_only_pl_result_intake_to_jsonable_dict(result),
                indent=2,
                sort_keys=True,
            )
        )
    elif args.markdown:
        print(oanda_demo_read_only_pl_result_intake_to_markdown(result), end="")
    else:
        print(oanda_demo_read_only_pl_result_intake_to_operator_text(result))
    return 0


def _sample_evidence(args: argparse.Namespace) -> object:
    if args.sample_loss:
        return build_sample_loss_pl_evidence()
    if args.sample_breakeven:
        return build_sample_breakeven_pl_evidence()
    if args.sample_incomplete:
        return build_sample_incomplete_pl_evidence()
    if args.sample_unsafe:
        return build_sample_unsafe_pl_evidence()
    return build_sample_profit_pl_evidence()


if __name__ == "__main__":
    raise SystemExit(main())
