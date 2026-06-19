from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_read_only_client import (  # noqa: E402
    OandaReadOnlyClient,
    ReadOnlyMethodRejected,
)
from automation.forex_engine.read_only_live_data_sanitizer import (  # noqa: E402
    sanitize_account_summary,
    sanitize_tree,
    source_fields,
)


def test_oanda_client_rejects_any_method_other_than_get():
    client = OandaReadOnlyClient(
        api_token="runtime-token",
        account_id="101-222-333333-001",
        opener=lambda *_args, **_kwargs: None,
    )

    for method in ("POST", "PUT", "PATCH", "DELETE", "post"):
        with pytest.raises(ReadOnlyMethodRejected):
            client.request_json(method, "/v3/accounts/ignored")


def test_oanda_client_repr_masks_runtime_values():
    client = OandaReadOnlyClient(
        api_token="runtime-token",
        account_id="101-222-333333-001",
    )

    text = repr(client)
    assert "runtime-token" not in text
    assert "101-222-333333-001" not in text
    assert "MASKED" in text


def test_sanitizer_masks_account_and_strips_order_transaction_identifiers():
    raw = {
        "account": {
            "id": "101-222-333333-001",
            "accountID": "101-222-333333-001",
            "orders": [
                {
                    "orderID": "123",
                    "transactionID": "456",
                    "instrument": "EUR_USD",
                }
            ],
            "authorization": "Bearer SHOULD_NOT_APPEAR",
        }
    }

    sanitized = sanitize_tree(raw)
    text = str(sanitized)

    assert "101-222-333333-001" not in text
    assert "SHOULD_NOT_APPEAR" not in text
    assert "orderID" not in text
    assert "transactionID" not in text
    assert sanitized["account"]["accountID"] == "MASKED_ACCOUNT_ID"


def test_sanitize_account_summary_returns_safe_readiness_fields():
    context = source_fields(
        source_type="broker-live-read-only",
        source_label="OANDA_READ_ONLY_SANITIZED",
        freshness_utc="2026-06-19T12:00:00Z",
        stale_status="VALID",
        block_reason="read-only",
    )

    summary = sanitize_account_summary(
        {
            "account": {
                "id": "101-222-333333-001",
                "openPositionCount": 2,
                "pendingOrderCount": 1,
                "pl": "3.21",
                "unrealizedPL": "-0.10",
                "marginAvailable": "500.00",
            }
        },
        broker_mode="practice",
        freshness_utc="2026-06-19T12:00:00Z",
        source_context=context,
    )

    assert summary["account_reachable"] is True
    assert summary["open_positions_reconciled"] is True
    assert summary["pending_orders_reconciled"] is True
    assert summary["daily_pl_available"] is True
    assert summary["margin_risk_available"] is True
    assert "101-222-333333-001" not in str(summary)
