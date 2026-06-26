from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_live_evidence_requirement_matrix_v1 import (  # noqa: E402
    build_oanda_demo_live_evidence_requirement_matrix,
    build_sample_live_evidence_requirement_matrix_blocked_input,
    build_sample_live_evidence_requirement_matrix_ready_input,
    oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict,
    oanda_demo_live_evidence_requirement_matrix_to_markdown,
    oanda_demo_live_evidence_requirement_matrix_to_operator_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview the OANDA demo live evidence requirement matrix."
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument("--sample-missing-live-evidence", action="store_true")
    sample_group.add_argument("--sample-ready", action="store_true")
    sample_group.add_argument("--sample-blocked", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument("--markdown", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_blocked:
        config = build_sample_live_evidence_requirement_matrix_blocked_input()
    else:
        config = build_sample_live_evidence_requirement_matrix_ready_input()
    result = build_oanda_demo_live_evidence_requirement_matrix(config)
    if args.json:
        print(json.dumps(oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict(result), indent=2))
    elif args.markdown:
        print(oanda_demo_live_evidence_requirement_matrix_to_markdown(result), end="")
    else:
        print(oanda_demo_live_evidence_requirement_matrix_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
