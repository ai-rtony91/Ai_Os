"""CLI runner for Forex next repo-safe queue V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_next_repo_safe_queue_v1 import (
    build_next_codex_packet,
    build_report_markdown,
    run_forex_next_repo_safe_queue_v1,
)

STATE_PATH = ROOT / "Reports" / "forex_delivery" / "AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_STATE.json"
REPORT_PATH = ROOT / "Reports" / "forex_delivery" / "AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_REPORT.md"
NEXT_PACKET_PATH = ROOT / "Reports" / "forex_delivery" / "AIOS_FOREX_EVIDENCE_CANDIDATE_DEMO_READINESS_NEXT_CODEX_PACKET_V1.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    result = run_forex_next_repo_safe_queue_v1()
    if args.write_state:
        STATE_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if args.write_report:
        REPORT_PATH.write_text(build_report_markdown(result), encoding="utf-8")
        NEXT_PACKET_PATH.write_text(build_next_codex_packet(result), encoding="utf-8")
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
