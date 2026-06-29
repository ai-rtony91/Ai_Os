"""CLI runner for Forex 110 final dashboard closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_110_final_dashboard_closure_v1 import (  # noqa: E402
    build_bitwarden_blocker_markdown,
    build_clickable_emoji_window_map_markdown,
    build_completion_index_markdown,
    build_dashboard_contract_markdown,
    build_protected_boundary_handoff_markdown,
    build_report_markdown,
    run_forex_110_final_dashboard_closure_v1,
)


DEFAULT_REPORT_ROOT = ROOT / "Reports" / "forex_delivery"
DEFAULT_DOC_ROOT = ROOT / "docs" / "trading_lab" / "forex"

STATE_NAME = "AIOS_FOREX_110_FINAL_DASHBOARD_CLOSURE_V1_STATE.json"
REPORT_NAME = "AIOS_FOREX_110_FINAL_DASHBOARD_CLOSURE_V1_REPORT.md"
INDEX_NAME = "AIOS_FOREX_110_COMPLETION_INDEX_V1.md"
REPORT_CONTRACT_NAME = "AIOS_FOREX_DASHBOARD_END_USER_UX_CONTRACT_V1.md"
PROTECTED_BOUNDARY_NAME = "AIOS_FOREX_FINAL_PROTECTED_BOUNDARY_HANDOFF_V1.md"
BITWARDEN_BLOCKER_NAME = "AIOS_FOREX_POST_110_NEXT_PROJECT_BLOCKER_BITWARDEN_V1.md"

DOC_CLOSURE_NAME = "FOREX_110_FINAL_DASHBOARD_CLOSURE_V1.md"
DOC_CONTRACT_NAME = "FOREX_DASHBOARD_END_USER_UX_CONTRACT_V1.md"
DOC_WINDOW_MAP_NAME = "FOREX_DASHBOARD_CLICKABLE_EMOJI_WINDOW_MAP_V1.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", default=str(DEFAULT_REPORT_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_REPORT_ROOT))
    parser.add_argument("--doc-root", default=str(DEFAULT_DOC_ROOT))
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    parser.add_argument("--write-dashboard-contract", action="store_true")
    parser.add_argument("--write-protected-boundary-handoff", action="store_true")
    parser.add_argument("--write-bitwarden-blocker", action="store_true")
    args = parser.parse_args(argv)

    result = run_forex_110_final_dashboard_closure_v1(args.report_root)
    output_root = Path(args.output_root)
    doc_root = Path(args.doc_root)
    output_root.mkdir(parents=True, exist_ok=True)
    doc_root.mkdir(parents=True, exist_ok=True)

    report = build_report_markdown(result)
    contract = build_dashboard_contract_markdown(result)
    window_map = build_clickable_emoji_window_map_markdown(result)

    if args.write_state:
        (output_root / STATE_NAME).write_text(
            json.dumps(result, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    if args.write_report:
        (output_root / REPORT_NAME).write_text(report, encoding="utf-8")
        (doc_root / DOC_CLOSURE_NAME).write_text(report, encoding="utf-8")
    if args.write_index:
        (output_root / INDEX_NAME).write_text(
            build_completion_index_markdown(result),
            encoding="utf-8",
        )
    if args.write_dashboard_contract:
        (output_root / REPORT_CONTRACT_NAME).write_text(contract, encoding="utf-8")
        (doc_root / DOC_CONTRACT_NAME).write_text(contract, encoding="utf-8")
        (doc_root / DOC_WINDOW_MAP_NAME).write_text(window_map, encoding="utf-8")
    if args.write_protected_boundary_handoff:
        (output_root / PROTECTED_BOUNDARY_NAME).write_text(
            build_protected_boundary_handoff_markdown(result),
            encoding="utf-8",
        )
    if args.write_bitwarden_blocker:
        (output_root / BITWARDEN_BLOCKER_NAME).write_text(
            build_bitwarden_blocker_markdown(result),
            encoding="utf-8",
        )

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
