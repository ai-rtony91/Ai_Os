"""Safe local autonomy run ledger helper for AIOS APPLY runners.

The ledger writes one JSON record per approved local research/simulation run.
It refuses traversal and protected surfaces, and it never mutates queues,
locks, approvals, registries, reports, telemetry, relay state, broker paths,
or live-trading surfaces.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_AUTONOMY_RUN_LEDGER_RECORD.v1"
DEFAULT_OUTPUT_ROOT = "automation/orchestration/self_development/run_ledger"

FORBIDDEN_PATH_TOKENS = {
    ".env",
    "secret",
    "secrets",
    "broker",
    "live_trading",
    "forex_live",
    "trading_lab_live",
    "oanda",
    "webhook",
    "orders",
    "queue",
    "command_queue",
    "locks",
    "approval_inbox",
    "registry",
    "reports",
    "telemetry",
    "relay",
}


class LedgerPathError(ValueError):
    """Raised when a ledger path crosses an approved write boundary."""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if not text:
        return default
    return text in {"true", "1", "yes", "y", "on", "approved", "present"}


def _safety(writes_ledger: bool = False) -> dict[str, Any]:
    return {
        "writes_files": bool(writes_ledger),
        "writes_only_approved_run_ledger": bool(writes_ledger),
        "mutates_registry": False,
        "creates_ready_stage": False,
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approval": False,
        "mutates_approvals": False,
        "writes_reports": False,
        "writes_telemetry": False,
        "writes_relay": False,
        "starts_runtime": False,
        "launches_workers": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "touches_secrets_or_env": False,
        "broker_or_live_trading": False,
        "protected_actions_blocked": True,
        "human_owner_required_before_worker_launch": True,
    }


def _path_has_forbidden_token(path: Path) -> str:
    for part in path.parts:
        token = part.lower()
        if token in FORBIDDEN_PATH_TOKENS:
            return token
        if token.endswith(".env") or ".env" in token:
            return ".env"
    return ""


def resolve_ledger_output_root(output_root: str | Path | None = None, repo_root: str | Path | None = None) -> Path:
    raw_root = _safe_str(output_root) or DEFAULT_OUTPUT_ROOT
    raw_path = Path(raw_root)
    if ".." in raw_path.parts:
        raise LedgerPathError("Ledger output root must not contain path traversal.")

    if not raw_path.is_absolute():
        base = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
        raw_path = base / raw_path

    resolved = raw_path.resolve()
    forbidden = _path_has_forbidden_token(resolved)
    if forbidden:
        raise LedgerPathError(f"Ledger output root crosses protected surface: {forbidden}")
    return resolved


def _safe_run_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", _safe_str(value)).strip("._")
    if not cleaned:
        raise LedgerPathError("Ledger run_id must contain at least one safe character.")
    if ".." in cleaned:
        raise LedgerPathError("Ledger run_id must not contain traversal.")
    return cleaned[:120]


def build_ledger_record(
    *,
    run_id: str,
    mode: str,
    task_type: str,
    status: str,
    generated_utc: str | None = None,
    safety: dict[str, Any] | None = None,
    stop_reason: str = "",
    next_safe_action: str = "",
    result_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "run_id": _safe_run_id(run_id),
        "mode": _normalized(mode),
        "task_type": _normalized(task_type),
        "status": _normalized(status),
        "generated_utc": _safe_str(generated_utc) or _now(),
        "safety": safety or _safety(writes_ledger=False),
        "stop_reason": _safe_str(stop_reason),
        "next_safe_action": _safe_str(next_safe_action),
        "result_summary": result_summary or {},
    }


def write_ledger_record(
    output_root: str | Path | None,
    record: dict[str, Any],
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = resolve_ledger_output_root(output_root, repo_root=repo_root)
    run_id = _safe_run_id(_safe_str(record.get("run_id")))
    root.mkdir(parents=True, exist_ok=True)
    target = (root / f"{run_id}.json").resolve()
    if root not in target.parents:
        raise LedgerPathError("Ledger record target must stay inside output root.")

    forbidden = _path_has_forbidden_token(target)
    if forbidden:
        raise LedgerPathError(f"Ledger record target crosses protected surface: {forbidden}")

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
        "safety": _safety(writes_ledger=True),
    }


def build_in_memory_ledger_reference(
    *,
    run_id: str,
    mode: str,
    task_type: str,
    status: str,
    generated_utc: str | None = None,
    stop_reason: str = "",
    next_safe_action: str = "",
    result_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = build_ledger_record(
        run_id=run_id,
        mode=mode,
        task_type=task_type,
        status=status,
        generated_utc=generated_utc,
        stop_reason=stop_reason,
        next_safe_action=next_safe_action,
        result_summary=result_summary,
    )
    return {
        "written": False,
        "path": "",
        "output_root": "",
        "record": record,
        "safety": _safety(writes_ledger=False),
    }
