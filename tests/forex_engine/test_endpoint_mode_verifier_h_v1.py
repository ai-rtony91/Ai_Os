from automation.forex_engine.endpoint_mode_verifier_h_v1 import verify_endpoint_mode


def test_demo_endpoint_mode_is_allowed():
    result = verify_endpoint_mode("DEMO")

    assert result.allowed is True
    assert result.normalized_mode == "DEMO"
    assert result.blocked_reasons == ()


def test_live_endpoint_mode_is_rejected():
    result = verify_endpoint_mode("LIVE")

    assert result.allowed is False
    assert "live_endpoint_prohibited" in result.blocked_reasons


def test_missing_endpoint_mode_is_rejected():
    result = verify_endpoint_mode(None)

    assert result.allowed is False
    assert "endpoint_mode_missing" in result.blocked_reasons


def test_blank_endpoint_mode_is_rejected():
    result = verify_endpoint_mode("   ")

    assert result.allowed is False
    assert "endpoint_mode_missing" in result.blocked_reasons


def test_ambiguous_endpoint_mode_is_rejected():
    result = verify_endpoint_mode("DEMO/LIVE")

    assert result.allowed is False
    assert "endpoint_mode_ambiguous" in result.blocked_reasons


def test_unknown_endpoint_mode_is_rejected():
    result = verify_endpoint_mode("PAPER")

    assert result.allowed is False
    assert "endpoint_mode_unknown" in result.blocked_reasons