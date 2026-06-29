"""Run the Forex 110 C2 walk-forward/OOS source collection classifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_110_c2_walkforward_oos_source_collection_v1 import (  # noqa: E402
    REAL_SANITIZED_LOCAL_SOURCE_FOUND,
    REAL_SANITIZED_LOCAL_SOURCE_GENERATED,
    SOURCE_REPORT_NAME,
    build_report_markdown,
    build_source_markdown,
    collect_c2_walkforward_oos_source,
)


STATE_NAME = "AIOS_FOREX_110_C2_WALKFORWARD_OOS_SOURCE_COLLECTION_V1_STATE.json"
REPORT_NAME = "AIOS_FOREX_110_C2_WALKFORWARD_OOS_SOURCE_COLLECTION_V1_REPORT.md"
DEFAULT_OUTPUT_ROOT = ROOT / "Reports" / "forex_delivery"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    result = collect_c2_walkforward_oos_source(args.report_root, repo_root=ROOT)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    if args.write_state:
        (output_root / STATE_NAME).write_text(
            json.dumps(result, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.write_report:
        (output_root / REPORT_NAME).write_text(build_report_markdown(result), encoding="utf-8")
        if result.get("evidence_source_classification") in {
            REAL_SANITIZED_LOCAL_SOURCE_FOUND,
            REAL_SANITIZED_LOCAL_SOURCE_GENERATED,
        }:
            (output_root / SOURCE_REPORT_NAME).write_text(build_source_markdown(result), encoding="utf-8")
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=True, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
