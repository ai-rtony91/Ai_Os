from automation.forex_engine.account_metadata_sanitizer_h_v1 import sanitize_account_metadata


def test_empty_account_metadata_returns_empty_dict():
    assert sanitize_account_metadata({}) == {}


def test_account_id_is_removed():
    result = sanitize_account_metadata(
        {
            "account_id": "123-456",
            "replay_reference": "replay-001",
        }
    )

    assert "account_id" not in result
    assert result["replay_reference"] == "replay-001"


def test_account_number_is_removed():
    result = sanitize_account_metadata(
        {
            "account_number": "999999",
            "governance_reference": "gov-001",
        }
    )

    assert "account_number" not in result
    assert result["governance_reference"] == "gov-001"


def test_broker_account_is_removed():
    result = sanitize_account_metadata(
        {
            "broker_account": "broker-actual",
            "safe_label": "demo-sanitized",
        }
    )

    assert "broker_account" not in result
    assert result["safe_label"] == "demo-sanitized"


def test_safe_account_boundary_status_is_preserved():
    result = sanitize_account_metadata(
        {
            "account_boundary_status": "CLEAR",
            "account_boundary_clear": True,
        }
    )

    assert result["account_boundary_status"] == "CLEAR"
    assert result["account_boundary_clear"] is True