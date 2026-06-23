"""Adapter from sanitized OANDA broker proof into long-only supervisor state."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.forex_engine.oanda_long_only_broker_proof_intake_v1 import (
    OANDA_LONG_ONLY_BROKER_PROOF_READY,
)

AUTONOMOUS_BLOCKED_BY_BROKER_GATE = "AUTONOMOUS_BLOCKED_BY_BROKER_GATE"
AUTONOMOUS_BLOCKED_BY_POLICY = "AUTONOMOUS_BLOCKED_BY_POLICY"
AUTONOMOUS_DEMO_PREPARATION_READY = "AUTONOMOUS_DEMO_PREPARATION_READY"


def _safe_flags() -> dict[str, bool]:
    return {
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "short_side_enabled": False,
        "broker_mutation_allowed": False,
        "order_execution_allowed": False,
    }


def adapt_supervisor_with_broker_proof(
    supervisor_state: Mapping[str, Any] | None,
    broker_proof_result: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return a prepare-only supervisor view with broker proof attached."""
    state = dict(supervisor_state or {})
    proof = dict(broker_proof_result or {})
    blockers = list(state.get("blockers", [])) if isinstance(state.get("blockers"), list) else []

    if proof.get("status") != OANDA_LONG_ONLY_BROKER_PROOF_READY:
        status = AUTONOMOUS_BLOCKED_BY_BROKER_GATE
        blockers.extend(proof.get("blockers", []))
        broker_gate_clear = False
    else:
        broker_gate_clear = True
        status = AUTONOMOUS_DEMO_PREPARATION_READY
        blockers.append("policy_live_exception_gate_still_required")

    result = {
        "status": status,
        "broker_gate_clear_for_demo_preparation": broker_gate_clear,
        "policy_gate_clear": False,
        "blockers": list(dict.fromkeys(blockers)),
        "next_safe_action": (
            "provide_owner_policy_contract_before_any_order_arming"
            if broker_gate_clear
            else "provide_complete_sanitized_oanda_demo_practice_broker_proof"
        ),
    }
    result.update(_safe_flags())
    return result
