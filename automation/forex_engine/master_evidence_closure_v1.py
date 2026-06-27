"""Master evidence closure aggregator for AIOS Forex.

This module consumes existing repository-backed evidence adapters only. It
does not read environment variables, contact brokers, call network services,
submit orders, activate schedulers, or create owner approval authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.final_closure_evidence_v1 import FINAL_CLOSURE_REVIEW_READY
from automation.forex_engine.final_evidence_bundle_v1 import (
    FINAL_EVIDENCE_CHAIN_REVIEW_READY,
    build_replay_walkforward_profitability_evidence_chain,
)


MASTER_EVIDENCE_CLOSURE_VERSION = "master_evidence_closure_v1"
MASTER_EVIDENCE_READY = "MASTER_EVIDENCE_READY"
MASTER_EVIDENCE_PARTIAL = "MASTER_EVIDENCE_PARTIAL"
MASTER_EVIDENCE_BLOCKED = "MASTER_EVIDENCE_BLOCKED"
DEFAULT_REPORT_ROOT = Path("Reports/forex_delivery")
DEFAULT_REPORT_PATH = (
    DEFAULT_REPORT_ROOT / "AIOS_FOREX_MASTER_EVIDENCE_CLOSURE_60K_V1_REPORT.md"
)
MASTER_INPUT_SCHEMA_PATH = Path(
    "schemas/aios/forex/AIOS_FOREX_MASTER_EVIDENCE_INPUT.v1.schema.json"
)
PACKET_ID = "AIOS-FOREX-MASTER-EVIDENCE-CLOSURE-EXECUTOR-60K-V1"
BRANCH_NAME = "lane/forex-master-evidence-closure-60k-v1"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "broker_connection_allowed": False,
    "broker_api_call_allowed": False,
    "live_trading_allowed": False,
    "demo_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "money_movement_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
    "autonomous_trading_allowed": False,
    "owner_approval_created": False,
}

TOUCHED_FILES = (
    "automation/forex_engine/final_evidence_bundle_v1.py",
    "automation/forex_engine/master_evidence_closure_v1.py",
    "schemas/aios/forex/AIOS_FOREX_MASTER_EVIDENCE_INPUT.v1.schema.json",
    "scripts/forex_delivery/run_master_evidence_closure_v1.py",
    "tests/forex_engine/test_master_evidence_closure_v1.py",
    "Reports/forex_delivery/AIOS_FOREX_MASTER_EVIDENCE_CLOSURE_60K_V1_REPORT.md",
)

CATEGORY_DEFINITIONS = {
    "broker read-only": {
        "modules": ("automation/forex_engine/sanitized_broker_snapshot_intake_v1.py",),
        "runners": ("scripts/forex_delivery/run_sanitized_broker_snapshot_intake_v1.py",),
        "tests": ("tests/forex_engine/test_sanitized_broker_snapshot_intake_v1.py",),
        "reports": (
            "Reports/forex_delivery/AIOS_FOREX_READ_ONLY_EVIDENCE_APPROVAL_AND_RECONCILIATION_DRY_RUN_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_TRADING_HISTORY_WRITEBACK_VERIFICATION_DRY_RUN_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_READONLY_BROKER_SANITIZED_EVIDENCE_CLOSURE_V1.md",
        ),
    },
    "replay": {
        "modules": (
            "automation/forex_engine/replay_evidence_intake_v1.py",
            "automation/forex_engine/replay_proof_evidence_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_replay_evidence_intake_v1.py",
            "scripts/forex_delivery/run_replay_proof_evidence_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_replay_evidence_intake_v1.py",
            "tests/forex_engine/test_replay_proof_evidence_v1.py",
        ),
        "reports": ("Reports/forex_delivery/AIOS_FOREX_REPLAY_RECONCILIATION_PROOF_BUNDLE_V1_REPORT.md",),
    },
    "walk-forward": {
        "modules": (
            "automation/forex_engine/walk_forward_evidence_intake_v1.py",
            "automation/forex_engine/walk_forward_oos_evidence_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_walk_forward_evidence_intake_v1.py",
            "scripts/forex_delivery/run_walk_forward_oos_evidence_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_walk_forward_evidence_intake_v1.py",
            "tests/forex_engine/test_walk_forward_oos_evidence_v1.py",
        ),
        "reports": (
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md",
            "Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_OOS_CLOSURE_V2_REPORT.md",
        ),
    },
    "OOS": {
        "modules": (
            "automation/forex_engine/walk_forward_evidence_intake_v1.py",
            "automation/forex_engine/walk_forward_oos_evidence_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_walk_forward_evidence_intake_v1.py",
            "scripts/forex_delivery/run_walk_forward_oos_evidence_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_walk_forward_evidence_intake_v1.py",
            "tests/forex_engine/test_walk_forward_oos_evidence_v1.py",
        ),
        "reports": ("Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_OOS_CLOSURE_V2_REPORT.md",),
    },
    "profitability": {
        "modules": (
            "automation/forex_engine/profitability_evidence_intake_v1.py",
            "automation/forex_engine/persistent_profitability_evidence_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_profitability_evidence_intake_v1.py",
            "scripts/forex_delivery/run_persistent_profitability_evidence_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_profitability_evidence_intake_v1.py",
            "tests/forex_engine/test_persistent_profitability_evidence_v1.py",
        ),
        "reports": (
            "Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_VERDICT_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_STATISTICAL_PROFIT_PROOF_GATE_V1.md",
        ),
    },
    "persistent profitability": {
        "modules": (
            "automation/forex_engine/profitability_evidence_intake_v1.py",
            "automation/forex_engine/persistent_profitability_evidence_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_profitability_evidence_intake_v1.py",
            "scripts/forex_delivery/run_persistent_profitability_evidence_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_profitability_evidence_intake_v1.py",
            "tests/forex_engine/test_persistent_profitability_evidence_v1.py",
        ),
        "reports": ("Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_VERDICT_V1.md",),
    },
    "observation": {
        "modules": (
            "automation/forex_engine/observation_evidence_intake_v1.py",
            "automation/forex_engine/supervised_observation_22h6d_evidence_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_observation_evidence_intake_v1.py",
            "scripts/forex_delivery/run_supervised_observation_22h6d_evidence_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_observation_evidence_intake_v1.py",
            "tests/forex_engine/test_supervised_observation_22h6d_evidence_v1.py",
        ),
        "reports": ("Reports/forex_delivery/AIOS_FOREX_22H6D_OBSERVATION_CLOSURE_V2_REPORT.md",),
    },
    "22H/6D": {
        "modules": (
            "automation/forex_engine/observation_evidence_intake_v1.py",
            "automation/forex_engine/supervised_observation_22h6d_evidence_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_observation_evidence_intake_v1.py",
            "scripts/forex_delivery/run_supervised_observation_22h6d_evidence_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_observation_evidence_intake_v1.py",
            "tests/forex_engine/test_supervised_observation_22h6d_evidence_v1.py",
        ),
        "reports": (
            "Reports/forex_delivery/AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_22H6D_OBSERVATION_CLOSURE_V2_REPORT.md",
        ),
    },
    "compounding policy": {
        "modules": (
            "automation/forex_engine/supervised_compounding_policy_v1.py",
            "automation/forex_engine/forex_supervised_compounding_policy_gate_v1.py",
        ),
        "runners": ("scripts/forex_delivery/run_forex_supervised_compounding_policy_gate_v1.py",),
        "tests": (
            "tests/forex_engine/test_supervised_compounding_policy_v1.py",
            "tests/forex_engine/test_forex_supervised_compounding_policy_gate_v1.py",
        ),
        "reports": ("Reports/forex_delivery/AIOS_FOREX_SUPERVISED_COMPOUNDING_POLICY_GATE_V1.md",),
    },
    "final bundle": {
        "modules": ("automation/forex_engine/final_evidence_bundle_v1.py",),
        "runners": ("scripts/forex_delivery/run_final_evidence_bundle_v1.py",),
        "tests": ("tests/forex_engine/test_final_evidence_bundle_v1.py",),
        "reports": ("Reports/forex_delivery/AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md",),
    },
    "final closure": {
        "modules": ("automation/forex_engine/final_closure_evidence_v1.py",),
        "runners": ("scripts/forex_delivery/run_final_closure_evidence_v1.py",),
        "tests": ("tests/forex_engine/test_final_closure_evidence_v1.py",),
        "reports": ("Reports/forex_delivery/AIOS_FOREX_FINAL_CLOSURE_AUDIT_LANE_V1_REPORT.md",),
    },
    "owner readiness": {
        "modules": (
            "automation/forex_engine/forex_owner_decision_brief_v1.py",
            "automation/forex_engine/owner_gonogo_command_center_report_v1.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_forex_owner_decision_brief_v1.py",
            "scripts/forex_delivery/run_owner_gonogo_command_center_report_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_forex_owner_decision_brief_v1.py",
            "tests/forex_engine/test_owner_gonogo_command_center_report_v1.py",
        ),
        "reports": (
            "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_OWNER_GONOGO_COMMAND_CENTER_REPORT_V1_REPORT.md",
        ),
    },
    "demo readiness": {
        "modules": (
            "automation/forex_engine/demo_review_readiness_engine.py",
            "automation/forex_engine/governed_demo_advancement_gate.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_demo_review_engine_v1.py",
            "scripts/forex_delivery/run_supervised_demo_trade_readiness_epic_v1.py",
        ),
        "tests": (
            "tests/forex_engine/test_demo_review_readiness_engine.py",
            "tests/forex_engine/test_governed_demo_advancement_gate.py",
        ),
        "reports": (
            "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_EPIC_REPORT_V1.md",
            "Reports/forex_delivery/AIOS_FOREX_DEMO_READINESS_PROFIT_TRUST_SPINE_V1.md",
        ),
    },
    "live prohibition/safety": {
        "modules": (
            "automation/forex_engine/final_live_operator_bridge_v1.py",
            "automation/forex_engine/live_kill_switch_readiness_engine.py",
        ),
        "runners": (
            "scripts/forex_delivery/run_forex_final_readiness_checker_v1.py",
            "scripts/forex_delivery/run_live_micro_trade_arming_gate.py",
        ),
        "tests": (
            "tests/forex_engine/test_final_live_operator_bridge_v1.py",
            "tests/forex_engine/test_live_kill_switch_readiness_engine.py",
        ),
        "reports": (
            "Reports/forex_delivery/AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1_REPORT.md",
            "Reports/forex_delivery/AIOS_FOREX_LIVE_ARMING_EVIDENCE_GAP_DRY_RUN_V1_REPORT.md",
        ),
    },
}


def build_master_evidence_closure(
    report_root: str | Path = DEFAULT_REPORT_ROOT,
    repo_root: str | Path = ".",
    metadata: Mapping[str, Any] | None = None,
    validation_results: list[str] | None = None,
) -> dict[str, Any]:
    """Build a conservative master closure result from current local evidence."""

    report_root_path = Path(report_root)
    repo_root_path = Path(repo_root)
    chain = build_replay_walkforward_profitability_evidence_chain(report_root_path)
    bundle = dict(chain.get("final_evidence_bundle") or {})
    intakes = dict(bundle.get("intakes") or {})
    auxiliary = dict(bundle.get("final_readiness_auxiliary_evidence") or {})
    final_closure = dict(chain.get("final_closure_result") or {})
    missing_external = _missing_external_evidence(intakes, auxiliary, final_closure)
    unsafe_blockers = _unsafe_blockers(chain, bundle, final_closure)
    status = _master_status(chain, missing_external, unsafe_blockers)
    inventory = _category_inventory(repo_root_path, intakes, auxiliary, bundle, final_closure)
    local_closed = _local_evidence_closed(intakes, auxiliary, chain, final_closure)
    metadata_dict = _metadata(metadata)
    result = {
        "closure_version": MASTER_EVIDENCE_CLOSURE_VERSION,
        "packet_id": PACKET_ID,
        "branch": metadata_dict.get("branch", BRANCH_NAME),
        "status": status,
        "readiness_state": _readiness_state(status),
        "chain_status": chain.get("status"),
        "final_bundle_status": bundle.get("status"),
        "final_closure_status": final_closure.get("final_closure_status"),
        "category_inventory": inventory,
        "local_evidence_closed": local_closed,
        "local_evidence_generated": [
            str(DEFAULT_REPORT_PATH).replace("\\", "/"),
            str(MASTER_INPUT_SCHEMA_PATH).replace("\\", "/"),
        ],
        "missing_external_evidence": missing_external,
        "external_dependencies": _external_dependencies(missing_external),
        "owner_next_decision": _owner_next_decision(status, missing_external),
        "next_safe_packet": "AIOS-FOREX-COLLECT-MISSING-REAL-EVIDENCE-V1",
        "touched_files": list(TOUCHED_FILES),
        "exact_commit_message": "feat(forex): advance master evidence closure",
        "exact_pr_title": "feat(forex): advance master evidence closure",
        "exact_pr_body": _exact_pr_body(status, missing_external, validation_results or []),
        "protected_action_handoff": _protected_action_handoff(validation_results or []),
        "metadata": metadata_dict,
        "validation_results": list(validation_results or []),
        "source_chain": chain,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }
    return result


def write_master_evidence_closure_report(
    result: Mapping[str, Any] | None = None,
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> Path:
    active = dict(result or build_master_evidence_closure())
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(master_evidence_closure_to_markdown(active), encoding="utf-8")
    return path


def master_evidence_closure_to_markdown(result: Mapping[str, Any]) -> str:
    metadata = dict(result.get("metadata") or {})
    inventory = list(result.get("category_inventory") or [])
    missing = list(result.get("missing_external_evidence") or [])
    validation_results = list(result.get("validation_results") or [])
    lines = [
        "# AIOS Forex Master Evidence Closure 60K V1 Report",
        "",
        "## Packet",
        f"- packet_id: {result.get('packet_id')}",
        f"- generated_at: {metadata.get('generated_at')}",
        f"- branch: {result.get('branch')}",
        f"- base_commit: {metadata.get('base_commit', 'UNKNOWN')}",
        f"- current_commit: {metadata.get('current_commit', 'UNKNOWN')}",
        f"- pr_baseline: {metadata.get('pr_baseline', 'origin/main includes PR #1152 or newer when preflight passes')}",
        "",
        "## Summary",
        f"- master_status: {result.get('status')}",
        f"- readiness_state: {result.get('readiness_state')}",
        f"- chain_status: {result.get('chain_status')}",
        f"- final_bundle_status: {result.get('final_bundle_status')}",
        f"- final_closure_status: {result.get('final_closure_status')}",
        "",
        "## Evidence Categories Inspected",
        "| Category | Files Found | Runner Found | Test Found | Report Found | Status | Next Action |",
        "|---|---:|---|---|---|---|---|",
    ]
    for item in inventory:
        lines.append(
            "| {category} | {files_found} | {runner_found} | {test_found} | {report_found} | {status} | {next_action} |".format(
                category=item.get("category"),
                files_found=item.get("files_found"),
                runner_found=_bool_word(bool(item.get("runner_found"))),
                test_found=_bool_word(bool(item.get("test_found"))),
                report_found=_bool_word(bool(item.get("report_found"))),
                status=item.get("status"),
                next_action=str(item.get("next_action", "")).replace("|", "/"),
            )
        )
    lines.extend(
        [
            "",
            "## Local Evidence Closed",
        ]
    )
    lines.extend(f"- {item}" for item in result.get("local_evidence_closed") or ["none"])
    lines.extend(
        [
            "",
            "## Local Evidence Generated",
        ]
    )
    lines.extend(f"- {item}" for item in result.get("local_evidence_generated") or ["none"])
    lines.extend(
        [
            "",
            "## Missing Evidence",
        ]
    )
    lines.extend(f"- {item}" for item in missing or ["none"])
    lines.extend(
        [
            "",
            "## External Dependencies",
        ]
    )
    lines.extend(f"- {item}" for item in result.get("external_dependencies") or ["none"])
    lines.extend(
        [
            "",
            "## Validation Results",
        ]
    )
    lines.extend(f"- {item}" for item in validation_results or ["terminal validators not yet recorded in this generated report"])
    lines.extend(
        [
            "",
            "## Files Touched By This Packet",
        ]
    )
    lines.extend(f"- {item}" for item in result.get("touched_files") or [])
    lines.extend(
        [
            "",
            "## Safety Statement",
            "- no broker/API access was performed.",
            "- no credential access was performed.",
            "- no demo/live trade execution was performed.",
            "- no money movement was performed.",
            "- no production, scheduler, daemon, or webhook activation was performed.",
            "- owner approval was not created by this report.",
            "",
            "## Readiness State",
            f"- readiness_state: {result.get('readiness_state')}",
            f"- owner_next_decision: {result.get('owner_next_decision')}",
            f"- next_safe_packet: {result.get('next_safe_packet')}",
            "",
            "## Protected Action Handoff",
        ]
    )
    handoff = dict(result.get("protected_action_handoff") or {})
    for key in (
        "exact_git_status_command",
        "exact_git_add_command",
        "exact_cached_diff_check_command",
        "exact_commit_command",
        "exact_push_command",
        "exact_pr_create_command",
        "exact_pr_checks_command",
        "exact_pr_merge_command",
        "exact_post_merge_sync_command",
    ):
        lines.append(f"- {key}: `{handoff.get(key)}`")
    lines.extend(
        [
            "- merge_status: owner approval required before merge.",
            "",
            "## Exact Commit Message",
            f"`{result.get('exact_commit_message')}`",
            "",
            "## Exact PR Title",
            f"`{result.get('exact_pr_title')}`",
            "",
            "## Exact PR Body",
            "```markdown",
            str(result.get("exact_pr_body", "")),
            "```",
            "",
            "## Status",
            str(result.get("status")),
            "",
        ]
    )
    return "\n".join(lines)


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    return (
        "AIOS Forex Master Evidence Closure V1\n"
        f"status: {result.get('status')}\n"
        f"readiness_state: {result.get('readiness_state')}\n"
        f"missing_external_evidence: {len(result.get('missing_external_evidence') or [])}\n"
        f"next_safe_packet: {result.get('next_safe_packet')}\n"
    )


def _metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    active = dict(metadata or {})
    active.setdefault("generated_at", datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"))
    active.setdefault("branch", BRANCH_NAME)
    return active


def _master_status(
    chain: Mapping[str, Any],
    missing_external: list[str],
    unsafe_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return MASTER_EVIDENCE_BLOCKED
    if chain.get("status") == FINAL_EVIDENCE_CHAIN_REVIEW_READY and not missing_external:
        return MASTER_EVIDENCE_READY
    return MASTER_EVIDENCE_PARTIAL


def _readiness_state(status: str) -> str:
    if status == MASTER_EVIDENCE_READY:
        return "READY_FOR_OWNER_REVIEW_ONLY"
    if status == MASTER_EVIDENCE_PARTIAL:
        return "PARTIAL_EXTERNAL_EVIDENCE_REQUIRED"
    return "BLOCKED_UNSAFE_OR_INVALID_EVIDENCE"


def _category_inventory(
    repo_root: Path,
    intakes: Mapping[str, Mapping[str, Any]],
    auxiliary: Mapping[str, Mapping[str, Any]],
    bundle: Mapping[str, Any],
    final_closure: Mapping[str, Any],
) -> list[dict[str, Any]]:
    statuses = _category_statuses(intakes, auxiliary, bundle, final_closure)
    return [
        {
            "category": category,
            "files_found": len(_existing_files(repo_root, definition)),
            "runner_found": _any_exists(repo_root, definition.get("runners", ())),
            "test_found": _any_exists(repo_root, definition.get("tests", ())),
            "report_found": _any_exists(repo_root, definition.get("reports", ())),
            "status": statuses.get(category, "INSPECTED"),
            "next_action": _category_next_action(category, statuses.get(category, "")),
        }
        for category, definition in CATEGORY_DEFINITIONS.items()
    ]


def _category_statuses(
    intakes: Mapping[str, Mapping[str, Any]],
    auxiliary: Mapping[str, Mapping[str, Any]],
    bundle: Mapping[str, Any],
    final_closure: Mapping[str, Any],
) -> dict[str, str]:
    replay = str(intakes.get("replay", {}).get("status", "UNKNOWN"))
    walk = str(intakes.get("walk_forward", {}).get("status", "UNKNOWN"))
    profit = str(intakes.get("profitability", {}).get("status", "UNKNOWN"))
    observation = str(intakes.get("observation", {}).get("status", "UNKNOWN"))
    broker = "BROKER_READONLY_READY" if auxiliary.get("sanitized_broker_readonly_evidence", {}).get("ready") is True else "BROKER_READONLY_EXTERNAL_EVIDENCE_REQUIRED"
    return {
        "broker read-only": broker,
        "replay": replay,
        "walk-forward": walk,
        "OOS": walk,
        "profitability": profit,
        "persistent profitability": profit,
        "observation": observation,
        "22H/6D": observation,
        "compounding policy": "POLICY_PRESENT_NO_EXECUTION_AUTHORITY",
        "final bundle": str(bundle.get("status", "UNKNOWN")),
        "final closure": str(final_closure.get("final_closure_status", "UNKNOWN")),
        "owner readiness": "OWNER_REVIEW_READY" if final_closure.get("final_closure_status") == FINAL_CLOSURE_REVIEW_READY else "OWNER_REVIEW_BLOCKED_BY_EVIDENCE",
        "demo readiness": "DEMO_REVIEW_ONLY_EVIDENCE_PRESENT",
        "live prohibition/safety": "CLOSED_NO_EXECUTION_AUTHORITY_CREATED",
    }


def _category_next_action(category: str, status: str) -> str:
    if "READY" in status and "BLOCKED" not in status and "EXTERNAL" not in status:
        return "Preserve as local evidence; no execution authority."
    if category in {"walk-forward", "OOS"}:
        return "Provide sanitized OOS segment counts using the master evidence schema."
    if category in {"observation", "22H/6D"}:
        return "Provide real observed 22H/6D metrics using the master evidence schema."
    if category in {"profitability", "persistent profitability"}:
        return "Provide persistent after-cost profitability periods that meet threshold."
    if category == "broker read-only":
        return "Provide sanitized broker-live-read-only evidence; no raw broker payloads."
    if category in {"final bundle", "final closure", "owner readiness"}:
        return "Close upstream evidence blockers first."
    return "No local APPLY action required."


def _existing_files(repo_root: Path, definition: Mapping[str, Any]) -> list[str]:
    files: list[str] = []
    for key in ("modules", "runners", "tests", "reports"):
        for value in definition.get(key, ()):
            if (repo_root / str(value)).exists():
                files.append(str(value))
    return files


def _any_exists(repo_root: Path, paths: Any) -> bool:
    return any((repo_root / str(path)).exists() for path in paths)


def _missing_external_evidence(
    intakes: Mapping[str, Mapping[str, Any]],
    auxiliary: Mapping[str, Mapping[str, Any]],
    final_closure: Mapping[str, Any],
) -> list[str]:
    missing: list[str] = []
    walk = dict(intakes.get("walk_forward") or {})
    for field in walk.get("missing_fields") or []:
        missing.append(f"walk_forward_oos.{field}")

    profit = dict(intakes.get("profitability") or {})
    missing.extend(f"persistent_profitability.{field}" for field in profit.get("missing_fields") or [])
    missing.extend(_profitability_threshold_gaps(profit))

    observation = dict(intakes.get("observation") or {})
    missing.extend(f"observation_22h6d.{field}" for field in observation.get("missing_fields") or [])

    broker = dict(auxiliary.get("sanitized_broker_readonly_evidence") or {})
    missing.extend(f"broker_readonly.{field}" for field in broker.get("missing_fields") or [])
    missing.extend(_broker_readonly_blocker_summary(broker.get("blockers") or []))

    if final_closure.get("final_closure_status") != FINAL_CLOSURE_REVIEW_READY:
        missing.append("final_closure.upstream_evidence_not_ready")
    return _dedupe(missing)


def _profitability_threshold_gaps(profitability_intake: Mapping[str, Any]) -> list[str]:
    summary = dict(profitability_intake.get("normalized_summary") or {})
    gaps: list[str] = []
    periods = summary.get("consecutive_profitable_periods")
    min_periods = summary.get("min_profitable_periods")
    if periods is not None and min_periods is not None:
        try:
            if float(periods) < float(min_periods):
                gaps.append(
                    "persistent_profitability.consecutive_profitable_periods "
                    f"{periods} below min_profitable_periods {min_periods}"
                )
        except (TypeError, ValueError):
            gaps.append("persistent_profitability.consecutive_profitable_periods is not numeric")
    for blocker in profitability_intake.get("blockers") or []:
        if "profitable periods" not in str(blocker):
            gaps.append(f"persistent_profitability.blocker: {blocker}")
    return gaps


def _broker_readonly_blocker_summary(blockers: Any) -> list[str]:
    values = [str(item) for item in blockers if str(item)]
    summary: list[str] = []
    if any("not approved for future live review" in item for item in values):
        summary.append("broker_readonly.read_only_evidence_not_approved_for_future_live_review")
    if any("fixture" in item.lower() and "not_live" in item.lower() for item in values):
        summary.append("broker_readonly.source_is_fixture_not_live")
    if any("partial" in item.lower() or "left to finish" in item.lower() for item in values):
        summary.append("broker_readonly.historical_partial_reports_present")
    if any("private_identifier_marker_present" in item for item in values):
        summary.append("broker_readonly.private_identifier_marker_present")
    if values and not summary:
        summary.append(f"broker_readonly.blocker_count:{len(values)}")
    return summary


def _unsafe_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    joined = "\n".join(str(item) for payload in payloads for item in payload.get("blockers", []) if item)
    hard_patterns = (
        " is unsafe true",
        " is unsafe evidence source data",
        "broker_execution_allowed is unsafe",
        "live_trading_allowed is unsafe",
        "credential_access_allowed is unsafe",
        "raw_payload is unsafe",
    )
    return [line for line in joined.splitlines() if any(pattern in line.lower() for pattern in hard_patterns)]


def _local_evidence_closed(
    intakes: Mapping[str, Mapping[str, Any]],
    auxiliary: Mapping[str, Mapping[str, Any]],
    chain: Mapping[str, Any],
    final_closure: Mapping[str, Any],
) -> list[str]:
    closed: list[str] = []
    for name, intake in intakes.items():
        if str(intake.get("status", "")).endswith("_READY"):
            closed.append(f"{name} intake consumed {len(intake.get('source_files', []))} local source file(s).")
    validator = dict(auxiliary.get("validator_evidence") or {})
    if validator.get("ready") is True:
        closed.append(f"validator evidence found in {len(validator.get('source_files', []))} local source file(s).")
    if chain.get("chain_integrated_end_to_end") is True:
        closed.append("final replay-to-closure chain executed locally and failed closed where evidence is missing.")
    if all(value is False for value in PROTECTED_PERMISSION_FLAGS.values()):
        closed.append("protected execution permissions remain false.")
    if final_closure.get("owner_review_required") is True:
        closed.append("owner review remains required; no approval was created.")
    return _dedupe(closed)


def _external_dependencies(missing_external: list[str]) -> list[str]:
    if not missing_external:
        return ["none"]
    dependencies: list[str] = []
    if any(item.startswith("broker_readonly.") for item in missing_external):
        dependencies.append("sanitized broker-live read-only summary from owner-controlled runtime")
    if any(item.startswith("walk_forward_oos.") for item in missing_external):
        dependencies.append("repository-backed OOS segment count evidence")
    if any(item.startswith("persistent_profitability.") for item in missing_external):
        dependencies.append("persistent after-cost profitability sample evidence")
    if any(item.startswith("observation_22h6d.") for item in missing_external):
        dependencies.append("real supervised 22H/6D observation metrics")
    return _dedupe(dependencies)


def _owner_next_decision(status: str, missing_external: list[str]) -> str:
    if status == MASTER_EVIDENCE_READY:
        return "Review final evidence package only; this does not approve execution."
    if status == MASTER_EVIDENCE_PARTIAL:
        return "Provide missing sanitized external evidence fields or keep Forex readiness partial."
    return "Stop and review unsafe or invalid evidence before any further action."


def _protected_action_handoff(validation_results: list[str]) -> dict[str, str]:
    files = " ".join(f'"{path}"' for path in TOUCHED_FILES)
    body_arg = "$body = Get-Content Reports/forex_delivery/AIOS_FOREX_MASTER_EVIDENCE_CLOSURE_60K_V1_REPORT.md -Raw"
    return {
        "exact_git_status_command": "git status --short --branch",
        "exact_git_add_command": f"git add {files}",
        "exact_cached_diff_check_command": "git diff --cached --check",
        "exact_commit_command": 'git commit -m "feat(forex): advance master evidence closure"',
        "exact_push_command": f"git push -u origin {BRANCH_NAME}",
        "exact_pr_create_command": (
            f"{body_arg}; gh pr create --base main --head {BRANCH_NAME} "
            '--title "feat(forex): advance master evidence closure" --body $body'
        ),
        "exact_pr_checks_command": "gh pr checks --watch",
        "exact_pr_merge_command": "gh pr merge --squash",
        "exact_post_merge_sync_command": "git fetch origin; git switch main; git pull --ff-only origin main; git status --short --branch",
        "validation_summary": "; ".join(validation_results) if validation_results else "pending terminal validation",
    }


def _exact_pr_body(status: str, missing_external: list[str], validation_results: list[str]) -> str:
    lines = [
        "## Local Evidence Closed",
        "- Added master Forex evidence closure aggregator, schema, runner, tests, and canonical report.",
        "- Replay evidence remains locally closed when repository evidence is present.",
        "- Final chain remains conservative and fails closed for missing external evidence.",
        "",
        "## Missing External Evidence",
    ]
    lines.extend(f"- {item}" for item in missing_external or ["none"])
    lines.extend(
        [
            "",
            "## Validators",
        ]
    )
    lines.extend(f"- {item}" for item in validation_results or ["pending terminal validation"])
    lines.extend(
        [
            "",
            "## Safety Statement",
            "- No broker/API access.",
            "- No credentials.",
            "- No demo/live execution.",
            "- No money movement.",
            "- Owner review only.",
            "",
            f"## Status\n- {status}",
        ]
    )
    return "\n".join(lines)


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _bool_word(value: bool) -> str:
    return "yes" if value else "no"


__all__ = [
    "BRANCH_NAME",
    "DEFAULT_REPORT_PATH",
    "MASTER_EVIDENCE_BLOCKED",
    "MASTER_EVIDENCE_CLOSURE_VERSION",
    "MASTER_EVIDENCE_PARTIAL",
    "MASTER_EVIDENCE_READY",
    "MASTER_INPUT_SCHEMA_PATH",
    "PACKET_ID",
    "PROTECTED_PERMISSION_FLAGS",
    "TOUCHED_FILES",
    "build_master_evidence_closure",
    "master_evidence_closure_to_markdown",
    "result_to_jsonable_dict",
    "result_to_operator_text",
    "write_master_evidence_closure_report",
]
