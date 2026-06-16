from __future__ import annotations

from typing import Any

from automation.forex_engine import schema_contracts as schemas


PAPER_ONLY_CONTRACT = "PAPER_ONLY_CONTRACT"
NOT_READY = "NOT_READY"
WATCHLIST = "WATCHLIST"
CONTRACT_READY = "CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET"
ALLOWED_READINESS_STATUSES = {NOT_READY, WATCHLIST, CONTRACT_READY}
FORBIDDEN_READINESS_STATUSES = {"LIVE_READY", "BROKER_READY", "ORDER_READY", "AUTO_TRADE_READY"}


def default_broker_paper_sandbox_readiness_policy() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_SANDBOX_READINESS_POLICY.v1",
        "mode": PAPER_ONLY_CONTRACT,
        "minimum_fixture_count": 9,
        "minimum_regime_count": 7,
        "minimum_total_intents": 50,
        "minimum_simulated_ledger_entries": 50,
        "minimum_consistency_pct": 70.0,
        "minimum_oos_consistency_pct": 70.0,
        "stress_classification_cannot_be_fail": True,
        "combined_stress_oos_classification_cannot_be_fail": True,
        "live_trade_ready_must_be_false": True,
        "real_order_ready_must_be_false": True,
        "broker_integration_active_must_be_false": True,
        "credentials_required_now_must_be_false": True,
        "protected_gate_required_must_be_true": True,
        "future_broker_paper_packet_requires_approval": True,
        "presecurity_gate_landed": False,
    }


def evaluate_broker_paper_sandbox_readiness(
    evidence: dict[str, Any] | None = None,
    stress_oos: dict[str, Any] | None = None,
    risk_governor: dict[str, Any] | None = None,
    stress_repair: dict[str, Any] | None = None,
    expanded_oos: dict[str, Any] | None = None,
    oos_repair: dict[str, Any] | None = None,
    low_vol_edge_redesign: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = default_broker_paper_sandbox_readiness_policy()
    active_policy.update(dict(policy or {}))
    active_evidence = dict(evidence or _build_default_evidence())
    active_stress_oos = dict(stress_oos or active_evidence.get("combined_stress_oos_gate") or {})
    active_risk_governor = dict(
        risk_governor
        or active_evidence.get("risk_governor")
        or active_evidence.get("risk_governor_result")
        or {}
    )
    active_stress_repair = dict(stress_repair or active_evidence.get("stress_repair") or {})
    active_expanded_oos = dict(expanded_oos or active_evidence.get("expanded_oos") or {})
    active_oos_repair = dict(oos_repair or active_evidence.get("oos_repair") or {})
    active_low_vol_edge = dict(low_vol_edge_redesign or active_evidence.get("low_vol_edge_redesign") or {})
    evidence_gates = _evidence_gates(
        active_evidence,
        active_stress_oos,
        active_risk_governor,
        active_stress_repair,
        active_expanded_oos,
        active_oos_repair,
        active_low_vol_edge,
        active_policy,
    )
    passed_gates = [name for name, gate in evidence_gates.items() if gate["passed"] is True]
    failed_gates = [name for name, gate in evidence_gates.items() if gate["passed"] is not True]
    result = {
        "schema": "AIOS_BROKER_PAPER_SANDBOX_READINESS_CONTRACT.v1",
        "mode": PAPER_ONLY_CONTRACT,
        "policy": active_policy,
        "evidence_gates": evidence_gates,
        "passed_gates": passed_gates,
        "failed_gates": failed_gates,
        "blockers": _blockers(
            evidence_gates,
            active_evidence,
            active_stress_oos,
            active_risk_governor,
            active_stress_repair,
            active_expanded_oos,
            active_oos_repair,
            active_low_vol_edge,
        ),
        "required_future_protected_approvals": _required_future_protected_approvals(),
        "forbidden_current_actions": _forbidden_current_actions(),
        "broker_paper_sandbox_contract_ready": False,
        "broker_paper_contract_ready": False,
        "stress_repair_status": active_stress_repair.get("stress_repair_status", "not_run"),
        "stress_repair_classification": active_stress_repair.get("repaired_classification", "not_run"),
        "expanded_oos_status": active_expanded_oos.get("classification", "not_run"),
        "expanded_oos_classification": active_expanded_oos.get("classification", "not_run"),
        "oos_repair_status": active_oos_repair.get(
            "repaired_classification",
            active_oos_repair.get("classification", "not_run"),
        ),
        "oos_repair_classification": active_oos_repair.get(
            "repaired_classification",
            active_oos_repair.get("classification", "not_run"),
        ),
        "original_max_degradation_pct": float(active_oos_repair.get("original_max_degradation_pct", 0.0)),
        "repaired_max_degradation_pct": float(active_oos_repair.get("repaired_max_degradation_pct", 0.0)),
        "degradation_improvement_pct": float(active_oos_repair.get("degradation_improvement_pct", 0.0)),
        "low_vol_edge_status": active_low_vol_edge.get("classification", "not_run"),
        "low_vol_edge_classification": active_low_vol_edge.get("classification", "not_run"),
        "low_vol_policy_action": active_low_vol_edge.get("low_vol_policy_action", "not_run"),
        "redesigned_max_degradation_pct": float(active_low_vol_edge.get("redesigned_max_degradation_pct", 0.0)),
        "low_vol_rejected_intents": int(active_low_vol_edge.get("rejected_low_vol_intents", 0)),
        "live_trade_ready": False,
        "real_order_ready": False,
        "broker_integration_active": False,
        "credentials_required_now": False,
        "protected_gate_required": True,
        "future_broker_paper_packet_requires_approval": True,
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1",
        "security_gate_reason": "broker-paper requires secrets/network/broker boundaries before adapter work",
        "safety": broker_paper_sandbox_boundary_summary(),
    }
    result["readiness_status"] = classify_broker_paper_sandbox_readiness(result)
    result["broker_paper_sandbox_contract_ready"] = result["readiness_status"] == CONTRACT_READY
    result["broker_paper_contract_ready"] = result["broker_paper_sandbox_contract_ready"]
    result["next_safe_action"] = _next_safe_action(result["readiness_status"], result["blockers"])
    assert_no_broker_paper_side_effects(result)
    return result


def classify_broker_paper_sandbox_readiness(result: dict[str, Any]) -> str:
    payload = dict(result)
    if payload.get("readiness_status") in FORBIDDEN_READINESS_STATUSES:
        return NOT_READY
    if _critical_safety_failed(payload):
        return NOT_READY
    gates = {name: dict(gate) for name, gate in dict(payload.get("evidence_gates") or {}).items()}
    if not gates:
        return NOT_READY
    if any(gate.get("classification") == "FAIL" for gate in gates.values()):
        return NOT_READY
    if any(gate.get("passed") is not True for gate in gates.values()):
        return NOT_READY
    if any(gate.get("classification") == "WATCHLIST" for gate in gates.values()):
        return WATCHLIST
    blockers = [str(item) for item in list(payload.get("blockers") or [])]
    if any("watchlist" in blocker.lower() for blocker in blockers):
        return WATCHLIST
    if blockers:
        return NOT_READY
    return CONTRACT_READY


def broker_paper_sandbox_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_SANDBOX_READINESS_BOUNDARY.v1",
        "readiness_contract_only": True,
        "local_simulation_only": True,
        "broker_integration_active": False,
        "broker_sdk_allowed": False,
        "broker_paper_orders": False,
        "paper_order_execution": False,
        "real_order_ready": False,
        "network_allowed": False,
        "api_ingestion": False,
        "credentials_required_now": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "env_reads_allowed": False,
        "env_writes_allowed": False,
        "live_trading": False,
        "live_ready": False,
        "live_trade_ready": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "account_mutation": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "protected_gate_required": True,
        "reports_written": False,
        "files_written": [],
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1",
    }


def assert_no_broker_paper_side_effects(result: dict[str, Any]) -> None:
    payload = dict(result)
    status = payload.get("readiness_status")
    if status in FORBIDDEN_READINESS_STATUSES or status not in ALLOWED_READINESS_STATUSES:
        raise ValueError("Readiness status must stay inside the broker-paper sandbox contract status set")
    if payload.get("live_trade_ready") is not False:
        raise ValueError("live_trade_ready must remain false")
    if payload.get("real_order_ready") is not False:
        raise ValueError("real_order_ready must remain false")
    if payload.get("broker_integration_active") is not False:
        raise ValueError("broker_integration_active must remain false")
    if payload.get("credentials_required_now") is not False:
        raise ValueError("credentials_required_now must remain false")
    if payload.get("protected_gate_required") is not True:
        raise ValueError("protected_gate_required must remain true")
    if payload.get("future_broker_paper_packet_requires_approval") is not True:
        raise ValueError("future broker-paper packet approval must remain required")
    safety = dict(payload.get("safety") or {})
    blocked_true_fields = (
        "broker_integration_active",
        "broker_sdk_allowed",
        "broker_paper_orders",
        "paper_order_execution",
        "real_order_ready",
        "network_allowed",
        "api_ingestion",
        "credentials_required_now",
        "credentials_allowed",
        "secrets_allowed",
        "env_reads_allowed",
        "env_writes_allowed",
        "live_trading",
        "live_ready",
        "live_trade_ready",
        "execution_allowed",
        "orders_allowed",
        "account_mutation",
        "webhooks_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "worker_dispatch",
        "queue_mutation",
        "approval_mutation",
    )
    for field_name in blocked_true_fields:
        if safety.get(field_name) is True:
            raise ValueError(f"{field_name} must remain false in broker-paper sandbox readiness")
    schemas.assert_no_live_permissions(payload)


def _build_default_evidence() -> dict[str, Any]:
    from automation.forex_engine import paper_forward_evidence_v2

    return paper_forward_evidence_v2.build_paper_forward_evidence_v2()


def _evidence_gates(
    evidence: dict[str, Any],
    stress_oos: dict[str, Any],
    risk_governor: dict[str, Any],
    stress_repair: dict[str, Any],
    expanded_oos: dict[str, Any],
    oos_repair: dict[str, Any],
    low_vol_edge: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    multi = dict(evidence.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(evidence.get("regime_consistency") or {})
    broker_flags = _contract_flags(evidence)
    stress_classification = str(stress_oos.get("stress_classification") or _stress_summary(evidence).get("classification") or "FAIL")
    combined_classification = str(stress_oos.get("combined_classification") or "FAIL")
    risk_governor_classification = str(risk_governor.get("classification") or "FAIL")
    repair_classification = str(
        stress_repair.get("repaired_classification")
        or stress_repair.get("classification")
        or ""
    )
    if repair_classification == "PAPER_FORWARD_READY" and stress_classification == "WATCHLIST":
        stress_classification = "PAPER_FORWARD_READY"
    if repair_classification == "PAPER_FORWARD_READY" and combined_classification == "WATCHLIST":
        combined_classification = "PAPER_FORWARD_READY"
    expanded_oos_classification = str(expanded_oos.get("classification") or "")
    oos_repair_classification = str(
        oos_repair.get("repaired_classification")
        or oos_repair.get("classification")
        or ""
    )
    low_vol_edge_classification = str(low_vol_edge.get("classification") or "")
    gates = {
        "minimum_fixture_count": _minimum(int(multi.get("fixture_count", 0)), policy["minimum_fixture_count"]),
        "minimum_regime_count": _minimum(int(regime.get("total_regimes", 0)), policy["minimum_regime_count"]),
        "minimum_total_intents": _minimum(int(multi.get("total_intents", 0)), policy["minimum_total_intents"]),
        "minimum_simulated_ledger_entries": _minimum(
            int(multi.get("total_ledger_entries", 0)),
            policy["minimum_simulated_ledger_entries"],
        ),
        "minimum_consistency_pct": _minimum(float(multi.get("consistency_pct", 0.0)), policy["minimum_consistency_pct"]),
        "minimum_oos_consistency_pct": _minimum(
            float(stress_oos.get("heldout_consistency_pct", 0.0)),
            policy["minimum_oos_consistency_pct"],
        ),
        "stress_classification": _classification_gate(stress_classification),
        "combined_stress_oos_classification": _classification_gate(combined_classification),
        "risk_governor_classification": _classification_gate(risk_governor_classification),
        "live_trade_ready_false": _boolean_gate(broker_flags["live_trade_ready"] is False, broker_flags["live_trade_ready"], False),
        "real_order_ready_false": _boolean_gate(broker_flags["real_order_ready"] is False, broker_flags["real_order_ready"], False),
        "broker_integration_active_false": _boolean_gate(
            broker_flags["broker_integration_active"] is False,
            broker_flags["broker_integration_active"],
            False,
        ),
        "credentials_required_now_false": _boolean_gate(
            broker_flags["credentials_required_now"] is False,
            broker_flags["credentials_required_now"],
            False,
        ),
        "protected_gate_required_true": _boolean_gate(
            broker_flags["protected_gate_required"] is True,
            broker_flags["protected_gate_required"],
            True,
        ),
        "future_broker_paper_packet_requires_approval": _boolean_gate(True, True, True),
    }
    if repair_classification:
        gates["stress_repair_classification"] = _classification_gate(repair_classification)
    if expanded_oos_classification:
        gates["expanded_oos_classification"] = _classification_gate(expanded_oos_classification)
        gates["expanded_oos_consistency_pct"] = _minimum(
            float(expanded_oos.get("heldout_consistency_pct", 0.0)),
            policy["minimum_oos_consistency_pct"],
        )
    if oos_repair_classification:
        gates["oos_repair_classification"] = _classification_gate(oos_repair_classification)
        gates["oos_repair_degradation_improved"] = _boolean_gate(
            float(oos_repair.get("degradation_improvement_pct", 0.0)) > 0.0,
            float(oos_repair.get("degradation_improvement_pct", 0.0)) > 0.0,
            True,
        )
        gates["oos_repair_degradation_policy"] = _maximum_watchlist(
            float(oos_repair.get("repaired_max_degradation_pct", 100.0)),
            float(oos_repair.get("repair_plan", {}).get("max_allowed_degradation_pct", 35.0)),
        )
    if low_vol_edge_classification:
        gates["low_vol_edge_classification"] = _classification_gate(low_vol_edge_classification)
        gates["low_vol_edge_degradation_improved"] = _boolean_gate(
            float(low_vol_edge.get("degradation_improvement_from_repair_pct", 0.0)) > 0.0,
            float(low_vol_edge.get("degradation_improvement_from_repair_pct", 0.0)) > 0.0,
            True,
        )
        gates["low_vol_edge_degradation_policy"] = _maximum_watchlist(
            float(low_vol_edge.get("redesigned_max_degradation_pct", 100.0)),
            float(low_vol_edge.get("policy", {}).get("max_allowed_degradation_pct", 35.0)),
        )
        if low_vol_edge_classification == "PAPER_FORWARD_READY":
            presecurity_landed = bool(policy.get("presecurity_gate_landed", False))
            gates["presecurity_gate_landed_before_broker_paper"] = _boolean_watchlist(
                presecurity_landed,
                True,
            )
    return gates


def _minimum(actual: float, threshold: float) -> dict[str, Any]:
    return {
        "passed": float(actual) >= float(threshold),
        "actual": round(float(actual), 4),
        "threshold": round(float(threshold), 4),
        "comparator": ">=",
        "classification": "PAPER_FORWARD_READY" if float(actual) >= float(threshold) else "FAIL",
    }


def _classification_gate(classification: str) -> dict[str, Any]:
    if classification == "FAIL" or classification in FORBIDDEN_READINESS_STATUSES:
        passed = False
        normalized = "FAIL"
    elif classification == "WATCHLIST":
        passed = True
        normalized = "WATCHLIST"
    elif classification == "PAPER_FORWARD_READY":
        passed = True
        normalized = "PAPER_FORWARD_READY"
    else:
        passed = False
        normalized = "FAIL"
    return {
        "passed": passed,
        "actual": normalized,
        "threshold": "not FAIL",
        "comparator": "!=",
        "classification": normalized,
    }


def _maximum_watchlist(actual: float, threshold: float) -> dict[str, Any]:
    passed_policy = float(actual) <= float(threshold)
    return {
        "passed": True,
        "actual": round(float(actual), 4),
        "threshold": round(float(threshold), 4),
        "comparator": "<=",
        "classification": "PAPER_FORWARD_READY" if passed_policy else "WATCHLIST",
    }


def _boolean_gate(passed: bool, actual: bool, expected: bool) -> dict[str, Any]:
    return {
        "passed": bool(passed),
        "actual": bool(actual),
        "threshold": bool(expected),
        "comparator": "==",
        "classification": "PAPER_FORWARD_READY" if passed else "FAIL",
    }


def _boolean_watchlist(actual: bool, expected: bool) -> dict[str, Any]:
    passed = bool(actual) == bool(expected)
    return {
        "passed": True,
        "actual": bool(actual),
        "threshold": bool(expected),
        "comparator": "==",
        "classification": "PAPER_FORWARD_READY" if passed else "WATCHLIST",
    }


def _contract_flags(evidence: dict[str, Any]) -> dict[str, bool]:
    return {
        "live_trade_ready": bool(evidence.get("live_trade_ready", False)),
        "real_order_ready": bool(evidence.get("real_order_ready", False)),
        "broker_integration_active": bool(evidence.get("broker_integration_active", False)),
        "credentials_required_now": bool(evidence.get("credentials_required_now", False)),
        "protected_gate_required": bool(evidence.get("protected_gate_required", True)),
    }


def _stress_summary(evidence: dict[str, Any]) -> dict[str, Any]:
    paper_stress = dict(evidence.get("paper_forward_stress") or evidence.get("stress_result") or {})
    return dict(paper_stress.get("stress_summary") or {})


def _blockers(
    evidence_gates: dict[str, dict[str, Any]],
    evidence: dict[str, Any],
    stress_oos: dict[str, Any],
    risk_governor: dict[str, Any],
    stress_repair: dict[str, Any],
    expanded_oos: dict[str, Any],
    oos_repair: dict[str, Any],
    low_vol_edge: dict[str, Any],
) -> list[str]:
    blockers = []
    for name, gate in evidence_gates.items():
        if gate["passed"] is not True:
            blockers.append(f"gate_failed:{name}")
        elif gate.get("classification") == "WATCHLIST":
            blockers.append(f"gate_watchlist:{name}")
    blockers.extend([str(item) for item in list(evidence.get("blockers") or [])])
    blockers.extend([str(item) for item in list(stress_oos.get("blockers") or [])])
    blockers.extend([str(item) for item in list(risk_governor.get("blockers") or [])])
    blockers.extend([str(item) for item in list(stress_repair.get("blockers") or [])])
    blockers.extend([str(item) for item in list(expanded_oos.get("blockers") or [])])
    blockers.extend([str(item) for item in list(oos_repair.get("blockers") or [])])
    blockers.extend([str(item) for item in list(low_vol_edge.get("blockers") or [])])
    return _unique(blockers)


def _critical_safety_failed(payload: dict[str, Any]) -> bool:
    if payload.get("live_trade_ready") is not False:
        return True
    if payload.get("real_order_ready") is not False:
        return True
    if payload.get("broker_integration_active") is not False:
        return True
    if payload.get("credentials_required_now") is not False:
        return True
    if payload.get("protected_gate_required") is not True:
        return True
    return False


def _required_future_protected_approvals() -> list[str]:
    return [
        "broker selection approval",
        "credentials handling approval",
        "paper account approval",
        "network/API approval",
        "order intent to broker-paper translation approval",
        "kill switch approval",
        "audit log approval",
        "max loss / daily stop approval",
        "human owner confirmation",
    ]


def _forbidden_current_actions() -> list[str]:
    return [
        "connect to broker",
        "read credentials or secrets",
        "write credentials or secrets",
        "read .env",
        "write .env",
        "place broker paper orders",
        "place live orders",
        "mutate account state",
        "use network market APIs",
        "start scheduler",
        "start daemon",
        "send webhook",
        "bypass protected approval",
    ]


def _next_safe_action(readiness_status: str, blockers: list[str]) -> str:
    if readiness_status == CONTRACT_READY:
        return "Run the pre-security broker-paper gate before any adapter, credential, network, or order work."
    if readiness_status == WATCHLIST:
        if any("presecurity" in blocker for blocker in blockers):
            return "Run PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1 before any broker-paper adapter work."
        if any("low_vol" in blocker for blocker in blockers):
            return "Resolve low-vol edge redesign WATCHLIST evidence before broker-paper sandbox readiness."
        if any("oos_repair" in blocker for blocker in blockers):
            return "Repair low-vol OOS degradation before any protected broker-paper sandbox contract."
        if any("expanded_oos" in blocker for blocker in blockers):
            return "Repair expanded OOS blockers before any protected broker-paper sandbox adapter-stub contract."
        return "Repair WATCHLIST stress/OOS evidence before any protected broker-paper sandbox adapter-stub contract."
    if blockers:
        return f"Resolve readiness blocker: {blockers[0]}; broker-paper and live execution remain blocked."
    return "Collect missing local evidence and rerun the broker-paper sandbox readiness contract."


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
