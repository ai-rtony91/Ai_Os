"""AI_OS self-build decision consumer v1.

Reads self-build cycle evidence and emits a normalized observe-only readout for
operator/control-plane use. This module is not a decider and does not execute,
approve, dispatch, mutate approval state, or mutate packet state.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_DECISION_CONSUMER.v1"
DEFAULT_EVIDENCE_PATH = Path("Reports/self_build_cycle/latest_self_build_cycle.evidence.json")
PROTECTED_FLAGS = {
    "can_apply": False,
    "can_commit": False,
    "can_push": False,
    "can_merge": False,
    "can_dispatch": False,
    "can_mutate_approval_inbox": False,
    "can_mutate_work_packets": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get(data: dict[str, Any] | None, *keys: str) -> Any:
    current: Any = data or {}
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _base(source_path: Path | str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at": _now(),
        "mode": "DRY_RUN",
        "observe_only": True,
        "source_evidence_path": str(source_path),
        "source_cycle_id": None,
        "source_generated_at": None,
        "source_schema": None,
        "source_safety_status": None,
        "source_requires_human": None,
        "source_decision_action": None,
        "source_decision_reason": None,
        "source_blocked_reason": None,
        "source_runtime_gate": None,
        "source_completion_verdict": None,
        "normalized_status": "REVIEW_REQUIRED",
        "operator_route": "APPROVAL_REVIEW_REQUIRED",
        "escalation_level": "MEDIUM",
        "approval_required": True,
        "sos_required": False,
        "report_only": True,
        "reasons": [],
        "safe_next_action": "Review self-build decision evidence before taking any protected action.",
        **PROTECTED_FLAGS,
    }


def load_self_build_evidence(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, [f"missing evidence file: {path}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"malformed evidence JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, ["malformed evidence JSON: root must be an object"]
    return payload, []


def _set_status(
    readout: dict[str, Any],
    *,
    normalized_status: str,
    operator_route: str,
    escalation_level: str,
    approval_required: bool,
    sos_required: bool,
    reason: str,
    safe_next_action: str,
) -> dict[str, Any]:
    readout.update(
        {
            "normalized_status": normalized_status,
            "operator_route": operator_route,
            "escalation_level": escalation_level,
            "approval_required": approval_required,
            "sos_required": sos_required,
            "report_only": True,
            "safe_next_action": safe_next_action,
        }
    )
    readout["reasons"].append(reason)
    return readout


def consume_self_build_decision(payload: dict[str, Any], source_path: Path | str) -> dict[str, Any]:
    readout = _base(source_path)
    decision = payload.get("decision") if isinstance(payload.get("decision"), dict) else {}
    evidence_bundle = payload.get("evidence_bundle") if isinstance(payload.get("evidence_bundle"), dict) else {}
    runtime_gate = _get(evidence_bundle, "runtime", "runtime_gate")
    completion_verdict = _get(evidence_bundle, "completion", "verdict")
    safety_status = payload.get("safety_status")
    requires_human = bool(payload.get("requires_human")) if payload.get("requires_human") is not None else None

    readout.update(
        {
            "source_cycle_id": payload.get("cycle_id"),
            "source_generated_at": payload.get("generated_at") or payload.get("timestamp_utc"),
            "source_schema": payload.get("schema"),
            "source_safety_status": safety_status,
            "source_requires_human": requires_human,
            "source_decision_action": decision.get("action"),
            "source_decision_reason": decision.get("reason"),
            "source_blocked_reason": payload.get("blocked_reason") or decision.get("blocked_reason"),
            "source_runtime_gate": runtime_gate,
            "source_completion_verdict": completion_verdict,
        }
    )

    if safety_status == "BLOCKED":
        return _set_status(
            readout,
            normalized_status="BLOCKED",
            operator_route="SOS_REVIEW_REQUIRED",
            escalation_level="HIGH",
            approval_required=True,
            sos_required=True,
            reason="source safety_status is BLOCKED",
            safe_next_action="Escalate blocked self-build cycle evidence for SOS review.",
        )
    if runtime_gate == "TRUST_FAILED" or completion_verdict == "COMPLETION_CONTRADICTED":
        return _set_status(
            readout,
            normalized_status="TRUST_FAILED",
            operator_route="SOS_REVIEW_REQUIRED",
            escalation_level="HIGH",
            approval_required=True,
            sos_required=True,
            reason="trust evidence failed or contradicted completion claim",
            safe_next_action="Stop and review trust failure evidence before any protected action.",
        )
    if completion_verdict == "COMPLETION_UNPROVEN":
        return _set_status(
            readout,
            normalized_status="WAIT_FOR_EVIDENCE",
            operator_route="REPORT_ONLY",
            escalation_level="LOW",
            approval_required=bool(requires_human),
            sos_required=False,
            reason="completion verdict is unproven",
            safe_next_action="Collect stronger completion evidence before advancing.",
        )
    if completion_verdict == "NOT_EVALUATED":
        return _set_status(
            readout,
            normalized_status="WAIT_FOR_EVIDENCE",
            operator_route="REPORT_ONLY",
            escalation_level="LOW",
            approval_required=False,
            sos_required=False,
            reason="completion verdict is not evaluated",
            safe_next_action="Wait for completion evidence evaluation before advancing.",
        )
    if requires_human is True or safety_status == "HUMAN_REQUIRED":
        return _set_status(
            readout,
            normalized_status="HUMAN_REVIEW_REQUIRED",
            operator_route="APPROVAL_REVIEW_REQUIRED",
            escalation_level="MEDIUM",
            approval_required=True,
            sos_required=False,
            reason="source requires human review",
            safe_next_action="Route to Human Owner review; do not approve automatically.",
        )
    if safety_status == "SAFE" and runtime_gate == "READY_TO_REPORT" and requires_human is False:
        return _set_status(
            readout,
            normalized_status="REPORT_READY",
            operator_route="REPORT_ONLY",
            escalation_level="LOW",
            approval_required=False,
            sos_required=False,
            reason="source is safe and ready to report",
            safe_next_action="Report the decision readout only; no action is approved.",
        )
    return _set_status(
        readout,
        normalized_status="REVIEW_REQUIRED",
        operator_route="APPROVAL_REVIEW_REQUIRED",
        escalation_level="MEDIUM",
        approval_required=True,
        sos_required=False,
        reason="source evidence has unknown or incomplete fields",
        safe_next_action="Review incomplete self-build evidence before advancing.",
    )


def consume_self_build_evidence_file(path: Path) -> dict[str, Any]:
    payload, issues = load_self_build_evidence(path)
    if payload is None:
        readout = _base(path)
        reason = issues[0] if issues else "evidence unavailable"
        if "missing evidence" in reason:
            return _set_status(
                readout,
                normalized_status="WAIT_FOR_EVIDENCE",
                operator_route="REPORT_ONLY",
                escalation_level="LOW",
                approval_required=False,
                sos_required=False,
                reason=reason,
                safe_next_action="Wait for self-build cycle evidence to be produced.",
            )
        return _set_status(
            readout,
            normalized_status="BLOCKED_MALFORMED_EVIDENCE",
            operator_route="SOS_REVIEW_REQUIRED",
            escalation_level="HIGH",
            approval_required=True,
            sos_required=True,
            reason=reason,
            safe_next_action="Stop and repair malformed self-build evidence.",
        )
    return consume_self_build_decision(payload, path)


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Consume self-build cycle evidence into an observe-only readout.")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH))
    parser.add_argument("--output")
    args = parser.parse_args()

    evidence_path = Path(args.evidence)
    readout = consume_self_build_evidence_file(evidence_path)
    if args.output:
        _write_json_atomic(Path(args.output), readout)
    print(json.dumps(readout, indent=2, sort_keys=True))
    return 3 if readout["normalized_status"] == "BLOCKED_MALFORMED_EVIDENCE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
