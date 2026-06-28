"""CLI runner for owner decision authority gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import (
    forex_owner_decision_authority_gate_v1 as authority_lib,
    forex_demo_readiness_handoff_builder_v1 as handoff_lib,
    forex_final_review_decision_gate_v1 as gate_lib,
)
from automation.forex_engine import (
    forex_final_review_decision_evidence_loader_v1 as evidence_loader_lib,
    forex_owner_evidence_return_orchestrator_v1 as owner_orchestrator_lib,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate owner decision authority for final review")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_OWNER_DECISION_AUTHORITY_GATE_V1_REPORT.md",
    )
    parser.add_argument(
        "--decision-path",
        default=None,
        help="Optional final review decision JSON payload path",
    )
    return parser.parse_args(argv)


def _default_decision(repo_root: Path, strict: bool) -> dict:
    evidence = evidence_loader_lib.load_final_review_evidence_paths(
        [repo_root / "tests\\fixtures\\forex_delivery\\final_review_decision_gate_v1"],
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
    decision_payload = _default_decision(repo_root, args.strict)
    if args.decision_path:
        decision_payload = json.loads(Path(args.decision_path).read_text(encoding="utf-8"))
    handoff_payload = handoff_lib.build_demo_readiness_handoff(decision_payload, strict=args.strict)
    authority = authority_lib.evaluate_owner_decision_authority(
        decision_payload,
        demo_readiness_handoff=handoff_payload,
        strict=args.strict,
    )
    if args.json:
        output = json.dumps(authority_lib.owner_decision_authority_to_jsonable_dict(authority), indent=2, sort_keys=True)
    else:
        output = authority_lib.owner_decision_authority_to_markdown(authority)
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
