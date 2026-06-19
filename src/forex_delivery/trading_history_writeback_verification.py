"""Trading-history writeback verification for live-readiness review.

This module evaluates sanitized local evidence only. It never calls brokers,
reads secrets, writes orders, or changes live execution permission.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "AIOS_FOREX_TRADING_HISTORY_WRITEBACK_VERIFICATION.v1"
READ_ONLY_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_DRY_RUN_V1.md"
)
PAPER_LOOP_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md"
)
REPORT_PATH = Path(
    "Reports/forex_delivery/"
    "AIOS_FOREX_TRADING_HISTORY_WRITEBACK_VERIFICATION_DRY_RUN_V1.md"
)


def build_trading_history_writeback_verification_model(
    *,
    repo_root: Path | None = None,
    read_only_model: Mapping[str, Any] | None = None,
    paper_model: Mapping[str, Any] | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    read_only = (
        dict(read_only_model)
        if read_only_model is not None
        else load_evidence_model(root / READ_ONLY_EVIDENCE_PATH)
    )
    paper = (
        dict(paper_model)
        if paper_model is not None
        else load_evidence_model(root / PAPER_LOOP_EVIDENCE_PATH)
    )

    source_type = lower_text(first_present_nested(read_only, "source_type", default="missing"))
    source_label = str(first_present_nested(read_only, "source_label", default="MISSING"))
    freshness_utc = first_present_nested(
        read_only, "freshness_utc", "trading_history.freshness_utc", default="MISSING"
    )
    stale_status = upper_text(first_present_nested(read_only, "stale_status", default="MISSING"))
    history = dict(read_only.get("trading_history") or {})
    rows = first_present_nested(history, "history_rows", "rows", default=[])
    if not isinstance(rows, list):
        rows = []

    trading_history_available = coerce_bool(
        first_present_nested(
            history,
            "trading_history_available",
            "available",
            default=False,
        )
    )
    sanitized_history_rows_count = len(rows)
    real_broker_history_writeback_verified = (
        source_type == "broker-live-read-only"
        and stale_status == "VALID"
        and "SANITIZED" in source_label.upper()
        and trading_history_available
        and sanitized_history_rows_count > 0
    )
    paper_history_writeback_verified = coerce_bool(
        first_present_nested(
            paper,
            "trading_history_row_written",
            "dashboard_status.PAPER_LOOP_AVAILABLE",
            default=False,
        )
    )
    paper_evidence_path = str(
        first_present_nested(paper, "evidence_path", default=str(PAPER_LOOP_EVIDENCE_PATH))
    )
    trading_history_evidence_path = str(
        first_present_nested(
            history,
            "evidence_path",
            "sanitized_evidence_path",
            default=str(READ_ONLY_EVIDENCE_PATH),
        )
    )

    blocked_reasons: list[str] = []
    evidence_present: list[str] = []
    evidence_missing: list[str] = []
    if paper_history_writeback_verified:
        evidence_present.append("paper_history_writeback_verified")
    else:
        evidence_missing.append("paper_history_writeback_evidence")
        blocked_reasons.append("paper_history_writeback_not_verified")

    if real_broker_history_writeback_verified:
        evidence_present.append("real_broker_history_writeback_verified")
    else:
        evidence_missing.append("real_broker_history_writeback_evidence")
        blocked_reasons.append("real_trading_history_writeback_not_verified")

    if source_type == "fixture":
        blocked_reasons.append("fixture_history_cannot_verify_real_broker_writeback")
    if not trading_history_available:
        block_reason = str(
            first_present_nested(
                history,
                "block_reason",
                default="real broker trading history evidence is unavailable",
            )
        )
    elif not real_broker_history_writeback_verified:
        block_reason = "sanitized real broker history row is not verified"
    else:
        block_reason = "NONE"

    result = {
        "schema": SCHEMA,
        "trading_history_available": trading_history_available,
        "trading_history_writeback_verified": real_broker_history_writeback_verified,
        "paper_history_writeback_verified": paper_history_writeback_verified,
        "real_broker_history_writeback_verified": real_broker_history_writeback_verified,
        "trading_history_evidence_path": trading_history_evidence_path,
        "paper_history_evidence_path": paper_evidence_path,
        "trading_history_block_reason": block_reason,
        "sanitized_history_rows_count": sanitized_history_rows_count,
        "source_type": source_type,
        "source_label": source_label,
        "freshness_utc": freshness_utc,
        "stale_status": stale_status,
        "live_execution_allowed": False,
        "blocked_reasons": unique(blocked_reasons),
        "evidence_present": unique(evidence_present),
        "evidence_missing": unique(evidence_missing),
        "next_safe_action": next_safe_action(real_broker_history_writeback_verified),
        "generated_at_utc": generated_at_utc or utc_now_iso(),
    }
    assert_history_verification_sanitized(result)
    return result


def build_sanitized_report(result: Mapping[str, Any]) -> str:
    assert_history_verification_sanitized(result)
    return (
        "# AIOS Forex Trading History Writeback Verification Dry Run V1\n\n"
        "## Verification Status\n"
        f"- trading_history_available: {result.get('trading_history_available')}\n"
        f"- trading_history_writeback_verified: {result.get('trading_history_writeback_verified')}\n"
        f"- paper_history_writeback_verified: {result.get('paper_history_writeback_verified')}\n"
        f"- real_broker_history_writeback_verified: {result.get('real_broker_history_writeback_verified')}\n"
        f"- sanitized_history_rows_count: {result.get('sanitized_history_rows_count')}\n"
        f"- source_label: {result.get('source_label')}\n"
        f"- freshness_utc: {result.get('freshness_utc')}\n"
        f"- live_execution_allowed: {result.get('live_execution_allowed')}\n\n"
        "## Block Reason\n"
        f"{result.get('trading_history_block_reason')}\n\n"
        "## Blockers\n"
        f"{json.dumps(result.get('blocked_reasons', []), indent=2, sort_keys=True)}\n\n"
        "## Explicit Safety Confirmations\n"
        "- No live trade was placed.\n"
        "- No broker write calls were made.\n"
        "- No secrets, account identifier values, broker order identifier values, "
        "or transaction identifier values were recorded.\n\n"
        "## Sanitized JSON Summary\n"
        "```json\n"
        f"{json.dumps(cli_summary(result), indent=2, sort_keys=True)}\n"
        "```\n"
    )


def write_trading_history_writeback_verification_report(
    result: Mapping[str, Any], *, repo_root: Path | None = None
) -> Path:
    root = repo_root or Path(__file__).resolve().parents[2]
    report_path = root / REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_sanitized_report(result), encoding="utf-8")
    return report_path


def cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    assert_history_verification_sanitized(result)
    return {
        "schema": result.get("schema"),
        "trading_history_available": result.get("trading_history_available"),
        "trading_history_writeback_verified": result.get(
            "trading_history_writeback_verified"
        ),
        "paper_history_writeback_verified": result.get(
            "paper_history_writeback_verified"
        ),
        "real_broker_history_writeback_verified": result.get(
            "real_broker_history_writeback_verified"
        ),
        "sanitized_history_rows_count": result.get("sanitized_history_rows_count"),
        "source_label": result.get("source_label"),
        "freshness_utc": result.get("freshness_utc"),
        "live_execution_allowed": False,
        "blocked_reasons": result.get("blocked_reasons", []),
        "next_safe_action": result.get("next_safe_action"),
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


def assert_history_verification_sanitized(payload: Mapping[str, Any]) -> None:
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
            raise ValueError(f"unsafe_history_verification_marker:{marker}")
    if payload.get("live_execution_allowed") is not False:
        raise ValueError("history_verification_must_not_allow_live_execution")


def next_safe_action(real_verified: bool) -> str:
    if real_verified:
        return (
            "Use verified sanitized broker history as evidence only; keep live "
            "execution blocked until a separately approved execution packet exists."
        )
    return (
        "Keep live execution blocked and produce sanitized broker read-only "
        "history/writeback evidence before reducing the real history blocker."
    )


def first_present_nested(model: Mapping[str, Any], *paths: str, default: Any = None) -> Any:
    for path in paths:
        current: Any = model
        found = True
        for part in path.split("."):
            if not isinstance(current, Mapping) or part not in current:
                found = False
                break
            current = current[part]
        if found and current is not None:
            return current
    return default


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ready", "available"}
    return bool(value)


def lower_text(value: Any) -> str:
    return str(value or "").strip().lower()


def upper_text(value: Any) -> str:
    return str(value or "").strip().upper()


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
