"""Local-only YubiKey approval evidence scaffold for Operator Relief."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_pi_yubikey_approval_station_v1"
OUTPUT_ROOT = Path("Reports/operator_relief/approvals")

MODE_DRY_RUN = "DRY_RUN"
MODE_SIMULATED_TOUCH = "SIMULATED_TOUCH"
MODE_HARDWARE_FIDO2 = "HARDWARE_FIDO2"
SUPPORTED_MODES = {MODE_DRY_RUN, MODE_SIMULATED_TOUCH, MODE_HARDWARE_FIDO2}

DECISION_APPROVE_CONTINUE = "APPROVE_CONTINUE"
DECISION_DENY_STOP = "DENY_STOP"
DECISION_HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
DECISION_EXPIRE_REQUEST = "EXPIRE_REQUEST"
SUPPORTED_DECISIONS = {
    DECISION_APPROVE_CONTINUE,
    DECISION_DENY_STOP,
    DECISION_HOLD_FOR_REVIEW,
    DECISION_EXPIRE_REQUEST,
}

DEFAULT_REQUESTED_ACTION = "AI_OS_TASK_APPROVAL_REVIEW"


@dataclass(frozen=True)
class PiYubiKeyApprovalReport:
    report_type: str
    generated_at: str
    executable: bool
    task_id: str
    decision_id: str
    mode: str
    decision: str
    operator_decision: str
    approval_type: str
    requested_action: str
    protected_paths: list[str]
    protected_review_required: bool
    expires_at: str
    expired: bool
    yubikey_touch_required: bool
    yubikey_present: bool
    yubikey_touch_verified: bool
    approval_granted: bool
    approval_denied: bool
    hold_for_review: bool
    blocked_reasons: list[str]
    safety: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return slug or "task"


def _safe_timestamp(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safety() -> dict[str, bool]:
    return {
        "commit_authorized": False,
        "push_authorized": False,
        "merge_authorized": False,
        "protected_mutation_authorized": False,
        "cleanup_authorized": False,
        "live_trading_authorized": False,
        "broker_api_authorized": False,
        "secrets_authorized": False,
        "source_files_mutated": False,
        "executable": False,
    }


def _touch_state(
    mode: str,
    yubikey_present: bool | None,
    yubikey_touch_verified: bool | None,
) -> tuple[bool, bool, list[str]]:
    reasons: list[str] = []
    if mode == MODE_SIMULATED_TOUCH:
        present = True if yubikey_present is None else yubikey_present
        verified = True if yubikey_touch_verified is None else yubikey_touch_verified
        if not present:
            verified = False
            reasons.append("SIMULATED_TOUCH requested, but YubiKey presence was false.")
        return present, verified, reasons
    if mode == MODE_HARDWARE_FIDO2:
        present = bool(yubikey_present) if yubikey_present is not None else False
        verified = bool(yubikey_touch_verified) if yubikey_touch_verified is not None else False
        if not verified:
            reasons.append("HARDWARE_FIDO2 physical challenge is not implemented or available in this scaffold.")
        return present, verified, reasons
    present = bool(yubikey_present) if yubikey_present is not None else False
    verified = bool(yubikey_touch_verified) if yubikey_touch_verified is not None else False
    if verified:
        reasons.append("DRY_RUN mode cannot verify a physical YubiKey touch.")
        verified = False
    return present, verified, reasons


def build_yubikey_approval_report(
    task_id: str,
    decision: str,
    mode: str = MODE_DRY_RUN,
    requested_action: str = DEFAULT_REQUESTED_ACTION,
    protected_paths: list[str] | None = None,
    expires_minutes: int = 15,
    now: datetime | None = None,
    yubikey_present: bool | None = None,
    yubikey_touch_verified: bool | None = None,
) -> PiYubiKeyApprovalReport:
    if mode not in SUPPORTED_MODES:
        raise ValueError("Mode must be DRY_RUN, SIMULATED_TOUCH, or HARDWARE_FIDO2.")
    if decision not in SUPPORTED_DECISIONS:
        raise ValueError("Decision must be APPROVE_CONTINUE, DENY_STOP, HOLD_FOR_REVIEW, or EXPIRE_REQUEST.")
    if expires_minutes < 0:
        raise ValueError("expires_minutes must be zero or greater.")

    moment = now or datetime.now(timezone.utc)
    expires_at = moment + timedelta(minutes=expires_minutes)
    expired = decision == DECISION_EXPIRE_REQUEST or expires_at <= moment
    paths = [_normalize_path(path) for path in protected_paths or []]
    protected_review_required = bool(paths)
    present, touch_verified, touch_reasons = _touch_state(mode, yubikey_present, yubikey_touch_verified)

    blocked_reasons: list[str] = []
    blocked_reasons.extend(touch_reasons)
    if mode == MODE_DRY_RUN and decision == DECISION_APPROVE_CONTINUE:
        blocked_reasons.append("DRY_RUN mode records intent only and cannot grant approval.")
    if present and not touch_verified:
        blocked_reasons.append("YubiKey presence alone is not approval; physical touch verification is required.")
    if expired:
        blocked_reasons.append("Approval request is expired.")
    if protected_review_required:
        blocked_reasons.append("Protected paths require explicit protected review; this evidence does not authorize mutation.")

    approval_granted = (
        decision == DECISION_APPROVE_CONTINUE
        and touch_verified
        and not expired
        and mode == MODE_SIMULATED_TOUCH
    )
    approval_denied = decision == DECISION_DENY_STOP
    hold_for_review = decision == DECISION_HOLD_FOR_REVIEW

    if decision == DECISION_APPROVE_CONTINUE and not approval_granted and "Approval not granted." not in blocked_reasons:
        blocked_reasons.append("Approval not granted.")

    decision_id = f"yubikey_{_safe_slug(task_id)}_{_safe_timestamp(moment)}"
    return PiYubiKeyApprovalReport(
        report_type=REPORT_TYPE,
        generated_at=moment.isoformat(),
        executable=False,
        task_id=task_id,
        decision_id=decision_id,
        mode=mode,
        decision=decision,
        operator_decision=decision,
        approval_type="YUBIKEY_PHYSICAL_TOUCH",
        requested_action=requested_action,
        protected_paths=paths,
        protected_review_required=protected_review_required,
        expires_at=expires_at.isoformat(),
        expired=expired,
        yubikey_touch_required=True,
        yubikey_present=present,
        yubikey_touch_verified=touch_verified,
        approval_granted=approval_granted,
        approval_denied=approval_denied,
        hold_for_review=hold_for_review,
        blocked_reasons=blocked_reasons,
        safety=_safety(),
    )


def _resolve_output_path(repo_root: Path, task_id: str, generated_at: str) -> Path:
    root = repo_root.resolve()
    timestamp = _safe_timestamp(datetime.fromisoformat(generated_at))
    filename = f"yubikey_approval_{_safe_slug(task_id)}_{timestamp}.json"
    output = (root / OUTPUT_ROOT / filename).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("YubiKey approval reports must be written under Reports/operator_relief/approvals/.")
    return output


def write_report(result: PiYubiKeyApprovalReport, repo_root: Path) -> Path:
    path = _resolve_output_path(repo_root, result.task_id, result.generated_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build local YubiKey approval evidence for an AI_OS task.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--decision", required=True, choices=sorted(SUPPORTED_DECISIONS))
    parser.add_argument("--mode", choices=sorted(SUPPORTED_MODES), default=MODE_DRY_RUN)
    parser.add_argument("--requested-action", default=DEFAULT_REQUESTED_ACTION)
    parser.add_argument("--protected-path", action="append", default=[])
    parser.add_argument("--expires-minutes", type=int, default=15)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    result = build_yubikey_approval_report(
        task_id=args.task_id,
        decision=args.decision,
        mode=args.mode,
        requested_action=args.requested_action,
        protected_paths=args.protected_path,
        expires_minutes=args.expires_minutes,
    )
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_report(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
