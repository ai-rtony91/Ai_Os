"""DRY_RUN-only live-arming evidence gap analysis.

This module is a local reporting helper. It checks whether expected readiness
artifacts are present and reuses the existing fail-closed arming checklist, but
it never reads credentials, imports broker SDKs, calls the network, activates
endpoints, or submits orders or trades.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .governed_readiness import (
    REQUIRED_EXCEPTION_FIELDS,
    LiveExecutionBlocked,
    build_live_arming_checklist,
    submit_live_order,
)


REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_LIVE_ARMING_EVIDENCE_GAP_DRY_RUN_V1_REPORT.md"
)
DEFAULT_BASELINE_COMMIT = (
    "6defc062 feat(forex-delivery): checkpoint governed OANDA demo readiness (#791)"
)
MERGED_PR_REFERENCE = "#791 feat(forex-delivery): checkpoint governed OANDA demo readiness"

EXPECTED_EVIDENCE_ARTIFACTS: tuple[dict[str, str], ...] = (
    {
        "path": "docs/forex/AIOS_FOREX_DELIVERY_GOVERNED_PACKET.md",
        "evidence": "governed delivery chain and live-blocking authority references",
    },
    {
        "path": "docs/forex/SINGLE_LIVE_MICRO_TRADE_EXCEPTION_CHECKLIST_TEMPLATE.md",
        "evidence": "required Human Owner exception fields and hard blocks",
    },
    {
        "path": "docs/forex/LIVE_ARMING_EVIDENCE_BUNDLE_TEMPLATE.md",
        "evidence": "sanitized evidence bundle requirements and exclusions",
    },
    {
        "path": "docs/trading_lab/AIOS_FOREX_BUILDER_MONTH_END_READINESS.md",
        "evidence": "month-end readiness contract with live-ready blocked",
    },
    {
        "path": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_PAPER_DEMO_MAPPING.md",
        "evidence": "OANDA-shaped paper/demo mapping boundary",
    },
    {
        "path": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_AUTH_HANDOFF.md",
        "evidence": "sanitized external demo-auth handoff readiness contract",
    },
    {
        "path": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE.md",
        "evidence": "runtime-handoff intake boundary contract",
    },
    {
        "path": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF.md",
        "evidence": "runtime-only handoff boundary contract",
    },
    {
        "path": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_CONNECTION_GATE.md",
        "evidence": "one-shot practice/demo connection gate specification",
    },
    {
        "path": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT.md",
        "evidence": "protected connection attempt boundary and stop controls",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_DELIVERY_GOVERNED_APPLY_V2_REPORT.md",
        "evidence": "governed repo-side readiness completion report",
    },
    {
        "path": "Reports/forex_delivery/AIOS_FOREX_BROKER_SPECIFIC_PAPER_DEMO_INTEGRATION_V1_REPORT.md",
        "evidence": "broker-specific paper/demo integration report",
    },
    {
        "path": "Reports/forex_delivery/AIOS_OANDA_DEMO_AUTH_HANDOFF_READINESS_V1_REPORT.md",
        "evidence": "OANDA demo auth handoff readiness report",
    },
    {
        "path": "Reports/forex_delivery/AIOS_OANDA_DEMO_CONNECTION_GATE_SPEC_V1_REPORT.md",
        "evidence": "OANDA demo connection gate spec report",
    },
    {
        "path": "Reports/forex_delivery/AIOS_OANDA_DEMO_PROBE_RUNTIME_HANDOFF_V1_REPORT.md",
        "evidence": "OANDA demo probe runtime handoff report",
    },
    {
        "path": "Reports/forex_delivery/AIOS_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_V1_REPORT.md",
        "evidence": "OANDA demo runtime handoff intake report",
    },
    {
        "path": "Reports/forex_delivery/AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_V1_REPORT.md",
        "evidence": "OANDA protected connection attempt report",
    },
    {
        "path": "scripts/forex_delivery/validate_forex_delivery_readiness.py",
        "evidence": "paper and live-arming-check CLI remains DRY_RUN only",
    },
    {
        "path": "src/forex_delivery/governed_readiness.py",
        "evidence": "fail-closed governed readiness functions",
    },
    {
        "path": "tests/forex_delivery/test_governed_readiness.py",
        "evidence": "tests covering paper-only and live-submit blocked behavior",
    },
)

EXISTING_READINESS_GATES: tuple[dict[str, str], ...] = (
    {
        "gate": "AI_OS packet and protected-action governance",
        "source": "AGENTS.md and docs/forex/AIOS_FOREX_DELIVERY_GOVERNED_PACKET.md",
        "status": "present by repo governance reference",
    },
    {
        "gate": "Single Live Micro-Trade Exception checklist",
        "source": "docs/forex/SINGLE_LIVE_MICRO_TRADE_EXCEPTION_CHECKLIST_TEMPLATE.md",
        "status": "present as template only; no approval present",
    },
    {
        "gate": "Live arming evidence bundle",
        "source": "docs/forex/LIVE_ARMING_EVIDENCE_BUNDLE_TEMPLATE.md",
        "status": "present as template only; no completed bundle present",
    },
    {
        "gate": "OANDA demo auth handoff readiness",
        "source": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_AUTH_HANDOFF.md",
        "status": "present; default governed flow blocks when metadata is absent",
    },
    {
        "gate": "OANDA demo runtime handoff intake",
        "source": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE.md",
        "status": "present; sanitized metadata only",
    },
    {
        "gate": "OANDA demo runtime handoff",
        "source": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF.md",
        "status": "present; runtime boundary only",
    },
    {
        "gate": "OANDA demo connection gate",
        "source": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_CONNECTION_GATE.md",
        "status": "present; readiness review only, no connection attempt",
    },
    {
        "gate": "OANDA protected demo connection attempt",
        "source": "docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT.md",
        "status": "present; blocked without external runtime connector",
    },
    {
        "gate": "Governed live arming checklist function",
        "source": "src/forex_delivery/governed_readiness.py",
        "status": "present; returns live_execution_allowed false",
    },
)

MISSING_EVIDENCE: tuple[str, ...] = (
    "No active Human Owner-approved Single Live Micro-Trade Exception field set.",
    "No completed sanitized live arming evidence bundle.",
    "No approved broker path reference under Human Owner control.",
    "No active approval window with start and expiry.",
    "No approved maximum loss, daily loss cap, stop loss, order type, or exact size field set.",
    "No live account mode confirmation suitable for arming review.",
    "No paper/live mode confirmation suitable for arming review.",
    "No protected external runtime connector evidence available to the repo.",
    "No sanitized proof of a completed OANDA practice/demo connection attempt.",
    "No kill-switch, final disarm, timeout, and terminal-result evidence bundle for live exception use.",
    "No approval hash or equivalent Human Owner approval verification evidence.",
    "No final report path for a future terminal live exception result.",
)

HARD_BLOCKERS: tuple[str, ...] = (
    "Live order submission remains blocked by governed readiness and RISK_POLICY.md references.",
    "The arming checklist is missing every required exception field by default.",
    "Human Owner approval is absent.",
    "Credential material and account identifiers are not present in the repo and must not be added.",
    "No live endpoint, live account access, broker request, market-data request, account-state request, order route, or trade route is authorized.",
    "The OANDA protected connection attempt path has no injected external runtime connector evidence.",
    "Any future network, broker, secret, commit, push, PR, merge, or live-trading action requires separate protected approval.",
)

HUMAN_APPROVAL_GATES: tuple[str, ...] = (
    "Human Owner approval for a completed Single Live Micro-Trade Exception field set.",
    "Human Owner approval for any protected OANDA practice/demo network or broker-call attempt.",
    "Human Owner confirmation that auth material remains external operator-controlled and never enters the repo.",
    "Human Owner approval for any future credential handling outside the repo boundary.",
    "Human Owner approval for any future live account mode confirmation.",
    "Separate protected-action approval for commit, push, PR creation, merge, or branch actions.",
)

PAPER_DEMO_ONLY_SCOPE: tuple[str, ...] = (
    "Governed readiness validation.",
    "Paper/demo broker adapter evidence.",
    "OANDA-shaped paper/demo mapping.",
    "OANDA auth/runtime/connection gate metadata validation.",
    "Live arming checklist completeness review.",
    "Local sanitized reports and tests.",
)

NEXT_PACKET_RECOMMENDATION = {
    "packet_id": "AIOS-FOREX-LIVE-EXCEPTION-EVIDENCE-BUNDLE-COMPLETENESS-DRY-RUN-V1",
    "mode": "DRY_RUN",
    "lane": "FOREX_DELIVERY",
    "scope": (
        "Inspect only whether a Human Owner-supplied sanitized evidence bundle "
        "exists and maps to the Single Live Micro-Trade Exception checklist. "
        "No credentials, broker connection, network call, live endpoint, order, "
        "trade, commit, push, PR, or merge."
    ),
    "stop_point": "Stop after completeness report and no-live safety confirmation.",
}


def build_live_arming_evidence_gap_analysis(
    *,
    repo_root: str | Path | None = None,
    baseline_commit: str = DEFAULT_BASELINE_COMMIT,
    merged_pr_reference: str = MERGED_PR_REFERENCE,
) -> dict[str, Any]:
    """Build a deterministic fail-closed evidence gap analysis."""

    root = Path(repo_root) if repo_root is not None else Path.cwd()
    artifacts = _artifact_presence(root)
    checklist = build_live_arming_checklist({})
    live_submit_probe = _probe_live_submit_block()
    missing_artifact_paths = [
        artifact["path"] for artifact in artifacts if artifact["present"] is False
    ]
    status = _status_for(
        missing_artifact_paths=missing_artifact_paths,
        live_submit_probe=live_submit_probe,
    )

    return {
        "schema": "AIOS_FOREX_LIVE_ARMING_EVIDENCE_GAP_DRY_RUN.v1",
        "status": status,
        "mode": "DRY_RUN_ANALYSIS_ONLY",
        "baseline_commit": baseline_commit,
        "merged_pr_reference": merged_pr_reference,
        "report_path": REPORT_PATH,
        "existing_readiness_gates": list(EXISTING_READINESS_GATES),
        "evidence_artifacts": artifacts,
        "missing_artifact_paths": missing_artifact_paths,
        "required_exception_fields": list(REQUIRED_EXCEPTION_FIELDS),
        "missing_exception_fields": list(checklist["missing_fields"]),
        "checklist_blocker_reasons": list(checklist["blocker_reasons"]),
        "missing_evidence": list(MISSING_EVIDENCE),
        "hard_blockers": list(HARD_BLOCKERS),
        "human_approval_gates": list(HUMAN_APPROVAL_GATES),
        "paper_demo_only_scope": list(PAPER_DEMO_ONLY_SCOPE),
        "live_submit_probe": live_submit_probe,
        "ready_for_live_arming_review": False,
        "live_execution_allowed": False,
        "order_submit_allowed": False,
        "requirements": {
            "credentials_required": False,
            "network_required": False,
            "broker_sdk_required": False,
            "account_identifiers_required": False,
            "orders_required": False,
            "trades_required": False,
        },
        "no_live_action_confirmation": {
            "credential_values_read": False,
            "network_used": False,
            "broker_sdk_used": False,
            "account_identifiers_used": False,
            "live_endpoint_activated": False,
            "broker_request_sent": False,
            "order_route_enabled": False,
            "order_submitted": False,
            "trade_submitted": False,
            "scheduler_or_daemon_started": False,
        },
        "end_of_month_milestone_recommendation": (
            "Count PR #791 as a governed OANDA demo readiness checkpoint only. "
            "Do not call it live-ready. The milestone is ready for a DRY_RUN "
            "evidence-bundle completeness review, not for arming."
        ),
        "next_packet_recommendation": dict(NEXT_PACKET_RECOMMENDATION),
    }


def render_live_arming_evidence_gap_markdown(analysis: dict[str, Any]) -> str:
    """Render the analysis as the governed markdown report."""

    lines = [
        "# AIOS Forex Live-Arming Evidence Gap DRY_RUN V1 Report",
        "",
        "Status: blocker/gap report only. This report does not enable live trading.",
        "",
        "## Packet Context",
        "",
        f"- Current baseline commit: `{analysis['baseline_commit']}`",
        f"- Merged PR reference: `{analysis['merged_pr_reference']}`",
        "- Mode: `DRY_RUN_ANALYSIS_ONLY`",
        "- Lane: `FOREX_DELIVERY`",
        "- Live enablement: blocked",
        "",
        "## Existing Readiness Gates Found",
        "",
        "| Gate | Source | Status |",
        "|---|---|---|",
    ]
    for gate in analysis["existing_readiness_gates"]:
        lines.append(f"| {gate['gate']} | `{gate['source']}` | {gate['status']} |")

    lines.extend(
        [
            "",
            "## Existing OANDA Demo/Paper Artifacts Found",
            "",
            "| Artifact | Evidence | Status |",
            "|---|---|---|",
        ]
    )
    for artifact in analysis["evidence_artifacts"]:
        status = "FOUND" if artifact["present"] else "MISSING"
        lines.append(f"| `{artifact['path']}` | {artifact['evidence']} | {status} |")

    lines.extend(
        [
            "",
            "## Existing Evidence",
            "",
            "- Repo-side governed readiness chain exists.",
            "- OANDA-shaped paper/demo mapping exists.",
            "- OANDA demo auth, runtime handoff, connection gate, and protected attempt contracts exist.",
            "- The live arming checklist function exists and returns blocked by default.",
            "- Existing tests cover paper-only behavior and live-submit refusal.",
            "",
            "## Missing Evidence",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in analysis["missing_evidence"])
    lines.extend(["", "Missing required exception fields:"])
    lines.extend(f"- `{field}`" for field in analysis["missing_exception_fields"])

    lines.extend(["", "## Hard Blockers", ""])
    lines.extend(f"- {item}" for item in analysis["hard_blockers"])
    if analysis["missing_artifact_paths"]:
        lines.extend(["", "Missing expected repo artifacts:"])
        lines.extend(f"- `{path}`" for path in analysis["missing_artifact_paths"])

    lines.extend(["", "## Human Approval Gates Required Later", ""])
    lines.extend(f"- {item}" for item in analysis["human_approval_gates"])

    lines.extend(["", "## Strictly Paper/Demo Only", ""])
    lines.extend(f"- {item}" for item in analysis["paper_demo_only_scope"])

    safety = analysis["no_live_action_confirmation"]
    lines.extend(
        [
            "",
            "## No-Live-Action Confirmation",
            "",
            f"- Credential values read: `{safety['credential_values_read']}`",
            f"- Network used: `{safety['network_used']}`",
            f"- Broker SDK used: `{safety['broker_sdk_used']}`",
            f"- Account identifiers used: `{safety['account_identifiers_used']}`",
            f"- Live endpoint activated: `{safety['live_endpoint_activated']}`",
            f"- Broker request sent: `{safety['broker_request_sent']}`",
            f"- Order route enabled: `{safety['order_route_enabled']}`",
            f"- Order submitted: `{safety['order_submitted']}`",
            f"- Trade submitted: `{safety['trade_submitted']}`",
            f"- Scheduler or daemon started: `{safety['scheduler_or_daemon_started']}`",
            f"- Live submit probe blocked: `{analysis['live_submit_probe']['blocked']}`",
            "",
            "## End-Of-Month Milestone Recommendation",
            "",
            analysis["end_of_month_milestone_recommendation"],
            "",
            "## Exact Next Packet Recommendation",
            "",
        ]
    )
    next_packet = analysis["next_packet_recommendation"]
    lines.extend(
        [
            f"- Packet ID: `{next_packet['packet_id']}`",
            f"- Mode: `{next_packet['mode']}`",
            f"- Lane: `{next_packet['lane']}`",
            f"- Scope: {next_packet['scope']}",
            f"- Stop point: {next_packet['stop_point']}",
            "",
            "## Final Status",
            "",
            f"- Analyzer status: `{analysis['status']}`",
            "- Ready for live arming review: `False`",
            "- Live execution allowed: `False`",
            "- Order submit allowed: `False`",
        ]
    )
    return "\n".join(lines) + "\n"


def _artifact_presence(root: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for artifact in EXPECTED_EVIDENCE_ARTIFACTS:
        path = artifact["path"]
        artifacts.append(
            {
                "path": path,
                "evidence": artifact["evidence"],
                "present": (root / path).is_file(),
            }
        )
    return artifacts


def _probe_live_submit_block() -> dict[str, Any]:
    try:
        submit_live_order({})
    except LiveExecutionBlocked as exc:
        return {
            "blocked": True,
            "error_type": type(exc).__name__,
            "message": str(exc),
        }
    except Exception as exc:  # pragma: no cover - defensive fail-closed branch
        return {
            "blocked": True,
            "error_type": type(exc).__name__,
            "message": str(exc),
        }
    return {
        "blocked": False,
        "error_type": "UNSAFE_LIVE_SUBMIT_NOT_BLOCKED",
        "message": "Live submit probe returned without fail-closed exception.",
    }


def _status_for(
    *,
    missing_artifact_paths: list[str],
    live_submit_probe: dict[str, Any],
) -> str:
    if live_submit_probe["blocked"] is not True:
        return "UNSAFE_LIVE_SUBMIT_NOT_BLOCKED"
    if missing_artifact_paths:
        return "BLOCKED_EVIDENCE_ARTIFACTS_MISSING"
    return "BLOCKED_PENDING_HUMAN_OWNER_EXCEPTION_EVIDENCE"
