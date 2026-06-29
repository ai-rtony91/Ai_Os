from __future__ import annotations

import json

from automation.forex_engine import demo_readiness_decision_v1 as module
from automation.forex_engine.evidence_depth_walkforward_sufficiency_v1 import (
    PROTECTED_FALSE_FIELDS,
)


def test_result_is_deterministic_and_json_serializable():
    first = module.run_demo_readiness_decision_v1()
    second = module.run_demo_readiness_decision_v1()

    assert first == second
    json.dumps(first)


def test_demo_readiness_requires_owner_review_and_broker_proof():
    result = module.run_demo_readiness_decision_v1()

    assert result["demo_allowed"] is False
    assert result["owner_review_required"] is True
    assert result["broker_connection_required"] is True
    assert "owner_review_required" in result["demo_blockers"]
    assert "protected_broker_connection_proof_required" in result["demo_blockers"]


def test_demo_execution_remains_blocked_even_after_inputs():
    result = module.run_demo_readiness_decision_v1(
        owner_review_complete=True,
        protected_broker_proof_complete=True,
    )

    assert result["demo_allowed"] is False
    assert result["demo_authorized"] is False
    assert result["order_execution"] is False


def test_protected_booleans_remain_false():
    result = module.run_demo_readiness_decision_v1()

    for field in PROTECTED_FALSE_FIELDS:
        assert result[field] is False
