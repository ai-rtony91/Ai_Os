from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.demo_order_plan_builder_v1 import (
    build_demo_order_plan,
    build_sample_blocked_demo_order_plan_input,
    build_sample_demo_order_plan_input,
    demo_order_plan_to_jsonable_dict,
    demo_order_plan_to_markdown,
    demo_order_plan_to_operator_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local-only demo order plan builder sample.")
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument("--sample-ready", action="store_true", help="Use the deterministic review-ready sample.")
    sample.add_argument("--sample-blocked", action="store_true", help="Use the deterministic blocked sample.")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Emit JSON.")
    output.add_argument("--markdown", action="store_true", help="Emit markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sample_input = (
        build_sample_blocked_demo_order_plan_input()
        if args.sample_blocked
        else build_sample_demo_order_plan_input()
    )
    result = build_demo_order_plan(sample_input)
    if args.json:
        print(json.dumps(demo_order_plan_to_jsonable_dict(result), indent=2, sort_keys=True))
    elif args.markdown:
        print(demo_order_plan_to_markdown(result))
    else:
        print(demo_order_plan_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
