from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.post_trade_evidence_capture_v1 import (
    build_sample_post_trade_loss_input,
    build_sample_post_trade_missing_input,
    build_sample_post_trade_profit_input,
    capture_post_trade_evidence,
    post_trade_evidence_to_jsonable_dict,
    post_trade_evidence_to_markdown,
    post_trade_evidence_to_operator_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local-only post-trade evidence capture sample.")
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument("--sample-profit", action="store_true", help="Use the deterministic profit sample.")
    sample.add_argument("--sample-loss", action="store_true", help="Use the deterministic loss sample.")
    sample.add_argument("--sample-missing", action="store_true", help="Use the deterministic missing-result sample.")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Emit JSON.")
    output.add_argument("--markdown", action="store_true", help="Emit markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.sample_loss:
        sample_input = build_sample_post_trade_loss_input()
    elif args.sample_missing:
        sample_input = build_sample_post_trade_missing_input()
    else:
        sample_input = build_sample_post_trade_profit_input()
    result = capture_post_trade_evidence(sample_input)
    if args.json:
        print(json.dumps(post_trade_evidence_to_jsonable_dict(result), indent=2, sort_keys=True))
    elif args.markdown:
        print(post_trade_evidence_to_markdown(result))
    else:
        print(post_trade_evidence_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
