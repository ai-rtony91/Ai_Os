"""CLI runner for the owner evidence return orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_owner_evidence_return_orchestrator_v1 as orchestrator_lib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run owner evidence return orchestration",
    )
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--report-path", default="Reports\\forex_delivery\\AIOS_FOREX_OWNER_EVIDENCE_RETURN_ORCHESTRATION_V1_REPORT.md")
    parser.add_argument(
        "--checkpoint-report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_OWNER_EVIDENCE_RETURN_ORCHESTRATION_V1_CHECKPOINT.md",
    )
    parser.add_argument(
        "--include-already-present",
        action="store_true",
        help="Include families already present in intake output",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    result = orchestrator_lib.orchestrate_owner_evidence_return(
        repo_root=repo_root,
        strict=args.strict,
        include_already_present=args.include_already_present,
    )
    report_payload = (
        json.dumps(orchestrator_lib.orchestrate_to_jsonable_dict(result), indent=2, sort_keys=True)
        if args.json
        else orchestrator_lib.orchestrate_to_markdown(result)
    )
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (repo_root / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_payload, encoding="utf-8")
    else:
        print(report_payload)

    if args.write_report:
        checkpoint_payload = {
            "report_type": "checkpoint",
            "packet_id": result["packet_payload"]["packet_id"],
            "generated_at": result["checkpoint_ledger"]["generated_at"],
            "events": result["checkpoint_ledger"]["events"],
            "event_count": result["checkpoint_ledger"]["event_count"],
        }
        checkpoint_path = Path(args.checkpoint_report_path)
        if not checkpoint_path.is_absolute():
            checkpoint_path = (repo_root / checkpoint_path).resolve()
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(
            json.dumps(checkpoint_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
