from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_execution_truth_epic_v1 import (
    build_sample_oanda_demo_execution_truth_epic_blocked_input,
    build_sample_oanda_demo_execution_truth_epic_current_repo_input,
    oanda_demo_execution_truth_epic_to_jsonable_dict,
    oanda_demo_execution_truth_epic_to_markdown,
    oanda_demo_execution_truth_epic_to_operator_text,
    run_oanda_demo_execution_truth_epic,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the OANDA demo execution truth and profit-proof epic audit."
    )
    parser.add_argument("--sample-current-repo", action="store_true")
    parser.add_argument("--sample-blocked", action="store_true")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()

    sample_input = (
        build_sample_oanda_demo_execution_truth_epic_blocked_input()
        if args.sample_blocked
        else build_sample_oanda_demo_execution_truth_epic_current_repo_input()
    )
    result = run_oanda_demo_execution_truth_epic(sample_input)

    if args.emit_json:
        print(json.dumps(oanda_demo_execution_truth_epic_to_jsonable_dict(result), indent=2, sort_keys=True))
    elif args.markdown:
        print(oanda_demo_execution_truth_epic_to_markdown(result), end="")
    else:
        print(oanda_demo_execution_truth_epic_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
