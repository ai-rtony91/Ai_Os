from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_repeated_expectancy_accumulator_v1 import (
    build_oanda_demo_repeated_expectancy_accumulator,
    build_sample_insufficient_accumulator_input,
    build_sample_losing_accumulator_input,
    build_sample_strong_accumulator_input,
    build_sample_unsafe_accumulator_input,
    build_sample_weak_accumulator_input,
    oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict,
    oanda_demo_repeated_expectancy_accumulator_to_markdown,
    oanda_demo_repeated_expectancy_accumulator_to_operator_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic OANDA demo repeated expectancy accumulation."
    )
    parser.add_argument("--sample-strong", action="store_true")
    parser.add_argument("--sample-weak", action="store_true")
    parser.add_argument("--sample-insufficient", action="store_true")
    parser.add_argument("--sample-losing", action="store_true")
    parser.add_argument("--sample-unsafe", action="store_true")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()

    result = build_oanda_demo_repeated_expectancy_accumulator(_sample_input(args))
    if args.emit_json:
        print(
            json.dumps(
                oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict(result),
                indent=2,
                sort_keys=True,
            )
        )
    elif args.markdown:
        print(oanda_demo_repeated_expectancy_accumulator_to_markdown(result), end="")
    else:
        print(oanda_demo_repeated_expectancy_accumulator_to_operator_text(result))
    return 0


def _sample_input(args: argparse.Namespace) -> object:
    if args.sample_weak:
        return build_sample_weak_accumulator_input()
    if args.sample_insufficient:
        return build_sample_insufficient_accumulator_input()
    if args.sample_losing:
        return build_sample_losing_accumulator_input()
    if args.sample_unsafe:
        return build_sample_unsafe_accumulator_input()
    return build_sample_strong_accumulator_input()


if __name__ == "__main__":
    raise SystemExit(main())
