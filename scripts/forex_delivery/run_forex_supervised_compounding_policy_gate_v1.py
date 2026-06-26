from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_supervised_compounding_policy_gate_v1 import (  # noqa: E402
    build_sample_partial_input,
    build_sample_ready_input,
    build_sample_schema_invalid_input,
    build_sample_unsafe_input,
    evaluate_forex_supervised_compounding_policy_gate,
    to_jsonable_dict,
    to_markdown,
    to_operator_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview AIOS Forex supervised compounding policy gate."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument("--sample-ready", action="store_true")
    sample_group.add_argument("--sample-partial", action="store_true")
    sample_group.add_argument("--sample-unsafe", action="store_true")
    sample_group.add_argument("--sample-schema-invalid", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument("--markdown", action="store_true")
    return parser.parse_args()


def _select_sample(args: argparse.Namespace):
    if args.sample_partial:
        return build_sample_partial_input()
    if args.sample_unsafe:
        return build_sample_unsafe_input()
    if args.sample_schema_invalid:
        return build_sample_schema_invalid_input()
    return build_sample_ready_input()


def main() -> int:
    args = parse_args()
    result = evaluate_forex_supervised_compounding_policy_gate(_select_sample(args))
    if args.json:
        print(json.dumps(to_jsonable_dict(result), indent=2))
    elif args.markdown:
        print(to_markdown(result), end="")
    else:
        print(to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
