"""Deterministic live evidence requirement matrix for demo expectancy review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping, Sequence


OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_VERSION = (
    "oanda_demo_live_evidence_requirement_matrix_v1"
)
VERSION = OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_VERSION

CLASSIFICATION_READY = "OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_READY"
CLASSIFICATION_BLOCKED_EMPTY = "OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_BLOCKED_EMPTY"
CLASSIFICATION_BLOCKED_UNSAFE = "OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_BLOCKED_UNSAFE"

OWNER_WARNING = "Do not execute unless Anthony explicitly approves."
LIVE_GAP_WARNING = (
    "Live evidence gap review only. Codex is not authorized to execute, call a broker, "
    "access credentials, place orders, or approve live trading."
)

ALLOWED_EVIDENCE_STATUSES = ("PRESENT", "MISSING", "BLOCKED", "OWNER_ACTION_REQUIRED")

PERMISSION_DEFAULTS: dict[str, bool] = {
    "demo_execution_allowed": False,
    "broker_action_allowed": False,
    "real_money_allowed": False,
    "compounding_allowed": False,
    "bank_movement_allowed": False,
    "live_trading_allowed": False,
    "credential_access_allowed": False,
    "account_id_persistence_allowed": False,
    "autonomous_execution_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
    "live_micro_trade_exception_allowed": False,
    "live_evidence_bundle_approved": False,
}


@dataclass(frozen=True)
class OandaDemoLiveEvidenceRequirement:
    item_id: str
    category: str
    evidence_status: str
    description: str
    owner_action_required_when_missing: bool = True
    required: bool = True


@dataclass(frozen=True)
class OandaDemoLiveEvidenceRequirementMatrixConfig:
    requirements: Sequence[OandaDemoLiveEvidenceRequirement] | None = None
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)
    next_safe_action: str = (
        "Use this matrix to map demo expectancy proof into a preview-only live evidence gap review."
    )


@dataclass(frozen=True)
class OandaDemoLiveEvidenceRequirementMatrixResult:
    version: str
    classification: str
    requirement_count: int
    requirements: tuple[OandaDemoLiveEvidenceRequirement, ...]
    required_item_ids: tuple[str, ...]
    allowed_evidence_statuses: tuple[str, ...]
    owner_warning: str
    live_gap_warning: str
    next_safe_action: str
    protected_permission_flags: Mapping[str, bool]
    safety_notes: tuple[str, ...]
    metric_requirement_count: Decimal


def build_default_oanda_demo_live_evidence_requirements() -> tuple[OandaDemoLiveEvidenceRequirement, ...]:
    item_rows = (
        (
            "human_owner_live_exception_approval",
            "owner_approval",
            "Human Owner must approve any future live micro-trade exception separately.",
        ),
        (
            "live_account_boundary_verified",
            "account_boundary",
            "Live account boundary must be verified without storing account identifiers.",
        ),
        (
            "demo_account_boundary_verified",
            "account_boundary",
            "Demo account boundary must be verified separately from live account scope.",
        ),
        (
            "credential_boundary_verified",
            "credential_boundary",
            "Credential handling boundary must be reviewed without reading secrets.",
        ),
        (
            "secret_redaction_verified",
            "data_safety",
            "Secret redaction proof must be present before any owner exception review.",
        ),
        (
            "account_id_redaction_verified",
            "data_safety",
            "Account identifier redaction proof must be present in every review artifact.",
        ),
        (
            "live_endpoint_denial_or_boundary_proof",
            "endpoint_boundary",
            "Live endpoint denial or boundary proof must be documented before review.",
        ),
        (
            "broker_permissions_verified",
            "permission_boundary",
            "Broker permissions must be reviewed without granting Codex broker action authority.",
        ),
        (
            "max_loss_policy_verified",
            "risk_policy",
            "Maximum loss policy must be explicitly verified.",
        ),
        (
            "position_size_policy_verified",
            "risk_policy",
            "Position size policy must be explicitly verified.",
        ),
        (
            "daily_loss_limit_verified",
            "risk_policy",
            "Daily loss limit policy must be explicitly verified.",
        ),
        (
            "kill_switch_verified",
            "abort_control",
            "Kill switch proof must be present before any exception can be reviewed.",
        ),
        (
            "timeout_abort_verified",
            "abort_control",
            "Timeout abort behavior must be documented.",
        ),
        (
            "rollback_plan_verified",
            "recovery",
            "Rollback plan must be ready before owner exception review.",
        ),
        (
            "final_disarm_plan_verified",
            "recovery",
            "Final disarm plan must be present and owner-readable.",
        ),
        (
            "monitoring_plan_verified",
            "monitoring",
            "Monitoring plan must be documented.",
        ),
        (
            "audit_log_plan_verified",
            "audit",
            "Audit log plan must be documented.",
        ),
        (
            "order_ticket_review_verified",
            "order_review",
            "Order ticket review must be completed as evidence, not as approval.",
        ),
        (
            "spread_market_hours_review_verified",
            "market_review",
            "Spread and market hours review must be documented.",
        ),
        (
            "duplicate_order_guard_verified",
            "order_safety",
            "Duplicate order guard proof must be documented.",
        ),
        (
            "read_only_reconciliation_verified",
            "reconciliation",
            "Read-only reconciliation proof must be present.",
        ),
        (
            "post_trade_journal_plan_verified",
            "journal",
            "Post-trade journal plan must be present before exception review.",
        ),
        (
            "reconciliation_plan_verified",
            "reconciliation",
            "Reconciliation plan must be present.",
        ),
        (
            "one_shot_only_scope_verified",
            "scope_control",
            "One-shot-only scope must be verified.",
        ),
        (
            "no_compounding_scope_verified",
            "scope_control",
            "No-compounding scope must be verified.",
        ),
        (
            "no_bank_movement_scope_verified",
            "scope_control",
            "No bank movement scope must be verified.",
        ),
        (
            "no_autonomous_loop_scope_verified",
            "scope_control",
            "No autonomous loop scope must be verified.",
        ),
        (
            "evidence_bundle_owner_review_verified",
            "owner_review",
            "Evidence bundle owner review must be completed separately.",
        ),
    )
    return tuple(
        OandaDemoLiveEvidenceRequirement(
            item_id=item_id,
            category=category,
            evidence_status="OWNER_ACTION_REQUIRED",
            description=description,
        )
        for item_id, category, description in item_rows
    )


def build_sample_live_evidence_requirement_matrix_ready_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return OandaDemoLiveEvidenceRequirementMatrixConfig()


def build_sample_live_evidence_requirement_matrix_blocked_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return OandaDemoLiveEvidenceRequirementMatrixConfig(requirements=())


def build_sample_live_evidence_requirement_matrix_unsafe_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return OandaDemoLiveEvidenceRequirementMatrixConfig(unsafe_flags={"unsafe_source_state": True})


def build_sample_strong_expectancy_missing_live_evidence_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return build_sample_live_evidence_requirement_matrix_ready_input()


def build_sample_strong_expectancy_partial_live_evidence_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return build_sample_live_evidence_requirement_matrix_ready_input()


def build_sample_weak_expectancy_blocked_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return build_sample_live_evidence_requirement_matrix_blocked_input()


def build_sample_rejected_expectancy_blocked_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return build_sample_live_evidence_requirement_matrix_blocked_input()


def build_sample_unsafe_expectancy_blocked_input() -> OandaDemoLiveEvidenceRequirementMatrixConfig:
    return build_sample_live_evidence_requirement_matrix_unsafe_input()


def build_oanda_demo_live_evidence_requirement_matrix(
    config: OandaDemoLiveEvidenceRequirementMatrixConfig | None = None,
) -> OandaDemoLiveEvidenceRequirementMatrixResult:
    resolved_config = config or OandaDemoLiveEvidenceRequirementMatrixConfig()
    requirements = tuple(
        resolved_config.requirements
        if resolved_config.requirements is not None
        else build_default_oanda_demo_live_evidence_requirements()
    )
    unsafe = any(bool(value) for value in resolved_config.unsafe_flags.values())
    if unsafe:
        classification = CLASSIFICATION_BLOCKED_UNSAFE
        next_safe_action = "Stop and resolve unsafe source or policy flags before any gap review."
    elif not requirements:
        classification = CLASSIFICATION_BLOCKED_EMPTY
        next_safe_action = "Stop and restore the live evidence requirement matrix before gap review."
    else:
        classification = CLASSIFICATION_READY
        next_safe_action = resolved_config.next_safe_action
    return OandaDemoLiveEvidenceRequirementMatrixResult(
        version=VERSION,
        classification=classification,
        requirement_count=len(requirements),
        requirements=requirements,
        required_item_ids=tuple(requirement.item_id for requirement in requirements),
        allowed_evidence_statuses=ALLOWED_EVIDENCE_STATUSES,
        owner_warning=OWNER_WARNING,
        live_gap_warning=LIVE_GAP_WARNING,
        next_safe_action=next_safe_action,
        protected_permission_flags=dict(PERMISSION_DEFAULTS),
        safety_notes=(
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "Live profitable execution remains blocked.",
        ),
        metric_requirement_count=Decimal(len(requirements)),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict(
    result: OandaDemoLiveEvidenceRequirementMatrixResult,
) -> dict[str, Any]:
    return _jsonable(result)


def oanda_demo_live_evidence_requirement_matrix_to_operator_text(
    result: OandaDemoLiveEvidenceRequirementMatrixResult,
) -> str:
    return "\n".join(
        (
            f"Live evidence requirement matrix status: {result.classification}.",
            f"Requirement count: {result.requirement_count}.",
            result.owner_warning,
            result.live_gap_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "Live profitable execution remains blocked.",
            f"Next safe action: {result.next_safe_action}",
        )
    )


def oanda_demo_live_evidence_requirement_matrix_to_markdown(
    result: OandaDemoLiveEvidenceRequirementMatrixResult,
) -> str:
    rows = [
        "# OANDA Demo Live Evidence Requirement Matrix V1",
        "",
        f"- Classification: {result.classification}",
        f"- Requirement count: {result.requirement_count}",
        f"- Owner warning: {result.owner_warning}",
        f"- Live gap warning: {result.live_gap_warning}",
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- Live profitable execution remains blocked.",
        "",
        "## Requirements",
    ]
    for requirement in result.requirements:
        rows.append(
            f"- `{requirement.item_id}` | {requirement.category} | {requirement.evidence_status}"
        )
    rows.extend(
        (
            "",
            "## Permissions",
        )
    )
    for key in sorted(result.protected_permission_flags):
        rows.append(f"- `{key}`: {str(result.protected_permission_flags[key]).lower()}")
    rows.extend(("", f"Next safe action: {result.next_safe_action}"))
    return "\n".join(rows) + "\n"
