"""Run the local-only walk-forward/OOS evidence adapter V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.walk_forward_oos_evidence_v1 import (  # noqa: E402
    build_sample_walk_forward_oos_summary,
    evaluate_walk_forward_oos_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Walk-Forward/OOS Evidence V1 sample.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--blocked", action="store_true", help="Use a deterministic blocked sample.")
    parser.add_argument("--incomplete", action="store_true", help="Use a deterministic incomplete sample.")
    args = parser.parse_args(argv)

    sample = build_sample_walk_forward_oos_summary()
    if args.blocked:
        sample["windows_passed"] = 1
    if args.incomplete:
        sample.pop("windows_total", None)
    result = evaluate_walk_forward_oos_evidence(sample)
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
