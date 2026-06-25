from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.demo_manual_execution_exception_scope_gate_v1 import (  # noqa: E402
    build_sample_execution_authority_blocked_input,
    build_sample_missing_manual_execution_exception_scope_input,
    build_sample_real_money_scope_blocked_input,
    build_sample_valid_manual_execution_exception_scope_input,
    demo_manual_execution_exception_scope_to_jsonable_dict,
    demo_manual_execution_exception_scope_to_markdown,
    demo_manual_execution_exception_scope_to_operator_text,
    evaluate_demo_manual_execution_exception_scope,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the demo manual execution exception scope gate V1 sample.")
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument("--sample-ready", action="store_true", help="Run the deterministic ready sample.")
    sample.add_argument("--sample-blocked", action="store_true", help="Run the missing phrase sample.")
    sample.add_argument("--sample-execution-authority", action="store_true", help="Run the execution authority blocker sample.")
    sample.add_argument("--sample-real-money", action="store_true", help="Run the real money blocker sample.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown output.")
    args = parser.parse_args()

    if args.sample_blocked:
        scope_input = build_sample_missing_manual_execution_exception_scope_input()
    elif args.sample_execution_authority:
        scope_input = build_sample_execution_authority_blocked_input()
    elif args.sample_real_money:
        scope_input = build_sample_real_money_scope_blocked_input()
    else:
        scope_input = build_sample_valid_manual_execution_exception_scope_input()

    result = evaluate_demo_manual_execution_exception_scope(scope_input)
    if args.json:
        print(json.dumps(demo_manual_execution_exception_scope_to_jsonable_dict(result), indent=2, sort_keys=True))
        return 0
    if args.markdown:
        print(demo_manual_execution_exception_scope_to_markdown(result))
        return 0
    print(demo_manual_execution_exception_scope_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
