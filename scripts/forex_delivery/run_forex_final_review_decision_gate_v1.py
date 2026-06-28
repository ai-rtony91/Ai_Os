"""CLI runner for final review decision gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_final_review_decision_evidence_loader_v1 as evidence_loader_lib
from automation.forex_engine import forex_final_review_decision_gate_v1 as gate_lib
from automation.forex_engine import forex_owner_evidence_return_orchestrator_v1 as owner_orchestrator_lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Forex final review decision gate")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_FINAL_REVIEW_DECISION_GATE_V1_REPORT.md",
    )
    parser.add_argument(
        "--evidence-path",
        action="append",
        default=None,
        help="Optional file/folder path for final review evidence",
    )
    return parser.parse_args(argv)


def _default_decision(repo_root: Path, strict: bool, evidence_paths: list[str] | None) -> dict:
    paths = [Path(path) for path in evidence_paths or []]
    if not paths:
        paths = [repo_root / "tests\\fixtures\\forex_delivery\\final_review_decision_gate_v1"]
    evidence = evidence_loader_lib.load_final_review_evidence_paths(
        paths,
        strict=strict,
        source_family="final_review_decision_gate_v1",
    )
    owner_result = owner_orchestrator_lib.orchestrate_owner_evidence_return(
        repo_root=repo_root,
        strict=strict,
    )
    return gate_lib.decide_final_review_status(
        evidence_payload=evidence,
        owner_evidence_return_payload=owner_result,
        closure_gap_route_payload=owner_result.get("route_payload", {}),
        final_owner_review_packet_payload=owner_result.get("packet_payload", {}),
        readiness_checkpoint_payload=owner_result.get("checkpoint_ledger", {}),
        strict=strict,
    )


def run_cli(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    decision_payload = _default_decision(repo_root, args.strict, args.evidence_path)
    if args.json:
        output = json.dumps(gate_lib.final_review_decision_to_jsonable_dict(decision_payload), indent=2, sort_keys=True)
    else:
        output = gate_lib.final_review_decision_to_markdown(decision_payload)
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (repo_root / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    return output


def main() -> None:
    print(run_cli())


if __name__ == "__main__":
    main()
