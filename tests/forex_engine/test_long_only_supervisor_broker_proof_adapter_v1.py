from __future__ import annotations

from automation.forex_engine.long_only_supervisor_broker_proof_adapter_v1 import (
    AUTONOMOUS_BLOCKED_BY_BROKER_GATE,
    AUTONOMOUS_DEMO_PREPARATION_READY,
    adapt_supervisor_with_broker_proof,
)
from automation.forex_engine.oanda_long_only_broker_proof_intake_v1 import (
    OANDA_BROKER_PROOF_BLOCKED,
    OANDA_LONG_ONLY_BROKER_PROOF_READY,
)


def test_blocked_broker_proof_keeps_supervisor_broker_blocked():
    result = adapt_supervisor_with_broker_proof(
        {"status": "AUTONOMOUS_BLOCKED_BY_BROKER_GATE"},
        {"status": OANDA_BROKER_PROOF_BLOCKED, "blockers": ["missing_oanda_broker_proof"]},
    )
    assert result["status"] == AUTONOMOUS_BLOCKED_BY_BROKER_GATE
    assert "missing_oanda_broker_proof" in result["blockers"]
    assert result["execution_allowed"] is False


def test_valid_broker_proof_clears_demo_preparation_only():
    result = adapt_supervisor_with_broker_proof(
        {"status": "AUTONOMOUS_BLOCKED_BY_BROKER_GATE"},
        {"status": OANDA_LONG_ONLY_BROKER_PROOF_READY, "blockers": []},
    )
    assert result["status"] == AUTONOMOUS_DEMO_PREPARATION_READY
    assert result["broker_gate_clear_for_demo_preparation"] is True
    assert "policy_live_exception_gate_still_required" in result["blockers"]


def test_adapter_never_enables_execution_flags():
    result = adapt_supervisor_with_broker_proof(
        {"status": "AUTONOMOUS_BLOCKED_BY_POLICY"},
        {"status": OANDA_LONG_ONLY_BROKER_PROOF_READY, "blockers": []},
    )
    assert result["execution_allowed"] is False
    assert result["ready_to_execute"] is False
    assert result["demo_order_allowed"] is False
    assert result["live_autonomy_allowed"] is False
    assert result["short_side_enabled"] is False
    assert result["broker_mutation_allowed"] is False
    assert result["order_execution_allowed"] is False
