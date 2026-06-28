"""Overnight end-to-end Forex repo-safe execution contract definitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]

DOCS_DIR = REPO_ROOT / "docs" / "governance" / "programs"
REPORT_DIR = REPO_ROOT / "Reports" / "forex_delivery"

DOC_CONTRACT_PATH = (
    DOCS_DIR / "contracts" / "AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTRACT_V1.md"
)
DOC_FLOW2_PATH = DOCS_DIR / "flows" / "FLOW-FOREX-002-SUPERVISED-DEMO-EVIDENCE-COUNTDOWN-CAPTURE-V1.md"
DOC_FLOW3_PATH = DOCS_DIR / "flows" / "FLOW-FOREX-003-PROFIT-LOOP-LIVE-WEEK-VACATION-GATE-V1.md"
DOC_FLOW4_PATH = DOCS_DIR / "flows" / "FLOW-FOREX-004-LIVE-EXCEPTION-AND-REAL-MONEY-GATE-V1.md"

JSON_REPORT_PATH = REPORT_DIR / "AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTRACT_V1.json"
REPORT_PATH = REPORT_DIR / "AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTRACT_V1_REPORT.md"
QUEUE_PATH = REPORT_DIR / "AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_NEXT_ACTION_QUEUE_V1.md"
CONTINUATION_PATH = REPORT_DIR / "AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTINUATION_LEDGER_V1.md"
GATE_REGISTRY_PATH = REPORT_DIR / "AIOS_FOREX_EXTERNAL_GATE_BRIDGE_REGISTRY_V1.md"
FLOW2_CONTRACT_PATH = REPORT_DIR / "AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_CAPTURE_CONTRACT_V1.md"
FLOW3_CONTRACT_PATH = REPORT_DIR / "AIOS_FOREX_FLOW3_PROFIT_LOOP_LIVE_WEEK_VACATION_GATE_CONTRACT_V1.md"
LIVE_EXCEPTION_CONTRACT_PATH = REPORT_DIR / "AIOS_FOREX_LIVE_EXCEPTION_REAL_MONEY_GATE_CONTRACT_V1.md"
NEXT_FLOW2_PACKET_PATH = REPORT_DIR / "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1.md"
NEXT_FLOW3_PACKET_PATH = REPORT_DIR / "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1.md"
NEXT_EXCEPTION_PACKET_PATH = REPORT_DIR / "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1.md"

BANNED_OUTPUT_TOKENS = [
    "TODO",
    "TBD",
    "@filename",
    "probably",
    "roughly",
    "approximately",
    "I estimate",
    "guaranteed profit",
    "guaranteed returns",
    "100-120 percent verified",
    "100–120% verified",
    "target achieved without evidence",
    "live ready",
    "autonomous trading ready",
    "vacation mode active",
    "22h6d active",
    "22h/6d active",
    "live profitable week proven",
    "broker connected",
    "credentials loaded",
    "order placed",
    "trade executed",
    "demo trade executed",
    "live trade executed",
    "real order",
    "real trade",
    "approval granted",
    "API key accepted",
    "credentials accepted",
    "account id accepted",
    "broker connected successfully",
    "money machine",
    "mean machine",
]

FORBIDDEN_OWNER_FIELDS = {
    "account_identifier",
    "account_id",
    "account_number",
    "broker_account_id",
    "credentials",
    "credential",
    "password",
    "token",
    "api_key",
    "api_token",
    "broker_api_key",
}

REQUIRED_ACCEPTANCE_FIELDS = [
    "accepts_dependency_order",
    "accepts_flow2_contract",
    "accepts_flow3_contract",
    "accepts_live_exception_bridge",
    "accepts_no_false_claims",
    "accepts_external_gate_boundaries",
    "accepts_validator_truth",
]

FLOW_2 = "FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE"
FLOW_3 = "FLOW_3_PROFIT_LOOP_LIVE_WEEK_VACATION_GATE"
FLOW_4 = "LIVE_EXCEPTION_AND_REAL_MONEY_GATE"
FLOW_5 = "RUNTIME_SUPERVISOR_AND_SOS_GATE"


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on", "y"}:
            return True
        if lowered in {"false", "0", "no", "off", "n"}:
            return False
    return default


def build_dependency_order() -> list[dict]:
    return [
        {
            "flow_id": FLOW_2,
            "depends_on": ["Flow 1 PR #1194"],
            "produces": [
                "supervised_demo_evidence_contract",
                "broker_snapshot_capture_contract",
                "TP_SL_state_capture_contract",
                "realized_PL_capture_contract",
                "no_duplicate_order_evidence_contract",
                "no_runaway_exposure_contract",
                "post_trade_countdown_update_contract",
            ],
        },
        {
            "flow_id": FLOW_3,
            "depends_on": ["Flow 2 evidence output"],
            "produces": [
                "result_classification_contract",
                "next_candidate_selection_contract",
                "countdown_progress_update_contract",
                "live_week_readiness_contract",
                "runtime_22h6d_readiness_contract",
                "vacation_mode_readiness_contract",
            ],
        },
        {
            "flow_id": FLOW_4,
            "depends_on": [
                "Flow 3 proof output",
                "explicit owner approval",
                "broker gate",
                "credential gate",
                "risk gate",
                "evidence gate",
            ],
            "produces": [
                "live_exception_packet_contract",
                "real_money_readiness_bridge",
            ],
        },
        {
            "flow_id": FLOW_5,
            "depends_on": [
                "Flow 3 proof output",
                "SOS proof",
                "kill switch proof",
                "pause/resume proof",
                "no duplicate order proof",
            ],
            "produces": [
                "22h6d_runtime_eligibility_contract",
                "vacation_mode_eligibility_contract",
            ],
        },
    ]


def build_external_gate_registry() -> list[dict]:
    return [
        {
            "gate_name": "owner_input_gate",
            "blocked_capability": "Owner action acceptance is required before close-cycle continuation.",
            "why_gate_blocks_end_to_end_completion": "Without acceptance, safe enforce/proceed state is not established.",
            "required_owner_input": "overnight_action with acceptance booleans and owner_attestation.",
            "required_external_evidence": "None. Repo-safe evidence prepared by this contract.",
            "safe_repo_work_completed": "dependency order, contracts, and continuation ledger prepared.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "evaluate returns OVERNIGHT_CONTRACT_READY_TO_ENFORCE_FLOW2.",
            "continuation_after_gate": "Proceed directly to Flow 2 with host validation evidence.",
        },
        {
            "gate_name": "broker_snapshot_gate",
            "blocked_capability": "Flow 2 evidence bundle requires broker/demo snapshot.",
            "why_gate_blocks_end_to_end_completion": "Countdowns and contracts cannot update without snapshot input.",
            "required_owner_input": "Owner-supervised snapshot capture authority packet.",
            "required_external_evidence": "Broker snapshot artifact from supervised demo evidence packet.",
            "safe_repo_work_completed": "Flow 2 required inputs and outputs are defined.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 2 evidence_bundle output includes snapshot capture contract.",
            "continuation_after_gate": "Flow 2 evidence handoff transitions into Flow 3.",
        },
        {
            "gate_name": "broker_connection_gate",
            "blocked_capability": "Live exception contract cannot claim real-money readiness.",
            "why_gate_blocks_end_to_end_completion": "Proof bridge requires broker connection verification.",
            "required_owner_input": "Owner-approved broker connection packet and owner review.",
            "required_external_evidence": "Broker readiness evidence from dedicated gate packet.",
            "safe_repo_work_completed": "Live exception contract defines broker connection gate dependency.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "validator_to_confirm_gate_closed": "Live exception contract checks broker_connection_gate status in evidence packet.",
            "continuation_after_gate": "Prepare live exception bridge handoff after proof.",
        },
        {
            "gate_name": "credential_gate",
            "blocked_capability": "Live credentials cannot be loaded in this packet.",
            "why_gate_blocks_end_to_end_completion": "No credential gate means live operations are not safe.",
            "required_owner_input": "Owner accepts credential vault review and policy control.",
            "required_external_evidence": "Credential gate handoff artifact from external packet.",
            "safe_repo_work_completed": "All external authorization flags are false.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "validator_to_confirm_gate_closed": "Live exception contract remains not-authorized until external proof arrives.",
            "continuation_after_gate": "Cross into live exception packet after proof.",
        },
        {
            "gate_name": "supervised_demo_execution_gate",
            "blocked_capability": "Flow 2 cannot run without supervised demo execution.",
            "why_gate_blocks_end_to_end_completion": "Evidence-based promotion needs supervised evidence first.",
            "required_owner_input": "Owner attestation and supervision packet.",
            "required_external_evidence": "Supervised execution handoff artifact.",
            "safe_repo_work_completed": "Flow 2 contract and contract outputs are prepared.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 2 output contains evidence_bundle.",
            "continuation_after_gate": "Run Flow 2 handoff and move to candidate loop.",
        },
        {
            "gate_name": "trade_evidence_capture_gate",
            "blocked_capability": "No trade state evidence without trade packet execution.",
            "why_gate_blocks_end_to_end_completion": "Flow 3 classification requires trade evidence.",
            "required_owner_input": "Owner confirms evidence handoff readiness.",
            "required_external_evidence": "TP/SL, realized P/L, and trade state records.",
            "safe_repo_work_completed": "Flow 2 required outputs include evidence bundle and next_flow_handoff.",
            "next_packet_to_cross_gate": "AIOS_FOREX_FLOW_2",
            "validator_to_confirm_gate_closed": "Flow 2 contract lists evidence_bundle output.",
            "continuation_after_gate": "Generate countdown and classification state updates.",
        },
        {
            "gate_name": "realized_pl_capture_gate",
            "blocked_capability": "No realized P/L proof is available in this packet.",
            "why_gate_blocks_end_to_end_completion": "Profit loop readiness depends on closed trade P/L data.",
            "required_owner_input": "Owner confirms closed trade evidence and no duplicate order guard.",
            "required_external_evidence": "Close-result output from trusted read-only evidence packet.",
            "safe_repo_work_completed": "Realized PL capture contract included in Flow 2 dependencies.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 3 payload contains countdown_progress_update_contract.",
            "continuation_after_gate": "Flow 3 candidate and readiness contracts can proceed.",
        },
        {
            "gate_name": "profit_countdown_update_gate",
            "blocked_capability": "Countdown cannot update without post-trade evidence.",
            "why_gate_blocks_end_to_end_completion": "Progress controls need periodic post-trade updates.",
            "required_owner_input": "Owner review on no-runaway-exposure and duplicate checks.",
            "required_external_evidence": "Post-trade evidence bundle after Flow 2 run.",
            "safe_repo_work_completed": "Dependency output includes post_trade_countdown_update_contract.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 2 outputs include countdown_update.",
            "continuation_after_gate": "Flow 3 reads countdown_progress updates.",
        },
        {
            "gate_name": "flow3_candidate_selection_gate",
            "blocked_capability": "Candidate quality cannot update without score evidence.",
            "why_gate_blocks_end_to_end_completion": "Flow 3 result_classification depends on candidate scoring.",
            "required_owner_input": "Owner accepts candidate review handoff.",
            "required_external_evidence": "Flow 2 evidence bundle with candidate score inputs.",
            "safe_repo_work_completed": "Flow 3 outputs include candidate_update and next_candidate.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 3 contract validator reports next_candidate output.",
            "continuation_after_gate": "Prepare runtime and vacation readiness checks.",
        },
        {
            "gate_name": "live_exception_gate",
            "blocked_capability": "Live exception is an explicit external bridge.",
            "why_gate_blocks_end_to_end_completion": "No live capital execution without this bridge.",
            "required_owner_input": "Owner approves live exception checklist and governance packet.",
            "required_external_evidence": "Real-money gate evidence bundle.",
            "safe_repo_work_completed": "Live exception contract is prepared with false live authorization fields.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "validator_to_confirm_gate_closed": "Live exception bridge status moves to real_money_readiness_bridge with proof.",
            "continuation_after_gate": "Owner and policy review before live exception handoff.",
        },
        {
            "gate_name": "real_money_gate",
            "blocked_capability": "Real money readiness is not authorized by this packet.",
            "why_gate_blocks_end_to_end_completion": "Targeted progress cannot claim real-money state without evidence.",
            "required_owner_input": "Owner approves capital transition criteria.",
            "required_external_evidence": "Evidence board and policy-ready packet.",
            "safe_repo_work_completed": "All external authorization flags are false.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "validator_to_confirm_gate_closed": "Live exception contract real_money_authorized_by_this_contract remains false.",
            "continuation_after_gate": "Proceed only after proof packet and owner sign-off.",
        },
        {
            "gate_name": "runtime_supervisor_gate",
            "blocked_capability": "22h/6d runtime readiness requires external supervisor proof.",
            "why_gate_blocks_end_to_end_completion": "Objective execution state is target-defined only.",
            "required_owner_input": "Owner confirms runtime controls and stop policy.",
            "required_external_evidence": "Runtime supervisor verification evidence.",
            "safe_repo_work_completed": "Flow 3 includes runtime_readiness_status output.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 3 outputs runtime_readiness_status.",
            "continuation_after_gate": "Proceed with readiness handoff.",
        },
        {
            "gate_name": "sos_alert_gate",
            "blocked_capability": "SOS contract requires escalation evidence.",
            "why_gate_blocks_end_to_end_completion": "Kill-switch escalation cannot be proven without SOS evidence.",
            "required_owner_input": "Owner review of pause/resume and SOS policy.",
            "required_external_evidence": "SOS escalation evidence and pause/resume handoff.",
            "safe_repo_work_completed": "sos_alert_contract_status is set to REQUIRED_GATE_PENDING.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 3 and runtime gate include sos readiness checks.",
            "continuation_after_gate": "Continue to candidate and runtime readiness.",
        },
        {
            "gate_name": "vacation_mode_gate",
            "blocked_capability": "Vacation-mode activation is a target state only.",
            "why_gate_blocks_end_to_end_completion": "This packet cannot activate vacation mode.",
            "required_owner_input": "Owner confirms vacation mode target intent and controls.",
            "required_external_evidence": "Vacation mode readiness packet evidence.",
            "safe_repo_work_completed": "vacation_mode_status set to TARGET_DEFINED_GATE_PENDING.",
            "next_packet_to_cross_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "validator_to_confirm_gate_closed": "Flow 3 outputs vacation_mode_readiness_status.",
            "continuation_after_gate": "Progress to readiness gate and bridge ledger.",
        },
        {
            "gate_name": "publish_clean_merge_gate",
            "blocked_capability": "Hosting and merge evidence has not run.",
            "why_gate_blocks_end_to_end_completion": "Packet cannot be considered landed without host validation.",
            "required_owner_input": "Owner runs validator and publish scripts.",
            "required_external_evidence": "VALIDATION_PASSED and PUBLISH_COMPLETE_CLEAN outputs.",
            "safe_repo_work_completed": "validate and publish scripts are written in script path.",
            "next_packet_to_cross_gate": "owner_publish_ready",
            "validator_to_confirm_gate_closed": "publish script output indicates clean merge handoff.",
            "continuation_after_gate": "Move to next report queue entry after merge.",
        },
    ]


def build_flow2_contract(result: dict) -> dict:
    return {
        "flow_id": FLOW_2,
        "objective": "capture supervised demo evidence and update countdown",
        "required_inputs": [
            "Flow 1 output",
            "owner-supervised demo authorization",
            "broker/demo snapshot",
            "trade state evidence",
            "TP/SL state",
            "realized P/L",
        ],
        "outputs": [
            "evidence_bundle",
            "countdown_update",
            "duplicate_order_status",
            "runaway_exposure_status",
            "next_flow_handoff",
        ],
        "external_authority_required": True,
        "order_execution_authorized_by_this_contract": False,
        "contract_status": result["flow2_contract_status"],
    }


def build_flow3_contract(result: dict) -> dict:
    return {
        "flow_id": FLOW_3,
        "objective": "classify result, update candidate quality, and prepare promotion gates",
        "required_inputs": [
            "Flow 2 evidence bundle",
            "closed trade result",
            "countdown update",
            "candidate score inputs",
        ],
        "outputs": [
            "result_classification",
            "candidate_update",
            "next_candidate",
            "live_week_readiness_status",
            "runtime_readiness_status",
            "vacation_mode_readiness_status",
        ],
        "live_trading_authorized_by_this_contract": False,
        "external_authority_required": True,
        "contract_status": result["flow3_contract_status"],
    }


def build_live_exception_contract(result: dict) -> dict:
    return {
        "flow_id": FLOW_4,
        "objective": "define real-money activation requirements",
        "required_inputs": [
            "explicit owner approval",
            "broker connection gate",
            "credential gate",
            "risk gate",
            "evidence gate",
            "live exception checklist",
        ],
        "owner_live_capital_intent_usd": result["owner_live_capital_intent_usd"],
        "target_return_band": result["target_return_band"],
        "live_authorized_by_this_contract": False,
        "real_money_authorized_by_this_contract": False,
        "contract_status": result["live_exception_contract_status"],
    }


def _authorization_flags() -> Dict[str, bool]:
    return {
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "demo_order_placement_authorized": False,
        "live_trading_authorized": False,
        "execution_command_authorized": False,
        "runtime_22h6d_activated": False,
        "vacation_mode_activated": False,
        "autonomous_trading_authorized": False,
        "money_movement_authorized": False,
        "broker_connection_authorized": False,
        "order_submission_authorized": False,
    }


def _all_acceptances_true(owner_input: dict) -> bool:
    for name in REQUIRED_ACCEPTANCE_FIELDS:
        if not _to_bool(owner_input.get(name), False):
            return False
    return True


def _build_default_result() -> dict:
    result = {
        "overnight_contract_status": "OVERNIGHT_CONTRACT_BLOCKED_OWNER_INPUT_REQUIRED",
        "overnight_contract_mode": "PAUSE_READY",
        "anchor_status": "FLOW1_PR_1194_MERGED",
        "owner_live_capital_intent_usd": 1000,
        "requested_max_open_positions": 4,
        "requested_quantity_scale": 4.0,
        "target_return_band": "100_TO_120_PERCENT",
        "target_return_claim_status": "TARGET_NOT_YET_VERIFIED",
        "runtime_objective": "22_HOURS_PER_DAY_6_DAYS_PER_WEEK",
        "vacation_mode_status": "TARGET_DEFINED_GATE_PENDING",
        "sos_alert_contract_status": "REQUIRED_GATE_PENDING",
        "repo_safe_work_status": "READY_TO_CONTINUE",
        "external_trading_authority_status": "BLOCKED",
        "flow2_contract_status": "PREPARED",
        "flow3_contract_status": "PREPARED",
        "live_exception_contract_status": "PREPARED_NOT_AUTHORIZED",
        "next_required_packet": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
        "next_required_flow": "FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE",
        "publish_status": "NOT_READY_VALIDATION_REQUIRED",
        "owner_attestation": False,
        "overnight_action": None,
        "input_validation_status": "OWNER_INPUT_REQUIRED",
    }
    result.update(_authorization_flags())
    result["dependency_order"] = build_dependency_order()
    result["external_gate_registry"] = build_external_gate_registry()
    result["flow2_contract"] = build_flow2_contract(result)
    result["flow3_contract"] = build_flow3_contract(result)
    result["live_exception_contract"] = build_live_exception_contract(result)
    result["continuation_ledger"] = build_continuation_ledger(result)
    return result


def build_continuation_ledger(result: dict) -> list[dict]:
    ledger = []
    status = result["overnight_contract_status"]
    if status == "OVERNIGHT_CONTRACT_BLOCKED_OWNER_INPUT_REQUIRED":
        ledger.append(
            {
                "step": 1,
                "action": "collect_owner_input",
                "next_required_packet": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            }
        )
    if status == "OVERNIGHT_CONTRACT_READY_TO_ENFORCE_FLOW2":
        ledger.append(
            {
                "step": 1,
                "action": "enforce_flow2_ready",
                "next_required_packet": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            }
        )
    if status == "OVERNIGHT_CONTRACT_EXTERNAL_GATE_BRIDGES_READY":
        ledger.append(
            {
                "step": 1,
                "action": "cross_external_gates",
                "next_required_packet": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            }
        )
    if status in {"OVERNIGHT_CONTRACT_PAUSED_BY_OWNER", "OVERNIGHT_CONTRACT_STOPPED_BY_OWNER"}:
        ledger.append(
            {
                "step": 99,
                "action": "await_owner_release",
                "next_required_packet": "owner_decision",
            }
        )

    ledger.append(
        {
            "step": 2,
            "action": "prepare_flow3_packet",
            "next_required_packet": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
        }
    )
    ledger.append(
        {
            "step": 3,
            "action": "prepare_live_exception_bridge",
            "next_required_packet": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
        }
    )
    return ledger


def evaluate_forex_overnight_end_to_end_contract(owner_input: dict | None = None) -> dict:
    result = _build_default_result()

    if owner_input is None:
        return result
    if not isinstance(owner_input, dict):
        result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_INVALID_INPUT_TYPE"
        result["overnight_contract_mode"] = "BLOCKED"
        result["input_validation_status"] = "INVALID_INPUT_TYPE"
        return result

    forbidden = FORBIDDEN_OWNER_FIELDS.intersection(set(owner_input.keys()))
    if forbidden:
        result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_FORBIDDEN_FIELD_PRESENT"
        result["overnight_contract_mode"] = "BLOCKED"
        result["input_validation_status"] = "FORBIDDEN_FIELD_PRESENT"
        result["input_notes"] = "FORBIDDEN_FIELDS: " + ",".join(sorted(forbidden))
        return result

    action = str(owner_input.get("overnight_action", "PAUSE")).upper().strip()
    result["overnight_action"] = action
    result["owner_attestation"] = _to_bool(owner_input.get("owner_attestation", False))

    for name in REQUIRED_ACCEPTANCE_FIELDS:
        result[name] = _to_bool(owner_input.get(name), False)

    if action == "PAUSE":
        result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_PAUSED_BY_OWNER"
        result["overnight_contract_mode"] = "PAUSED"
        result["publish_status"] = "NOT_READY_PAUSED"
        result["input_validation_status"] = "OWNER_PAUSED"
        result["continuation_ledger"] = build_continuation_ledger(result)
        return result

    if action == "STOP":
        result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_STOPPED_BY_OWNER"
        result["overnight_contract_mode"] = "STOPPED"
        result["publish_status"] = "NOT_READY_STOPPED"
        result["input_validation_status"] = "OWNER_STOP"
        result["continuation_ledger"] = build_continuation_ledger(result)
        return result

    if action == "BRIDGE":
        result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_EXTERNAL_GATE_BRIDGES_READY"
        result["overnight_contract_mode"] = "BRIDGE_READY"
        result["publish_status"] = "NOT_READY_BRIDGES_PENDING"
        result["input_validation_status"] = "EXTERNAL_GATE_BRIDGES_REQUIRED"
        result["continuation_ledger"] = build_continuation_ledger(result)
        return result

    if action == "ENFORCE":
        if _all_acceptances_true(owner_input) and result["owner_attestation"]:
            result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_READY_TO_ENFORCE_FLOW2"
            result["overnight_contract_mode"] = "ENFORCE_READY"
            result["publish_status"] = "READY_AFTER_HOST_VALIDATION"
            result["input_validation_status"] = "ENFORCE_ACCEPTED"
        else:
            result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_ENFORCE_NOT_READY"
            result["overnight_contract_mode"] = "PAUSE_READY"
            result["input_validation_status"] = "ENFORCE_ACCEPTANCE_MISSING"
        result["continuation_ledger"] = build_continuation_ledger(result)
        return result

    if action == "CONTINUE":
        if _all_acceptances_true(owner_input) and result["owner_attestation"]:
            result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_CONTINUE_READY"
            result["overnight_contract_mode"] = "CONTINUE_READY"
            result["input_validation_status"] = "CONTINUE_ACCEPTED"
            result["publish_status"] = "NOT_READY_VALIDATION_REQUIRED"
        else:
            result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_BLOCKED_OWNER_INPUT_REQUIRED"
            result["overnight_contract_mode"] = "PAUSE_READY"
            result["input_validation_status"] = "CONTINUE_MISSING_ACCEPTANCE"
        result["continuation_ledger"] = build_continuation_ledger(result)
        return result

    result["overnight_contract_status"] = "OVERNIGHT_CONTRACT_INVALID_ACTION"
    result["overnight_contract_mode"] = "BLOCKED"
    result["input_validation_status"] = "INVALID_ACTION"
    result["continuation_ledger"] = build_continuation_ledger(result)
    return result


def render_owner_report(result: dict) -> str:
    dependencies = "\n".join(
        f"- {item['flow_id']}" for item in result["dependency_order"]
    )
    return (
        "# AIOS Forex Overnight End-to-End Repo-Safe Execution Contract V1\n\n"
        "Flow 1 PR #1194 is the current anchor.\n\n"
        f"overnight_contract_status: {result['overnight_contract_status']}\n"
        f"overnight_contract_mode: {result['overnight_contract_mode']}\n"
        f"anchor_status: {result['anchor_status']}\n"
        f"target_return_band: {result['target_return_band']}\n"
        f"runtime_objective: {result['runtime_objective']}\n"
        "runtime_objective is a target and not active state.\n"
        f"vacation_mode_status: {result['vacation_mode_status']}\n"
        f"sos_alert_contract_status: {result['sos_alert_contract_status']}\n\n"
        "Dependency order:\n"
        f"{dependencies}\n\n"
        f"flow2_contract_status: {result['flow2_contract_status']}\n"
        f"flow3_contract_status: {result['flow3_contract_status']}\n"
        f"live_exception_contract_status: {result['live_exception_contract_status']}\n\n"
        f"next_required_flow: {result['next_required_flow']}\n"
        f"next_required_packet: {result['next_required_packet']}\n\n"
        "This packet builds Flow 2 evidence capture scope, Flow 3 profit loop scope, "
        "and live-exception bridge scope in a repo-safe way.\n"
        "Live action and live money movement remain gated by external bridges.\n"
        "Flow 2 captures evidence. Flow 3 updates candidate gates. Live exception remains separate.\n"
        "Real-money trading is not authorized by this packet.\n"
        "100–120% is target band, not verified proof.\n"
        "22h/6d is runtime objective, not active state.\n"
        "vacation mode is target state, not active state.\n\n"
        f"overnight_contract_sentence: AIOS Forex overnight end-to-end repo-safe execution contract is established locally: "
        "Flow 1 PR #1194 is the anchor, Flow 2 supervised demo evidence capture, Flow 3 profit loop gating, "
        "live exception bridging, real-money readiness bridging, 100–120% target tracking, requested 4-position capacity, "
        "22h/6d runtime objective, vacation-mode target, and SOS escalation are dependency-ordered for continuation while broker/API access, "
        "credentials, order submission, live trading, autonomous operation, and money movement remain separately gated.\n"
    )


def render_next_action_queue(result: dict) -> str:
    actions = "\n".join(
        f"- step {entry['step']}: {entry['action']} -> {entry['next_required_packet']}"
        for entry in result["continuation_ledger"]
    )
    return (
        "# AIOS Forex Overnight End-to-End Next Action Queue V1\n\n"
        "Repo-safe execution continues by dependency order.\n\n"
        f"{actions}\n\n"
        f"overnight_contract_status: {result['overnight_contract_status']}\n"
        f"overnight_contract_mode: {result['overnight_contract_mode']}\n"
        f"next_required_flow: {result['next_required_flow']}\n"
        "Flow 2 must complete evidence bridge inputs before Flow 3 candidate checks.\n"
        "Live exception bridge remains a separate packet with external gates.\n"
    )


def render_continuation_ledger(result: dict) -> str:
    rows = "\n".join(
        f"- {entry['step']}: {entry['action']} -> {entry['next_required_packet']}"
        for entry in result["continuation_ledger"]
    )
    return "# AIOS Forex Overnight Continuation Ledger V1\n\n" + rows + "\n"


def render_external_gate_registry(result: dict) -> str:
    text = ["# AIOS Forex External Gate Registry V1", ""]
    for item in result["external_gate_registry"]:
        text.extend(
            [
                f"## {item['gate_name']}",
                f"blocked_capability: {item['blocked_capability']}",
                f"why_gate_blocks_end_to_end_completion: {item['why_gate_blocks_end_to_end_completion']}",
                f"required_owner_input: {item['required_owner_input']}",
                f"required_external_evidence: {item['required_external_evidence']}",
                f"safe_repo_work_completed: {item['safe_repo_work_completed']}",
                f"next_packet_to_cross_gate: {item['next_packet_to_cross_gate']}",
                f"validator_to_confirm_gate_closed: {item['validator_to_confirm_gate_closed']}",
                f"continuation_after_gate: {item['continuation_after_gate']}",
                "",
            ]
        )
    return "\n".join(text)


def render_next_packet_prompt(packet_name: str, result: dict) -> str:
    return (
        "CODEX-ONLY PROMPT\n\n"
        "AI_OS EXECUTION TOKEN\nAI_OS BOOTSTRAP REQUIRED\n\n"
        f"CONTRACT TITLE\n{packet_name}\n\n"
        "IDENTITY MARKER\n"
        "Project: AI_OS\n"
        "Repository: ai-rtony91/Ai_Os\n"
        "Worktree: C:/Dev/Ai.Os\n"
        "Branch: main\n"
        "Supervisor identity: ChatGPT planning supervisor\n"
        "Worker identity: Codex Forex overnight continuation executor\n"
        "Packet ID: AIOS-FOREX-NIGHTLY-OVER-NEXT-PACKET\n"
        "Mode: LOCAL_APPLY\n"
        "Zone: FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION\n"
        "Lane: lane/forex-overnight-end-to-end-repo-safe-execution-contract-v1\n\n"
        "CORE OBJECTIVE\n"
        "Execute the next bound packet using the generated overnight contract state and dependency order.\n\n"
        f"CURRENT VERIFIED ANCHOR\nFlow 1 PR #1194 merged.\n\n"
        f"NEXT_REQUIRED_FLOW\n{result['next_required_flow']}\n"
        "STOP POINT\nHOST_VALIDATION_REQUIRED\n"
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def generate_artifacts(owner_input: dict | None = None) -> dict:
    result = evaluate_forex_overnight_end_to_end_contract(owner_input)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    result["dependency_order"] = build_dependency_order()
    result["external_gate_registry"] = build_external_gate_registry()
    result["flow2_contract"] = build_flow2_contract(result)
    result["flow3_contract"] = build_flow3_contract(result)
    result["live_exception_contract"] = build_live_exception_contract(result)
    result["continuation_ledger"] = build_continuation_ledger(result)

    JSON_REPORT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    _write_text(DOC_CONTRACT_PATH, render_owner_report(result))
    _write_text(REPORT_PATH, render_owner_report(result))
    _write_text(QUEUE_PATH, render_next_action_queue(result))
    _write_text(CONTINUATION_PATH, render_continuation_ledger(result))
    _write_text(GATE_REGISTRY_PATH, render_external_gate_registry(result))
    _write_text(
        FLOW2_CONTRACT_PATH,
        json.dumps(result["flow2_contract"], indent=2, sort_keys=True),
    )
    _write_text(
        FLOW3_CONTRACT_PATH,
        json.dumps(result["flow3_contract"], indent=2, sort_keys=True),
    )
    _write_text(
        LIVE_EXCEPTION_CONTRACT_PATH,
        json.dumps(result["live_exception_contract"], indent=2, sort_keys=True),
    )
    _write_text(NEXT_FLOW2_PACKET_PATH, render_next_packet_prompt("AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1", result))
    _write_text(NEXT_FLOW3_PACKET_PATH, render_next_packet_prompt("AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1", result))
    _write_text(NEXT_EXCEPTION_PACKET_PATH, render_next_packet_prompt("AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1", result))
    return result


if __name__ == "__main__":
    generate_artifacts()
