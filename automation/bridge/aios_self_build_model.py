from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class SelfBuildRecommendation:
    recommendation_id: str
    created_utc: str
    title: str
    problem: str
    evidence: list[str]
    risk_tier: str
    suggested_mode: str
    suggested_lane: str
    suggested_allowed_paths: list[str]
    suggested_forbidden_paths: list[str]
    suggested_validator_chain: list[str]
    protected_actions: list[str]
    approval_required: bool
    safe_next_prompt: str
    status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_recommendations(timestamp_utc: str, phase_summaries: dict[str, object]) -> list[SelfBuildRecommendation]:
    recommendations = [
        SelfBuildRecommendation(
            recommendation_id="AIOS-SB-001",
            created_utc=timestamp_utc,
            title="Add approval inbox schema validator",
            problem="Approval evidence exists in multiple places and needs a local schema validator before promotion.",
            evidence=["automation/orchestration/approval_inbox/", "telemetry/approval_inbox/"],
            risk_tier="LOCAL_APPLY",
            suggested_mode="DRY_RUN",
            suggested_lane="APPROVAL_INBOX_SCHEMA_VALIDATOR_ONLY",
            suggested_allowed_paths=["automation/validators/", "tests/governance/", "Reports/"],
            suggested_forbidden_paths=["AGENTS.md", "README.md", "docs/architecture/AI_OS_WHITEPAPER.md"],
            suggested_validator_chain=["python -m pytest tests/governance", "git diff --check"],
            protected_actions=[],
            approval_required=True,
            safe_next_prompt="Packet draft required: validate approval inbox schema without mutating approvals.",
            status="READY_FOR_PACKET",
        ),
        SelfBuildRecommendation(
            recommendation_id="AIOS-SB-002",
            created_utc=timestamp_utc,
            title="Wire validator registry into bridge status",
            problem="Validators are discoverable but not yet enforced by a single local command.",
            evidence=["automation/validators/", "automation/orchestration/validators/"],
            risk_tier="LOCAL_APPLY",
            suggested_mode="DRY_RUN",
            suggested_lane="VALIDATOR_REGISTRY_BRIDGE_ONLY",
            suggested_allowed_paths=["automation/bridge/", "telemetry/validator_results/", "tests/operator_relief/"],
            suggested_forbidden_paths=["AGENTS.md", "README.md", ".github/workflows/"],
            suggested_validator_chain=["python automation/bridge/aios_phase_bridge.py --mode DRY_RUN --repo-root ."],
            protected_actions=[],
            approval_required=True,
            safe_next_prompt="Packet draft required: connect validator registry evidence to bridge status only.",
            status="READY_FOR_PACKET",
        ),
        SelfBuildRecommendation(
            recommendation_id="AIOS-SB-003",
            created_utc=timestamp_utc,
            title="Keep live broker execution blocked",
            problem="Any live broker execution path remains production/live and is blocked.",
            evidence=["AGENTS.md Trading Safety Rules", "README.md Trading Lab Boundary"],
            risk_tier="PRODUCTION_OR_LIVE_BLOCKED",
            suggested_mode="DRY_RUN",
            suggested_lane="TRADING_BOUNDARY_REVIEW_ONLY",
            suggested_allowed_paths=["Reports/"],
            suggested_forbidden_paths=["apps/trading_lab/trading_lab/execution/", "aios/modules/trader/", ".env"],
            suggested_validator_chain=["safe risk-term scan only"],
            protected_actions=["broker_execution", "live_trading"],
            approval_required=True,
            safe_next_prompt="No execution packet recommended for live broker work.",
            status="BLOCKED",
        ),
    ]
    if phase_summaries.get("missing_expected_files"):
        recommendations.append(
            SelfBuildRecommendation(
                recommendation_id="AIOS-SB-004",
                created_utc=timestamp_utc,
                title="Repair missing optional authority references",
                problem="Optional startup authority files were missing during bridge inventory.",
                evidence=list(phase_summaries.get("missing_expected_files", [])),
                risk_tier="DRY_RUN_PLAN",
                suggested_mode="DRY_RUN",
                suggested_lane="AUTHORITY_REFERENCE_REPAIR_PLAN_ONLY",
                suggested_allowed_paths=["Reports/", "docs/workflows/"],
                suggested_forbidden_paths=["AGENTS.md", "README.md"],
                suggested_validator_chain=["git diff --check"],
                protected_actions=[],
                approval_required=False,
                safe_next_prompt="Create a read-only repair plan before editing authority references.",
                status="WAIT",
            )
        )
    return recommendations

