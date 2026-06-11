"""AI_OS relay proof review refresh (observe-only).

This module consumes the relay predecessor proof bundle and distills the relay
proof review surface that the runtime proof gate should read. It does not
authorize execution, scheduler registration, SOS send, live trading, or queue
mutation. It only refreshes review evidence.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from automation.orchestration.relay_proof.aios_relay_predecessor_proof import (
    REPORT_DIR as PREDECESSOR_REPORT_DIR,
    REPORT_JSON_NAME as PREDECESSOR_REPORT_JSON_NAME,
    build_relay_predecessor_proof_bundle,
    validate_relay_predecessor_proof_report,
)
from automation.orchestration.runtime_closure.aios_relay_dry_run_proof_review import (
    validate_relay_dry_run_proof_review,
)


SCHEMA = "AIOS_RELAY_PROOF_REVIEW.v1"
MODE = "DRY_RUN_REVIEW"
REPORT_DIR = Path("Reports") / "relay_proof_review"
REPORT_JSON_NAME = "relay_proof_review.json"
REPORT_MD_NAME = "relay_proof_review.md"
DEFAULT_PREDECESSOR_REPORT = PREDECESSOR_REPORT_DIR / PREDECESSOR_REPORT_JSON_NAME


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path(__file__).resolve().parents[3]
    return Path(repo_root)


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists():
            return None
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _load_predecessor_bundle(
    *,
    repo_root: Path,
    now: str | None = None,
    state_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cached = _read_json(repo_root / DEFAULT_PREDECESSOR_REPORT)
    if isinstance(cached, dict):
        return cached
    return build_relay_predecessor_proof_bundle(repo_root=repo_root, now=now, state_overrides=state_overrides)


def build_relay_proof_review_report(
    *,
    repo_root: str | Path = ".",
    predecessor_bundle: dict[str, Any] | None = None,
    state_overrides: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    generated_at = _now(now)
    predecessor = _deepcopy(predecessor_bundle) if isinstance(predecessor_bundle, dict) else _load_predecessor_bundle(repo_root=root, now=generated_at, state_overrides=state_overrides)

    predecessor_validation = validate_relay_predecessor_proof_report(predecessor)
    relay_review = _deepcopy(predecessor.get("relay_proof_review") or {})
    relay_review_validation = validate_relay_dry_run_proof_review(relay_review) if isinstance(relay_review, dict) else {"status": "BLOCK", "blockers": ["relay review missing"], "unsafe_flags": []}

    predecessor_status = str(predecessor.get("status") or "UNKNOWN")
    review_status = str(relay_review.get("review_status") or "BLOCKED")
    missing_proofs = list(relay_review.get("missing_proofs") or predecessor.get("missing_proofs") or [])
    blocked_human_gates = list(relay_review.get("blocked_human_gates") or [])
    unsafe_autonomy_claim = False

    if predecessor_status != "PASS":
        review_status = "BLOCKED"
    if missing_proofs and review_status == "REVIEWABLE":
        review_status = "BLOCKED"

    proof_reviewable = review_status == "REVIEWABLE"
    proof_status = str(relay_review.get("proof_status") or "READY_FOR_DRY_RUN")
    safe_next_action = (
        "Use the relay proof review as evidence only, then refresh runtime proof gate; do not execute runtime, scheduler, SOS, or live trading."
        if proof_reviewable
        else "Resolve the missing predecessor proofs before the relay proof review can become reviewable."
    )

    runtime_queue_readout = _deepcopy(predecessor.get("runtime_queue_readout") or {})
    relay_processor_readout = _deepcopy(predecessor.get("relay_processor_readout") or {})
    operator_dependency_ledger = _deepcopy(predecessor.get("operator_dependency_ledger") or {})
    reduction_target_selector = _deepcopy(predecessor.get("reduction_target_selector") or {})

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": generated_at,
        "packet_id": predecessor.get("packet_id"),
        "relay_predecessor_status": predecessor_status,
        "relay_predecessor_missing_proofs": list(predecessor.get("missing_proofs") or []),
        "review_status": review_status,
        "proof_reviewable": proof_reviewable,
        "proof_status": proof_status,
        "missing_proofs": missing_proofs,
        "blocked_human_gates": blocked_human_gates,
        "unsafe_autonomy_claim": unsafe_autonomy_claim,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_mutation_allowed": False,
        "vacation_mode_complete": False,
        "safe_next_action": safe_next_action,
        "relay_predecessor_report": predecessor,
        "relay_predecessor_validation": predecessor_validation,
        "relay_review_validation": relay_review_validation,
        "relay_proof_review": relay_review,
        "runtime_queue_readout": runtime_queue_readout,
        "relay_processor_readout": relay_processor_readout,
        "operator_dependency_ledger": operator_dependency_ledger,
        "reduction_target_selector": reduction_target_selector,
        "source_runtime_queue_validation": _deepcopy(predecessor.get("runtime_queue_validation") or {}),
        "source_relay_processor_validation": _deepcopy(predecessor.get("relay_processor_validation") or {}),
        "source_operator_dependency_validation": _deepcopy(predecessor.get("operator_dependency_validation") or {}),
        "source_reduction_target_validation": _deepcopy(predecessor.get("reduction_target_validation") or {}),
        "report_paths": [str((root / REPORT_DIR / REPORT_JSON_NAME).as_posix()), str((root / REPORT_DIR / REPORT_MD_NAME).as_posix())],
    }
    report["validation"] = validate_relay_proof_review_report(report)
    report["summary"] = summarize_relay_proof_review_report(report)
    return report


def validate_relay_proof_review_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report must be an object"],
            "unsafe_flags": ["report_not_object"],
            "checked_fields": [],
        }

    required_fields = [
        "schema",
        "mode",
        "generated_at_utc",
        "packet_id",
        "relay_predecessor_status",
        "review_status",
        "proof_reviewable",
        "proof_status",
        "missing_proofs",
        "blocked_human_gates",
        "unsafe_autonomy_claim",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "vacation_mode_complete",
        "safe_next_action",
        "relay_predecessor_report",
        "relay_predecessor_validation",
        "relay_review_validation",
        "relay_proof_review",
        "runtime_queue_readout",
        "relay_processor_readout",
        "operator_dependency_ledger",
        "reduction_target_selector",
        "report_paths",
    ]
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    missing = [field for field in required_fields if field not in report]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if report.get("schema") != SCHEMA:
        blockers.append("schema must match AIOS_RELAY_PROOF_REVIEW.v1")
        unsafe_flags.append("schema_mismatch")
    if report.get("mode") != MODE:
        blockers.append("mode must be DRY_RUN_REVIEW")
        unsafe_flags.append("mode_mismatch")
    if report.get("review_status") not in {"REVIEWABLE", "BLOCKED", "INVALID"}:
        blockers.append("review_status must be REVIEWABLE, BLOCKED, or INVALID")
        unsafe_flags.append("review_status_invalid")
    if report.get("proof_reviewable") is not (report.get("review_status") == "REVIEWABLE"):
        blockers.append("proof_reviewable must match review_status")
        unsafe_flags.append("proof_reviewable_mismatch")
    if report.get("unsafe_autonomy_claim") is True:
        blockers.append("unsafe_autonomy_claim must remain false")
        unsafe_flags.append("unsafe_autonomy_claim_true")
    if report.get("dispatch_allowed") is True:
        blockers.append("dispatch_allowed must remain false")
        unsafe_flags.append("dispatch_allowed_true")
    if report.get("apply_allowed") is True:
        blockers.append("apply_allowed must remain false")
        unsafe_flags.append("apply_allowed_true")
    if report.get("runtime_mutation_allowed") is True:
        blockers.append("runtime_mutation_allowed must remain false")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if report.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must remain false")
        unsafe_flags.append("vacation_mode_complete_true")

    if report.get("review_status") == "REVIEWABLE" and report.get("relay_predecessor_status") != "PASS":
        blockers.append("REVIEWABLE review requires a passing predecessor bundle")
        unsafe_flags.append("reviewable_without_passing_predecessor")
    if report.get("review_status") == "REVIEWABLE" and list(report.get("missing_proofs") or []):
        blockers.append("REVIEWABLE review cannot have missing proofs")
        unsafe_flags.append("reviewable_with_missing_proofs")

    if not isinstance(report.get("safe_next_action"), str) or not report.get("safe_next_action"):
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "unsafe_flags": unsafe_flags,
        "checked_fields": required_fields,
    }


def summarize_relay_proof_review_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "review_status": None,
            "proof_reviewable": None,
            "relay_predecessor_status": None,
            "missing_proofs": [],
            "blocked_human_gates": [],
            "unsafe_autonomy_claim": None,
            "safe_next_action": None,
        }
    return {
        "review_status": report.get("review_status"),
        "proof_reviewable": report.get("proof_reviewable"),
        "relay_predecessor_status": report.get("relay_predecessor_status"),
        "missing_proofs": list(report.get("missing_proofs") or []),
        "blocked_human_gates": list(report.get("blocked_human_gates") or []),
        "unsafe_autonomy_claim": report.get("unsafe_autonomy_claim"),
        "safe_next_action": report.get("safe_next_action"),
    }


def build_relay_proof_review_markdown(report: dict[str, Any]) -> str:
    summary = summarize_relay_proof_review_report(report)
    lines = [
        "# AI_OS Relay Proof Review",
        "",
        f"- review_status: `{summary.get('review_status')}`",
        f"- proof_reviewable: `{summary.get('proof_reviewable')}`",
        f"- relay_predecessor_status: `{summary.get('relay_predecessor_status')}`",
        f"- unsafe_autonomy_claim: `{summary.get('unsafe_autonomy_claim')}`",
        f"- safe_next_action: {summary.get('safe_next_action')}",
        "",
        "## Missing Proofs",
    ]
    if summary.get("missing_proofs"):
        lines.extend(f"- {item}" for item in summary.get("missing_proofs") or [])
    else:
        lines.append("- none")
    lines.extend(["", "## Blocked Human Gates"])
    if summary.get("blocked_human_gates"):
        lines.extend(f"- {item}" for item in summary.get("blocked_human_gates") or [])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Evidence Sources",
            f"- runtime_queue_status: `{(report.get('source_runtime_queue_validation') or {}).get('status')}`",
            f"- relay_processor_status: `{(report.get('source_relay_processor_validation') or {}).get('status')}`",
            f"- operator_dependency_status: `{(report.get('source_operator_dependency_validation') or {}).get('status')}`",
            f"- reduction_target_status: `{(report.get('source_reduction_target_validation') or {}).get('status')}`",
            "",
            "## Safety",
            "- This review is observe-only and does not authorize runtime execution, scheduler registration, SOS send, queue mutation, or live trading.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_relay_proof_review_reports(
    report: dict[str, Any],
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    out_dir = Path(output_dir) if output_dir is not None else root / REPORT_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / REPORT_JSON_NAME
    md_path = out_dir / REPORT_MD_NAME
    report = _deepcopy(report)
    report["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    report["validation"] = validate_relay_proof_review_report(report)
    report["summary"] = summarize_relay_proof_review_report(report)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_relay_proof_review_markdown(report), encoding="utf-8")
    return report


def run_relay_proof_review(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    predecessor_bundle: dict[str, Any] | None = None,
    state_overrides: dict[str, Any] | None = None,
    now: str | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    report = build_relay_proof_review_report(
        repo_root=repo_root,
        predecessor_bundle=predecessor_bundle,
        state_overrides=state_overrides,
        now=now,
    )
    if write_report:
        report = write_relay_proof_review_reports(report, repo_root=repo_root, output_dir=output_dir)
    return report


def _cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the AI_OS relay proof review report.")
    parser.add_argument("--repo-root", default=".", help="repository root for output resolution")
    parser.add_argument("--output-dir", default=None, help="optional report output directory")
    parser.add_argument("--no-write", action="store_true", help="build without writing report files")
    parser.add_argument("--predecessor-json", default=None, help="optional JSON string containing a predecessor bundle")
    parser.add_argument("--state-json", default=None, help="optional JSON string containing proof-state overrides")
    parser.add_argument("--now", default=None, help="optional timestamp override")
    return parser.parse_args()


def _load_json_arg(raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON input must decode to an object")
    return value


def main() -> int:
    args = _cli_args()
    report = run_relay_proof_review(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        predecessor_bundle=_load_json_arg(args.predecessor_json),
        state_overrides=_load_json_arg(args.state_json),
        now=args.now,
        write_report=not args.no_write,
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
