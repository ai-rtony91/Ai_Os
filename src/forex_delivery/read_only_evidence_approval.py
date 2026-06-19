"""Read-only broker evidence approval and reconciliation evaluator.

This layer approves sanitized read-only evidence for future live review only.
It never reads secrets, calls brokers, places orders, or changes execution
permission.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "AIOS_FOREX_READ_ONLY_EVIDENCE_APPROVAL_AND_RECONCILIATION.v1"
READ_ONLY_BRIDGE_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_DRY_RUN_V1.md"
)
APPROVAL_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/"
    "AIOS_FOREX_READ_ONLY_EVIDENCE_APPROVAL_AND_RECONCILIATION_DRY_RUN_V1.md"
)
APPROVED_SOURCE_TYPE = "broker-live-read-only"
APPROVED_SOURCE_LABELS = {"OANDA_READ_ONLY_SANITIZED", "BROKER_READ_ONLY_SANITIZED"}


def build_read_only_evidence_approval_model(
    read_only_model: Mapping[str, Any] | None = None,
    *,
    repo_root: Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    """Evaluate sanitized read-only evidence for future live-review use."""

    root = repo_root or Path(__file__).resolve().parents[2]
    model = (
        dict(read_only_model)
        if read_only_model is not None
        else load_evidence_model(root / READ_ONLY_BRIDGE_EVIDENCE_PATH)
    )

    source_type = lower_text(
        first_present_nested(
            model,
            "source_type",
            "market.source_type",
            "execution_readiness.source_type",
            default="missing",
        )
    )
    source_label = upper_text(
        first_present_nested(
            model,
            "source_label",
            "market.source_label",
            "execution_readiness.source_label",
            default="MISSING",
        )
    )
    freshness_utc = first_present_nested(
        model,
        "freshness_utc",
        "market.freshness_utc",
        "execution_readiness.freshness_utc",
        "generated_at_utc",
    )
    stale_status = upper_text(
        first_present_nested(
            model,
            "stale_status",
            "market.stale_status",
            "execution_readiness.stale_status",
            default="MISSING",
        )
    )

    broker_account_reachable = coerce_bool(
        first_present_nested(
            model,
            "broker_state.account_reachable",
            "broker_state.reachable",
            "account_reachable",
            "broker_reachable",
            default=False,
        )
    )
    open_position_count = coerce_int_or_none(
        first_present_nested(
            model,
            "broker_state.open_position_count",
            "positions.open_position_count",
            "open_position_count",
        )
    )
    open_positions_reconciled = coerce_bool(
        first_present_nested(
            model,
            "broker_state.open_positions_reconciled",
            "positions.positions_reconciled",
            "positions.open_positions_reconciled",
            "open_positions_reconciled",
            default=False,
        )
    )
    if broker_account_reachable and open_position_count is not None:
        open_positions_reconciled = True

    daily_pl_available = coerce_bool(
        first_present_nested(
            model,
            "broker_state.daily_pl_available",
            "risk_pl.daily_pl_available",
            "daily_pl_available",
            "pl_available",
            default=False,
        )
    )
    realized_pl = first_present_nested(
        model,
        "broker_state.realized_pl",
        "risk_pl.realized_pl",
        "realized_pl",
    )
    unrealized_pl = first_present_nested(
        model,
        "broker_state.unrealized_pl",
        "risk_pl.unrealized_pl",
        "unrealized_pl",
    )
    realized_pl_available = is_available_value(realized_pl)
    unrealized_pl_available = is_available_value(unrealized_pl)
    margin_risk_available = coerce_bool(
        first_present_nested(
            model,
            "broker_state.margin_risk_available",
            "risk_pl.margin_risk_available",
            "margin_risk_available",
            default=False,
        )
    )
    trading_history_available = coerce_bool(
        first_present_nested(
            model,
            "trading_history.trading_history_available",
            "trading_history.available",
            "trading_history_available",
            default=False,
        )
    )
    history_rows = first_present_nested(
        model,
        "trading_history.history_rows",
        "trading_history.rows",
        "history_rows",
        default=[],
    )
    trading_history_writeback_verified = trading_history_available and bool(history_rows)
    trading_history_block_reason = str(
        first_present_nested(
            model,
            "trading_history.block_reason",
            "trading_history_block_reason",
            "block_reason",
            default="",
        )
    )

    capabilities = dict(model.get("capabilities") or {})
    broker_write_calls_allowed = coerce_bool(
        capabilities.get("broker_write_calls_allowed", False)
    )
    order_placement_allowed = coerce_bool(
        capabilities.get("order_placement_allowed", False)
    )
    close_trade_allowed = coerce_bool(capabilities.get("close_trade_allowed", False))

    evidence_present: list[str] = []
    evidence_missing: list[str] = []
    blocked_reasons: list[str] = []

    if source_type == APPROVED_SOURCE_TYPE:
        evidence_present.append("broker_live_read_only_source_type")
    else:
        evidence_missing.append("broker_live_read_only_source_type")
        if source_type == "fixture":
            blocked_reasons.append("read_only_bridge_fixture_source_not_live_permitted")
        else:
            blocked_reasons.append("read_only_source_type_not_broker_live_read_only")

    if source_label in APPROVED_SOURCE_LABELS or source_label.endswith("_READ_ONLY_SANITIZED"):
        evidence_present.append("sanitized_broker_source_label")
    else:
        evidence_missing.append("sanitized_broker_source_label")
        blocked_reasons.append("sanitized_broker_source_label_missing")

    if freshness_utc:
        evidence_present.append("freshness_utc_present")
    else:
        evidence_missing.append("freshness_utc")
        blocked_reasons.append("freshness_utc_missing")

    if stale_status == "VALID":
        evidence_present.append("stale_status_valid")
    else:
        evidence_missing.append("valid_stale_status")
        blocked_reasons.append("read_only_evidence_not_valid")

    if broker_account_reachable:
        evidence_present.append("broker_account_reachable")
    else:
        evidence_missing.append("broker_account_reachable")
        blocked_reasons.append("broker_account_not_reachable_in_read_only_evidence")

    if open_positions_reconciled:
        evidence_present.append("open_positions_reconciled")
    else:
        evidence_missing.append("open_positions_reconciled")
        blocked_reasons.append("open_positions_not_reconciled_in_read_only_evidence")

    if open_position_count is None:
        evidence_missing.append("open_position_count")
        blocked_reasons.append("open_position_count_missing")
    elif open_position_count == 0:
        evidence_present.append("zero_open_positions_reconciled")
    else:
        evidence_present.append("open_position_count_preserved")
        blocked_reasons.append("open_live_positions_present_review_required")

    if daily_pl_available:
        evidence_present.append("daily_pl_available")
    else:
        evidence_missing.append("daily_pl_available")
        blocked_reasons.append("daily_pl_not_available_in_read_only_evidence")

    if realized_pl_available:
        evidence_present.append("realized_pl_available")
    else:
        evidence_missing.append("realized_pl_available")
        blocked_reasons.append("realized_pl_not_available_in_read_only_evidence")

    if unrealized_pl_available:
        evidence_present.append("unrealized_pl_available")
    else:
        evidence_missing.append("unrealized_pl_available")
        blocked_reasons.append("unrealized_pl_not_available_in_read_only_evidence")

    if margin_risk_available:
        evidence_present.append("margin_risk_available")
    else:
        evidence_missing.append("margin_risk_available")
        blocked_reasons.append("margin_risk_not_available_in_read_only_evidence")

    if trading_history_available:
        evidence_present.append("trading_history_available")
    elif trading_history_block_reason:
        evidence_present.append("trading_history_unavailable_with_explicit_block_reason")
    else:
        evidence_missing.append("trading_history_available_or_block_reason")
        blocked_reasons.append("real_trading_history_unavailable_or_blocked")

    if trading_history_writeback_verified:
        evidence_present.append("trading_history_writeback_verified")
    else:
        blocked_reasons.append("real_trading_history_writeback_not_verified")

    if broker_write_calls_allowed:
        blocked_reasons.append("broker_write_calls_allowed_must_remain_false")
    else:
        evidence_present.append("broker_write_calls_blocked")
    if order_placement_allowed:
        blocked_reasons.append("order_placement_allowed_must_remain_false")
    else:
        evidence_present.append("order_placement_blocked")
    if close_trade_allowed:
        blocked_reasons.append("close_trade_allowed_must_remain_false")
    else:
        evidence_present.append("close_trade_blocked")

    secret_safe = payload_has_no_forbidden_identifiers(model)
    if secret_safe:
        evidence_present.append("no_secret_or_private_identifier_values")
    else:
        blocked_reasons.append("secret_or_private_identifier_marker_present")

    blockers_without_history_writeback = [
        reason
        for reason in blocked_reasons
        if reason != "real_trading_history_writeback_not_verified"
    ]
    approved = not blockers_without_history_writeback

    result = {
        "schema": SCHEMA,
        "READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW": approved,
        "live_execution_allowed": False,
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
        "source_type": source_type,
        "source_label": source_label,
        "freshness_utc": freshness_utc or "MISSING",
        "stale_status": stale_status,
        "broker_account_reachable": broker_account_reachable,
        "open_positions_reconciled": open_positions_reconciled,
        "open_position_count": open_position_count if open_position_count is not None else 0,
        "daily_pl_available": daily_pl_available,
        "realized_pl_available": realized_pl_available,
        "unrealized_pl_available": unrealized_pl_available,
        "margin_risk_available": margin_risk_available,
        "trading_history_available": trading_history_available,
        "trading_history_writeback_verified": trading_history_writeback_verified,
        "block_reason": "NONE" if approved else unique(blocked_reasons)[0],
        "blocked_reasons": unique(blocked_reasons),
        "evidence_present": unique(evidence_present),
        "evidence_missing": unique(evidence_missing),
        "blockers_removed_when_satisfied": blockers_removed_when_satisfied(approved),
        "next_safe_action": next_safe_action(approved),
        "sanitized_evidence_path": str(APPROVAL_EVIDENCE_PATH),
        "no_secret_status": "PASS_NO_SECRET_VALUES_RECORDED" if secret_safe else "BLOCKED",
        "no_account_id_status": "PASS_NO_ACCOUNT_IDENTIFIER_VALUES_RECORDED"
        if secret_safe
        else "BLOCKED",
        "no_order_id_status": "PASS_NO_ORDER_IDENTIFIER_VALUES_RECORDED"
        if secret_safe
        else "BLOCKED",
        "no_transaction_id_status": "PASS_NO_TRANSACTION_IDENTIFIER_VALUES_RECORDED"
        if secret_safe
        else "BLOCKED",
        "generated_at_utc": generated_at_utc or utc_now_iso(),
    }
    assert_approval_sanitized(result)
    return result


def blockers_removed_when_satisfied(approved: bool) -> list[str]:
    if not approved:
        return []
    return [
        "read_only_data_not_approved_for_future_live_execution",
        "broker_account_not_reachable_in_read_only_evidence",
        "open_positions_not_reconciled_in_read_only_evidence",
        "daily_pl_not_available_in_read_only_evidence",
        "open_live_position_state_not_reconciled",
    ]


def build_sanitized_report(result: Mapping[str, Any]) -> str:
    assert_approval_sanitized(result)
    present = "\n".join(f"- {item}" for item in result.get("evidence_present", [])) or "- none"
    missing = "\n".join(f"- {item}" for item in result.get("evidence_missing", [])) or "- none"
    removed = (
        "\n".join(f"- {item}" for item in result.get("blockers_removed_when_satisfied", []))
        or "- none"
    )
    remaining = "\n".join(f"- {item}" for item in result.get("blocked_reasons", [])) or "- none"

    return (
        "# AIOS Forex Read-Only Evidence Approval And Reconciliation Dry Run V1\n\n"
        "## Approval Status\n"
        f"- READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW: "
        f"{result.get('READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW')}\n"
        f"- live_execution_allowed: {result.get('live_execution_allowed')}\n"
        f"- source_type: {result.get('source_type')}\n"
        f"- source_label: {result.get('source_label')}\n"
        f"- stale_status: {result.get('stale_status')}\n"
        f"- freshness_utc: {result.get('freshness_utc')}\n\n"
        "## Reconciliation Status\n"
        f"- broker_account_reachable: {result.get('broker_account_reachable')}\n"
        f"- open_positions_reconciled: {result.get('open_positions_reconciled')}\n"
        f"- open_position_count: {result.get('open_position_count')}\n"
        f"- daily_pl_available: {result.get('daily_pl_available')}\n"
        f"- realized_pl_available: {result.get('realized_pl_available')}\n"
        f"- unrealized_pl_available: {result.get('unrealized_pl_available')}\n"
        f"- margin_risk_available: {result.get('margin_risk_available')}\n"
        f"- trading_history_available: {result.get('trading_history_available')}\n"
        f"- trading_history_writeback_verified: "
        f"{result.get('trading_history_writeback_verified')}\n\n"
        "## Evidence Present\n"
        f"{present}\n\n"
        "## Evidence Missing\n"
        f"{missing}\n\n"
        "## Blockers Removed When Satisfied\n"
        f"{removed}\n\n"
        "## Blockers Remaining\n"
        f"{remaining}\n\n"
        "## Next Safe Action\n"
        f"{result.get('next_safe_action')}\n\n"
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


def write_read_only_evidence_approval_report(
    result: Mapping[str, Any], *, repo_root: Path | None = None
) -> Path:
    root = repo_root or Path(__file__).resolve().parents[2]
    report_path = root / APPROVAL_EVIDENCE_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_sanitized_report(result), encoding="utf-8")
    return report_path


def cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    assert_approval_sanitized(result)
    return {
        "schema": result.get("schema"),
        "READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW": result.get(
            "READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW"
        ),
        "live_execution_allowed": result.get("live_execution_allowed"),
        "source_type": result.get("source_type"),
        "source_label": result.get("source_label"),
        "freshness_utc": result.get("freshness_utc"),
        "stale_status": result.get("stale_status"),
        "broker_account_reachable": result.get("broker_account_reachable"),
        "open_positions_reconciled": result.get("open_positions_reconciled"),
        "open_position_count": result.get("open_position_count"),
        "daily_pl_available": result.get("daily_pl_available"),
        "trading_history_writeback_verified": result.get(
            "trading_history_writeback_verified"
        ),
        "blocked_reasons": result.get("blocked_reasons", []),
        "blockers_removed_when_satisfied": result.get(
            "blockers_removed_when_satisfied", []
        ),
        "next_safe_action": result.get("next_safe_action"),
        "sanitized_evidence_path": result.get("sanitized_evidence_path"),
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


def assert_approval_sanitized(payload: Mapping[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    for marker in forbidden_markers():
        if marker in serialized:
            raise ValueError(f"Unsafe secret or identifier marker present: {marker}")
    for field in (
        "live_execution_allowed",
        "broker_write_calls_allowed",
        "order_placement_allowed",
        "close_trade_allowed",
    ):
        if payload.get(field) is not False:
            raise ValueError(f"{field} must remain false")


def payload_has_no_forbidden_identifiers(payload: Mapping[str, Any]) -> bool:
    serialized = json.dumps(payload, sort_keys=True)
    return all(marker not in serialized for marker in forbidden_markers())


def forbidden_markers() -> tuple[str, ...]:
    return (
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
        "Authorization",
        "Bearer ",
        "accountID",
        "account_id_value",
        "orderID",
        "order_id_value",
        "transactionID",
        "transaction_id_value",
        "rawBroker",
    )


def next_safe_action(approved: bool) -> str:
    if approved:
        return (
            "Use approved sanitized read-only evidence to reduce satisfied review "
            "blockers only; keep live execution blocked pending auto-exit and "
            "trading-history verification gates."
        )
    return (
        "Run the read-only live data bridge with permitted broker read-only "
        "inputs, then rerun this approval evaluator. Do not execute trades."
    )


def first_present_nested(
    model: Mapping[str, Any], *paths: str, default: Any = None
) -> Any:
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
        return value.strip().lower() in {"true", "1", "yes", "valid", "available"}
    return bool(value)


def coerce_int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def is_available_value(value: Any) -> bool:
    if value is None:
        return False
    return str(value).strip().upper() not in {"", "MISSING", "UNAVAILABLE", "NONE", "NULL"}


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
