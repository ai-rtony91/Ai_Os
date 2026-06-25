"""Local-only AIOS Forex Profit Autonomy Master Bucket Pack V1.

This module defines the ordered bucket sequence, evaluates current readiness,
and emits deterministic operator text, JSON-safe data, and markdown. It does
not call brokers, read credentials, read .env files, place orders, mutate repo
state, start automation, or enable live trading.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Mapping, Sequence


PROFIT_AUTONOMY_MASTER_BUCKET_VERSION = "profit_autonomy_master_bucket_pack_v1"
BUCKET_ID = "AIOS-FOREX-PROFIT-AUTONOMY-MASTER-BUCKET-PACK-V1"

BUCKET_STATUS_CURRENT_REVIEW_READY_SELECTOR_LOCAL_ONLY = (
    "BUCKET_STATUS_CURRENT_REVIEW_READY_SELECTOR_LOCAL_ONLY"
)
BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED = (
    "BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED"
)
BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED = (
    "BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED"
)
BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED = (
    "BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED"
)
BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED = (
    "BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED"
)
BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED = (
    "BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED"
)
BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR = (
    "BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR"
)
BUCKET_STATUS_BLOCKED_BY_MISSING_PROFIT_PROOF = (
    "BUCKET_STATUS_BLOCKED_BY_MISSING_PROFIT_PROOF"
)
BUCKET_STATUS_BLOCKED_BY_MISSING_BROKER_STATE = (
    "BUCKET_STATUS_BLOCKED_BY_MISSING_BROKER_STATE"
)
BUCKET_STATUS_BLOCKED_BY_MISSING_RISK_CONTROLS = (
    "BUCKET_STATUS_BLOCKED_BY_MISSING_RISK_CONTROLS"
)
BUCKET_STATUS_BLOCKED_BY_OWNER_APPROVAL = "BUCKET_STATUS_BLOCKED_BY_OWNER_APPROVAL"
BUCKET_STATUS_BLOCKED_REAL_MONEY_NOT_ALLOWED = (
    "BUCKET_STATUS_BLOCKED_REAL_MONEY_NOT_ALLOWED"
)
BUCKET_STATUS_BLOCKED_COMPOUNDING_NOT_ALLOWED = (
    "BUCKET_STATUS_BLOCKED_COMPOUNDING_NOT_ALLOWED"
)
BUCKET_STATUS_BLOCKED_BANK_MOVEMENT_NOT_ALLOWED = (
    "BUCKET_STATUS_BLOCKED_BANK_MOVEMENT_NOT_ALLOWED"
)
BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_NOT_READY = (
    "BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_NOT_READY"
)
BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED = (
    "BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED"
)

LANDED_MILESTONES = (
    "MILESTONE:PR-1109-PROFIT-VALIDATION-LOOP-V1-LANDED",
    "MILESTONE:PR-1110-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1-LANDED",
    "MILESTONE:PR-1111-CANDIDATE-EVIDENCE-INTAKE-V1-LANDED",
    "MILESTONE:PR-1112-CANDIDATE-TO-GATE-BRIDGE-V1-LANDED",
)

LOCAL_SELECTOR_DEPENDENCIES = (
    "automation/forex_engine/review_ready_candidate_selector_v1.py",
    "scripts/forex_delivery/run_review_ready_candidate_selector_v1.py",
    "tests/forex_engine/test_review_ready_candidate_selector_v1.py",
    "Reports/forex_delivery/AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1_REPORT.md",
)

REQUIRED_PROOF_CATEGORIES = (
    "candidate_evidence_present",
    "selector_present",
    "sample_size_sufficient",
    "expectancy_positive",
    "profit_factor_sufficient",
    "max_drawdown_within_limit",
    "consecutive_losses_within_limit",
    "walk_forward_passed",
    "out_of_sample_passed",
    "market_regime_coverage",
    "spread_sensitivity_passed",
    "slippage_sensitivity_passed",
    "latency_sensitivity_passed",
    "news_filter_validated",
    "demo_execution_reconciled",
    "broker_state_reconciled",
    "risk_controls_reconciled",
    "post_trade_reconciliation_passed",
    "loss_response_validated",
    "strategy_decay_monitor_present",
    "real_money_evidence_present",
    "compounding_evidence_present",
    "bank_movement_policy_present",
    "owner_approval_present",
)


@dataclass(frozen=True)
class BucketGate:
    gate_id: str
    title: str
    required_evidence: tuple[str, ...]
    validators: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    owner_approval_required: bool = True


@dataclass(frozen=True)
class BucketStage:
    stage_id: str
    title: str
    phase: str
    lane: str
    category: str
    status_hint: str
    objective: str
    why_it_matters: str
    entry_criteria: tuple[str, ...]
    exit_criteria: tuple[str, ...]
    creates_or_changes: tuple[str, ...]
    validators: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    owner_approval_required: bool
    protected_action: bool
    depends_on: tuple[str, ...]
    next_stage_id: str
    codex_packet_intent: str
    stop_point: str
    evidence_required: tuple[str, ...]
    failure_label: str


@dataclass(frozen=True)
class BucketStageResult:
    stage_id: str
    status: str
    passed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_safe_action: str


@dataclass(frozen=True)
class BucketPermissionState:
    candidate_review_allowed: bool = False
    next_demo_trade_allowed: bool = False
    broker_action_allowed: bool = False
    real_money_allowed: bool = False
    compounding_allowed: bool = False
    bank_movement_allowed: bool = False
    live_trading_allowed: bool = False
    scheduler_allowed: bool = False
    daemon_allowed: bool = False
    credential_access_allowed: bool = False
    repo_commit_allowed: bool = False
    repo_push_allowed: bool = False
    pr_creation_allowed: bool = False
    owner_approval_required: bool = True


@dataclass(frozen=True)
class BucketCurrentState:
    selector_present: bool = False
    selector_local_only: bool = False
    selector_landed: bool = False
    proof_ledger_present: bool = False
    broker_read_only_state_present: bool = False
    risk_envelope_present: bool = False
    demo_permission_envelope_present: bool = False
    demo_review_path_ready: bool = False
    owner_demo_approval_present: bool = False
    source_files_missing: tuple[str, ...] = field(default_factory=tuple)
    local_dependencies: tuple[str, ...] = field(default_factory=tuple)
    landed_milestones: tuple[str, ...] = LANDED_MILESTONES


@dataclass(frozen=True)
class BucketEvaluationResult:
    bucket_id: str
    bucket_version: str
    selector_status: str
    current_status: str
    current_stage_id: str
    next_stage_id: str
    next_safe_action: str
    next_codex_packet_intent: str
    landed_milestones: tuple[str, ...]
    local_dependencies: tuple[str, ...]
    source_files_missing: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    permissions: BucketPermissionState
    stages: tuple[BucketStage, ...]
    stage_results: tuple[BucketStageResult, ...]
    proof_summary: Mapping[str, bool]
    guaranteed_profit_target: bool
    guaranteed_profit_proven: bool
    operator_answer: str


def build_master_bucket_stages() -> tuple[BucketStage, ...]:
    """Return the deterministic stage sequence for the master bucket."""

    stages = (
        _stage(
            "FX-BUCKET-00-STATE-AUTHORITY-PREFLIGHT",
            "State, Authority, and Dirty-File Preflight",
            "authority",
            "repo-state",
            "Confirm repo, branch, dirty files, AGENTS.md, README.md, whitepaper, source-of-truth map, and active system map.",
            "Wrong path, stale state, or conflicting authority can invalidate every later trading decision.",
            (),
            "FX-BUCKET-01-SELECTOR-LANDED-GATE",
            "Run read-only state and authority preflight before any bucket mutation.",
            ("worktree_verified", "authority_stack_read", "dirty_files_classified"),
            ("wrong_worktree", "unrelated_dirty_files", "conflicting_authority"),
        ),
        _stage(
            "FX-BUCKET-01-SELECTOR-LANDED-GATE",
            "Review-Ready Candidate Selector Landing Gate",
            "selector",
            "repo-protected-action",
            "Complete selector local validation, then require commit, push, PR, checks, and merge through protected-action approval.",
            "The selector is current local dependency work and must be landed before more feature layers depend on it.",
            ("FX-BUCKET-00-STATE-AUTHORITY-PREFLIGHT",),
            "FX-BUCKET-02-PROFIT-PROOF-LEDGER",
            "Prepare protected selector landing packet; do not stage or commit from this bucket.",
            ("selector_files_present", "selector_tests_passed", "protected_commit_pr_merge_approval"),
            ("stage", "commit", "push", "pr_create", "merge"),
            protected_action=True,
        ),
        _stage(
            "FX-BUCKET-02-PROFIT-PROOF-LEDGER",
            "Profit Proof Ledger V1",
            "proof",
            "profit-proof-ledger",
            "Centralize evidence proving or blocking profit-autonomy claims.",
            "Guaranteed profit autonomy is a proof target, not a claim. Missing proof must block readiness.",
            ("FX-BUCKET-01-SELECTOR-LANDED-GATE",),
            "FX-BUCKET-03-CANDIDATE-REVIEW-DECISION-PACKET",
            "Build a local-only proof ledger with all required proof categories.",
            REQUIRED_PROOF_CATEGORIES,
            ("guaranteed_profit_claim", "real_money_approval", "compounding_approval"),
        ),
        _stage(
            "FX-BUCKET-03-CANDIDATE-REVIEW-DECISION-PACKET",
            "Candidate Review to Operator Decision Packet V1",
            "review",
            "operator-decision-packet",
            "Turn the selected review-ready candidate into a human-readable decision packet.",
            "Anthony needs one clear decision packet before approving any controlled demo path.",
            ("FX-BUCKET-02-PROFIT-PROOF-LEDGER",),
            "FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE",
            "Create selected-candidate review packet with blockers and not-approved actions.",
            ("selected_candidate", "selection_reason", "blocked_actions", "next_safe_action"),
            ("demo_trade_approval", "broker_action", "real_money_approval"),
        ),
        _stage(
            "FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE",
            "Demo Trade Permission Envelope V1",
            "demo",
            "demo-permission",
            "Determine whether another controlled demo trade is eligible for approval.",
            "Demo execution must require proof, risk, broker state, and owner approval before any bridge can act.",
            ("FX-BUCKET-03-CANDIDATE-REVIEW-DECISION-PACKET",),
            "FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER",
            "Build demo permission envelope that keeps broker_action_allowed false.",
            ("review_ready_selected_candidate", "proof_ledger_sufficient", "risk_envelope_complete", "owner_demo_approval"),
            ("broker_action", "live_trading", "real_money_approval"),
        ),
        _stage(
            "FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER",
            "Broker Read-Only State Reconciler V1",
            "broker-readonly",
            "broker-state-readonly",
            "Read, listen, hear, and interpret broker-side account state without mutation.",
            "AIOS cannot plan a safe demo action without fresh exposure, spread, margin, and stale-state evidence.",
            ("FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE",),
            "FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER",
            "Build credential-free read-only broker state reconciler contract.",
            (
                "balance_present",
                "margin_available",
                "open_trades",
                "open_positions",
                "pending_orders",
                "last_transaction_id_runtime_only",
                "spread",
                "market_hours",
            ),
            ("broker_write", "order_submit", "credential_persistence", "account_id_persistence"),
        ),
        _stage(
            "FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER",
            "Risk Envelope and Position Sizer V1",
            "risk",
            "risk-envelope-position-sizer",
            "Calculate allowed demo-only position size under max loss rules.",
            "Position sizing is where a good candidate becomes either bounded risk or an unsafe trade.",
            ("FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER",),
            "FX-BUCKET-07-DEMO-ORDER-INTENT-PLANNER",
            "Build risk envelope and demo-only position-size preview.",
            (
                "max_risk_per_trade",
                "max_daily_loss",
                "max_exposure",
                "stop_loss",
                "take_profit",
                "kill_switch_clear",
                "duplicate_order_guard_clear",
                "spread_limit",
                "market_hours_clear",
            ),
            ("real_money_approval", "broker_action", "live_trading"),
        ),
        _stage(
            "FX-BUCKET-07-DEMO-ORDER-INTENT-PLANNER",
            "Demo Order Intent Planner V1",
            "planning",
            "demo-order-intent",
            "Create a local-only order intent preview.",
            "Intent planning lets Anthony review symbol, direction, units, risk, stop, take-profit, and rejection reasons before any bridge exists.",
            ("FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER",),
            "FX-BUCKET-08-EXECUTION-BRIDGE-DRY-RUN",
            "Build local-only demo order intent planner.",
            ("symbol", "direction", "units", "stop_loss", "take_profit", "risk_amount", "spread_gate", "rejection_reasons"),
            ("broker_call", "order_submit", "live_trading"),
        ),
        _stage(
            "FX-BUCKET-08-EXECUTION-BRIDGE-DRY-RUN",
            "Controlled Demo Execution Bridge Dry Run V1",
            "execution-dry-run",
            "demo-execution-bridge-dry-run",
            "Prepare a future demo execution bridge without enabling broker action.",
            "The bridge must be a separately approved protected lane because it can approach broker mutation.",
            ("FX-BUCKET-07-DEMO-ORDER-INTENT-PLANNER",),
            "FX-BUCKET-09-TRADE-MONITOR-KILL-SWITCH",
            "Create dry-run-only bridge review packet; keep broker_action_allowed false.",
            ("separate_future_packet", "owner_approval_required", "broker_action_false"),
            ("broker_action", "order_submit", "daemon", "scheduler"),
        ),
        _stage(
            "FX-BUCKET-09-TRADE-MONITOR-KILL-SWITCH",
            "Trade Monitor and Kill Switch V1",
            "monitoring",
            "trade-monitor-kill-switch",
            "Monitor open demo trade state and stop conditions.",
            "Any future supervised execution needs stop controls before, during, and after a trade.",
            ("FX-BUCKET-08-EXECUTION-BRIDGE-DRY-RUN",),
            "FX-BUCKET-10-POST-TRADE-RECONCILIATION",
            "Build non-daemonized monitor and kill-switch proof contract.",
            ("max_loss_breach", "daily_loss_breach", "spread_blowout", "stale_broker_state", "unexpected_open_exposure", "human_stop_flag"),
            ("daemon", "scheduler", "live_trading", "broker_mutation"),
        ),
        _stage(
            "FX-BUCKET-10-POST-TRADE-RECONCILIATION",
            "Post-Trade Reconciliation and Loss Response V1",
            "reconciliation",
            "post-trade-reconciliation",
            "Reconcile a closed demo trade with transaction data, candidate evidence, and profit/loss loops.",
            "The next candidate loop must learn from both wins and losses without faking proof.",
            ("FX-BUCKET-09-TRADE-MONITOR-KILL-SWITCH",),
            "FX-BUCKET-11-AUDIT-REPLAY-EVIDENCE",
            "Build post-trade reconciliation feed into validation, loss gate, intake, and selector.",
            ("closed_trade_evidence", "profit_validation_feed", "loss_gate_feed", "selector_feed"),
            ("profit_claim_without_reconciliation", "real_money_approval"),
        ),
        _stage(
            "FX-BUCKET-11-AUDIT-REPLAY-EVIDENCE",
            "Audit Replay and Evidence Ledger V1",
            "audit",
            "audit-replay-evidence",
            "Preserve sanitized local-only evidence replay for decision proof.",
            "AIOS must prove what happened before it asks for another decision.",
            ("FX-BUCKET-10-POST-TRADE-RECONCILIATION",),
            "FX-BUCKET-12-OPERATOR-DASHBOARD-VISIBILITY",
            "Build sanitized replay ledger with no credentials or account identifiers.",
            ("sanitized_replay", "decision_trace", "validator_evidence", "no_sensitive_fields"),
            ("credential_storage", "account_identifier_storage", "raw_broker_payload_storage"),
        ),
        _stage(
            "FX-BUCKET-12-OPERATOR-DASHBOARD-VISIBILITY",
            "Operator Visibility and Dashboard Evidence V1",
            "visibility",
            "operator-dashboard-evidence",
            "Expose status, not authority.",
            "Dashboards can help Anthony see state, but they must not approve trades or protected actions.",
            ("FX-BUCKET-11-AUDIT-REPLAY-EVIDENCE",),
            "FX-BUCKET-13-NIGHT-SUPERVISOR-RELAY-HANDOFF",
            "Build display-only evidence projection contract.",
            ("status_projection", "blocked_actions", "approval_required", "execution_allowed_false"),
            ("dashboard_trade_approval", "dashboard_commit_approval", "dashboard_merge_approval"),
        ),
        _stage(
            "FX-BUCKET-13-NIGHT-SUPERVISOR-RELAY-HANDOFF",
            "Night Supervisor and Relay Evidence Handoff V1",
            "handoff",
            "night-supervisor-relay-evidence",
            "Route evidence into summaries while preserving human approval.",
            "Supervisor summaries are useful evidence, not authority.",
            ("FX-BUCKET-12-OPERATOR-DASHBOARD-VISIBILITY",),
            "FX-BUCKET-14-GOVERNED-DEMO-AUTONOMY-READINESS",
            "Build read-only evidence handoff contract.",
            ("relay_evidence", "night_summary", "approval_required", "protected_actions_false"),
            ("night_supervisor_trade_approval", "relay_commit_approval", "protected_action_self_approval"),
        ),
        _stage(
            "FX-BUCKET-14-GOVERNED-DEMO-AUTONOMY-READINESS",
            "Governed Demo Autonomy Readiness Gate V1",
            "readiness",
            "governed-demo-autonomy-readiness",
            "Decide whether AIOS has a complete supervised demo autonomy loop.",
            "This is the readiness checkpoint before any separately approved execution lane.",
            ("FX-BUCKET-13-NIGHT-SUPERVISOR-RELAY-HANDOFF",),
            "FX-BUCKET-15-SINGLE-LIVE-MICRO-TRADE-EXCEPTION-REVIEW",
            "Evaluate all prior demo gates and require owner approval for execution.",
            ("all_prior_demo_gates_passed", "owner_approval_required", "execution_still_separate"),
            ("automatic_execution", "broker_action", "live_trading"),
        ),
        _stage(
            "FX-BUCKET-15-SINGLE-LIVE-MICRO-TRADE-EXCEPTION-REVIEW",
            "Single Live Micro-Trade Exception Review Gate V1",
            "live-exception-review",
            "single-live-micro-trade-exception-review",
            "Future review only through governed live micro-trade exception doctrine.",
            "Live action is a separate high-risk exception path, not a bucket permission.",
            ("FX-BUCKET-14-GOVERNED-DEMO-AUTONOMY-READINESS",),
            "FX-BUCKET-16-REAL-MONEY-LOCK",
            "Prepare future exception review requirements without enabling live trading.",
            ("explicit_human_approval", "runtime_only_credentials", "one_order_only", "micro_size", "stop_loss", "take_profit", "kill_switch"),
            ("live_trade", "credential_persistence", "account_id_persistence", "broker_call"),
            protected_action=True,
        ),
        _stage(
            "FX-BUCKET-16-REAL-MONEY-LOCK",
            "Real Money Lock V1",
            "money-lock",
            "real-money-lock",
            "Keep real-money trading blocked until evidence and owner approval exist.",
            "Synthetic, paper, and demo evidence cannot become real-money readiness by assertion.",
            ("FX-BUCKET-15-SINGLE-LIVE-MICRO-TRADE-EXCEPTION-REVIEW",),
            "FX-BUCKET-17-COMPOUNDING-LOCK",
            "Maintain real_money_allowed false.",
            ("non_synthetic_profit_evidence", "owner_real_money_approval", "risk_policy_review"),
            ("real_money_trade", "funding_approval", "live_trading"),
            protected_action=True,
        ),
        _stage(
            "FX-BUCKET-17-COMPOUNDING-LOCK",
            "Compounding Lock V1",
            "money-lock",
            "compounding-lock",
            "Keep compounding blocked until growth proof, drawdown control, and owner approval exist.",
            "Compounding magnifies both edge and failure, so it needs stronger proof than a single candidate.",
            ("FX-BUCKET-16-REAL-MONEY-LOCK",),
            "FX-BUCKET-18-BROKER-TO-BANK-MOVEMENT-LOCK",
            "Maintain compounding_allowed false.",
            ("real_money_growth_proof", "drawdown_control", "owner_compounding_approval"),
            ("compounding_approval", "automatic_size_increase", "money_movement"),
            protected_action=True,
        ),
        _stage(
            "FX-BUCKET-18-BROKER-TO-BANK-MOVEMENT-LOCK",
            "Broker To Bank Movement Lock V1",
            "money-lock",
            "bank-movement-lock",
            "Keep deposits, withdrawals, bank movement, account movement, and funding automation out of the Forex engine.",
            "Trading logic must not become bank movement automation.",
            ("FX-BUCKET-17-COMPOUNDING-LOCK",),
            "FX-BUCKET-19-MASTER-CONTINUATION-ROUTER",
            "Maintain bank_movement_allowed false and require separate future lane.",
            ("separate_bank_lane_required", "owner_bank_action_approval", "no_forex_engine_money_movement"),
            ("deposit", "withdrawal", "bank_linkage", "account_movement"),
            protected_action=True,
        ),
        _stage(
            "FX-BUCKET-19-MASTER-CONTINUATION-ROUTER",
            "Master Continuation Router V1",
            "routing",
            "master-continuation-router",
            "Determine the single next safe Codex packet or protected action after current status.",
            "AIOS should move one dependency at a time instead of scattering Forex autonomy work.",
            ("FX-BUCKET-18-BROKER-TO-BANK-MOVEMENT-LOCK",),
            "NONE",
            "Emit one next safe action only.",
            ("current_status", "next_stage", "next_safe_action", "blocked_actions"),
            ("multiple_next_actions", "self_approval", "protected_action_execution"),
        ),
    )
    validate_bucket_integrity(stages)
    return stages


def build_default_current_state() -> BucketCurrentState:
    return build_current_state_selector_local_only()


def build_current_state_selector_local_only() -> BucketCurrentState:
    return BucketCurrentState(
        selector_present=True,
        selector_local_only=True,
        selector_landed=False,
        proof_ledger_present=False,
        broker_read_only_state_present=False,
        risk_envelope_present=False,
        demo_permission_envelope_present=False,
        demo_review_path_ready=False,
        source_files_missing=("automation/forex_engine/evidence_promotion_gate.py",),
        local_dependencies=LOCAL_SELECTOR_DEPENDENCIES,
    )


def build_current_state_no_selector() -> BucketCurrentState:
    return BucketCurrentState(
        selector_present=False,
        selector_local_only=False,
        selector_landed=False,
        proof_ledger_present=False,
        broker_read_only_state_present=False,
        risk_envelope_present=False,
        demo_permission_envelope_present=False,
        demo_review_path_ready=False,
        source_files_missing=(
            "automation/forex_engine/review_ready_candidate_selector_v1.py",
            "automation/forex_engine/evidence_promotion_gate.py",
        ),
    )


def build_current_state_demo_review_path_ready() -> BucketCurrentState:
    return BucketCurrentState(
        selector_present=True,
        selector_local_only=False,
        selector_landed=True,
        proof_ledger_present=True,
        broker_read_only_state_present=True,
        risk_envelope_present=True,
        demo_permission_envelope_present=True,
        demo_review_path_ready=True,
        owner_demo_approval_present=False,
        source_files_missing=("automation/forex_engine/evidence_promotion_gate.py",),
    )


def build_current_state_selector_landed() -> BucketCurrentState:
    return BucketCurrentState(
        selector_present=True,
        selector_local_only=False,
        selector_landed=True,
        proof_ledger_present=False,
        broker_read_only_state_present=False,
        risk_envelope_present=False,
        demo_permission_envelope_present=False,
        demo_review_path_ready=False,
        source_files_missing=("automation/forex_engine/evidence_promotion_gate.py",),
    )


def evaluate_master_bucket(
    current_state: BucketCurrentState | Mapping[str, Any] | None = None,
) -> BucketEvaluationResult:
    """Evaluate the master bucket against a supplied or built-in current state."""

    state = _coerce_current_state(current_state)
    stages = build_master_bucket_stages()
    current_status = _current_status(state)
    current_stage_id = _current_stage_id(current_status)
    next_stage_id = _next_stage_id(current_status)
    proof_summary = _proof_summary(state)
    guaranteed_profit_proven = all(proof_summary.values())
    permissions = _permissions(state)
    blockers = _blockers(current_status, state, proof_summary)
    warnings = _warnings(proof_summary)
    next_safe_action = _next_safe_action(current_status)
    next_intent = _next_packet_intent(current_status)

    return BucketEvaluationResult(
        bucket_id=BUCKET_ID,
        bucket_version=PROFIT_AUTONOMY_MASTER_BUCKET_VERSION,
        selector_status=_selector_status(state),
        current_status=current_status,
        current_stage_id=current_stage_id,
        next_stage_id=next_stage_id,
        next_safe_action=next_safe_action,
        next_codex_packet_intent=next_intent,
        landed_milestones=state.landed_milestones,
        local_dependencies=state.local_dependencies,
        source_files_missing=state.source_files_missing,
        blockers=blockers,
        warnings=warnings,
        permissions=permissions,
        stages=stages,
        stage_results=_stage_results(stages, current_stage_id, current_status),
        proof_summary=proof_summary,
        guaranteed_profit_target=True,
        guaranteed_profit_proven=guaranteed_profit_proven,
        operator_answer=_operator_answer(current_status),
    )


def result_to_jsonable_dict(result: BucketEvaluationResult) -> dict[str, Any]:
    """Return deterministic JSON-safe bucket evaluation data."""

    return _json_value(result)


def result_to_operator_text(result: BucketEvaluationResult) -> str:
    """Return concise operator-readable bucket status."""

    permissions = result.permissions
    lines = [
        "AIOS Forex Profit Autonomy Master Bucket Pack V1",
        f"bucket_id: {result.bucket_id}",
        f"current_status: {result.current_status}",
        f"current_stage_id: {result.current_stage_id}",
        f"next_stage_id: {result.next_stage_id}",
        "permissions:",
        f"- candidate_review_allowed: {_bool_text(permissions.candidate_review_allowed)}",
        f"- next_demo_trade_allowed: {_bool_text(permissions.next_demo_trade_allowed)}",
        f"- broker_action_allowed: {_bool_text(permissions.broker_action_allowed)}",
        f"- real_money_allowed: {_bool_text(permissions.real_money_allowed)}",
        f"- compounding_allowed: {_bool_text(permissions.compounding_allowed)}",
        f"- bank_movement_allowed: {_bool_text(permissions.bank_movement_allowed)}",
        f"- live_trading_allowed: {_bool_text(permissions.live_trading_allowed)}",
        f"- credential_access_allowed: {_bool_text(permissions.credential_access_allowed)}",
        f"- repo_commit_allowed: {_bool_text(permissions.repo_commit_allowed)}",
        f"- repo_push_allowed: {_bool_text(permissions.repo_push_allowed)}",
        f"- pr_creation_allowed: {_bool_text(permissions.pr_creation_allowed)}",
        f"- owner_approval_required: {_bool_text(permissions.owner_approval_required)}",
        f"guaranteed_profit_target: {_bool_text(result.guaranteed_profit_target)}",
        f"guaranteed_profit_proven: {_bool_text(result.guaranteed_profit_proven)}",
        f"next_safe_action: {result.next_safe_action}",
        f"operator_answer: {result.operator_answer}",
    ]
    return "\n".join(lines) + "\n"


def bucket_to_markdown(result: BucketEvaluationResult | None = None) -> str:
    """Return the full readable bucket pack markdown."""

    active = result or evaluate_master_bucket(build_current_state_selector_local_only())
    lines = [
        "# AIOS Forex Profit Autonomy Master Bucket Pack V1",
        "",
        "## Bucket Identity",
        f"bucket_id: {BUCKET_ID}",
        "lane: forex-profit-autonomy-master-bucket-pack",
        "mode: APPLY",
        r"worktree: C:\Dev\Ai.Os",
        "branch: resolved after preflight",
        "",
        "## Anthony Mission",
        (
            "Anthony's mission is to build AIOS toward profit autonomy through "
            "evidence, governed execution, risk controls, broker-state "
            "reconciliation, operator approval, and compounding only after proof."
        ),
        "",
        "## Hard Requirement",
        (
            "Guaranteed profit autonomy is treated as a proof requirement. "
            "AIOS must prove it or block it. This bucket does not fake proof."
        ),
        "",
        "## Current Landed Milestones",
    ]
    lines.extend(f"- {milestone}" for milestone in active.landed_milestones)
    if active.local_dependencies:
        lines.append("- Review-Ready Candidate Selector V1 local-only dependency detected.")
    lines.extend(
        [
            "",
            "## Master Bucket Sequence",
        ]
    )
    for stage in active.stages:
        lines.extend(_stage_markdown_lines(stage))
    lines.extend(
        [
            "",
            "## Proof Categories",
        ]
    )
    lines.extend(f"- {category}" for category in REQUIRED_PROOF_CATEGORIES)
    lines.extend(
        [
            "",
            "## Current Permission Defaults",
        ]
    )
    defaults = BucketPermissionState()
    for key, value in asdict(defaults).items():
        suffix = " by default" if key == "candidate_review_allowed" else ""
        lines.append(f"{key}: {_bool_text(value)}{suffix}.")
    lines.extend(
        [
            "",
            "## Protected Action Locks",
            "- no commit without Anthony approval.",
            "- no push without Anthony approval.",
            "- no PR without Anthony approval.",
            "- no merge without Anthony approval.",
            "- no broker action without Anthony approval.",
            "- no credential access without Anthony approval and separate scoped packet.",
            "- no demo trade without Anthony approval and separate scoped packet.",
            "- no live trade without existing governed live micro-trade exception path and Anthony approval.",
            "- no bank movement in Forex engine.",
            "- no compounding approval in this bucket.",
            "",
            "## Next Safe Action Logic",
            "- If Review-Ready Candidate Selector V1 files are untracked, next safe action is protected commit / push / PR / merge workflow for selector.",
            "- If selector is missing, next safe action is recover or build selector.",
            "- If selector is landed, next safe action is Profit Proof Ledger V1.",
            "- If proof ledger is landed, next safe action is Broker Read-Only Reconciler V1.",
            "- If broker reconciler is landed, next safe action is Risk Envelope and Position Sizer V1.",
            "- If risk envelope is landed, next safe action is Demo Permission Envelope V1.",
            "- If demo permission is landed, next safe action is Demo Order Intent Planner V1.",
            "- Broker execution remains separate future protected action.",
            "- Real money, compounding, and bank movement remain locked.",
            "",
            "## Operator Answer",
            (
                "AIOS now has a master bucket path for Forex profit autonomy. "
                "It does not approve a trade, broker action, real money, "
                "compounding, or bank movement. It defines the exact sequence "
                "required to keep moving without losing context or bypassing proof."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def validate_bucket_integrity(stages: Sequence[BucketStage] | None = None) -> bool:
    active_stages = tuple(stages) if stages is not None else build_master_bucket_stages()
    if len(active_stages) < 20:
        raise ValueError("bucket must include at least twenty stages")
    stage_ids = tuple(stage.stage_id for stage in active_stages)
    if stage_ids != tuple(sorted(stage_ids)):
        raise ValueError("bucket stages must be deterministically ordered by stage_id")
    if len(set(stage_ids)) != len(stage_ids):
        raise ValueError("bucket stages must have unique stage_id values")
    required = {f"FX-BUCKET-{index:02d}" for index in range(20)}
    present_prefixes = {stage_id[:12] for stage_id in stage_ids}
    missing = sorted(required - present_prefixes)
    if missing:
        raise ValueError(f"missing required bucket stage prefix: {missing[0]}")
    allowed_dependencies = set(stage_ids) | set(LANDED_MILESTONES)
    for stage in active_stages:
        for field_name in (
            "entry_criteria",
            "exit_criteria",
            "validators",
            "blocked_actions",
            "stop_point",
            "evidence_required",
            "codex_packet_intent",
        ):
            value = getattr(stage, field_name)
            if not value:
                raise ValueError(f"{stage.stage_id} missing {field_name}")
        for dependency in stage.depends_on:
            if dependency not in allowed_dependencies:
                raise ValueError(
                    f"{stage.stage_id} depends on unknown stage or milestone: {dependency}"
                )
        if stage.next_stage_id != "NONE" and stage.next_stage_id not in stage_ids:
            raise ValueError(f"{stage.stage_id} next_stage_id is unknown")
    return True


def next_stage_to_operator_packet_text(result: BucketEvaluationResult) -> str:
    """Return a non-executable packet-intent report for the next stage."""

    return "\n".join(
        [
            "NON-EXECUTABLE PACKET INTENT REPORT",
            f"bucket_id: {result.bucket_id}",
            f"current_status: {result.current_status}",
            f"next_stage_id: {result.next_stage_id}",
            f"next_codex_packet_intent: {result.next_codex_packet_intent}",
            f"next_safe_action: {result.next_safe_action}",
            "approval_status: human_owner_required_for_any_protected_action",
            "executable_packet_created: false",
            "reason: child packet fields, branch plan, exact protected approvals, and validator evidence must be supplied by a separate packet.",
            "self_approval: false",
            "",
        ]
    )


def _stage(
    stage_id: str,
    title: str,
    category: str,
    lane: str,
    objective: str,
    why_it_matters: str,
    depends_on: tuple[str, ...],
    next_stage_id: str,
    codex_packet_intent: str,
    evidence_required: tuple[str, ...],
    blocked_actions: tuple[str, ...],
    *,
    protected_action: bool = False,
) -> BucketStage:
    return BucketStage(
        stage_id=stage_id,
        title=title,
        phase=stage_id.split("-")[2],
        lane=lane,
        category=category,
        status_hint="defined",
        objective=objective,
        why_it_matters=why_it_matters,
        entry_criteria=(
            "AGENTS.md authority preserved",
            "current stage dependencies reviewed",
            "no forbidden action authorized",
        ),
        exit_criteria=(
            "local-only output created or reviewed",
            "validators defined or run",
            "next safe action identified",
        ),
        creates_or_changes=(lane,),
        validators=(
            "python -m py_compile when Python changes exist",
            "focused pytest when tests exist",
            "git diff --check",
            "operator readback",
        ),
        blocked_actions=blocked_actions,
        owner_approval_required=True,
        protected_action=protected_action,
        depends_on=depends_on,
        next_stage_id=next_stage_id,
        codex_packet_intent=codex_packet_intent,
        stop_point="Stop after local evaluation/report; do not execute protected actions.",
        evidence_required=evidence_required,
        failure_label=f"{stage_id}-BLOCKED",
    )


def _coerce_current_state(
    raw: BucketCurrentState | Mapping[str, Any] | None,
) -> BucketCurrentState:
    if isinstance(raw, BucketCurrentState):
        return raw
    if raw is None:
        return build_default_current_state()
    if isinstance(raw, Mapping):
        return BucketCurrentState(
            selector_present=bool(raw.get("selector_present", False)),
            selector_local_only=bool(raw.get("selector_local_only", False)),
            selector_landed=bool(raw.get("selector_landed", False)),
            proof_ledger_present=bool(raw.get("proof_ledger_present", False)),
            broker_read_only_state_present=bool(
                raw.get("broker_read_only_state_present", False)
            ),
            risk_envelope_present=bool(raw.get("risk_envelope_present", False)),
            demo_permission_envelope_present=bool(
                raw.get("demo_permission_envelope_present", False)
            ),
            demo_review_path_ready=bool(raw.get("demo_review_path_ready", False)),
            owner_demo_approval_present=bool(
                raw.get("owner_demo_approval_present", False)
            ),
            source_files_missing=tuple(raw.get("source_files_missing", ())),
            local_dependencies=tuple(raw.get("local_dependencies", ())),
            landed_milestones=tuple(raw.get("landed_milestones", LANDED_MILESTONES)),
        )
    raise TypeError("unsupported master bucket current state")


def _current_status(state: BucketCurrentState) -> str:
    if not state.selector_present:
        return BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR
    if state.selector_local_only:
        return BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED
    if state.selector_landed and not state.proof_ledger_present:
        return BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED
    if state.proof_ledger_present and not state.broker_read_only_state_present:
        return BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED
    if state.broker_read_only_state_present and not state.risk_envelope_present:
        return BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED
    if state.risk_envelope_present and not state.demo_permission_envelope_present:
        return BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED
    if state.demo_review_path_ready or (
        state.selector_landed
        and state.proof_ledger_present
        and state.broker_read_only_state_present
        and state.risk_envelope_present
        and state.demo_permission_envelope_present
    ):
        return BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED
    return BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_NOT_READY


def _selector_status(state: BucketCurrentState) -> str:
    if not state.selector_present:
        return "selector_missing"
    if state.selector_local_only:
        return "selector_local_only_untracked_dependency"
    if state.selector_landed:
        return "selector_landed"
    return "selector_present_unclassified"


def _current_stage_id(status: str) -> str:
    return {
        BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR: "FX-BUCKET-01-SELECTOR-LANDED-GATE",
        BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED: "FX-BUCKET-01-SELECTOR-LANDED-GATE",
        BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED: "FX-BUCKET-02-PROFIT-PROOF-LEDGER",
        BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED: "FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER",
        BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED: "FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER",
        BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED: "FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE",
        BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED: "FX-BUCKET-14-GOVERNED-DEMO-AUTONOMY-READINESS",
    }.get(status, "FX-BUCKET-19-MASTER-CONTINUATION-ROUTER")


def _next_stage_id(status: str) -> str:
    return {
        BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR: "FX-BUCKET-01-SELECTOR-LANDED-GATE",
        BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED: "FX-BUCKET-01-SELECTOR-LANDED-GATE",
        BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED: "FX-BUCKET-02-PROFIT-PROOF-LEDGER",
        BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED: "FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER",
        BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED: "FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER",
        BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED: "FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE",
        BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED: "FX-BUCKET-15-SINGLE-LIVE-MICRO-TRADE-EXCEPTION-REVIEW",
    }.get(status, "FX-BUCKET-19-MASTER-CONTINUATION-ROUTER")


def _next_safe_action(status: str) -> str:
    return {
        BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR: "Recover or build Review-Ready Candidate Selector V1 before any new Forex autonomy feature lane.",
        BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED: "Complete protected commit, push, PR, checks, and merge for Review-Ready Candidate Selector V1 before the next feature lane.",
        BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED: "Build Profit Proof Ledger V1 as the next local-only evidence bucket.",
        BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED: "Build Broker Read-Only State Reconciler V1 after proof ledger lands.",
        BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED: "Build Risk Envelope and Position Sizer V1 after broker read-only state exists.",
        BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED: "Build Demo Trade Permission Envelope V1 after risk envelope exists.",
        BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED: "Prepare owner review for governed demo autonomy; do not execute trades in this bucket.",
    }.get(status, "Use Master Continuation Router V1 to select one safe next packet.")


def _next_packet_intent(status: str) -> str:
    return {
        BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR: "recover_or_build_review_ready_candidate_selector_v1",
        BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED: "protected_commit_pr_merge_review_ready_candidate_selector_v1",
        BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED: "build_profit_proof_ledger_v1",
        BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED: "build_broker_read_only_state_reconciler_v1",
        BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED: "build_risk_envelope_position_sizer_v1",
        BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED: "build_demo_permission_envelope_v1",
        BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED: "prepare_governed_demo_autonomy_operator_review_packet",
    }.get(status, "run_master_continuation_router_v1")


def _permissions(state: BucketCurrentState) -> BucketPermissionState:
    return BucketPermissionState(
        candidate_review_allowed=bool(
            state.selector_present
            and (state.selector_local_only or state.selector_landed or state.demo_review_path_ready)
        )
    )


def _proof_summary(state: BucketCurrentState) -> dict[str, bool]:
    proof = {category: False for category in REQUIRED_PROOF_CATEGORIES}
    proof["candidate_evidence_present"] = state.selector_present
    proof["selector_present"] = state.selector_present
    if state.proof_ledger_present:
        for category in (
            "sample_size_sufficient",
            "expectancy_positive",
            "profit_factor_sufficient",
            "max_drawdown_within_limit",
            "consecutive_losses_within_limit",
            "walk_forward_passed",
        ):
            proof[category] = True
    if state.broker_read_only_state_present:
        proof["broker_state_reconciled"] = True
    if state.risk_envelope_present:
        proof["risk_controls_reconciled"] = True
    if state.demo_review_path_ready:
        proof["demo_execution_reconciled"] = True
        proof["post_trade_reconciliation_passed"] = True
        proof["loss_response_validated"] = True
    if state.owner_demo_approval_present:
        proof["owner_approval_present"] = True
    return proof


def _blockers(
    status: str,
    state: BucketCurrentState,
    proof_summary: Mapping[str, bool],
) -> tuple[str, ...]:
    blockers: list[str] = []
    if status == BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR:
        blockers.append("Review-Ready Candidate Selector V1 is missing")
    if status == BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED:
        blockers.append("Review-Ready Candidate Selector V1 is local-only and untracked")
        blockers.append("protected commit/push/PR/merge approval is required")
    if status == BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED:
        blockers.append("Profit Proof Ledger V1 is missing")
    if status == BUCKET_STATUS_NEXT_ACTION_BROKER_READ_ONLY_REQUIRED:
        blockers.append("Broker read-only state is missing")
    if status == BUCKET_STATUS_NEXT_ACTION_RISK_ENVELOPE_REQUIRED:
        blockers.append("Risk envelope and position sizer are missing")
    if status == BUCKET_STATUS_NEXT_ACTION_DEMO_PERMISSION_REQUIRED:
        blockers.append("Demo permission envelope is missing")
    if not all(proof_summary.values()):
        missing = [key for key, value in proof_summary.items() if not value]
        blockers.append("guaranteed profit proof missing: " + ", ".join(missing))
    if state.source_files_missing:
        blockers.extend(f"source file missing: {path}" for path in state.source_files_missing)
    blockers.extend(
        (
            "real money remains locked",
            "compounding remains locked",
            "bank movement remains locked",
            "broker action remains locked",
        )
    )
    return tuple(dict.fromkeys(blockers))


def _warnings(proof_summary: Mapping[str, bool]) -> tuple[str, ...]:
    warnings = [
        "guaranteed_profit_target_is_not_a_profit_claim",
        "synthetic_or_demo_evidence_cannot_prove_real_money_readiness",
    ]
    if not all(proof_summary.values()):
        warnings.append("guaranteed_profit_proven_false_until_all_proof_categories_pass")
    return tuple(warnings)


def _stage_results(
    stages: Sequence[BucketStage],
    current_stage_id: str,
    current_status: str,
) -> tuple[BucketStageResult, ...]:
    stage_ids = [stage.stage_id for stage in stages]
    current_index = stage_ids.index(current_stage_id) if current_stage_id in stage_ids else len(stage_ids) - 1
    output: list[BucketStageResult] = []
    for index, stage in enumerate(stages):
        if index < current_index:
            status = "DEFINED_PREREQUISITE"
            passed = True
            blockers: tuple[str, ...] = ()
        elif index == current_index:
            status = current_status
            passed = current_status == BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED
            blockers = (current_status,)
        else:
            status = "PENDING"
            passed = False
            blockers = ("prior_stage_not_complete",)
        output.append(
            BucketStageResult(
                stage_id=stage.stage_id,
                status=status,
                passed=passed,
                blockers=blockers,
                warnings=(),
                next_safe_action=stage.codex_packet_intent,
            )
        )
    return tuple(output)


def _operator_answer(status: str) -> str:
    if status == BUCKET_STATUS_NEXT_ACTION_SELECTOR_COMMIT_PR_MERGE_REQUIRED:
        return (
            "AIOS has a master bucket path, and the current strongest safe next "
            "action is to land Review-Ready Candidate Selector V1 through the "
            "protected commit, push, PR, checks, and merge workflow. This bucket "
            "does not approve a trade, broker action, real money, compounding, "
            "or bank movement."
        )
    if status == BUCKET_STATUS_BLOCKED_BY_MISSING_CANDIDATE_SELECTOR:
        return (
            "AIOS cannot continue Forex profit autonomy sequencing until the "
            "Review-Ready Candidate Selector V1 is recovered or built."
        )
    if status == BUCKET_STATUS_NEXT_ACTION_PROOF_BUCKET_REQUIRED:
        return (
            "Review-Ready Candidate Selector V1 is treated as landed. The next "
            "safe build is Profit Proof Ledger V1. No trade, real money, broker "
            "action, or compounding is approved."
        )
    if status == BUCKET_STATUS_GOVERNED_DEMO_AUTONOMY_REVIEW_PATH_DEFINED:
        return (
            "AIOS has a governed demo autonomy review path defined, but this "
            "bucket still does not execute or approve trades. Anthony approval "
            "and a separate scoped execution packet remain required."
        )
    return (
        "AIOS has a master bucket path for Forex profit autonomy, but the "
        "current state is still blocked by missing prerequisite evidence."
    )


def _stage_markdown_lines(stage: BucketStage) -> list[str]:
    return [
        "",
        f"### {stage.stage_id}",
        f"title: {stage.title}",
        f"purpose: {stage.objective}",
        "entry criteria:",
        *[f"- {item}" for item in stage.entry_criteria],
        "exit criteria:",
        *[f"- {item}" for item in stage.exit_criteria],
        "validators:",
        *[f"- {item}" for item in stage.validators],
        "blocked actions:",
        *[f"- {item}" for item in stage.blocked_actions],
        f"owner approval boundary: {_bool_text(stage.owner_approval_required)}",
        f"next stage: {stage.next_stage_id}",
        f"stop point: {stage.stop_point}",
    ]


def _json_value(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def _bool_text(value: bool) -> str:
    return "true" if value else "false"

