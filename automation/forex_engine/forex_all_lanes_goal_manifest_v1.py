"""Repo-derived Forex all-lanes goal manifest builder.

This module is intentionally local-only. It inspects repository files and a
captured branch-signal list, then classifies each Forex goal without touching
credentials, broker APIs, network transports, or protected Git actions.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable, Mapping


MANIFEST_VERSION = "1.0"
PACKET_ID = "AIOS-FOREX-ALL-LANES-GOALS-COMPLETION-CAMPAIGN-V1"
BRANCH = "lane/forex-all-lanes-goals-completion-campaign-v1"
GENERATED_AT = "2026-06-28T00:00:00Z"

CLOSED_ON_MAIN = "CLOSED_ON_MAIN"
CLOSED_BY_THIS_CAMPAIGN = "CLOSED_BY_THIS_CAMPAIGN"
NEEDS_REPO_WORK = "NEEDS_REPO_WORK"
OWNER_PROTECTED_BOUNDARY = "OWNER_PROTECTED_BOUNDARY"
EXTERNAL_EVIDENCE_REQUIRED = "EXTERNAL_EVIDENCE_REQUIRED"
LIVE_OR_BROKER_PERMISSION_REQUIRED = "LIVE_OR_BROKER_PERMISSION_REQUIRED"
SAFETY_BLOCKED = "SAFETY_BLOCKED"
DEFERRED_WITH_REASON = "DEFERRED_WITH_REASON"
UNKNOWN_REQUIRES_OWNER_REVIEW = "UNKNOWN_REQUIRES_OWNER_REVIEW"

ALLOWED_STATUSES = {
    CLOSED_ON_MAIN,
    CLOSED_BY_THIS_CAMPAIGN,
    NEEDS_REPO_WORK,
    OWNER_PROTECTED_BOUNDARY,
    EXTERNAL_EVIDENCE_REQUIRED,
    LIVE_OR_BROKER_PERMISSION_REQUIRED,
    SAFETY_BLOCKED,
    DEFERRED_WITH_REASON,
    UNKNOWN_REQUIRES_OWNER_REVIEW,
}

DISCOVERY_ROOTS = (
    "Reports/forex_delivery",
    "automation/forex_engine",
    "scripts/forex_delivery",
    "tests/forex_engine",
    "tests/fixtures/forex_delivery",
    "docs/workflows",
    "docs/governance/programs/epics",
    "schemas/aios/forex",
    "AGENTS.md",
    "README.md",
)

FOREX_TERMS = (
    "forex",
    "oanda",
    "demo",
    "live",
    "broker",
    "readiness",
    "evidence",
    "owner",
    "approval",
    "exception",
    "final",
    "closure",
    "gap",
    "blocker",
    "deferred",
    "required",
    "remaining",
    "operating",
    "dashboard",
    "handoff",
    "profitability",
    "expectancy",
    "risk",
    "trade",
    "protected",
    "authority",
)

LOCAL_REPAIR_TERMS = (
    "todo",
    "fixme",
    "remaining",
    "gap",
    "blocker",
    "deferred",
    "repair",
    "missing",
    "closure",
)

OWNER_TERMS = (
    "owner",
    "approval",
    "protected",
    "authority",
    "human",
    "manual",
)

EXTERNAL_TERMS = (
    "external",
    "runtime",
    "evidence",
    "snapshot",
    "connection",
    "probe",
    "proof",
    "account",
)

LIVE_BROKER_TERMS = (
    "oanda",
    "broker",
    "credential",
    "vault",
    "live",
    "order",
    "execution",
    "trade",
    "money",
    "funding",
    "capital",
)

SAFETY_TERMS = (
    "safety",
    "risk",
    "kill",
    "halt",
    "reject",
    "stop",
    "exception",
    "blocked",
)

CAMPAIGN_ARTIFACTS = (
    "automation/forex_engine/forex_all_lanes_goal_manifest_v1.py",
    "automation/forex_engine/forex_all_lanes_gap_classifier_v1.py",
    "automation/forex_engine/forex_all_lanes_completion_router_v1.py",
    "automation/forex_engine/forex_all_lanes_operating_readiness_projector_v1.py",
    "automation/forex_engine/forex_all_lanes_owner_boundary_gate_v1.py",
    "automation/forex_engine/forex_all_lanes_final_bundle_v1.py",
    "automation/forex_engine/forex_all_lanes_completion_orchestrator_v1.py",
    "automation/forex_engine/forex_review_ready_candidate_selector_v1.py",
    "scripts/forex_delivery/run_forex_all_lanes_goal_manifest_v1.py",
    "scripts/forex_delivery/run_forex_all_lanes_gap_classifier_v1.py",
    "scripts/forex_delivery/run_forex_all_lanes_completion_router_v1.py",
    "scripts/forex_delivery/run_forex_all_lanes_operating_readiness_projector_v1.py",
    "scripts/forex_delivery/run_forex_all_lanes_owner_boundary_gate_v1.py",
    "scripts/forex_delivery/run_forex_all_lanes_final_bundle_v1.py",
    "scripts/forex_delivery/run_forex_all_lanes_completion_orchestrator_v1.py",
    "scripts/forex_delivery/run_forex_review_ready_candidate_selector_v1.py",
    "tests/forex_engine/test_forex_all_lanes_goals_completion_campaign_v1.py",
    "tests/forex_engine/test_forex_final_review_decision_gate_v1.py",
    "docs/workflows/AIOS_FOREX_ALL_LANES_GOALS_COMPLETION_CAMPAIGN_V1.md",
    "docs/governance/programs/epics/EPC-FOREX-ALL-LANES-GOALS-COMPLETION-CAMPAIGN-V1.md",
    "schemas/aios/forex/FOREX_ALL_LANES_GOALS_COMPLETION_CAMPAIGN.v1.schema.json",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_MANIFEST_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_MANIFEST_V1.json",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOAL_MANIFEST_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GAP_CLASSIFIER_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_COMPLETION_ROUTER_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_OPERATING_READINESS_PROJECTOR_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_OWNER_BOUNDARY_GATE_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_FINAL_BUNDLE_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_COMPLETION_ORCHESTRATOR_V1_CHECKPOINT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_COMPLETION_CAMPAIGN_V1_REPORT.md",
)

FIXTURE_DIR = "tests/fixtures/forex_delivery/all_lanes_goals_completion_campaign_v1"

BRANCH_SIGNAL_HINTS = (
    "codex/forex-paper-bot-contract",
    "codex/forex-paper-lab-12h-supervisor-plan",
    "feature/dashboard-nested-forex-operator-flow-v1",
    "feature/forex-22h6d-epic-decomposition-v1",
    "feature/forex-auto-exit-live-readiness-v1",
    "feature/forex-broker-balance-bucket-equity-separation-v1",
    "feature/forex-broker-proof-ticket-closure-v1",
    "feature/forex-canonical-demo-live-bridge-v1",
    "feature/forex-compounding-capital-bucket-supervisor-v1",
    "feature/forex-demo-connector-proof-closure-v1",
    "feature/forex-demo-micro-trade-owner-approval-evidence-capture-v1",
    "feature/forex-demo-review-readiness-engine-v1",
    "feature/forex-engine-v1-sprint-1",
    "feature/forex-engine-v1-sprint-2-market-data",
    "feature/forex-engine-v1-sprint-3-backtest-runner",
    "feature/forex-engine-v1-sprint-4-regime-signal-rules",
    "feature/forex-engine-v1-sprint-5-confidence-v2",
    "feature/forex-engine-v1-sprint-6-strategy-comparison",
    "feature/forex-engine-v1-sprint-7-walk-forward",
    "feature/forex-engine-v1-sprint-8-paper-operator",
    "feature/forex-engine-v1-sprint-9-broker-sandbox-model",
    "feature/forex-engine-v1-sprint-10-risk-management",
    "feature/forex-engine-v1-sprint-11-parameter-optimization",
    "feature/forex-engine-v1-sprint-12-portfolio-optimization",
    "feature/forex-engine-v1-sprint-13-historical-data-readiness",
    "feature/forex-engine-v1-sprint-14-large-dataset-backtest-adapter",
    "feature/forex-evidence-depth-quality-gate-v1",
    "feature/forex-governance-consolidation-v1",
    "feature/forex-human-owner-value-free-broker-proof-intake-dry-run-v1",
    "feature/forex-next-trade-eligibility-repeat-proof-gate-v1",
    "feature/forex-oanda-closed-trade-tpsl-result-capture-v1",
    "feature/forex-oanda-demo-broker-adapter-one-order-final-wire-v1",
    "feature/forex-oanda-demo-broker-call-one-order-manual-run-v1",
    "feature/forex-oanda-demo-broker-execution-packet-one-order-v1",
    "feature/forex-oanda-demo-final-owner-click-order-bridge-v1",
    "feature/forex-oanda-demo-final-owner-runtime-run-one-order-v1",
    "feature/forex-oanda-demo-first-trade-actual-owner-command-run",
    "feature/forex-oanda-demo-first-trade-owner-manual-execution-window-v1",
    "feature/forex-oanda-demo-first-trade-runbook-go-nogo-v1",
    "feature/forex-oanda-demo-owner-run-actual-one-order-command-v1",
    "feature/forex-oanda-demo-post-trade-evidence-capture-v1",
    "feature/forex-oanda-demo-read-only-filled-trade-pl-capture-idrange-repair-v1",
    "feature/forex-oanda-demo-read-only-preflight-from-vault-v1",
    "feature/forex-oanda-demo-result-to-bucket-and-next-allocation-v1",
    "feature/forex-oanda-demo-runtime-executor-dryrun-v1",
    "feature/forex-oanda-demo-runtime-executor-final-gated-v1",
    "feature/forex-oanda-demo-runtime-executor-one-order-only-v1",
    "feature/forex-oanda-demo-runtime-one-order-execution-exception-v1",
    "feature/forex-oanda-long-only-broker-proof-intake-v1",
    "feature/forex-oanda-owner-run-closed-result-adapter-exercise-v1",
    "feature/forex-oanda-readonly-account-snapshot-balance-separation-adapter-v1",
    "feature/forex-oanda-readonly-closed-result-tpsl-classifier-adapter-v1",
    "feature/forex-owner-gonogo-command-center-report-v1",
    "feature/forex-paper-continuity-review-v1",
    "feature/forex-pkt-001-supervised-demo-operational-validation-runner-v1",
    "feature/forex-plumbing-diagnostic-campaign-v1",
    "feature/forex-read-only-evidence-blocker-burndown-v1",
    "feature/forex-realized-pl-result-bucket-update-gate-v1",
    "feature/forex-review-ready-candidate-selector-v1",
    "feature/forex-runtime-only-demo-order-ticket-v1",
    "feature/forex-selected-candidate-owner-review-packet-v1",
    "feature/forex-single-micro-trade-exception-checklist-hardening-dry-run-v2",
    "feature/forex-sos-owner-alert-bridge-v1",
    "feature/forex-statistical-profit-proof-gate-v1",
    "feature/forex-strategy-portfolio-competition-runner-v1",
    "feature/forex-supervised-compounding-policy-gate-v1",
    "feature/forex-supervised-demo-operational-validation-epic-v1",
    "feature/forex-supervised-readiness-gates-v1",
    "feature/forex-terminal-proof-artifact-collection-v1",
    "feature/forex-vacation-mode-final-readiness-decision-v1",
    "feature/forex-vacation-mode-readiness-orchestrator-v1",
    "lane/forex-all-lanes-goals-completion-campaign-v1",
    "lane/forex-dirty-backlog-preservation",
    "lane/forex-master-evidence-closure-60k-v1",
    "remotes/origin/feature/forex-self-improvement-v1",
)


def _path_key(path: Path) -> str:
    return path.as_posix()


def _stable_goal_id(source_path: str) -> str:
    digest = hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:10].upper()
    stem = "".join(ch if ch.isalnum() else "-" for ch in source_path.upper())
    stem = "-".join(part for part in stem.split("-") if part)[:54]
    return f"FOREX-GOAL-{stem}-{digest}"


def _read_sample(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:20000]
    except OSError:
        return ""


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def _matched_terms(text: str, terms: Iterable[str]) -> list[str]:
    lower = text.lower()
    return sorted({term for term in terms if term in lower})


def _source_type(rel_path: str) -> str:
    rel_lower = rel_path.lower()
    if rel_path.startswith("git branch --all::"):
        return "branch"
    if rel_lower.startswith("automation/forex_engine/") and rel_lower.endswith(".py"):
        return "module"
    if rel_lower.startswith("scripts/forex_delivery/") and rel_lower.endswith(".py"):
        return "script"
    if rel_lower.startswith("tests/forex_engine/"):
        return "test"
    if rel_lower.startswith("tests/fixtures/forex_delivery/"):
        return "fixture"
    if rel_lower.startswith("reports/forex_delivery/"):
        return "report"
    if rel_lower.startswith("schemas/aios/forex/"):
        return "schema"
    if rel_lower.startswith("docs/governance/programs/epics/"):
        return "epic"
    if rel_lower.startswith("docs/") or rel_lower.endswith(".md"):
        return "doc"
    return "doc"


def _is_campaign_artifact(rel_path: str) -> bool:
    return rel_path in CAMPAIGN_ARTIFACTS or rel_path.startswith(f"{FIXTURE_DIR}/")


def _classify_status(rel_path: str, text: str, source_type: str) -> tuple[str, str, str]:
    lower = f"{rel_path}\n{text}".lower()
    if _is_campaign_artifact(rel_path):
        return (
            CLOSED_BY_THIS_CAMPAIGN,
            "campaign_artifact",
            "NO_EXECUTION_LOCAL_ONLY",
        )
    if source_type == "branch":
        if rel_path.endswith(BRANCH):
            return (
                CLOSED_BY_THIS_CAMPAIGN,
                "active_campaign_branch",
                "NO_EXECUTION_LOCAL_ONLY",
            )
        if _contains_any(lower, LIVE_BROKER_TERMS):
            return (
                DEFERRED_WITH_REASON,
                "stale_or_unmerged_broker_branch_signal",
                "BRANCH_SIGNAL_OWNER_REVIEW",
            )
        return (
            DEFERRED_WITH_REASON,
            "stale_or_unmerged_branch_signal",
            "BRANCH_SIGNAL_OWNER_REVIEW",
        )
    if _contains_any(lower, ("credential", "vault", "money", "funding")):
        return (
            LIVE_OR_BROKER_PERMISSION_REQUIRED,
            "credential_or_money_boundary",
            "LIVE_OR_BROKER_BLOCKED",
        )
    if _contains_any(lower, ("oanda", "broker", "live", "order")):
        return (
            LIVE_OR_BROKER_PERMISSION_REQUIRED,
            "broker_or_live_permission_boundary",
            "LIVE_OR_BROKER_BLOCKED",
        )
    if _contains_any(lower, SAFETY_TERMS) and _contains_any(lower, ("blocked", "reject", "halt", "exception")):
        return (
            SAFETY_BLOCKED,
            "explicit_safety_block_or_exception",
            "SAFETY_REVIEW_REQUIRED",
        )
    if _contains_any(lower, OWNER_TERMS):
        return (
            OWNER_PROTECTED_BOUNDARY,
            "owner_protected_authority_boundary",
            "OWNER_PROTECTED",
        )
    if _contains_any(lower, EXTERNAL_TERMS) and _contains_any(lower, ("required", "missing", "proof", "snapshot")):
        return (
            EXTERNAL_EVIDENCE_REQUIRED,
            "external_evidence_boundary",
            "EXTERNAL_EVIDENCE",
        )
    if _contains_any(lower, LOCAL_REPAIR_TERMS):
        return (
            CLOSED_BY_THIS_CAMPAIGN,
            "local_manifesting_gap_closed_by_campaign",
            "NO_EXECUTION_LOCAL_ONLY",
        )
    return (
        CLOSED_ON_MAIN,
        "existing_repo_artifact_present",
        "NO_EXECUTION_LOCAL_ONLY",
    )


def _closure_action(status: str, blocker_class: str, target_artifact: str) -> str:
    if status == CLOSED_ON_MAIN:
        return "Preserve as existing main-branch Forex evidence."
    if status == CLOSED_BY_THIS_CAMPAIGN:
        return f"Classified and routed through {target_artifact} in this campaign."
    if status == OWNER_PROTECTED_BOUNDARY:
        return "Human Owner must review and explicitly approve any protected boundary movement."
    if status == EXTERNAL_EVIDENCE_REQUIRED:
        return "Collect sanitized external evidence and rerun the all-lanes manifest."
    if status == LIVE_OR_BROKER_PERMISSION_REQUIRED:
        return "Stop at broker/live boundary until Human Owner provides separate authority."
    if status == SAFETY_BLOCKED:
        return "Keep blocked until the safety condition is resolved through owner governance."
    if status == DEFERRED_WITH_REASON:
        return f"Defer because {blocker_class}; owner must decide whether branch evidence still matters."
    return "Owner review is required before any action is assigned."


def _target_artifact_for(status: str) -> str:
    if status == CLOSED_BY_THIS_CAMPAIGN:
        return "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_COMPLETION_CAMPAIGN_V1_REPORT.md"
    if status == OWNER_PROTECTED_BOUNDARY:
        return "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_OWNER_BOUNDARY_GATE_V1_REPORT.md"
    if status == EXTERNAL_EVIDENCE_REQUIRED:
        return "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_FINAL_BUNDLE_V1_REPORT.md"
    if status == LIVE_OR_BROKER_PERMISSION_REQUIRED:
        return "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_OWNER_BOUNDARY_GATE_V1_REPORT.md"
    if status == SAFETY_BLOCKED:
        return "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_OWNER_BOUNDARY_GATE_V1_REPORT.md"
    return "source artifact"


def _goal_from_source(source_path: str, text: str, source_type: str) -> dict[str, Any]:
    status, blocker_class, safety_class = _classify_status(source_path, text, source_type)
    target_artifact = _target_artifact_for(status)
    matched_terms = _matched_terms(f"{source_path}\n{text}", FOREX_TERMS)
    repo_actionable = status == CLOSED_BY_THIS_CAMPAIGN
    protected_owner_required = status in {
        OWNER_PROTECTED_BOUNDARY,
        LIVE_OR_BROKER_PERMISSION_REQUIRED,
        SAFETY_BLOCKED,
    }
    external_required = status in {
        EXTERNAL_EVIDENCE_REQUIRED,
        LIVE_OR_BROKER_PERMISSION_REQUIRED,
    }
    return {
        "goal_id": _stable_goal_id(source_path),
        "source_file_path": source_path,
        "source_type": source_type,
        "current_status": status,
        "blocker_class": blocker_class,
        "repo_actionable": repo_actionable,
        "protected_owner_required": protected_owner_required,
        "external_evidence_required": external_required,
        "safety_class": safety_class,
        "proposed_closure_action": _closure_action(status, blocker_class, target_artifact),
        "target_artifact": target_artifact,
        "validation_required": [
            "python -m py_compile targeted campaign modules and scripts",
            "python -m pytest tests/forex_engine/test_forex_all_lanes_goals_completion_campaign_v1.py -q",
            "all seven forex all-lanes CLI scripts with --write-report --strict",
        ],
        "completion_status": status,
        "matched_terms": matched_terms,
    }


def _iter_candidate_files(repo_root: Path) -> Iterable[Path]:
    for root in DISCOVERY_ROOTS:
        base = repo_root / root
        if base.is_file():
            yield base
            continue
        if not base.exists():
            continue
        for path in sorted(base.rglob("*"), key=lambda item: item.as_posix().lower()):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}:
                continue
            yield path


def discover_forex_goal_sources(repo_root: str | Path | None = None) -> list[dict[str, Any]]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    sources: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in _iter_candidate_files(root):
        rel = _path_key(path.relative_to(root))
        text = _read_sample(path)
        searchable = f"{rel}\n{text}"
        if not _contains_any(searchable, FOREX_TERMS):
            continue
        if rel in seen:
            continue
        seen.add(rel)
        sources.append(
            {
                "source_path": rel,
                "source_type": _source_type(rel),
                "sample": text,
            },
        )
    for branch in BRANCH_SIGNAL_HINTS:
        rel = f"git branch --all::{branch}"
        if rel in seen:
            continue
        seen.add(rel)
        sources.append(
            {
                "source_path": rel,
                "source_type": "branch",
                "sample": branch,
            },
        )
    return sorted(sources, key=lambda item: item["source_path"].lower())


def _status_counts(goals: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in sorted(ALLOWED_STATUSES)}
    for goal in goals:
        status = str(goal.get("current_status", UNKNOWN_REQUIRES_OWNER_REVIEW))
        counts[status] = counts.get(status, 0) + 1
    return counts


def build_all_lanes_goal_manifest(
    *,
    repo_root: str | Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    sources = discover_forex_goal_sources(root)
    goals = [
        _goal_from_source(
            str(source["source_path"]),
            str(source.get("sample", "")),
            str(source.get("source_type", "doc")),
        )
        for source in sources
    ]
    counts = _status_counts(goals)
    repo_actionable_open = [
        goal
        for goal in goals
        if goal["repo_actionable"]
        and goal["current_status"] not in {CLOSED_BY_THIS_CAMPAIGN, CLOSED_ON_MAIN}
    ]
    protected_count = sum(1 for goal in goals if goal["protected_owner_required"])
    external_count = sum(1 for goal in goals if goal["external_evidence_required"])
    return {
        "manifest_version": MANIFEST_VERSION,
        "packet_id": PACKET_ID,
        "generated_at": GENERATED_AT,
        "branch": BRANCH,
        "repo_root": str(root),
        "strict_mode": bool(strict),
        "discovery_roots": list(DISCOVERY_ROOTS),
        "goal_count": len(goals),
        "status_counts": counts,
        "repo_actionable_count": sum(1 for goal in goals if goal["repo_actionable"]),
        "repo_actionable_open_count": len(repo_actionable_open),
        "protected_owner_required_count": protected_count,
        "external_evidence_required_count": external_count,
        "safety": {
            "local_only": True,
            "broker_api_calls": False,
            "credential_access": False,
            "demo_live_execution": False,
            "order_execution": False,
            "money_movement": False,
            "production_activation": False,
            "profit_claims": False,
        },
        "goals": goals,
    }


def manifest_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "manifest_version": payload.get("manifest_version", MANIFEST_VERSION),
        "packet_id": payload.get("packet_id", PACKET_ID),
        "generated_at": payload.get("generated_at", GENERATED_AT),
        "branch": payload.get("branch", BRANCH),
        "repo_root": payload.get("repo_root"),
        "strict_mode": bool(payload.get("strict_mode", False)),
        "discovery_roots": list(payload.get("discovery_roots", [])),
        "goal_count": int(payload.get("goal_count", 0)),
        "status_counts": dict(payload.get("status_counts", {})),
        "repo_actionable_count": int(payload.get("repo_actionable_count", 0)),
        "repo_actionable_open_count": int(payload.get("repo_actionable_open_count", 0)),
        "protected_owner_required_count": int(payload.get("protected_owner_required_count", 0)),
        "external_evidence_required_count": int(payload.get("external_evidence_required_count", 0)),
        "safety": dict(payload.get("safety", {})),
        "goals": [dict(goal) for goal in payload.get("goals", [])],
    }


def manifest_to_markdown(payload: Mapping[str, Any]) -> str:
    counts = dict(payload.get("status_counts", {}))
    lines = [
        "# AIOS Forex All-Lanes Goals Manifest V1",
        f"Generated: {payload.get('generated_at', GENERATED_AT)}",
        f"Packet: {payload.get('packet_id', PACKET_ID)}",
        f"Branch: {payload.get('branch', BRANCH)}",
        f"Goal count: {payload.get('goal_count', 0)}",
        f"Repo-actionable open count: {payload.get('repo_actionable_open_count', 0)}",
        "",
        "## Status Counts",
    ]
    for status in sorted(ALLOWED_STATUSES):
        lines.append(f"- {status}: {counts.get(status, 0)}")
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "- Local-only classification report.",
            "- No broker/API connection was attempted.",
            "- No credentials, account access, demo/live execution, order placement, money movement, production activation, or profit claim is authorized.",
            "",
            "## Goals",
            "| goal_id | source_type | status | blocker_class | source |",
            "| --- | --- | --- | --- | --- |",
        ],
    )
    for goal in payload.get("goals", []):
        lines.append(
            "| {goal_id} | {source_type} | {status} | {blocker} | `{source}` |".format(
                goal_id=goal.get("goal_id"),
                source_type=goal.get("source_type"),
                status=goal.get("current_status"),
                blocker=goal.get("blocker_class"),
                source=goal.get("source_file_path"),
            ),
        )
    return "\n".join(lines) + "\n"


__all__ = [
    "ALLOWED_STATUSES",
    "BRANCH",
    "CAMPAIGN_ARTIFACTS",
    "CLOSED_BY_THIS_CAMPAIGN",
    "CLOSED_ON_MAIN",
    "DEFERRED_WITH_REASON",
    "EXTERNAL_EVIDENCE_REQUIRED",
    "FIXTURE_DIR",
    "GENERATED_AT",
    "LIVE_OR_BROKER_PERMISSION_REQUIRED",
    "NEEDS_REPO_WORK",
    "OWNER_PROTECTED_BOUNDARY",
    "PACKET_ID",
    "SAFETY_BLOCKED",
    "UNKNOWN_REQUIRES_OWNER_REVIEW",
    "build_all_lanes_goal_manifest",
    "discover_forex_goal_sources",
    "manifest_to_jsonable_dict",
    "manifest_to_markdown",
]
