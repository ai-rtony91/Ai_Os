from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.supervised_demo_manual_execution_exception_epic_v1 import (  # noqa: E402
    build_sample_supervised_demo_manual_execution_exception_blocked_input,
    build_sample_supervised_demo_manual_execution_exception_ready_input,
    run_supervised_demo_manual_execution_exception_epic,
    supervised_demo_manual_execution_exception_epic_to_jsonable_dict,
    supervised_demo_manual_execution_exception_epic_to_markdown,
    supervised_demo_manual_execution_exception_epic_to_operator_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the supervised demo manual execution exception epic V1 sample.")
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument("--sample-ready", action="store_true", help="Run the deterministic ready sample.")
    sample.add_argument("--sample-blocked", action="store_true", help="Run the deterministic blocked sample.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown output.")
    args = parser.parse_args()

    epic_input = (
        build_sample_supervised_demo_manual_execution_exception_blocked_input()
        if args.sample_blocked
        else build_sample_supervised_demo_manual_execution_exception_ready_input()
    )
    result = run_supervised_demo_manual_execution_exception_epic(epic_input)
    if args.json:
        print(json.dumps(supervised_demo_manual_execution_exception_epic_to_jsonable_dict(result), indent=2, sort_keys=True))
        return 0
    if args.markdown:
        print(supervised_demo_manual_execution_exception_epic_to_markdown(result))
        return 0
    print(supervised_demo_manual_execution_exception_epic_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
