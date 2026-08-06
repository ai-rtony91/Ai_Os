"""Deterministic, local-only intake for supervised Profit Track P1 evidence."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from automation.forex_engine.forex_profit_track_p1_strategy_evidence_v1 import (
    evaluate_strategy_evidence,
)

VERSION = "forex_p1_supervised_paper_evidence_pipeline_v1"
REQUIRED_FIELDS = (
    "trade_id", "evidence_type", "strategy_id", "instrument", "direction",
    "entry_timestamp_utc", "exit_timestamp_utc", "entry_price", "exit_price",
    "stop_price", "target_price", "quantity_or_units", "realized_pl", "fees",
    "risk_amount", "exit_reason", "entry_rationale", "evidence_source",
    "reviewed_by", "review_timestamp_utc",
)
NUMERIC_FIELDS = (
    "entry_price", "exit_price", "stop_price", "target_price",
    "quantity_or_units", "realized_pl", "fees", "risk_amount",
)
ALLOWED_EVIDENCE_TYPES = {"paper", "supervised_demo"}
PRIVATE_KEY_PARTS = (
    "account_id", "account_number", "api_key", "authorization", "credential",
    "order_id", "password", "private_id", "secret", "token",
)
RAW_KEYS = {"broker_payload", "raw_broker_payload", "raw_payload", "broker_raw"}
SECRET_VALUE = re.compile(
    r"(?i)(?:bearer\s+[a-z0-9._-]+|api[_ -]?key\s*[:=]|password\s*[:=]|secret\s*[:=])"
)
SAFETY_FLAGS = {
    "broker_call_performed": False,
    "broker_write_performed": False,
    "credentials_loaded": False,
    "account_access_performed": False,
    "order_submission_allowed": False,
    "order_modification_allowed": False,
    "order_close_allowed": False,
    "live_execution_allowed": False,
    "money_movement_allowed": False,
    "scheduler_created": False,
    "daemon_created": False,
    "webhook_created": False,
}


def _utc_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _unsafe_content(value: Any) -> tuple[bool, bool]:
    private = raw = False
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            raw = raw or normalized in RAW_KEYS
            private = private or any(part in normalized for part in PRIVATE_KEY_PARTS)
            child_private, child_raw = _unsafe_content(child)
            private, raw = private or child_private, raw or child_raw
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            child_private, child_raw = _unsafe_content(child)
            private, raw = private or child_private, raw or child_raw
    elif isinstance(value, str):
        private = bool(SECRET_VALUE.search(value))
    return private, raw


def _validate(raw: Any, index: int, known_ids: set[str]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(raw, Mapping):
        return None, {"record_index": index, "trade_id": None, "reasons": ["malformed_record"]}
    reasons: list[str] = []
    private, raw_payload = _unsafe_content(raw)
    if raw_payload:
        reasons.append("raw_broker_payload_rejected")
    if private:
        reasons.append("secret_or_private_identifier_rejected")
    missing = [field for field in REQUIRED_FIELDS if field not in raw or raw[field] in (None, "")]
    reasons.extend(f"missing_{field}" for field in missing)
    trade_id = str(raw.get("trade_id", "")).strip()
    if trade_id and trade_id in known_ids:
        reasons.append("duplicate_trade_id")
    evidence_type = str(raw.get("evidence_type", "")).strip().lower()
    if evidence_type and evidence_type not in ALLOWED_EVIDENCE_TYPES:
        reasons.append("unsupported_evidence_type")
    normalized = dict(raw)
    for field in NUMERIC_FIELDS:
        if field not in missing:
            number = _finite(raw.get(field))
            if number is None:
                reasons.append(f"non_finite_or_invalid_{field}")
            else:
                normalized[field] = number
    timestamps = {
        field: _utc_timestamp(raw.get(field))
        for field in ("entry_timestamp_utc", "exit_timestamp_utc", "review_timestamp_utc")
    }
    for field, parsed in timestamps.items():
        if field not in missing and parsed is None:
            reasons.append(f"invalid_{field}")
    if timestamps["entry_timestamp_utc"] and timestamps["exit_timestamp_utc"]:
        if timestamps["exit_timestamp_utc"] <= timestamps["entry_timestamp_utc"]:
            reasons.append("invalid_timestamp_order")
    if timestamps["exit_timestamp_utc"] and timestamps["review_timestamp_utc"]:
        if timestamps["review_timestamp_utc"] < timestamps["exit_timestamp_utc"]:
            reasons.append("review_precedes_exit")
    if reasons:
        return None, {"record_index": index, "trade_id": trade_id or None, "reasons": reasons}
    normalized["trade_id"] = trade_id
    normalized["evidence_type"] = evidence_type
    return {field: normalized[field] for field in REQUIRED_FIELDS}, None


def _evaluator_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "trade_id": record["trade_id"],
            "entry": record["entry_price"],
            "exit": record["exit_price"],
            "realized_pl": record["realized_pl"],
            "timestamp": record["exit_timestamp_utc"],
            "evidence_type": record["evidence_type"],
        }
        for record in records
    ]


def _as_of(records: Sequence[Mapping[str, Any]]) -> datetime:
    timestamps = [_utc_timestamp(record["review_timestamp_utc"]) for record in records]
    return max((item for item in timestamps if item), default=datetime(1970, 1, 1, tzinfo=timezone.utc))


def _read_records(input_path: Path) -> tuple[list[Any], list[dict[str, Any]]]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload, []
    if isinstance(payload, Mapping) and isinstance(payload.get("records"), list):
        return list(payload["records"]), []
    return [], [{"record_index": None, "trade_id": None, "reasons": ["malformed_record_container"]}]


def _load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": VERSION, "records": [], **SAFETY_FLAGS}
    ledger = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(ledger, Mapping) or not isinstance(ledger.get("records"), list):
        raise ValueError("invalid_existing_ledger")
    if any(ledger.get(key) is not False for key in SAFETY_FLAGS):
        raise ValueError("existing_ledger_claims_execution_authority")
    return dict(ledger)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def run_pipeline(input_path: Path, ledger_path: Path, state_path: Path, report_path: Path) -> dict[str, Any]:
    """Run exactly one bounded evidence collection and evaluation cycle."""
    incoming, container_rejections = _read_records(input_path)
    ledger = _load_ledger(ledger_path)
    prior_records = list(ledger["records"])
    known_ids = {str(record["trade_id"]) for record in prior_records}
    before = evaluate_strategy_evidence(_evaluator_records(prior_records), as_of=_as_of(prior_records))
    accepted: list[dict[str, Any]] = []
    rejected = list(container_rejections)
    for index, raw in enumerate(incoming):
        record, rejection = _validate(raw, index, known_ids)
        if rejection:
            rejected.append(rejection)
            continue
        assert record is not None
        accepted.append(record)
        known_ids.add(record["trade_id"])
    combined = sorted(prior_records + accepted, key=lambda item: (item["exit_timestamp_utc"], item["trade_id"]))
    after = evaluate_strategy_evidence(_evaluator_records(combined), as_of=_as_of(combined))
    ledger = {"version": VERSION, "records": combined, **SAFETY_FLAGS}
    duplicate_count = sum("duplicate_trade_id" in item["reasons"] for item in rejected)
    counts = dict(sorted(Counter(item["evidence_type"] for item in combined).items()))
    state = {
        "version": VERSION,
        "pipeline_status": "COMPLETE",
        "input_records": len(incoming),
        "accepted_records": len(accepted),
        "rejected_records": len(rejected),
        "duplicate_records": duplicate_count,
        "rejections": rejected,
        "qualifying_trade_count": after["trade_count"],
        "evidence_type_counts": counts,
        "latest_trade_timestamp": after["evidence_date_range"]["end"],
        "evidence_freshness": after["evidence_freshness"],
        "p1_status_before": before["strategy_evidence_status"],
        "p1_status_after": after["strategy_evidence_status"],
        "profitability_proven": after["profitability_proven"],
        "ready_for_p2_review": after["ready_for_p2_review"],
        "next_safe_action": "Owner review of sanitized P1 evidence; no execution is authorized.",
        "p1_evaluator_result": after,
        **SAFETY_FLAGS,
    }
    _write_json(ledger_path, ledger)
    _write_json(state_path, state)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(result_to_markdown(state), encoding="utf-8")
    return state


def result_to_markdown(state: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex P1 Supervised Paper Evidence Pipeline V1", "",
        f"- Pipeline status: {state['pipeline_status']}",
        f"- Accepted records: {state['accepted_records']}",
        f"- Rejected records: {state['rejected_records']}",
        f"- Duplicate records: {state['duplicate_records']}",
        f"- Qualifying trade count: {state['qualifying_trade_count']}",
        f"- Evidence type counts: {json.dumps(state['evidence_type_counts'], sort_keys=True)}",
        f"- P1 status before: {state['p1_status_before']}",
        f"- P1 status after: {state['p1_status_after']}",
        f"- Profitability proven: {str(state['profitability_proven']).lower()}",
        f"- Ready for P2 review: {str(state['ready_for_p2_review']).lower()}",
        f"- Live execution allowed: {str(state['live_execution_allowed']).lower()}",
        "",
        "## Safety flags",
        "",
    ]
    lines.extend(f"- {key}: {str(state[key]).lower()}" for key in SAFETY_FLAGS)
    lines.extend([
        "", state["next_safe_action"],
        "All broker, credential, account, order, money-movement, scheduler, daemon, and webhook permissions remain false.", "",
    ])
    return "\n".join(lines)
