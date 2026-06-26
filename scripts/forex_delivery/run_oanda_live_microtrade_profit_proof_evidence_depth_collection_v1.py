from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_live_microtrade_profit_proof_evidence_depth_collection_v1 import (  # noqa: E402
    OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID,
    OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE,
    build_sample_complete_collection_input,
    build_sample_empty_collection_input,
    build_sample_partial_collection_input,
    build_sample_schema_invalid_collection_input,
    build_sample_unsafe_collection_input,
    evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection,
    load_collection_json,
    to_jsonable_dict,
    to_markdown,
    to_operator_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a sanitized local evidence-depth collection."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument("--sample-complete", action="store_true")
    sample_group.add_argument("--sample-partial", action="store_true")
    sample_group.add_argument("--sample-empty", action="store_true")
    sample_group.add_argument("--sample-unsafe", action="store_true")
    sample_group.add_argument("--sample-schema-invalid", action="store_true")
    parser.add_argument("--input-json")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument("--markdown", action="store_true")
    return parser.parse_args()


def _select_sample(args: argparse.Namespace):
    if args.input_json:
        return load_collection_json(args.input_json)
    if args.sample_partial:
        return build_sample_partial_collection_input()
    if args.sample_empty:
        return build_sample_empty_collection_input()
    if args.sample_unsafe:
        return build_sample_unsafe_collection_input()
    if args.sample_schema_invalid:
        return build_sample_schema_invalid_collection_input()
    return build_sample_complete_collection_input()


def main() -> int:
    args = parse_args()
    result = evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection(
        _select_sample(args)
    )
    if args.json:
        print(json.dumps(to_jsonable_dict(result), indent=2))
    elif args.markdown:
        print(to_markdown(result), end="")
    else:
        print(to_operator_text(result))
    if args.input_json and result.classification in (
        OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID,
        OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE,
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
