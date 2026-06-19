"""Auto-exit live readiness model for forex live-readiness review.

The model is evidence/readiness only. It never implements live close, broker
write calls, or order placement.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "AIOS_FOREX_AUTO_EXIT_LIVE_READINESS.v1"
PAPER_LOOP_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md"
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_AUTO_EXIT_LIVE_READINESS_DRY_RUN_V1.md"
)


def build_auto_exit_live_readiness_model(
    *,
    repo_root: Path | None = None,
    policy_evidence: Mapping[str, Any] | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    evidence = (
        dict(policy_evidence)
        if policy_evidence is not None
        else load_evidence_model(root / PAPER_LOOP_EVIDENCE_PATH)
    )

    stop_loss_ready = has_policy(
        first_present(evidence, "stop_loss_policy", "stop_loss_required")
    )
    take_profit_policy_ready = has_policy(first_present(evidence, "take_profit_policy"))
    trailing_stop_policy_ready = has_policy(
        first_present(evidence, "trailing_stop_policy", default="OPTIONAL_NOT_READY")
    )
    max_time_policy_ready = has_policy(first_present(evidence, "max_time_policy"))
    manual_fallback_ready = has_policy(
        first_present(
            evidence,
            "manual_close_fallback",
            "manual_broker_ui_fallback",
            default="MANUAL_BROKER_UI_FALLBACK_REQUIRED",
        )
    )

    blocked_reasons: list[str] = []
    if not stop_loss_ready:
        blocked_reasons.append("stop_loss_policy_missing_for_live_exit")
    if not take_profit_policy_ready:
        blocked_reasons.append("take_profit_policy_missing_for_live_exit")
    if not max_time_policy_ready:
        blocked_reasons.append("max_time_policy_missing_for_live_exit")
    if not manual_fallback_ready:
        blocked_reasons.append("manual_broker_ui_fallback_missing_for_live_exit")
    blocked_reasons.append("auto_exit_readiness_not_implemented_for_live_execution")
    blocked_reasons.append("future_live_safe_close_packet_not_approved")

    result = {
        "schema": SCHEMA,
        "AUTO_EXIT_LIVE_READY": False,
        "live_execution_allowed": False,
        "stop_loss_required": True,
        "stop_loss_ready": stop_loss_ready,
        "take_profit_policy_ready": take_profit_policy_ready,
        "trailing_stop_policy_ready": trailing_stop_policy_ready,
        "max_time_policy_ready": max_time_policy_ready,
        "manual_broker_ui_fallback_required": True,
        "manual_broker_ui_fallback_ready": manual_fallback_ready,
        "auto_exit_write_calls_allowed": False,
        "broker_write_calls_allowed": False,
        "close_trade_allowed": False,
        "blocked_reasons": unique(blocked_reasons),
        "next_safe_action": next_safe_action(),
        "evidence_path": str(REPORT_PATH),
        "generated_at_utc": generated_at_utc or utc_now_iso(),
    }
    assert_auto_exit_sanitized(result)
    return result


def build_sanitized_report(result: Mapping[str, Any]) -> str:
    assert_auto_exit_sanitized(result)
    return (
        "# AIOS Forex Auto-Exit Live Readiness Dry Run V1\n\n"
        "## Readiness Status\n"
        f"- AUTO_EXIT_LIVE_READY: {result.get('AUTO_EXIT_LIVE_READY')}\n"
        f"- live_execution_allowed: {result.get('live_execution_allowed')}\n"
        f"- stop_loss_required: {result.get('stop_loss_required')}\n"
        f"- stop_loss_ready: {result.get('stop_loss_ready')}\n"
        f"- take_profit_policy_ready: {result.get('take_profit_policy_ready')}\n"
        f"- trailing_stop_policy_ready: {result.get('trailing_stop_policy_ready')}\n"
        f"- max_time_policy_ready: {result.get('max_time_policy_ready')}\n"
        f"- manual_broker_ui_fallback_required: "
        f"{result.get('manual_broker_ui_fallback_required')}\n"
        f"- close_trade_allowed: {result.get('close_trade_allowed')}\n"
        f"- broker_write_calls_allowed: {result.get('broker_write_calls_allowed')}\n\n"
        "## Blockers\n"
        f"{json.dumps(result.get('blocked_reasons', []), indent=2, sort_keys=True)}\n\n"
        "## Explicit Safety Confirmations\n"
        "- No live close implementation exists here.\n"
        "- No broker write calls were made.\n"
        "- No live trade was placed.\n"
        "- No secrets, account identifier values, broker order identifier values, "
        "or transaction identifier values were recorded.\n\n"
        "## Sanitized JSON Summary\n"
        "```json\n"
        f"{json.dumps(cli_summary(result), indent=2, sort_keys=True)}\n"
        "```\n"
    )


def write_auto_exit_live_readiness_report(
    result: Mapping[str, Any], *, repo_root: Path | None = None
) -> Path:
    root = repo_root or Path(__file__).resolve().parents[2]
    report_path = root / REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_sanitized_report(result), encoding="utf-8")
    return report_path


def cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    assert_auto_exit_sanitized(result)
    return {
        "schema": result.get("schema"),
        "AUTO_EXIT_LIVE_READY": result.get("AUTO_EXIT_LIVE_READY"),
        "live_execution_allowed": False,
        "stop_loss_ready": result.get("stop_loss_ready"),
        "take_profit_policy_ready": result.get("take_profit_policy_ready"),
        "trailing_stop_policy_ready": result.get("trailing_stop_policy_ready"),
        "max_time_policy_ready": result.get("max_time_policy_ready"),
        "manual_broker_ui_fallback_required": result.get(
            "manual_broker_ui_fallback_required"
        ),
        "auto_exit_write_calls_allowed": False,
        "broker_write_calls_allowed": False,
        "close_trade_allowed": False,
        "blocked_reasons": result.get("blocked_reasons", []),
        "next_safe_action": result.get("next_safe_action"),
        "evidence_path": result.get("evidence_path"),
    }


def load_evidence_model(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    blocks = text.split("```")
    for index in range(len(blocks) - 1, -1, -1):
        if index % 2 != 1:
            continue
        block = blocks[index].removeprefix("json").strip()
        try:
            loaded = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            return loaded
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def assert_auto_exit_sanitized(payload: Mapping[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    for marker in (
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
        "Authorization",
        "Bearer ",
        "accountID",
        "orderID",
        "transactionID",
        "rawBroker",
    ):
        if marker in serialized:
            raise ValueError(f"unsafe_auto_exit_marker:{marker}")
    for field in (
        "AUTO_EXIT_LIVE_READY",
        "live_execution_allowed",
        "auto_exit_write_calls_allowed",
        "broker_write_calls_allowed",
        "close_trade_allowed",
    ):
        if payload.get(field) is not False:
            raise ValueError(f"{field} must remain false")


def next_safe_action() -> str:
    return (
        "Keep live execution blocked. Implement a separately approved live-safe "
        "exit/close readiness packet before any broker close path can exist."
    )


def first_present(model: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in model and model[name] is not None:
            return model[name]
    return default


def has_policy(value: Any) -> bool:
    text = str(value or "").strip().upper()
    return bool(text and text not in {"FALSE", "MISSING", "NONE", "NULL"})


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output
