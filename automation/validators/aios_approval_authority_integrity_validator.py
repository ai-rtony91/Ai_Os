from __future__ import annotations

import argparse
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


PLACEHOLDER_TIMESTAMPS = {
    "2026-06-08T00:00:00Z",
    "2026-06-02T00:00:00Z",
}


@dataclass(frozen=True)
class ApprovalAuthorityResult:
    status: str
    hardened_approval_verified: bool
    failed_checks: list[str]
    evidence_type: str
    next_safe_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "validator": "aios_approval_authority_integrity_validator",
            "status": self.status,
            "hardened_approval_verified": self.hardened_approval_verified,
            "failed_checks": self.failed_checks,
            "evidence_type": self.evidence_type,
            "next_safe_action": self.next_safe_action,
        }


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip().replace("\\", "/").strip("/") for item in value if str(item).strip()]


def _is_midnight_placeholder(value: str) -> bool:
    if value in PLACEHOLDER_TIMESTAMPS:
        return True
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.hour == 0 and parsed.minute == 0 and parsed.second == 0


def _canonical_payload(gate: dict[str, Any]) -> str:
    approval_evidence = gate.get("approval_evidence")
    if not isinstance(approval_evidence, dict):
        approval_evidence = {}
    payload = {
        "packet_id": str(gate.get("packet_id") or ""),
        "allowed_paths": sorted(_as_list(gate.get("allowed_paths"))),
        "blocked_paths": sorted(_as_list(gate.get("blocked_paths"))),
        "approval_timestamp_utc": str(
            gate.get("approval_timestamp_utc")
            or gate.get("bound_at")
            or gate.get("approval_timestamp_placeholder")
            or ""
        ),
        "validator_chain": [str(item) for item in _as_list(gate.get("validator_chain"))],
        "approval_nonce": str(approval_evidence.get("approval_nonce") or gate.get("approval_nonce") or ""),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _valid_hmac(gate: dict[str, Any], key: str | None) -> bool:
    approval_evidence = gate.get("approval_evidence")
    if not isinstance(approval_evidence, dict):
        return False
    provided = str(approval_evidence.get("approval_hmac_sha256") or "")
    if not key or not provided:
        return False
    expected = hmac.new(key.encode("utf-8"), _canonical_payload(gate).encode("utf-8"), sha256).hexdigest()
    return hmac.compare_digest(provided, expected)


def validate_approval_gate(gate: dict[str, Any], *, hmac_key: str | None = None) -> ApprovalAuthorityResult:
    failed: list[str] = []
    evidence = gate.get("approval_evidence") if isinstance(gate.get("approval_evidence"), dict) else {}
    evidence_type = str(evidence.get("type") or "MISSING")

    if str(gate.get("approval_status") or "") != "approved_for_apply":
        return ApprovalAuthorityResult(
            status="PENDING_REVIEW",
            hardened_approval_verified=False,
            failed_checks=[],
            evidence_type=evidence_type,
            next_safe_action="Human Owner approval is pending; do not APPLY.",
        )

    if gate.get("approved_by_human") is not True:
        failed.append("approved_by_human_not_true")
    if not str(gate.get("packet_id") or "").strip():
        failed.append("packet_id_missing")
    if not _as_list(gate.get("allowed_paths")):
        failed.append("allowed_paths_missing")
    if not _as_list(gate.get("blocked_paths")):
        failed.append("blocked_paths_missing")
    if not (gate.get("validator_chain_required") is True or _as_list(gate.get("validator_chain"))):
        failed.append("validator_chain_missing")

    approval_timestamp = str(
        gate.get("approval_timestamp_utc")
        or gate.get("bound_at")
        or gate.get("approval_timestamp_placeholder")
        or ""
    )
    if not approval_timestamp:
        failed.append("approval_timestamp_missing")
    elif _is_midnight_placeholder(approval_timestamp):
        failed.append("approval_timestamp_placeholder")

    if str(gate.get("bound_by") or "").strip() and not evidence:
        failed.append("bound_by_free_text_without_hardened_evidence")

    if evidence_type != "HMAC_SHA256":
        failed.append("approval_evidence_type_missing_or_unsupported")
    if not _valid_hmac(gate, hmac_key):
        failed.append("approval_hmac_missing_or_invalid")

    status = "PASS" if not failed else "BLOCKED"
    return ApprovalAuthorityResult(
        status=status,
        hardened_approval_verified=status == "PASS",
        failed_checks=failed,
        evidence_type=evidence_type,
        next_safe_action=(
            "Hardened human approval evidence verified."
            if status == "PASS"
            else "Do not APPLY; collect exact-scope Human Owner approval evidence."
        ),
    )


def load_gate(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default="automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    gate = load_gate(Path(args.gate))
    result = validate_approval_gate(gate, hmac_key=os.environ.get("AIOS_HUMAN_APPROVAL_HMAC_KEY"))
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"status={result.status}")
        print(f"hardened_approval_verified={str(result.hardened_approval_verified).lower()}")
        print(f"failed_checks={','.join(result.failed_checks)}")
    return 0 if result.status in {"PASS", "PENDING_REVIEW"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
