from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from automation.orchestration.dashboard.aios_dashboard_state_report_writer import write_dashboard_state_report


MODE = "MANUAL_DASHBOARD_SNAPSHOT"
SUCCESS_STATUS = "WROTE"


def create_manual_dashboard_snapshot(
    projected_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
    output_root: str | Path | None = None,
    filename: str | None = None,
    overwrite: bool = False,
    manual_trigger: bool = True,
) -> dict[str, Any]:
    if manual_trigger is not True:
        return _metadata(
            "BLOCKED",
            reason="manual_trigger_required",
            writer_status="NOT_CALLED",
            safety_flags=_safety_flags(manual_trigger=False, writer_called=False),
        )

    try:
        result = write_dashboard_state_report(
            projected_state=projected_state,
            evidence=evidence,
            now_utc=now_utc,
            output_root=output_root,
            filename=filename,
            overwrite=overwrite,
        )
    except Exception as exc:  # pragma: no cover
        return _metadata(
            "BLOCKED",
            reason=f"writer_exception:{exc.__class__.__name__}",
            writer_status="ERROR",
            safety_flags=_safety_flags(manual_trigger=True, writer_called=True),
        )

    if not isinstance(result, Mapping):
        return _metadata(
            "BLOCKED",
            reason="invalid_writer_result",
            writer_status="UNKNOWN",
            safety_flags=_safety_flags(manual_trigger=True, writer_called=True),
        )

    writer_status = str(result.get("status") or "UNKNOWN")
    flags = _merge_flags(result.get("safety_flags"), manual_trigger=True)
    output_path = str(result.get("output_path") or "")
    bytes_written = int(result.get("bytes_written") or 0)
    reason = str(result.get("reason") or "unknown")

    if writer_status == SUCCESS_STATUS and output_path:
        return _metadata(
            SUCCESS_STATUS,
            output_path=output_path,
            bytes_written=bytes_written,
            reason=reason,
            writer_status=writer_status,
            safety_flags=flags,
        )

    status = "BLOCKED" if writer_status == "BLOCKED" else "NEEDS_REVIEW"
    return _metadata(
        status,
        output_path=output_path,
        bytes_written=bytes_written,
        reason=reason,
        writer_status=writer_status,
        safety_flags=flags,
    )


def _safety_flags(*, manual_trigger: bool, writer_called: bool) -> dict[str, bool]:
    return {
        "manual_trigger": manual_trigger,
        "writer_called": writer_called,
        "output_written": False,
        "control_authority": False,
        "execution_allowed": False,
        "mutation_allowed": False,
        "broker_allowed": False,
        "live_trading_allowed": False,
    }


def _merge_flags(value: Any, *, manual_trigger: bool) -> dict[str, bool]:
    flags = _safety_flags(manual_trigger=manual_trigger, writer_called=True)
    if isinstance(value, Mapping):
        flags.update({str(key): bool(flag) for key, flag in value.items()})
    flags["manual_trigger"] = manual_trigger
    flags["writer_called"] = True
    flags["output_written"] = False
    flags["control_authority"] = False
    flags["execution_allowed"] = False
    flags["mutation_allowed"] = False
    flags["broker_allowed"] = False
    flags["live_trading_allowed"] = False
    return flags


def _metadata(
    status: str,
    *,
    output_path: str = "",
    bytes_written: int = 0,
    reason: str,
    writer_status: str,
    safety_flags: Mapping[str, bool],
) -> dict[str, Any]:
    flags = dict(safety_flags)
    if status == SUCCESS_STATUS:
        flags["output_written"] = True
    return {
        "status": status,
        "output_path": output_path,
        "bytes_written": bytes_written,
        "mode": MODE,
        "safety_flags": flags,
        "reason": reason,
        "writer_status": writer_status,
    }


__all__ = ["create_manual_dashboard_snapshot"]
