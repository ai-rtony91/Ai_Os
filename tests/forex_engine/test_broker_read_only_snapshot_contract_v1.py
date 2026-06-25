from __future__ import annotations

import json
from dataclasses import replace

import pytest

from automation.forex_engine.broker_read_only_snapshot_contract_v1 import (
    BROKER_SNAPSHOT_BLOCKED_INSTRUMENT_NOT_TRADEABLE,
    BROKER_SNAPSHOT_BLOCKED_MARKET_CLOSED,
    BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT,
    BROKER_SNAPSHOT_BLOCKED_MISSING_BALANCE,
    BROKER_SNAPSHOT_BLOCKED_MISSING_MARGIN,
    BROKER_SNAPSHOT_BLOCKED_SPREAD_MISSING,
    BROKER_SNAPSHOT_BLOCKED_STALE_OR_UNRECONCILED,
    BROKER_SNAPSHOT_BLOCKED_UNKNOWN_EXPOSURE,
    BROKER_SNAPSHOT_BLOCKED_UNSANITIZED,
    BROKER_SNAPSHOT_VALID,
    PLACEHOLDER_ACCOUNT_REFERENCE,
    broker_snapshot_result_to_operator_text,
    broker_snapshot_to_jsonable_dict,
    build_sample_valid_broker_snapshot,
    validate_broker_read_only_snapshot,
)


def test_valid_broker_snapshot_passes() -> None:
    result = validate_broker_read_only_snapshot(build_sample_valid_broker_snapshot())
    assert result.classification == BROKER_SNAPSHOT_VALID
    assert result.valid_for_review is True


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        ({"account_present": False, "account_reference": ""}, BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT),
        ({"balance_present": False}, BROKER_SNAPSHOT_BLOCKED_MISSING_BALANCE),
        ({"margin_available_present": False}, BROKER_SNAPSHOT_BLOCKED_MISSING_MARGIN),
        ({"no_unknown_open_exposure": False}, BROKER_SNAPSHOT_BLOCKED_UNKNOWN_EXPOSURE),
        ({"market_hours_open": False}, BROKER_SNAPSHOT_BLOCKED_MARKET_CLOSED),
        ({"instrument_tradeable": False}, BROKER_SNAPSHOT_BLOCKED_INSTRUMENT_NOT_TRADEABLE),
        ({"spread_present": False}, BROKER_SNAPSHOT_BLOCKED_SPREAD_MISSING),
        ({"read_only_reconciled": False}, BROKER_SNAPSHOT_BLOCKED_STALE_OR_UNRECONCILED),
        ({"sanitized": False}, BROKER_SNAPSHOT_BLOCKED_UNSANITIZED),
    ],
)
def test_broker_snapshot_blockers_classify(updates: dict[str, object], expected: str) -> None:
    result = validate_broker_read_only_snapshot(replace(build_sample_valid_broker_snapshot(), **updates))
    assert result.classification == expected


def test_account_reference_is_placeholder_only() -> None:
    result = validate_broker_read_only_snapshot(
        replace(build_sample_valid_broker_snapshot(), account_reference="REAL-ACCOUNT-123")
    )
    assert result.account_reference_allowed is False
    assert result.classification == BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT
    assert PLACEHOLDER_ACCOUNT_REFERENCE == "DEMO_ACCOUNT_REFERENCE_PRESENT"


def test_broker_snapshot_json_has_required_keys() -> None:
    data = broker_snapshot_to_jsonable_dict(build_sample_valid_broker_snapshot())
    assert {
        "account_present",
        "account_reference",
        "balance_present",
        "balance",
        "margin_available_present",
        "open_trades_present",
        "market_hours_open",
        "instrument_tradeable",
        "spread_present",
        "timestamp_present",
        "read_only_reconciled",
        "sanitized",
    }.issubset(data)
    json.dumps(data)


def test_broker_snapshot_operator_text_is_plain() -> None:
    text = broker_snapshot_result_to_operator_text()
    assert "review-ready" in text
    assert "No trade was placed." in text
