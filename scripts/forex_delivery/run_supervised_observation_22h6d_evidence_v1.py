"""Run the local-only 22H/6D supervised observation evidence adapter V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.supervised_observation_22h6d_evidence_v1 import (  # noqa: E402
    build_sample_observation_summary,
    evaluate_supervised_observation_22h6d_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run 22H/6D Supervised Observation Evidence V1 sample.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--blocked", action="store_true", help="Use a deterministic blocked sample.")
    parser.add_argument("--incomplete", action="store_true", help="Use a deterministic incomplete sample.")
    args = parser.parse_args(argv)

    sample = build_sample_observation_summary()
    if args.blocked:
        sample["observed_hours"] = 10
    if args.incomplete:
        sample.pop("observed_hours", None)
    result = evaluate_supervised_observation_22h6d_evidence(sample)
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
