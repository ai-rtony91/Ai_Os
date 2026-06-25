from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.demo_owner_approval_phrase_gate_v1 import (  # noqa: E402
    build_sample_missing_owner_approval_phrase_input,
    build_sample_valid_owner_approval_phrase_input,
    build_sample_wrong_scope_owner_approval_phrase_input,
    demo_owner_approval_phrase_gate_to_jsonable_dict,
    demo_owner_approval_phrase_gate_to_markdown,
    demo_owner_approval_phrase_gate_to_operator_text,
    evaluate_demo_owner_approval_phrase_gate,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the demo owner approval phrase gate V1 sample.")
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument("--sample-ready", action="store_true", help="Run the deterministic ready sample.")
    sample.add_argument("--sample-blocked", action="store_true", help="Run the deterministic blocked sample.")
    sample.add_argument("--sample-wrong-scope", action="store_true", help="Run the wrong-scope sample.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown output.")
    args = parser.parse_args()

    if args.sample_blocked:
        phrase_input = build_sample_missing_owner_approval_phrase_input()
    elif args.sample_wrong_scope:
        phrase_input = build_sample_wrong_scope_owner_approval_phrase_input()
    else:
        phrase_input = build_sample_valid_owner_approval_phrase_input()

    result = evaluate_demo_owner_approval_phrase_gate(phrase_input)
    if args.json:
        print(json.dumps(demo_owner_approval_phrase_gate_to_jsonable_dict(result), indent=2, sort_keys=True))
        return 0
    if args.markdown:
        print(demo_owner_approval_phrase_gate_to_markdown(result))
        return 0
    print(demo_owner_approval_phrase_gate_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
