"""Governed intake for sanitized, closed OANDA practice trade receipts.

The intake is local and append-only. It never calls OANDA, reads credentials,
places orders, moves money, or grants live/autonomous trading authority.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "aios.forex.oanda_practice_closed_trade_receipt.v1"
RESULT_SCHEMA = "aios.forex.oanda_practice_receipt_intake_result.v1"
LEDGER_SCHEMA = "aios.forex.demo_proof_ledger.v1"
LEDGER_RELATIVE_PATH = Path("telemetry/forex/demo_proof_ledger.jsonl")
LOCK_RELATIVE_PATH = Path("telemetry/forex/.oanda_practice_receipt_intake.lock")
SOURCE = "oanda_practice_closed_trade_receipt_intake_v1"

BLOCKED_RECEIPT_MISSING = "BLOCKED_RECEIPT_MISSING"
BLOCKED_RECEIPT_INVALID = "BLOCKED_RECEIPT_INVALID"
BLOCKED_RECEIPT_UNSAFE = "BLOCKED_RECEIPT_UNSAFE"
BLOCKED_NOT_CLOSED = "BLOCKED_NOT_CLOSED"
BLOCKED_CONFIRMATION = "BLOCKED_CONFIRMATION"
BLOCKED_DUPLICATE_RECEIPT = "BLOCKED_DUPLICATE_RECEIPT"
BLOCKED_LEDGER_INVALID = "BLOCKED_LEDGER_INVALID"
BLOCKED_LEDGER_LOCKED = "BLOCKED_LEDGER_LOCKED"
READY_TO_APPEND = "READY_TO_APPEND"
APPENDED = "APPENDED"

REQUIRED_CONFIRMATIONS = (
    "owner_confirmed_receipt_reviewed",
    "owner_confirmed_demo_practice_only",
    "owner_confirmed_closed_trade_only",
    "owner_confirmed_no_credentials_or_account_id",
    "owner_confirmed_no_raw_broker_payload",
    "owner_confirmed_no_order_created_by_intake",
    "owner_confirmed_append_only",
)

SENSITIVE_KEY_TERMS = (
    "account_id",
    "accountid",
    "access_token",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
    "api_key",
    "apikey",
)

FORBIDDEN_KEY_TERMS = (
    "raw_payload",
    "raw_broker",
    "request_headers",
    "response_headers",
    "http_headers",
)

SAFE_REFERENCE_RE = re.compile(r"^[A-Za-z0-9._:-]{1,96}$")
INSTRUMENT_RE = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")
WINDOW_RE = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")
TEXT_RE = re.compile(r"^[A-Za-z0-9 _./:-]{1,96}$")

ALLOWED_SIDES = {"BUY", "SELL"}
ALLOWED_CLOSE_REASONS = {
    "STOP_LOSS",
    "TAKE_PROFIT",
    "TRAILING_STOP",
    "MANUAL",
    "TIME_EXIT",
    "BROKER_CLOSE",
    "OTHER",
}
ALLOWED_MARKET_SESSIONS = {
    "ASIA",
    "LONDON",
    "NEW_YORK",
    "LONDON_NEW_YORK_OVERLAP",
    "OTHER",
}

BALANCE_TOLERANCE_USD = 0.02
MAX_ABSOLUTE_PNL_USD = 1_000_000.0
MAX_UNITS = 100_000_000


def evaluate_receipt(
    receipt: Mapping[str, Any] | None,
    *,
    ledger_entries: Sequence[Mapping[str, Any]] | None = None,
    confirmations: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate one sanitized closed-trade receipt without writing files."""

    payload = dict(receipt or {})
    entries = [dict(item) for item in (ledger_entries or []) if isinstance(item, Mapping)]
    confirmation_map = dict(confirmations or {})

    if not payload:
        return _result(
            status=BLOCKED_RECEIPT_MISSING,
            blockers=["receipt_missing_or_empty"],
            receipt=payload,
            confirmations=confirmation_map,
            ledger_entry=None,
        )

    unsafe_blockers = _unsafe_blockers(payload)
    if unsafe_blockers:
        return _result(
            status=BLOCKED_RECEIPT_UNSAFE,
            blockers=unsafe_blockers,
            receipt=payload,
            confirmations=confirmation_map,
            ledger_entry=None,
        )

    receipt_blockers = _receipt_blockers(payload)
    if payload.get("trade_status") != "CLOSED":
        status = BLOCKED_NOT_CLOSED
    elif receipt_blockers:
        status = BLOCKED_RECEIPT_INVALID
    else:
        status = READY_TO_APPEND

    confirmation_blockers = _confirmation_blockers(confirmation_map)
    if not receipt_blockers and status == READY_TO_APPEND and confirmation_blockers:
        status = BLOCKED_CONFIRMATION

    fingerprint = _fingerprint(payload)
    duplicate_blockers = _duplicate_blockers(payload, fingerprint, entries)
    if status == READY_TO_APPEND and duplicate_blockers:
        status = BLOCKED_DUPLICATE_RECEIPT

    blockers = receipt_blockers + confirmation_blockers + duplicate_blockers
    ledger_entry = None
    if status == READY_TO_APPEND:
        ledger_entry = _build_ledger_entry(payload, fingerprint, entries)

    return _result(
        status=status,
        blockers=_unique(blockers),
        receipt=payload,
        confirmations=confirmation_map,
        ledger_entry=ledger_entry,
    )


def intake_receipt(
    repo_root: str | Path,
    receipt: Mapping[str, Any] | None,
    *,
    confirmations: Mapping[str, Any] | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    """Evaluate and optionally append one receipt to the governed ledger."""

    root = Path(repo_root).resolve()
    ledger_path = _safe_path(root, LEDGER_RELATIVE_PATH)
    lock_path = _safe_path(root, LOCK_RELATIVE_PATH)

    try:
        entries = _read_jsonl(ledger_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _result(
            status=BLOCKED_LEDGER_INVALID,
            blockers=[f"ledger_invalid:{type(exc).__name__}"],
            receipt=dict(receipt or {}),
            confirmations=dict(confirmations or {}),
            ledger_entry=None,
            apply=apply,
        )

    evaluation = evaluate_receipt(
        receipt,
        ledger_entries=entries,
        confirmations=confirmations,
    )
    evaluation["apply_requested"] = bool(apply)
    evaluation["ledger_path"] = str(LEDGER_RELATIVE_PATH).replace("\\", "/")

    if not apply or evaluation["status"] != READY_TO_APPEND:
        evaluation["appended"] = False
        return evaluation

    lock_fd: int | None = None
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return _result(
                status=BLOCKED_LEDGER_LOCKED,
                blockers=["receipt_intake_lock_exists"],
                receipt=dict(receipt or {}),
                confirmations=dict(confirmations or {}),
                ledger_entry=None,
                apply=True,
                ledger_path=str(LEDGER_RELATIVE_PATH).replace("\\", "/"),
            )

        os.write(lock_fd, f"pid={os.getpid()}\n".encode("utf-8"))
        os.close(lock_fd)
        lock_fd = None

        latest_entries = _read_jsonl(ledger_path)
        final_evaluation = evaluate_receipt(
            receipt,
            ledger_entries=latest_entries,
            confirmations=confirmations,
        )
        if final_evaluation["status"] != READY_TO_APPEND:
            final_evaluation["apply_requested"] = True
            final_evaluation["appended"] = False
            final_evaluation["ledger_path"] = str(LEDGER_RELATIVE_PATH).replace("\\", "/")
            return final_evaluation

        ledger_entry = dict(final_evaluation["ledger_entry"])
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(ledger_entry, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

        final_evaluation["status"] = APPENDED
        final_evaluation["passed"] = True
        final_evaluation["apply_requested"] = True
        final_evaluation["appended"] = True
        final_evaluation["ledger_path"] = str(LEDGER_RELATIVE_PATH).replace("\\", "/")
        final_evaluation["next_safe_action"] = (
            "Run the read-only extended evidence verdict. Do not place another order from this intake."
        )
        return final_evaluation
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _receipt_blockers(receipt: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []

    if receipt.get("schema") != SCHEMA:
        blockers.append("schema_invalid")
    if receipt.get("broker") != "OANDA":
        blockers.append("broker_must_be_OANDA")
    if receipt.get("environment") != "PRACTICE":
        blockers.append("environment_must_be_PRACTICE")
    if receipt.get("trade_status") != "CLOSED":
        blockers.append("trade_status_must_be_CLOSED")

    reference = _text(receipt.get("broker_trade_reference"))
    if not reference or not SAFE_REFERENCE_RE.fullmatch(reference):
        blockers.append("broker_trade_reference_invalid_or_missing")

    instrument = _text(receipt.get("instrument"))
    if not instrument or not INSTRUMENT_RE.fullmatch(instrument):
        blockers.append("instrument_invalid_or_missing")

    side = receipt.get("side")
    if side not in ALLOWED_SIDES:
        blockers.append("side_must_be_BUY_or_SELL")

    units = _integer(receipt.get("units"))
    if units is None or units <= 0 or units > MAX_UNITS:
        blockers.append("units_invalid")

    entry_time = _parse_utc(receipt.get("entry_time_utc"))
    exit_time = _parse_utc(receipt.get("exit_time_utc"))
    if entry_time is None:
        blockers.append("entry_time_utc_invalid_or_missing")
    if exit_time is None:
        blockers.append("exit_time_utc_invalid_or_missing")
    if entry_time is not None and exit_time is not None and exit_time <= entry_time:
        blockers.append("exit_time_must_be_after_entry_time")

    entry_price = _positive_number(receipt.get("entry_price"))
    exit_price = _positive_number(receipt.get("exit_price"))
    if entry_price is None:
        blockers.append("entry_price_invalid")
    if exit_price is None:
        blockers.append("exit_price_invalid")

    net_pnl = _finite_number(receipt.get("net_realized_pnl_usd"))
    if net_pnl is None or abs(net_pnl) > MAX_ABSOLUTE_PNL_USD:
        blockers.append("net_realized_pnl_usd_invalid")

    pre_balance = _positive_number(receipt.get("pre_balance_usd"))
    post_balance = _positive_number(receipt.get("post_balance_usd"))
    if pre_balance is None:
        blockers.append("pre_balance_usd_invalid")
    if post_balance is None:
        blockers.append("post_balance_usd_invalid")

    balance_adjustment = _finite_number(receipt.get("balance_adjustment_usd"))
    if balance_adjustment is None or abs(balance_adjustment) > BALANCE_TOLERANCE_USD:
        blockers.append("balance_adjustment_usd_must_be_zero")

    if pre_balance is not None and post_balance is not None and net_pnl is not None:
        expected = pre_balance + net_pnl + (balance_adjustment or 0.0)
        if not math.isclose(post_balance, expected, abs_tol=BALANCE_TOLERANCE_USD):
            blockers.append("post_balance_does_not_reconcile_to_net_pnl")

    close_reason = receipt.get("close_reason")
    if close_reason not in ALLOWED_CLOSE_REASONS:
        blockers.append("close_reason_invalid")
    if close_reason == "OTHER" and not _safe_text(receipt.get("close_reason_note")):
        blockers.append("close_reason_note_required_for_OTHER")

    market_session = receipt.get("market_session")
    if market_session not in ALLOWED_MARKET_SESSIONS:
        blockers.append("market_session_invalid")

    for field in ("strategy_name", "timeframe"):
        if not _safe_text(receipt.get(field)):
            blockers.append(f"{field}_invalid_or_missing")

    window_id = _text(receipt.get("walk_forward_window_id"))
    if not window_id or not WINDOW_RE.fullmatch(window_id):
        blockers.append("walk_forward_window_id_invalid_or_missing")

    spread_pips = _non_negative_number(receipt.get("spread_pips"))
    slippage_pips = _non_negative_number(receipt.get("absolute_slippage_pips"))
    if spread_pips is None:
        blockers.append("spread_pips_invalid")
    if slippage_pips is None:
        blockers.append("absolute_slippage_pips_invalid")

    trade_drawdown = _bounded_percentage(receipt.get("trade_drawdown_pct"))
    if trade_drawdown is None:
        blockers.append("trade_drawdown_pct_invalid")

    for bool_field in (
        "broker_reported_closed_trade",
        "stop_loss_attached",
        "take_profit_attached",
        "raw_broker_payload_included",
        "credential_data_included",
        "account_identifier_included",
        "live_money_used",
        "order_created_by_intake",
    ):
        if not isinstance(receipt.get(bool_field), bool):
            blockers.append(f"{bool_field}_must_be_boolean")

    if receipt.get("broker_reported_closed_trade") is not True:
        blockers.append("broker_reported_closed_trade_must_be_true")
    if receipt.get("raw_broker_payload_included") is not False:
        blockers.append("raw_broker_payload_included_must_be_false")
    if receipt.get("credential_data_included") is not False:
        blockers.append("credential_data_included_must_be_false")
    if receipt.get("account_identifier_included") is not False:
        blockers.append("account_identifier_included_must_be_false")
    if receipt.get("live_money_used") is not False:
        blockers.append("live_money_used_must_be_false")
    if receipt.get("order_created_by_intake") is not False:
        blockers.append("order_created_by_intake_must_be_false")

    if receipt.get("stop_loss_attached") is True and _positive_number(receipt.get("stop_loss_price")) is None:
        blockers.append("stop_loss_price_required_when_attached")
    if receipt.get("take_profit_attached") is True and _positive_number(receipt.get("take_profit_price")) is None:
        blockers.append("take_profit_price_required_when_attached")

    return blockers


def _unsafe_blockers(receipt: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any, path: str = "receipt") -> None:
        if isinstance(node, Mapping):
            for raw_key, child in node.items():
                key = str(raw_key).lower()
                child_path = f"{path}.{raw_key}"
                if any(term in key for term in SENSITIVE_KEY_TERMS):
                    if key not in {"credential_data_included", "account_identifier_included"}:
                        blockers.append(f"sensitive_key_detected:{child_path}")
                if any(term in key for term in FORBIDDEN_KEY_TERMS):
                    blockers.append(f"forbidden_raw_payload_key:{child_path}")
                visit(child, child_path)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                visit(child, f"{path}[{index}]")
        elif isinstance(node, str) and node.strip().lower().startswith("bearer "):
            blockers.append(f"authorization_value_detected:{path}")

    visit(receipt)
    return _unique(blockers)


def _confirmation_blockers(confirmations: Mapping[str, Any]) -> list[str]:
    return [
        f"{field}_required"
        for field in REQUIRED_CONFIRMATIONS
        if confirmations.get(field) is not True
    ]


def _duplicate_blockers(
    receipt: Mapping[str, Any],
    fingerprint: str,
    entries: Sequence[Mapping[str, Any]],
) -> list[str]:
    reference = _text(receipt.get("broker_trade_reference"))
    blockers: list[str] = []
    for entry in entries:
        if entry.get("evidence_fingerprint") == fingerprint:
            blockers.append("duplicate_receipt_fingerprint")
        rows = entry.get("trade_rows")
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, Mapping) and row.get("broker_trade_reference") == reference:
                    blockers.append("duplicate_broker_trade_reference")
    return _unique(blockers)


def _build_ledger_entry(
    receipt: Mapping[str, Any],
    fingerprint: str,
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    exit_time = _parse_utc(receipt.get("exit_time_utc"))
    assert exit_time is not None
    pnl = float(receipt["net_realized_pnl_usd"])
    pre_balance = float(receipt["pre_balance_usd"])
    post_balance = float(receipt["post_balance_usd"])
    window_id = str(receipt["walk_forward_window_id"])

    prior_market_entries = [
        entry
        for entry in entries
        if entry.get("record_type") == "REAL_DEMO_DAY"
        and entry.get("session_source") == SOURCE
    ]

    prior_windows: set[str] = set()
    prior_max_drawdown = 0.0
    observed_balances: list[float] = [pre_balance]
    for entry in prior_market_entries:
        window = entry.get("walk_forward_window_id")
        if isinstance(window, str) and window:
            prior_windows.add(window)
        value = _finite_number(entry.get("max_drawdown_pct"))
        if value is not None:
            prior_max_drawdown = max(prior_max_drawdown, value)
        rows = entry.get("trade_rows")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, Mapping):
                    continue
                for field in ("pre_balance_usd", "post_balance_usd"):
                    balance = _positive_number(row.get(field))
                    if balance is not None:
                        observed_balances.append(balance)

    prior_windows.add(window_id)
    observed_balances.append(post_balance)
    peak_balance = max(observed_balances)
    current_drawdown = max(0.0, ((peak_balance - post_balance) / peak_balance) * 100.0)
    max_drawdown = round(
        max(prior_max_drawdown, current_drawdown, float(receipt["trade_drawdown_pct"])),
        8,
    )

    win = pnl > 0
    loss = pnl < 0
    trade_row = {
        "schema": SCHEMA,
        "broker": "OANDA",
        "environment": "PRACTICE",
        "broker_trade_reference": receipt["broker_trade_reference"],
        "instrument": receipt["instrument"],
        "pair": receipt["instrument"],
        "side": receipt["side"],
        "units": int(receipt["units"]),
        "entry_time": receipt["entry_time_utc"],
        "exit_time": receipt["exit_time_utc"],
        "entry_price": float(receipt["entry_price"]),
        "exit_price": float(receipt["exit_price"]),
        "realized_pnl_usd": pnl,
        "pre_balance_usd": pre_balance,
        "post_balance_usd": post_balance,
        "balance_adjustment_usd": float(receipt["balance_adjustment_usd"]),
        "spread_pips": float(receipt["spread_pips"]),
        "absolute_slippage_pips": float(receipt["absolute_slippage_pips"]),
        "trade_drawdown_pct": float(receipt["trade_drawdown_pct"]),
        "stop_loss_attached": receipt["stop_loss_attached"],
        "stop_loss_price": receipt.get("stop_loss_price"),
        "take_profit_attached": receipt["take_profit_attached"],
        "take_profit_price": receipt.get("take_profit_price"),
        "close_reason": receipt["close_reason"],
        "close_reason_note": receipt.get("close_reason_note"),
        "strategy": receipt["strategy_name"],
        "timeframe": receipt["timeframe"],
        "market_session": receipt["market_session"],
        "walk_forward_window_id": window_id,
        "evidence_status": "OANDA_PRACTICE_CLOSED_TRADE_RECEIPT_ACCEPTED",
        "broker_reported_closed_trade": True,
        "raw_broker_payload_recorded": False,
        "private_identifiers_recorded": False,
        "secret_values_recorded": False,
    }

    return {
        "schema": LEDGER_SCHEMA,
        "record_type": "REAL_DEMO_DAY",
        "date": exit_time.date().isoformat(),
        "recorded_at_utc": _utc_now(),
        "session_mode": "OANDA_PRACTICE",
        "session_source": SOURCE,
        "source_label": "OWNER_REVIEWED_SANITIZED_OANDA_PRACTICE_RECEIPT",
        "evidence_source": "broker_sanitized_closed_trade_receipt",
        "broker": "OANDA_PRACTICE",
        "environment": "PRACTICE",
        "strategy_name": receipt["strategy_name"],
        "walk_forward_window_id": window_id,
        "windows_toward_verdict": len(prior_windows),
        "fills": 1,
        "wins": 1 if win else 0,
        "losses": 1 if loss else 0,
        "win_rate_pct": 100.0 if win else 0.0,
        "realized_pnl_usd": pnl,
        "max_drawdown_pct": max_drawdown,
        "evidence_fingerprint": fingerprint,
        "trade_rows": [trade_row],
        "live_trading_allowed": False,
        "live_order_execution_allowed": False,
        "live_capital_action_authorized": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "order_placement_allowed": False,
        "credential_access_allowed": False,
        "automatic_evidence_append_allowed": False,
        "owner_reviewed_receipt": True,
    }


def _result(
    *,
    status: str,
    blockers: list[str],
    receipt: Mapping[str, Any],
    confirmations: Mapping[str, Any],
    ledger_entry: Mapping[str, Any] | None,
    apply: bool = False,
    ledger_path: str | None = None,
) -> dict[str, Any]:
    fingerprint = _fingerprint(receipt) if receipt else None
    return {
        "schema": RESULT_SCHEMA,
        "status": status,
        "passed": status in {READY_TO_APPEND, APPENDED},
        "blockers": list(blockers),
        "apply_requested": bool(apply),
        "appended": status == APPENDED,
        "receipt_fingerprint": fingerprint,
        "receipt_summary": {
            "schema": receipt.get("schema"),
            "broker": receipt.get("broker"),
            "environment": receipt.get("environment"),
            "trade_status": receipt.get("trade_status"),
            "broker_trade_reference": receipt.get("broker_trade_reference"),
            "instrument": receipt.get("instrument"),
            "side": receipt.get("side"),
            "net_realized_pnl_usd": receipt.get("net_realized_pnl_usd"),
            "exit_time_utc": receipt.get("exit_time_utc"),
            "walk_forward_window_id": receipt.get("walk_forward_window_id"),
        },
        "confirmation_summary": {
            field: confirmations.get(field) is True for field in REQUIRED_CONFIRMATIONS
        },
        "ledger_entry": dict(ledger_entry) if ledger_entry is not None else None,
        "ledger_path": ledger_path,
        "safety": {
            "read_only_evaluation": True,
            "broker_call_performed": False,
            "credential_access_performed": False,
            "order_created": False,
            "order_modified": False,
            "order_closed": False,
            "money_movement_performed": False,
            "live_trading_allowed": False,
            "autonomous_order_execution_allowed": False,
        },
        "next_safe_action": _next_safe_action(status),
    }


def _next_safe_action(status: str) -> str:
    if status == READY_TO_APPEND:
        return "Owner may rerun with explicit apply after reviewing the normalized ledger entry."
    if status == APPENDED:
        return "Run the read-only extended evidence verdict; do not place another order from this intake."
    if status == BLOCKED_DUPLICATE_RECEIPT:
        return "Do not append or resubmit this broker trade receipt."
    if status == BLOCKED_LEDGER_LOCKED:
        return "Stop. Resolve the existing intake process or stale lock before retrying."
    return "Correct the listed receipt or confirmation blockers; do not fabricate missing evidence."


def _safe_path(root: Path, relative: Path) -> Path:
    path = (root / relative).resolve()
    allowed = (root / "telemetry" / "forex").resolve()
    if path != allowed and allowed not in path.parents:
        raise RuntimeError("path_outside_telemetry_forex")
    return path


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError(f"line_{line_number}_not_object")
            entries.append(parsed)
    return entries


def _fingerprint(receipt: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(receipt),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_utc(value: Any) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    parsed_utc = parsed.astimezone(timezone.utc)
    if parsed_utc.utcoffset() != timezone.utc.utcoffset(parsed_utc):
        return None
    return parsed_utc


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _safe_text(value: Any) -> str:
    text = _text(value)
    return text if text and TEXT_RE.fullmatch(text) else ""


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _positive_number(value: Any) -> float | None:
    number = _finite_number(value)
    return number if number is not None and number > 0 else None


def _non_negative_number(value: Any) -> float | None:
    number = _finite_number(value)
    return number if number is not None and number >= 0 else None


def _bounded_percentage(value: Any) -> float | None:
    number = _finite_number(value)
    return number if number is not None and 0 <= number <= 100 else None


def _integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if isinstance(value, float) and not value.is_integer():
        return None
    return number


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(values))
