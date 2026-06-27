"""Run deterministic AIOS Forex final evidence bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.final_evidence_bundle_v1 import (  # noqa: E402
    build_replay_walkforward_profitability_evidence_chain,
    result_to_jsonable_dict,
    result_to_operator_text,
    write_final_evidence_report,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run AIOS Forex final evidence bundle.")
    parser.add_argument("--report-root", default="Reports/forex_delivery")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = build_replay_walkforward_profitability_evidence_chain(args.report_root)
    if args.write_report:
        write_final_evidence_report(result.get("final_evidence_bundle", result))
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
