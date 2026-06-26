"""Run the local-only AIOS Forex final readiness checker V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_closure_integration_bridge_v1 import run_forex_closure_integration_bridge  # noqa: E402
from automation.forex_engine.forex_final_readiness_checker_v1 import (  # noqa: E402
    build_sample_evidence_age_metadata,
    build_sample_validator_evidence,
    evaluate_forex_final_readiness,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Forex Final Readiness Checker V1 sample.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--missing", action="store_true", help="Use deterministic missing-evidence sample.")
    args = parser.parse_args(argv)

    evidence = build_sample_validator_evidence()
    if args.missing:
        evidence["persistent_profitability_proof"] = False
    result = evaluate_forex_final_readiness(
        run_forex_closure_integration_bridge(),
        evidence,
        build_sample_evidence_age_metadata(),
    )
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
