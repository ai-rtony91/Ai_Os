"""Final deterministic evidence bundle for AIOS Forex real evidence intake."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.evidence_milestone_selector_v1 import (
    EVIDENCE_MILESTONE_COMPLETE,
    result_to_jsonable_dict as evidence_milestone_result_to_jsonable_dict,
    select_evidence_milestone,
)
from automation.forex_engine.final_closure_evidence_v1 import (
    FINAL_CLOSURE_BLOCKED,
    FINAL_CLOSURE_REVIEW_READY,
    evaluate_final_closure_evidence,
    result_to_jsonable_dict as final_closure_result_to_jsonable_dict,
)
from automation.forex_engine.forex_final_readiness_checker_v1 import (
    FOREX_FINAL_READINESS_BLOCKED,
    FOREX_FINAL_READINESS_REVIEW_READY,
)
from automation.forex_engine.forex_owner_decision_brief_v1 import (
    OWNER_DECISION_BRIEF_BLOCKED,
    OWNER_DECISION_BRIEF_REVIEW_READY,
)
from automation.forex_engine.observation_evidence_intake_v1 import (
    SUPERVISED_OBSERVATION_READY,
    intake_observation_evidence,
)
from automation.forex_engine.persistent_profitability_evidence_v1 import (
    PERSISTENT_PROFITABILITY_READY,
)
from automation.forex_engine.profitability_evidence_intake_v1 import intake_profitability_evidence
from automation.forex_engine.replay_evidence_intake_v1 import intake_replay_evidence
from automation.forex_engine.replay_proof_evidence_v1 import REPLAY_PROOF_READY
from automation.forex_engine.walk_forward_evidence_intake_v1 import intake_walk_forward_evidence
from automation.forex_engine.walk_forward_oos_evidence_v1 import WALK_FORWARD_OOS_READY


FINAL_EVIDENCE_BUNDLE_VERSION = "final_evidence_bundle_v1"
FINAL_EVIDENCE_BUNDLE_REVIEW_READY = "FINAL_EVIDENCE_BUNDLE_REVIEW_READY"
FINAL_EVIDENCE_BUNDLE_BLOCKED = "FINAL_EVIDENCE_BUNDLE_BLOCKED"
FINAL_EVIDENCE_CHAIN_REVIEW_READY = "FINAL_EVIDENCE_CHAIN_FINAL_CLOSURE_REVIEW_READY"
FINAL_EVIDENCE_CHAIN_BLOCKED = "FINAL_EVIDENCE_CHAIN_BLOCKED"
DEFAULT_REPORT_ROOT = Path("Reports/forex_delivery")
DEFAULT_REPORT_PATH = DEFAULT_REPORT_ROOT / "AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md"
EVIDENCE_CHAIN_STAGE_ORDER = (
    "replay_evidence",
    "replay_proof",
    "walk_forward_evidence",
    "walk_forward_oos_evidence",
    "profitability_intake",
    "persistent_profitability_evidence",
    "observation_intake",
    "supervised_observation_22h6d_evidence",
    "evidence_milestone_selector",
    "final_evidence_bundle",
    "final_closure_evidence",
)
OWNER_REVIEW_REPORTS = (
    "AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_V1.md",
    "AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_EPIC_REPORT_V1.md",
    "AIOS_FOREX_SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_V1.md",
    "AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_EPIC_REPORT_V1.md",
)
VALIDATOR_EVIDENCE_REPORTS = (
    "AIOS_FOREX_FINAL_BUNDLE_REPAIR_V1_REPORT.md",
    "AIOS_FOREX_COMPLETION_FULL_RERUN_VALIDATION_V1_REPORT.md",
    "AIOS_FOREX_CONTINUOUS_EVIDENCE_ADVANCEMENT_V1_REPORT.md",
)
BROKER_READONLY_REPORTS = (
    "AIOS_FOREX_READ_ONLY_EVIDENCE_APPROVAL_AND_RECONCILIATION_DRY_RUN_V1.md",
    "AIOS_FOREX_TRADING_HISTORY_WRITEBACK_VERIFICATION_DRY_RUN_V1.md",
    "AIOS_FOREX_READONLY_BROKER_SANITIZED_EVIDENCE_CLOSURE_V1.md",
)
OWNER_REVIEW_DISCOVERY_PATTERN = re.compile(
    r"(?i)(READY_FOR_OWNER_REVIEW|Anthony may review|OWNER_GONOGO_READY_FOR_REVIEW|"
    r"owner decision|owner review)"
)
VALIDATOR_DISCOVERY_PATTERN = re.compile(
    r"(?i)(VALIDATION PASSED|VALIDATORS? PASSED|VALIDATORS? RUN|py_compile|pytest|git diff --check)"
)
BROKER_READONLY_DISCOVERY_PATTERN = re.compile(
    r"(?i)(READ_ONLY_EVIDENCE|READ[-_ ]ONLY.*BROKER|source_type:|broker_account_reachable|"
    r"broker_reachable|trading_history_writeback_verified|read-only preflight)"
)

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "broker_connection_allowed": False,
    "broker_api_call_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "money_movement_allowed": False,
    "all_money_control_allowed": False,
    "bank_movement_allowed": False,
    "withdrawal_allowed": False,
    "deposit_allowed": False,
    "compounding_allowed": False,
    "compounding_execution_allowed": False,
    "autonomous_compounding_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

SOURCE_UNSAFE_FIELD_PATTERN = re.compile(
    r"(?im)^\s*-?\s*(?P<key>"
    r"broker_execution_allowed|broker_connection_allowed|broker_api_call_allowed|"
    r"live_trading_allowed|order_submission_allowed|"
    r"credential_access_allowed|account_access_allowed|dashboard_execution_authority|"
    r"owner_approval_created|execution_allowed|trade_allowed|broker_access_allowed|"
    r"money_movement_allowed|all_money_control_allowed|bank_movement_allowed|"
    r"withdrawal_allowed|deposit_allowed|compounding_allowed|"
    r"compounding_execution_allowed|autonomous_compounding_allowed|"
    r"scheduler_allowed|daemon_allowed|webhook_allowed|real_money_allowed|"
    r"vacation_mode_execution_allowed|api_key|access_token|"
    r"refresh_token|authorization|bearer|password|secret|credential|account_id|"
    r"accountid|account_number|account_reference|broker_order_id|raw_order_id|"
    r"raw_transaction_id|raw_payload|order_payload"
    r")\s*:\s*`?(?P<value>[^`\n]+)`?\s*$"
)


def build_final_evidence_bundle(report_root: str | Path = DEFAULT_REPORT_ROOT) -> dict[str, Any]:
    """Build the final evidence bundle from deterministic local intakes."""

    root = Path(report_root)
    replay = intake_replay_evidence(root)
    walk_forward = intake_walk_forward_evidence(root)
    profitability = intake_profitability_evidence(root)
    observation = intake_observation_evidence(root)
    intakes = {
        "replay": replay,
        "walk_forward": walk_forward,
        "profitability": profitability,
        "observation": observation,
    }

    auxiliary_evidence = _collect_final_readiness_auxiliary_evidence(root)
    final_readiness = _build_final_readiness_evidence(intakes, auxiliary_evidence)
    owner_brief = _build_owner_brief_evidence(final_readiness, intakes)
    closure_inputs = {
        "replay_evidence": _closure_input(replay),
        "walk_forward_oos_evidence": _closure_input(walk_forward),
        "persistent_profitability_evidence": _closure_input(profitability),
        "supervised_observation_22h6d_evidence": _closure_input(observation),
        "final_readiness_evidence": final_readiness,
        "owner_brief_evidence": owner_brief,
    }
    closure_result = final_closure_result_to_jsonable_dict(
        evaluate_final_closure_evidence(closure_inputs)
    )
    milestone_result = evidence_milestone_result_to_jsonable_dict(
        select_evidence_milestone(
            {
                "replay_proof_evidence": closure_inputs["replay_evidence"],
                "walk_forward_oos_evidence": closure_inputs["walk_forward_oos_evidence"],
                "persistent_profitability_evidence": closure_inputs[
                    "persistent_profitability_evidence"
                ],
                "supervised_observation_22h6d_evidence": closure_inputs[
                    "supervised_observation_22h6d_evidence"
                ],
                "final_closure_evidence": closure_result,
            }
        )
    )
    bundle_status = (
        FINAL_EVIDENCE_BUNDLE_REVIEW_READY
        if closure_result.get("final_closure_status") == FINAL_CLOSURE_REVIEW_READY
        and milestone_result.get("status") == EVIDENCE_MILESTONE_COMPLETE
        else FINAL_EVIDENCE_BUNDLE_BLOCKED
    )
    remaining = _remaining_evidence(
        intakes,
        final_readiness,
        owner_brief,
        closure_result,
        milestone_result,
    )
    return {
        "bundle_version": FINAL_EVIDENCE_BUNDLE_VERSION,
        "status": bundle_status,
        "program_status": "PROGRAM_COMPLETE" if bundle_status == FINAL_EVIDENCE_BUNDLE_REVIEW_READY else "CONTINUE_READY",
        "evidence_chain": _evidence_chain(
            intakes,
            milestone_result,
            bundle_status,
            closure_result,
            final_readiness,
            owner_brief,
        ),
        "intakes": intakes,
        "final_readiness_auxiliary_evidence": auxiliary_evidence,
        "closure_inputs": closure_inputs,
        "evidence_milestone_result": milestone_result,
        "final_closure_result": closure_result,
        "remaining_evidence": remaining,
        "next_unfinished_milestone": _next_unfinished_milestone(remaining),
        "next_safe_packet": _next_safe_packet(remaining),
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def build_replay_walkforward_profitability_evidence_chain(
    report_root: str | Path = DEFAULT_REPORT_ROOT,
) -> dict[str, Any]:
    """Run the deterministic replay-to-final-closure evidence chain locally."""

    bundle = build_final_evidence_bundle(report_root)
    intakes = dict(bundle.get("intakes", {}))
    closure_inputs = dict(bundle.get("closure_inputs", {}))
    milestone_inputs = {
        "replay_proof_evidence": dict(closure_inputs.get("replay_evidence", {})),
        "walk_forward_oos_evidence": dict(closure_inputs.get("walk_forward_oos_evidence", {})),
        "persistent_profitability_evidence": dict(
            closure_inputs.get("persistent_profitability_evidence", {})
        ),
        "supervised_observation_22h6d_evidence": dict(
            closure_inputs.get("supervised_observation_22h6d_evidence", {})
        ),
    }
    milestone_result = select_evidence_milestone(milestone_inputs)
    source_safety_blockers = _source_safety_blockers(report_root, intakes)

    final_closure = dict(bundle.get("final_closure_result", {}))
    if source_safety_blockers:
        final_closure = _blocked_final_closure(final_closure, source_safety_blockers)
        bundle = dict(bundle)
        bundle["status"] = FINAL_EVIDENCE_BUNDLE_BLOCKED
        bundle["program_status"] = "CONTINUE_READY"
        bundle["final_closure_result"] = final_closure
        bundle["remaining_evidence"] = _dedupe(
            list(bundle.get("remaining_evidence", []))
            + [f"source_safety: {item}" for item in source_safety_blockers]
        )
        bundle["next_unfinished_milestone"] = _next_unfinished_milestone(
            list(bundle.get("remaining_evidence", []))
        )
        bundle["next_safe_packet"] = _next_safe_packet(list(bundle.get("remaining_evidence", [])))

    final_milestone_result = select_evidence_milestone(
        {**milestone_inputs, "final_closure_evidence": final_closure}
    )
    stage_results = {
        "replay_evidence": intakes.get("replay", {}),
        "replay_proof": milestone_inputs["replay_proof_evidence"],
        "walk_forward_evidence": intakes.get("walk_forward", {}),
        "walk_forward_oos_evidence": milestone_inputs["walk_forward_oos_evidence"],
        "profitability_intake": intakes.get("profitability", {}),
        "persistent_profitability_evidence": milestone_inputs["persistent_profitability_evidence"],
        "observation_intake": intakes.get("observation", {}),
        "supervised_observation_22h6d_evidence": milestone_inputs[
            "supervised_observation_22h6d_evidence"
        ],
        "evidence_milestone_selector": milestone_result,
        "final_evidence_bundle": bundle,
        "final_closure_evidence": final_closure,
    }
    chain_ready = final_closure.get("final_closure_status") == FINAL_CLOSURE_REVIEW_READY
    status = FINAL_EVIDENCE_CHAIN_REVIEW_READY if chain_ready else FINAL_EVIDENCE_CHAIN_BLOCKED
    blockers = _chain_blockers(bundle, milestone_result, final_milestone_result, final_closure)
    return {
        "chain_version": "replay_walkforward_profitability_evidence_chain_v1",
        "status": status,
        "chain_integrated_end_to_end": True,
        "deterministic_sample_only": True,
        "real_profit_proving": False,
        "canonical_entrypoint": "build_replay_walkforward_profitability_evidence_chain",
        "canonical_final_output": "final_closure_result",
        "stage_order": list(EVIDENCE_CHAIN_STAGE_ORDER),
        "stage_results": stage_results,
        "evidence_milestone_result": milestone_result,
        "final_evidence_milestone_result": final_milestone_result,
        "final_evidence_bundle": bundle,
        "final_closure_result": final_closure,
        "blockers": blockers,
        "next_safe_packet": bundle.get("next_safe_packet"),
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def write_final_evidence_report(
    bundle: Mapping[str, Any] | None = None,
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> Path:
    """Write the operator report for this packet."""

    active = dict(bundle or build_final_evidence_bundle())
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(final_evidence_bundle_to_markdown(active), encoding="utf-8")
    return path


def final_evidence_bundle_to_markdown(bundle: Mapping[str, Any]) -> str:
    intakes = dict(bundle.get("intakes", {}))
    closure = dict(bundle.get("final_closure_result", {}))
    remaining = list(bundle.get("remaining_evidence", []))
    lines = [
        "# AIOS Forex Real Evidence Intake V1 Report",
        "",
        "## SUMMARY",
        f"- bundle_status: {bundle.get('status')}",
        f"- final_closure_status: {closure.get('final_closure_status', 'UNKNOWN')}",
        "- protected permissions: false",
        "",
        "## DISCOVERED EVIDENCE",
    ]
    for name, intake in intakes.items():
        lines.append(f"- {name}: {len(intake.get('source_files', []))} source file(s)")
    auxiliary = dict(bundle.get("final_readiness_auxiliary_evidence", {}))
    for name, intake in auxiliary.items():
        lines.append(f"- {name}: {len(intake.get('source_files', []))} source file(s)")
    lines.extend(
        [
            "",
            "## EVIDENCE CHAIN",
        ]
    )
    for stage in bundle.get("evidence_chain", []):
        lines.append(f"- {stage.get('stage')}: {stage.get('status')}")
    milestone = dict(bundle.get("evidence_milestone_result", {}))
    lines.extend(
        [
            "",
            "## EVIDENCE MILESTONE",
            f"- status: {milestone.get('status', 'UNKNOWN')}",
            f"- next_evidence_milestone: {milestone.get('next_evidence_milestone', '')}",
            "",
            "## REPLAY EVIDENCE",
            _intake_line(intakes.get("replay", {})),
            "",
            "## WALK FORWARD EVIDENCE",
            _intake_line(intakes.get("walk_forward", {})),
            "",
            "## PROFITABILITY EVIDENCE",
            _intake_line(intakes.get("profitability", {})),
            "",
            "## OBSERVATION EVIDENCE",
            _intake_line(intakes.get("observation", {})),
            "",
            "## OWNER REVIEW EVIDENCE",
            _auxiliary_line(auxiliary.get("owner_review_evidence", {})),
            "",
            "## VALIDATOR EVIDENCE",
            _auxiliary_line(auxiliary.get("validator_evidence", {})),
            "",
            "## SANITIZED BROKER READONLY EVIDENCE",
            _auxiliary_line(auxiliary.get("sanitized_broker_readonly_evidence", {})),
            "",
            "## FINAL BUNDLE STATUS",
            f"- status: {bundle.get('status')}",
            f"- final_closure_blockers: {', '.join(closure.get('blockers', [])) if closure.get('blockers') else 'none'}",
            "",
            "## FILES CREATED",
            "- automation/forex_engine/replay_evidence_intake_v1.py",
            "- automation/forex_engine/walk_forward_evidence_intake_v1.py",
            "- automation/forex_engine/profitability_evidence_intake_v1.py",
            "- automation/forex_engine/observation_evidence_intake_v1.py",
            "- automation/forex_engine/final_evidence_bundle_v1.py",
            "- tests/forex_engine/test_replay_evidence_intake_v1.py",
            "- tests/forex_engine/test_walk_forward_evidence_intake_v1.py",
            "- tests/forex_engine/test_profitability_evidence_intake_v1.py",
            "- tests/forex_engine/test_observation_evidence_intake_v1.py",
            "- tests/forex_engine/test_final_evidence_bundle_v1.py",
            "- scripts/forex_delivery/run_replay_evidence_intake_v1.py",
            "- scripts/forex_delivery/run_walk_forward_evidence_intake_v1.py",
            "- scripts/forex_delivery/run_profitability_evidence_intake_v1.py",
            "- scripts/forex_delivery/run_observation_evidence_intake_v1.py",
            "- scripts/forex_delivery/run_final_evidence_bundle_v1.py",
            "- Reports/forex_delivery/AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md",
            "",
            "## FILES MODIFIED",
            "- none outside packet-created allowed files",
            "",
            "## VALIDATORS RUN",
            "- Not recorded by this generated report; run packet validators after generation.",
            "",
            "## VALIDATORS PASSED",
            "- Not recorded by this generated report; use current packet validation output.",
            "",
            "## VALIDATORS FAILED",
            "- Not recorded by this generated report; no validator result is inferred here.",
            "",
            "## REPAIRS MADE",
            "- none recorded by this evidence intake generator",
            "",
            "## REMAINING EVIDENCE",
        ]
    )
    lines.extend(f"- {item}" for item in remaining or ["none"])
    lines.extend(
        [
            "",
            "## NEXT UNFINISHED MILESTONE",
            f"- {bundle.get('next_unfinished_milestone')}",
            "",
            "## NEXT SAFE PACKET",
            f"- {bundle.get('next_safe_packet')}",
            "",
            "## COMMIT STATUS",
            "- NO COMMIT",
            "",
            "## PUSH STATUS",
            "- NO PUSH",
            "",
            "## STATUS:",
            str(bundle.get("program_status", "CONTINUE_READY")),
            "",
        ]
    )
    return "\n".join(lines)


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    if result.get("canonical_entrypoint") == "build_replay_walkforward_profitability_evidence_chain":
        final_closure = dict(result.get("final_closure_result", {}))
        return (
            "AIOS Forex Replay Walk-Forward Profitability Evidence Chain V1\n"
            f"status: {result.get('status')}\n"
            f"final_closure_status: {final_closure.get('final_closure_status')}\n"
            f"next_safe_packet: {result.get('next_safe_packet')}\n"
        )
    return (
        "AIOS Forex Final Evidence Bundle V1\n"
        f"status: {result.get('status')}\n"
        f"program_status: {result.get('program_status')}\n"
        f"next_unfinished_milestone: {result.get('next_unfinished_milestone')}\n"
        f"next_safe_packet: {result.get('next_safe_packet')}\n"
    )


def _closure_input(intake: Mapping[str, Any]) -> dict[str, Any]:
    evidence = dict(intake.get("adapter_result") or {})
    summary = dict(intake.get("normalized_summary") or {})
    if summary.get("sanitized") is True:
        evidence["sanitized"] = True
    if "evidence_age_days" in summary:
        evidence["evidence_age_days"] = summary["evidence_age_days"]
    if "max_evidence_age_days" in summary:
        evidence["max_evidence_age_days"] = summary["max_evidence_age_days"]
    return evidence


def _build_final_readiness_evidence(
    intakes: Mapping[str, Mapping[str, Any]],
    auxiliary_evidence: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    required = {
        "persistent_profitability_proof": ("profitability", PERSISTENT_PROFITABILITY_READY),
        "twenty_two_hour_six_day_observation": ("observation", SUPERVISED_OBSERVATION_READY),
        "replay_proof": ("replay", REPLAY_PROOF_READY),
        "walk_forward_proof": ("walk_forward", WALK_FORWARD_OOS_READY),
    }
    missing = [
        key
        for key, (intake_name, ready_status) in required.items()
        if intakes[intake_name].get("status") != ready_status
    ]
    for key in (
        "sanitized_broker_readonly_evidence",
        "owner_review_evidence",
        "validator_evidence",
    ):
        if auxiliary_evidence.get(key, {}).get("ready") is not True:
            missing.append(key)
    missing = _dedupe(missing)
    auxiliary_blockers = _auxiliary_blockers(auxiliary_evidence)
    status = FOREX_FINAL_READINESS_REVIEW_READY if not missing else FOREX_FINAL_READINESS_BLOCKED
    blockers = [f"missing evidence: {item}" for item in missing] + auxiliary_blockers
    return {
        "status": status,
        "final_readiness_status": status,
        "closure_blockers": blockers,
        "missing_evidence": missing,
        "stale_evidence": [],
        "sanitized": _all_sanitized(intakes),
        "source_files": _dedupe(
            [
                source
                for evidence in auxiliary_evidence.values()
                for source in evidence.get("source_files", [])
            ]
        ),
        "auxiliary_evidence": {key: dict(value) for key, value in auxiliary_evidence.items()},
        "next_safe_action": (
            "Prepare owner decision brief for review only; do not approve execution."
            if status == FOREX_FINAL_READINESS_REVIEW_READY
            else "Close final readiness blockers before owner decision review."
        ),
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _build_owner_brief_evidence(
    final_readiness: Mapping[str, Any],
    intakes: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    ready = final_readiness.get("status") == FOREX_FINAL_READINESS_REVIEW_READY
    status = OWNER_DECISION_BRIEF_REVIEW_READY if ready else OWNER_DECISION_BRIEF_BLOCKED
    blockers = [] if ready else ["final readiness is not review-ready"]
    return {
        "status": status,
        "owner_decision_brief_status": status,
        "blockers": blockers,
        "evidence_gaps": list(final_readiness.get("missing_evidence", [])),
        "owner_review_required": True,
        "sanitized": _all_sanitized(intakes),
        "next_safe_action": (
            "Anthony may review the brief; this output creates no approval or execution authority."
            if ready
            else "Close blockers and evidence gaps before owner decision review."
        ),
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _remaining_evidence(
    intakes: Mapping[str, Mapping[str, Any]],
    final_readiness: Mapping[str, Any],
    owner_brief: Mapping[str, Any],
    closure_result: Mapping[str, Any],
    milestone_result: Mapping[str, Any],
) -> list[str]:
    remaining: list[str] = []
    for name, intake in intakes.items():
        if intake.get("blockers"):
            remaining.extend(f"{name}: {item}" for item in intake.get("blockers", []))
        if intake.get("missing_fields"):
            remaining.extend(f"{name}: missing {item}" for item in intake.get("missing_fields", []))
    remaining.extend(f"final_readiness: {item}" for item in final_readiness.get("closure_blockers", []))
    remaining.extend(f"owner_brief: {item}" for item in owner_brief.get("blockers", []))
    remaining.extend(f"final_closure: {item}" for item in closure_result.get("blockers", []))
    if milestone_result.get("status") != EVIDENCE_MILESTONE_COMPLETE:
        remaining.extend(
            f"evidence_milestone: {item}" for item in milestone_result.get("blockers", [])
        )
        remaining.extend(
            f"evidence_milestone: missing {item}"
            for item in milestone_result.get("incomplete_evidence_milestones", [])
        )
    return _dedupe(remaining)


def _blocked_final_closure(
    final_closure: Mapping[str, Any],
    blockers: list[str],
) -> dict[str, Any]:
    active = dict(final_closure)
    active["status"] = FINAL_CLOSURE_BLOCKED
    active["final_closure_status"] = FINAL_CLOSURE_BLOCKED
    active["blockers"] = _dedupe(list(active.get("blockers", [])) + blockers)
    active["next_safe_action"] = "Remove unsafe evidence source fields before owner review."
    active["permissions"] = dict(PROTECTED_PERMISSION_FLAGS)
    active.update(PROTECTED_PERMISSION_FLAGS)
    return active


def _chain_blockers(
    bundle: Mapping[str, Any],
    milestone_result: Mapping[str, Any],
    final_milestone_result: Mapping[str, Any],
    final_closure: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    blockers.extend(str(item) for item in bundle.get("remaining_evidence", []) if str(item))
    blockers.extend(str(item) for item in final_closure.get("blockers", []) if str(item))
    if milestone_result.get("status") == "EVIDENCE_MILESTONE_BLOCKED":
        blockers.extend(str(item) for item in milestone_result.get("blockers", []) if str(item))
    if final_milestone_result.get("status") == "EVIDENCE_MILESTONE_BLOCKED":
        blockers.extend(str(item) for item in final_milestone_result.get("blockers", []) if str(item))
    return _dedupe(blockers)


def _source_safety_blockers(
    report_root: str | Path,
    intakes: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    root = Path(report_root)
    blockers: list[str] = []
    for intake_name, intake in intakes.items():
        for source in intake.get("source_files", []):
            path = _resolve_source_path(root, str(source))
            if path is None:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for match in SOURCE_UNSAFE_FIELD_PATTERN.finditer(text):
                key = match.group("key")
                value = match.group("value").strip()
                if _source_field_is_blocking(key, value):
                    blockers.append(f"{intake_name}:{path.name}:{key} is unsafe evidence source data")
    return _dedupe(blockers)


def _resolve_source_path(root: Path, source: str) -> Path | None:
    source_path = Path(source)
    candidates = [source_path]
    if not source_path.is_absolute():
        candidates.append(root / source_path.name)
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _source_field_is_blocking(key: str, value: str) -> bool:
    lowered_key = key.lower()
    if lowered_key in {
        "broker_execution_allowed",
        "broker_connection_allowed",
        "broker_api_call_allowed",
        "live_trading_allowed",
        "order_submission_allowed",
        "credential_access_allowed",
        "account_access_allowed",
        "dashboard_execution_authority",
        "owner_approval_created",
        "execution_allowed",
        "trade_allowed",
        "broker_access_allowed",
        "money_movement_allowed",
        "all_money_control_allowed",
        "bank_movement_allowed",
        "withdrawal_allowed",
        "deposit_allowed",
        "compounding_allowed",
        "compounding_execution_allowed",
        "autonomous_compounding_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "webhook_allowed",
        "real_money_allowed",
        "vacation_mode_execution_allowed",
    }:
        return _safe_bool(value) is True
    return True


def _evidence_chain(
    intakes: Mapping[str, Mapping[str, Any]],
    milestone_result: Mapping[str, Any],
    bundle_status: str,
    closure_result: Mapping[str, Any],
    final_readiness: Mapping[str, Any],
    owner_brief: Mapping[str, Any],
) -> list[dict[str, str]]:
    return [
        {"stage": "replay_evidence", "status": str(intakes.get("replay", {}).get("status", ""))},
        {
            "stage": "walk_forward_evidence",
            "status": str(intakes.get("walk_forward", {}).get("status", "")),
        },
        {
            "stage": "out_of_sample_evidence",
            "status": str(intakes.get("walk_forward", {}).get("status", "")),
        },
        {
            "stage": "persistent_profitability",
            "status": str(intakes.get("profitability", {}).get("status", "")),
        },
        {"stage": "evidence_milestone", "status": str(milestone_result.get("status", ""))},
        {"stage": "final_evidence_bundle", "status": bundle_status},
        {
            "stage": "closure_evidence",
            "status": str(closure_result.get("final_closure_status", "")),
        },
        {
            "stage": "readiness_evidence",
            "status": str(final_readiness.get("final_readiness_status", "")),
        },
        {
            "stage": "owner_review",
            "status": str(owner_brief.get("owner_decision_brief_status", "")),
        },
    ]


def _next_unfinished_milestone(remaining: list[str]) -> str:
    if not remaining:
        return "PROGRAM_COMPLETE"
    if any("walk_forward" in item or "OOS" in item for item in remaining):
        return "collect walk-forward and out-of-sample segment counts"
    if any("profitability" in item for item in remaining):
        return "collect persistent after-cost profitability periods"
    if any("observation" in item for item in remaining):
        return "collect real 22H/6D supervised observation evidence"
    return "close final readiness evidence gaps"


def _next_safe_packet(remaining: list[str]) -> str:
    if not remaining:
        return "No packet required; owner review can proceed without execution authority."
    return "AIOS-FOREX-COLLECT-MISSING-REAL-EVIDENCE-V1"


def _intake_line(intake: Mapping[str, Any]) -> str:
    blockers = intake.get("blockers") or []
    missing = intake.get("missing_fields") or []
    return (
        f"- status: {intake.get('status')}; "
        f"sources: {len(intake.get('source_files', []))}; "
        f"blockers: {', '.join(blockers) if blockers else 'none'}; "
        f"missing_fields: {', '.join(missing) if missing else 'none'}"
    )


def _auxiliary_line(evidence: Mapping[str, Any]) -> str:
    blockers = evidence.get("blockers") or []
    missing = evidence.get("missing_fields") or []
    return (
        f"- ready: {_bool_text(evidence.get('ready') is True)}; "
        f"sources: {len(evidence.get('source_files', []))}; "
        f"blockers: {', '.join(blockers) if blockers else 'none'}; "
        f"missing_fields: {', '.join(missing) if missing else 'none'}"
    )


def _collect_final_readiness_auxiliary_evidence(root: Path) -> dict[str, dict[str, Any]]:
    return {
        "owner_review_evidence": _owner_review_evidence(root),
        "validator_evidence": _validator_evidence(root),
        "sanitized_broker_readonly_evidence": _sanitized_broker_readonly_evidence(root),
    }


def _owner_review_evidence(root: Path) -> dict[str, Any]:
    sources: list[str] = []
    blockers: list[str] = []
    ready = False
    for path in _candidate_report_paths(root, OWNER_REVIEW_REPORTS, OWNER_REVIEW_DISCOVERY_PATTERN):
        name = path.name
        text = path.read_text(encoding="utf-8")
        sources.append(_display_path(path))
        report_ready = bool(re.search(r"(?i)READY_FOR_OWNER_REVIEW|Anthony may review", text))
        if report_ready:
            ready = True
        if re.search(r"(?i)No broker call was made|no broker action is authorized|does not authorize execution", text):
            ready = ready or False
        if not report_ready and re.search(r"(?i)Owner packet status:\s*`?[^`\n]*BLOCKED", text):
            blockers.append(f"{name}: owner review packet is blocked")
    if not ready:
        blockers.append("no owner review-ready report found")
    return {
        "ready": ready and not blockers,
        "source_files": _dedupe(sources),
        "blockers": _dedupe(blockers),
        "missing_fields": [] if ready else ["owner_review_ready_status"],
        "sanitized": True,
    }


def _validator_evidence(root: Path) -> dict[str, Any]:
    sources: list[str] = []
    blockers: list[str] = []
    validators: list[dict[str, str]] = []
    ready = False
    for path in _candidate_report_paths(root, VALIDATOR_EVIDENCE_REPORTS, VALIDATOR_DISCOVERY_PATTERN):
        name = path.name
        text = path.read_text(encoding="utf-8")
        sources.append(_display_path(path))
        if _validation_report_passed(text):
            ready = True
            validators.extend(_validator_records(text))
        elif _validation_report_failed(text):
            blockers.append(f"{name}: validation failed or did not complete")
    if not ready:
        blockers.append("no passing validator evidence report found")
    if ready and not validators:
        validators.append({"name": "repository_validation_report", "status": "PASS"})
    return {
        "ready": ready,
        "source_files": _dedupe(sources),
        "blockers": _dedupe(blockers if not ready else []),
        "missing_fields": [] if ready else ["passing_validator_records"],
        "validators": validators,
        "sanitized": True,
    }


def _sanitized_broker_readonly_evidence(root: Path) -> dict[str, Any]:
    sources: list[str] = []
    blockers: list[str] = []
    missing_fields: list[str] = []
    fields: dict[str, str] = {}
    for path in _candidate_report_paths(root, BROKER_READONLY_REPORTS, BROKER_READONLY_DISCOVERY_PATTERN):
        name = path.name
        text = path.read_text(encoding="utf-8")
        sources.append(_display_path(path))
        fields.update(_key_values(text))
        missing_fields.extend(_section_bullets(text, "Evidence Missing"))
        blockers.extend(_section_bullets(text, "Blockers Remaining"))
        if re.search(r"(?i)\bLEFT TO FINISH\b", text):
            blockers.append(f"{name}: broker-readonly evidence remains left to finish")
        if re.search(r"(?i)\bPARTIAL\b", text):
            blockers.append(f"{name}: broker-readonly evidence is partial")

    approved = _bool_first(
        fields,
        "READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW",
        "read only evidence approved for future live review",
    )
    source_type = fields.get(_key("source_type"), "") or fields.get(_key("broker_read_mode_used"), "")
    source_label = fields.get(_key("source_label"), "") or fields.get(_key("source"), "")
    broker_reachable = _bool_first(
        fields,
        "broker_account_reachable",
        "broker_reachable",
        "account details accessible",
        "account summary accessible",
    )
    positions_reconciled = _bool_first(fields, "open_positions_reconciled", "positions_reconciled")
    daily_pl = _bool_first(fields, "daily_pl_available", "pl_available")
    realized_pl = _bool_first(fields, "realized_pl_available")
    unrealized_pl = _bool_first(fields, "unrealized_pl_available")
    margin_risk = _bool_first(fields, "margin_risk_available")
    history_writeback = _bool_first(fields, "trading_history_writeback_verified")
    required_truths = {
        "broker_account_reachable": broker_reachable,
        "open_positions_reconciled": positions_reconciled,
        "daily_pl_available": daily_pl,
        "realized_pl_available": realized_pl,
        "unrealized_pl_available": unrealized_pl,
        "margin_risk_available": margin_risk,
        "trading_history_writeback_verified": history_writeback,
    }
    for key, value in required_truths.items():
        if value is not True:
            missing_fields.append(key)
    if approved is not True:
        blockers.append("read-only broker evidence is not approved for future live review")
    if "broker" not in source_type.lower() or "read" not in source_type.lower():
        missing_fields.append("broker_live_read_only_source_type")
    if not source_label or source_label.upper() == "FIXTURE_NOT_LIVE":
        missing_fields.append("sanitized_broker_source_label")

    ready = bool(sources) and approved is True and not blockers and not missing_fields
    if not sources:
        blockers.append("no sanitized broker-readonly evidence report found")
    return {
        "ready": ready,
        "source_files": _dedupe(sources),
        "blockers": _dedupe(blockers),
        "missing_fields": _dedupe(missing_fields),
        "sanitized": True,
        "observed_source_type": source_type,
        "observed_source_label": source_label,
    }


def _validation_report_passed(text: str) -> bool:
    if not re.search(r"(?i)VALIDATORS? (?:PASSED|RUN|RESULTS?)|VALIDATION PASSED", text):
        return False
    if re.search(r"(?i)(FAILED TO LAUNCH|TIMED OUT|Traceback|VALIDATION FAILED:\s*(?!\s*- None))", text):
        return False
    return bool(re.search(r"(?i)\b(?:passed|PASS)\b", text))


def _candidate_report_paths(
    root: Path,
    preferred_names: tuple[str, ...],
    discovery_pattern: re.Pattern[str],
) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.resolve()
        if resolved not in seen and path.exists() and path.is_file():
            seen.add(resolved)
            paths.append(path)

    for name in preferred_names:
        add(root / name)
    if not root.exists():
        return paths
    for path in sorted(root.glob("*.md")):
        if path.resolve() in seen:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if discovery_pattern.search(path.name) or discovery_pattern.search(text):
            add(path)
    return paths


def _validation_report_failed(text: str) -> bool:
    return bool(re.search(r"(?i)FAILED TO LAUNCH|TIMED OUT|VALIDATORS? FAILED|VALIDATION FAILED", text)) and not bool(
        re.search(r"(?i)VALIDATION FAILED:\s*\n\s*-\s*None", text)
    )


def _validator_records(text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for line in text.splitlines():
        if not re.search(r"(?i)\b(pass|passed)\b", line):
            continue
        cleaned = line.strip().lstrip("-").strip()
        if not cleaned:
            continue
        records.append({"name": cleaned[:120], "status": "PASS"})
    return records[:20]


def _auxiliary_blockers(auxiliary_evidence: Mapping[str, Mapping[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for name, evidence in auxiliary_evidence.items():
        if evidence.get("ready") is True:
            continue
        blockers.extend(f"{name}: {item}" for item in evidence.get("blockers", []))
        blockers.extend(f"{name}: missing {item}" for item in evidence.get("missing_fields", []))
    return _dedupe(blockers)


def _all_sanitized(intakes: Mapping[str, Mapping[str, Any]]) -> bool:
    return all(bool(intake.get("sanitized")) for intake in intakes.values())


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(r"(?im)^\s*-?\s*([A-Za-z0-9 _/\-]+):\s*`?([^`\n]+?)`?\s*\.?\s*$")
    for match in pattern.finditer(text):
        values[_key(match.group(1))] = match.group(2).strip()
    return values


def _section_bullets(text: str, heading: str) -> list[str]:
    match = re.search(
        rf"(?ims)^##\s+{re.escape(heading)}\s*\n(?P<body>.*?)(?=^##\s+|\Z)",
        text,
    )
    if not match:
        return []
    body = match.group("body")
    bullets: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def _bool_first(values: Mapping[str, str], *keys: str) -> bool | None:
    for key in keys:
        value = _safe_bool(values.get(_key(key)))
        if value is not None:
            return value
    return None


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().strip("`").lower()
        if lowered in {"true", "1", "yes", "pass", "passed", "ready", "ok"}:
            return True
        if lowered in {"false", "0", "no", "fail", "failed", "blocked"}:
            return False
    return None


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _display_path(path: Path) -> str:
    return path.as_posix()


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


__all__ = [
    "EVIDENCE_CHAIN_STAGE_ORDER",
    "FINAL_EVIDENCE_CHAIN_BLOCKED",
    "FINAL_EVIDENCE_CHAIN_REVIEW_READY",
    "FINAL_EVIDENCE_BUNDLE_BLOCKED",
    "FINAL_EVIDENCE_BUNDLE_REVIEW_READY",
    "FINAL_EVIDENCE_BUNDLE_VERSION",
    "build_final_evidence_bundle",
    "build_replay_walkforward_profitability_evidence_chain",
    "final_evidence_bundle_to_markdown",
    "result_to_jsonable_dict",
    "result_to_operator_text",
    "write_final_evidence_report",
]
