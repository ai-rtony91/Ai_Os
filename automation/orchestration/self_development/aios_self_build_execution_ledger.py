"""Approved local self-build execution ledger helper."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_EXECUTION_LEDGER_RECORD.v1"
DEFAULT_OUTPUT_ROOT = "automation/orchestration/self_development/run_ledger"

FORBIDDEN_PATH_TOKENS = {
    ".env",
    "secret",
    "secrets",
    "broker",
    "live",
    "live_trading",
    "forex_live",
    "trading_lab_live",
    "oanda",
    "webhook",
    "orders",
    "queue",
    "command_queue",
    "locks",
    "approval",
    "approval_inbox",
    "registry",
    "reports",
    "telemetry",
    "relay",
}


class SelfBuildLedgerPathError(ValueError):
    """Raised when a self-build ledger path crosses approved boundaries."""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _safe_run_id(value: Any) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", _safe_str(value)).strip("._")
    if not cleaned:
        raise SelfBuildLedgerPathError("Self-build ledger run_id must contain a safe character.")
    if ".." in cleaned:
        raise SelfBuildLedgerPathError("Self-build ledger run_id must not contain traversal.")
    return cleaned[:120]


def _path_has_forbidden_token(path: Path) -> str:
    for part in path.parts:
        token = part.lower()
        if token in FORBIDDEN_PATH_TOKENS:
            return token
        if ".env" in token:
            return ".env"
    return ""


def _safety(writes_ledger: bool = False) -> dict[str, Any]:
    return {
        "writes_files": bool(writes_ledger),
        "writes_only_approved_run_ledger": bool(writes_ledger),
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approval": False,
        "mutates_registry": False,
        "creates_ready_stage": False,
        "starts_runtime": False,
        "launches_workers": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "touches_secrets_or_env": False,
        "broker_or_live_trading": False,
        "pushes": False,
        "creates_pr": False,
        "merges": False,
        "protected_actions_blocked": True,
    }


def resolve_self_build_ledger_output_root(
    output_root: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> Path:
    raw_root = _safe_str(output_root) or DEFAULT_OUTPUT_ROOT
    raw_path = Path(raw_root)
    if ".." in raw_path.parts:
        raise SelfBuildLedgerPathError("Self-build ledger output root must not contain traversal.")
    if not raw_path.is_absolute():
        base = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
        raw_path = base / raw_path
    resolved = raw_path.resolve()
    forbidden = _path_has_forbidden_token(resolved)
    if forbidden:
        raise SelfBuildLedgerPathError(f"Self-build ledger output root crosses protected surface: {forbidden}")
    return resolved


def build_self_build_ledger_record(
    *,
    run_id: str,
    candidate_id: str,
    packet_id: str,
    mode: str,
    status: str,
    generated_utc: str | None = None,
    validator_summary: dict[str, Any] | None = None,
    repair_attempts: int = 0,
    safety: dict[str, Any] | None = None,
    stop_reason: str = "",
    next_safe_action: str = "",
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "run_id": _safe_run_id(run_id),
        "generated_utc": _safe_str(generated_utc) or _now(),
        "candidate_id": _safe_str(candidate_id),
        "packet_id": _safe_str(packet_id),
        "mode": _normalized(mode),
        "status": _normalized(status),
        "validator_summary": validator_summary or {},
        "repair_attempts": int(repair_attempts),
        "safety": safety or _safety(writes_ledger=False),
        "stop_reason": _safe_str(stop_reason),
        "next_safe_action": _safe_str(next_safe_action),
    }


def write_self_build_ledger_record(
    output_root: str | Path | None,
    record: dict[str, Any],
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = resolve_self_build_ledger_output_root(output_root, repo_root=repo_root)
    run_id = _safe_run_id(record.get("run_id"))
    root.mkdir(parents=True, exist_ok=True)
    target = (root / f"{run_id}.json").resolve()
    if root not in target.parents:
        raise SelfBuildLedgerPathError("Self-build ledger target must stay inside output root.")
    forbidden = _path_has_forbidden_token(target)
    if forbidden:
        raise SelfBuildLedgerPathError(f"Self-build ledger target crosses protected surface: {forbidden}")

    payload = dict(record)
    payload["safety"] = dict(payload.get("safety") or {})
    payload["safety"].update(_safety(writes_ledger=True))
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "written": True,
        "path": str(target).replace("\\", "/"),
        "output_root": str(root).replace("\\", "/"),
        "schema": SCHEMA,
        "run_id": run_id,
        "record": payload,
        "safety": _safety(writes_ledger=True),
    }


def build_in_memory_self_build_ledger_reference(
    *,
    run_id: str,
    candidate_id: str,
    packet_id: str,
    mode: str,
    status: str,
    generated_utc: str | None = None,
    validator_summary: dict[str, Any] | None = None,
    repair_attempts: int = 0,
    stop_reason: str = "",
    next_safe_action: str = "",
) -> dict[str, Any]:
    record = build_self_build_ledger_record(
        run_id=run_id,
        candidate_id=candidate_id,
        packet_id=packet_id,
        mode=mode,
        status=status,
        generated_utc=generated_utc,
        validator_summary=validator_summary,
        repair_attempts=repair_attempts,
        stop_reason=stop_reason,
        next_safe_action=next_safe_action,
    )
    return {
        "written": False,
        "path": "",
        "output_root": "",
        "record": record,
        "safety": _safety(writes_ledger=False),
    }
