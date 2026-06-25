from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_profit_proof_gap_bridge_v1 import (
    bridge_oanda_demo_profit_proof_gap,
    build_sample_blocked_no_result_input,
    build_sample_current_repo_profit_gap_input,
    oanda_demo_profit_proof_gap_to_jsonable_dict,
    oanda_demo_profit_proof_gap_to_markdown,
    oanda_demo_profit_proof_gap_to_operator_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the OANDA demo profit-proof evidence gap."
    )
    parser.add_argument("--sample-current-repo", action="store_true")
    parser.add_argument("--sample-blocked", action="store_true")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()

    sample_input = (
        build_sample_blocked_no_result_input()
        if args.sample_blocked
        else build_sample_current_repo_profit_gap_input()
    )
    result = bridge_oanda_demo_profit_proof_gap(sample_input)

    if args.emit_json:
        print(json.dumps(oanda_demo_profit_proof_gap_to_jsonable_dict(result), indent=2, sort_keys=True))
    elif args.markdown:
        print(oanda_demo_profit_proof_gap_to_markdown(result), end="")
    else:
        print(oanda_demo_profit_proof_gap_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
