"""Run the local-only Forex evidence milestone selector V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.evidence_milestone_selector_v1 import (  # noqa: E402
    build_sample_evidence_results,
    result_to_jsonable_dict,
    result_to_operator_text,
    select_evidence_milestone,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Forex Evidence Milestone Selector V1 sample.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--blocked", action="store_true", help="Use a deterministic blocked sample.")
    parser.add_argument("--incomplete", action="store_true", help="Use a deterministic incomplete sample.")
    args = parser.parse_args(argv)

    sample = build_sample_evidence_results()
    if args.blocked:
        sample["replay_proof_evidence"]["status"] = "REPLAY_PROOF_BLOCKED"
        sample["replay_proof_evidence"]["blockers"] = ["replay evidence is stale"]
    if args.incomplete:
        sample.pop("replay_proof_evidence", None)
    result = select_evidence_milestone(sample)
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
