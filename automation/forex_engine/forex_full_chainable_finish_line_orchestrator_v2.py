"""Full chainable finish-line orchestrator for the governed AIOS Forex lane.

This module is an offline planning and packet-generation layer. It reads only
repo-local state artifacts and keeps broker, credential, environment, order, and
runtime automation boundaries locked.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from automation.validators import aios_governance_validator


PACKET_ID = "PKT-FOREX-FULL-CHAINABLE-FINISH-LINE-ORCHESTRATOR-V2"
PACKET_NAME = "Build Full Chainable Forex Finish-Line Orchestrator V2"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
MISSION_NAME = "Governed Forex Finish Line"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
PROGRAM_NAME = "Forex Profit Autonomy System"
EPIC_ID = "EPC-FOREX-FULL-CHAINABLE-FINISH-LINE-ORCHESTRATOR-001"
EPIC_NAME = "Full Chainable Forex Finish-Line Orchestrator"
BUCKET_ID = "BKT-FOREX-FULL-CHAINABLE-FINISH-LINE-ORCHESTRATOR-001"
BUCKET_NAME = "Repo-Safe Finish-Line Stage Graph And Relay Packet Generator"

STATUS_READY = "CHAINABLE_FOREX_ORCHESTRATOR_READY_FOR_HOURS_REPO_ONLY"
STATUS_OWNER_WAKE = "OWNER_WAKE_REQUIRED_FOR_PROTECTED_FOREX_BOUNDARY"
STATUS_FAIL_CLOSED = "CHAINABLE_FOREX_ORCHESTRATOR_FAIL_CLOSED"
ULTIMATE_FINISH_LINE = "22hr/day 6day/week governed operating readiness"

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "Reports" / "forex_delivery"
PLANNER_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_SAFE_OVERNIGHT_FINISH_LINE_CAMPAIGN_PLANNER_V1_STATE.json"
)
PLANNER_NEXT_PACKET_PATH = (
    REPORTS_DIR / "AIOS_FOREX_SAFE_OVERNIGHT_FINISH_LINE_CAMPAIGN_PLANNER_NEXT_CODEX_PACKET_V1.md"
)
OWNER_APPROVAL_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json"
)
SCOPE_REVIEW_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json"
)
MISSION_CONTROLLER_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json"
)
DEFAULT_STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_REPORT.md"
)
DEFAULT_NEXT_PACKET_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_NEXT_CODEX_PACKET_V2.md"
)

VALIDATOR_CHAIN = (
    "python -m py_compile automation/forex_engine/forex_full_chainable_finish_line_orchestrator_v2.py scripts/forex_delivery/run_forex_full_chainable_finish_line_orchestrator_v2.py",
    "python -m pytest tests/forex_engine/test_forex_full_chainable_finish_line_orchestrator_v2.py -q",
    "python scripts/forex_delivery/run_forex_full_chainable_finish_line_orchestrator_v2.py --write-state --write-report --write-next-packet",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json",
    "python automation/validators/aios_governance_validator.py --input Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_NEXT_CODEX_PACKET_V2.md",
    "git diff --check -- automation/forex_engine/forex_full_chainable_finish_line_orchestrator_v2.py scripts/forex_delivery/run_forex_full_chainable_finish_line_orchestrator_v2.py tests/forex_engine/test_forex_full_chainable_finish_line_orchestrator_v2.py Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_REPORT.md Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_NEXT_CODEX_PACKET_V2.md",
    "git status --short --branch",
)


@dataclass(frozen=True)
class Stage:
    name: str
    repo_only: bool
    owner_approval_required: bool
    broker_contact_required: bool
    credentials_required: bool
    env_required: bool
    account_identifier_required: bool
    trade_evidence_required: bool
    demo_required: bool
    live_required: bool
    scheduler_required: bool = False
    daemon_required: bool = False
    webhook_required: bool = False
    background_loop_required: bool = False

    def to_state(self) -> dict[str, Any]:
        protected_action = any(
            (
                self.owner_approval_required,
                self.broker_contact_required,
                self.credentials_required,
                self.env_required,
                self.account_identifier_required,
                self.demo_required,
                self.live_required,
                self.scheduler_required,
                self.daemon_required,
                self.webhook_required,
                self.background_loop_required,
            )
        )
        safe_for_hours = self.repo_only and not protected_action
        payload = asdict(self)
        payload["safe_for_hours"] = safe_for_hours
        payload["protected_action"] = protected_action
        payload["protected_action_reasons"] = protected_reasons(payload)
        return payload


def build_stage_graph() -> list[dict[str, Any]]:
    stages = [
        Stage(
            "first read-only broker probe review",
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ),
        Stage("broker connection proof", False, True, True, True, True, True, False, False, False),
        Stage("demo status and instrument probe", False, True, True, True, True, True, False, False, False),
        Stage("demo readiness", False, True, True, True, True, True, False, False, False),
        Stage("supervised demo execution readiness", False, True, True, True, True, True, True, True, False),
        Stage("repeated demo P/L evidence intake", False, True, True, True, True, True, True, True, False),
        Stage("strategy profitability evidence closure", False, True, False, False, False, False, True, False, False),
        Stage("live micro exception review", False, True, False, False, False, False, True, False, True),
        Stage("first live micro workflow readiness", False, True, True, True, True, True, True, False, True),
        Stage("live monitoring evidence intake", False, True, True, True, True, True, True, False, True),
        Stage("scaling and compounding policy", False, True, False, False, False, False, True, False, True),
        Stage(
            "long-session autonomy readiness",
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            scheduler_required=True,
            daemon_required=True,
            webhook_required=True,
            background_loop_required=True,
        ),
        Stage(
            ULTIMATE_FINISH_LINE,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            scheduler_required=True,
            daemon_required=True,
            webhook_required=True,
            background_loop_required=True,
        ),
    ]
    return [stage.to_state() for stage in stages]


def run_forex_full_chainable_finish_line_orchestrator_v2(
    *,
    packet_builder: Callable[[Mapping[str, Any]], str] | None = None,
) -> dict[str, Any]:
    source_state = load_source_state()
    source_errors = source_state.get("source_errors", [])
    stage_graph = build_stage_graph()
    current_stage = detect_current_stage(source_state)
    next_stage = select_next_stage(stage_graph, current_stage)
    packet_builder = packet_builder or build_next_codex_packet

    draft_result = {
        "current_stage": current_stage,
        "next_stage": next_stage["name"],
        "stage_graph": stage_graph,
    }
    next_packet_text = packet_builder(draft_result)
    next_packet_validation = aios_governance_validator.validate_packet_text(
        next_packet_text,
        _relative_path(DEFAULT_NEXT_PACKET_OUTPUT_PATH),
    )
    next_packet_governance_valid = next_packet_validation["status"] == "PASS"
    protected_action_detected = bool(next_stage["protected_action"])
    protected_action_reasons = list(next_stage["protected_action_reasons"])
    owner_wake_required = protected_action_detected
    owner_wake_reason = (
        "Next stage requires protected owner approval boundary: "
        + ", ".join(protected_action_reasons)
        if owner_wake_required
        else ""
    )

    if source_errors:
        orchestrator_status = STATUS_FAIL_CLOSED
        owner_wake_required = True
        owner_wake_reason = "Missing or invalid source state: " + ", ".join(source_errors)
    elif not next_packet_governance_valid:
        orchestrator_status = STATUS_FAIL_CLOSED
        owner_wake_required = True
        owner_wake_reason = "Generated next packet failed governance validation."
    elif protected_action_detected:
        orchestrator_status = STATUS_OWNER_WAKE
    else:
        orchestrator_status = STATUS_READY

    remaining_stages = remaining_stage_slice(stage_graph, next_stage["name"])
    repo_only_remaining = [
        stage
        for stage in remaining_stages
        if stage["repo_only"] and not stage["protected_action"]
    ]
    external_blockers = [stage for stage in remaining_stages if stage["protected_action"]]

    return {
        "orchestrator_status": orchestrator_status,
        "current_stage": current_stage,
        "next_stage": next_stage["name"],
        "stage_graph": stage_graph,
        "safe_for_hours": bool(next_stage["safe_for_hours"]) and not source_errors,
        "hours_ready": bool(next_stage["safe_for_hours"]) and not source_errors,
        "owner_wake_required": owner_wake_required,
        "owner_wake_reason": owner_wake_reason,
        "protected_action_detected": protected_action_detected,
        "protected_action_reasons": protected_action_reasons,
        "ultimate_finish_line": ULTIMATE_FINISH_LINE,
        "remaining_stage_count": len(remaining_stages),
        "repo_only_remaining_stage_count": len(repo_only_remaining),
        "external_blocker_stage_count": len(external_blockers),
        "next_packet_path": _relative_path(DEFAULT_NEXT_PACKET_OUTPUT_PATH),
        "next_packet_mode": "DRY_RUN",
        "next_packet_governance_valid": next_packet_governance_valid,
        "next_packet_validation_status": next_packet_validation["status"],
        "source_errors": source_errors,
        "source_state_summary": source_state.get("summary", {}),
        "broker_api_used": False,
        "credentials_used": False,
        "env_read": False,
        "account_identifiers_used": False,
        "order_execution": False,
        "demo_authorized": False,
        "live_authorized": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "background_loop_started": False,
        "commit_created": False,
        "push_created": False,
        "pr_created": False,
        "validator_chain": list(VALIDATOR_CHAIN),
        "packet_id": PACKET_ID,
        "packet_name": PACKET_NAME,
        "mission_id": MISSION_ID,
        "mission_name": MISSION_NAME,
        "program_id": PROGRAM_ID,
        "program_name": PROGRAM_NAME,
        "epic_id": EPIC_ID,
        "epic_name": EPIC_NAME,
        "bucket_id": BUCKET_ID,
        "bucket_name": BUCKET_NAME,
    }


def load_source_state() -> dict[str, Any]:
    required_paths = {
        "planner_state": PLANNER_STATE_PATH,
        "planner_next_packet": PLANNER_NEXT_PACKET_PATH,
        "owner_approval_state": OWNER_APPROVAL_STATE_PATH,
        "scope_review_state": SCOPE_REVIEW_STATE_PATH,
        "mission_controller_state": MISSION_CONTROLLER_STATE_PATH,
    }
    loaded: dict[str, Any] = {}
    errors: list[str] = []
    for key, path in required_paths.items():
        if not path.exists():
            errors.append(f"{key} missing at {_relative_path(path)}")
            continue
        if path.suffix.lower() == ".json":
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"{key} invalid json at {_relative_path(path)}")
                continue
            if not isinstance(value, dict):
                errors.append(f"{key} is not an object at {_relative_path(path)}")
                continue
            loaded[key] = value
        else:
            loaded[key] = path.read_text(encoding="utf-8")

    planner_state = _mapping(loaded.get("planner_state"))
    source_status = _mapping(planner_state.get("source_status"))
    owner_state = _mapping(loaded.get("owner_approval_state"))
    scope_state = _mapping(loaded.get("scope_review_state"))
    mission_state = _mapping(loaded.get("mission_controller_state"))
    return {
        **loaded,
        "source_errors": errors,
        "summary": {
            "planner_status": planner_state.get("planner_status"),
            "selected_next_safe_packet": planner_state.get("selected_next_safe_packet"),
            "owner_approval_review_status": owner_state.get("owner_approval_review_status"),
            "owner_approval_status": owner_state.get("owner_approval_status"),
            "source_scope_review_status": owner_state.get("source_scope_review_status")
            or scope_state.get("broker_probe_scope_status"),
            "controller_status": mission_state.get("controller_status")
            or source_status.get("controller_status"),
            "current_phase": mission_state.get("current_phase")
            or source_status.get("current_phase"),
            "broker_probe_readiness_approved": bool(
                owner_state.get("broker_probe_readiness_approved")
            ),
            "demo_proof_exists": bool(owner_state.get("demo_proof_exists")),
            "owner_live_micro_exception_approved": bool(
                owner_state.get("owner_live_micro_exception_approved")
            ),
            "live_trading_owner_authorization_exists": bool(
                owner_state.get("live_trading_owner_authorization_exists")
            ),
        },
    }


def detect_current_stage(source_state: Mapping[str, Any]) -> str:
    summary = _mapping(source_state.get("summary"))
    selected_packet = str(summary.get("selected_next_safe_packet") or "")
    current_phase = str(summary.get("current_phase") or "")
    if selected_packet == "FIRST_READ_ONLY_BROKER_PROBE_REVIEW_DRY_RUN":
        return "first read-only broker probe review"
    if current_phase == "BROKER_PROBE_SCOPE_APPROVAL_REQUIRED":
        return "first read-only broker probe review"
    return "first read-only broker probe review"


def select_next_stage(
    stage_graph: list[dict[str, Any]],
    current_stage: str,
) -> dict[str, Any]:
    for stage in stage_graph:
        if stage["name"] == current_stage:
            return stage
    return stage_graph[0]


def remaining_stage_slice(stage_graph: list[dict[str, Any]], stage_name: str) -> list[dict[str, Any]]:
    for index, stage in enumerate(stage_graph):
        if stage["name"] == stage_name:
            return stage_graph[index:]
    return list(stage_graph)


def protected_reasons(stage: Mapping[str, Any]) -> list[str]:
    labels = {
        "owner_approval_required": "owner approval",
        "broker_contact_required": "broker contact",
        "credentials_required": "credentials",
        "env_required": ".env access",
        "account_identifier_required": "account identifiers",
        "trade_evidence_required": "trade evidence",
        "demo_required": "demo action",
        "live_required": "live action",
        "scheduler_required": "scheduler",
        "daemon_required": "daemon",
        "webhook_required": "webhook",
        "background_loop_required": "background loop",
    }
    return [label for key, label in labels.items() if bool(stage.get(key))]


def build_report_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex Full Chainable Finish-Line Orchestrator V2 Report",
        "",
        f"Status: {result.get('orchestrator_status')}",
        f"Current branch: {_git_value('branch', '--show-current')}",
        f"Current head: {_git_value('log', '-1', '--oneline')}",
        f"Current stage: {result.get('current_stage')}",
        f"Next stage: {result.get('next_stage')}",
        f"Ultimate finish line: {result.get('ultimate_finish_line')}",
        f"Safe for hours: {result.get('safe_for_hours')}",
        f"Hours ready: {result.get('hours_ready')}",
        f"Owner wake required: {result.get('owner_wake_required')}",
        f"Owner wake reason: {result.get('owner_wake_reason')}",
        "",
        "Stage graph:",
    ]
    for stage in _list_of_mappings(result.get("stage_graph")):
        lines.append(
            "- {name}: repo_only={repo_only}, safe_for_hours={safe_for_hours}, "
            "protected_action={protected_action}".format(**stage)
        )
    lines.extend(
        [
            "",
            "Safety boundary retained:",
            f"- Broker API used: {result.get('broker_api_used')}",
            f"- Credentials used: {result.get('credentials_used')}",
            f"- .env read: {result.get('env_read')}",
            f"- Account identifiers used: {result.get('account_identifiers_used')}",
            f"- Order execution: {result.get('order_execution')}",
            f"- Demo authorized: {result.get('demo_authorized')}",
            f"- Live authorized: {result.get('live_authorized')}",
            f"- Scheduler started: {result.get('scheduler_started')}",
            f"- Daemon started: {result.get('daemon_started')}",
            f"- Webhook started: {result.get('webhook_started')}",
            f"- Background loop started: {result.get('background_loop_started')}",
            "",
            f"Next packet: `{result.get('next_packet_path')}`",
            f"Next packet mode: {result.get('next_packet_mode')}",
            f"Next packet governance valid: {result.get('next_packet_governance_valid')}",
            "",
            "Validators:",
        ]
    )
    for validator in _string_list(result.get("validator_chain")):
        lines.append(f"- `{validator}`")
    lines.extend(
        [
            "",
            "Next safe action:",
            _next_safe_action(result),
        ]
    )
    return "\n".join(lines) + "\n"


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    branch = "resolve after preflight"
    return f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_FIRST_READ_ONLY_BROKER_PROBE_REVIEW_RELAY_DRY_RUN_V2

IDENTITY MARKER
AIOS_FOREX_FIRST_READ_ONLY_BROKER_PROBE_REVIEW_RELAY_DRY_RUN_V2

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-FIRST-READ-ONLY-BROKER-PROBE-REVIEW-RELAY-DRY-RUN-V2

PACKET NAME
First Read-Only Broker Probe Review Relay Dry Run V2

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
First Read-Only Broker Probe Review Relay Dry Run

WORKTREE
C:\\Dev\\Ai.Os

BRANCH
{branch}

MISSION ID
{MISSION_ID}

MISSION NAME
{MISSION_NAME}

PROGRAM ID
{PROGRAM_ID}

PROGRAM NAME
{PROGRAM_NAME}

EPIC ID
EPC-FOREX-BROKER-PROBE-SCOPE-REVIEW-001

EPIC NAME
Value-Free Broker Probe Scope Review

BUCKET ID
BKT-FOREX-FIRST-READ-ONLY-BROKER-PROBE-REVIEW-001

BUCKET NAME
First Read-Only Broker Probe Review

APPROVAL AUTHORITY
Anthony is the only authority for APPLY, commit, push, PR, merge, broker contact, credential use, .env access, account identifier use, demo action, live action, order execution, scheduler activation, daemon activation, webhook activation, background-loop activation, and live trading authorization.
A later Human Owner message that explicitly approves APPLY is required before any file write.
A later Human Owner message that explicitly approves broker contact is required before any broker contact.
A later Human Owner message that explicitly approves credential use is required before any credential use.
A later Human Owner message that explicitly approves .env access is required before any .env access.
A later Human Owner message that explicitly approves account identifier use is required before any account identifier use.
A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.
A later Human Owner message that explicitly approves merge is required before merge.

MISSION
Perform a DRY_RUN-only relay review for the first read-only broker probe path from current repo evidence.

This packet may inspect only listed local artifacts.
This packet must not create files.
This packet must not modify files.
This packet must not contact a broker.
This packet must not use credentials.
This packet must not read .env.
This packet must not use account identifiers.
This packet must not inspect private broker data.
This packet must not authorize demo action.
This packet must not authorize live micro action.
This packet must not authorize live trading.
This packet must not start scheduler, daemon, webhook, or background loop.
This packet must not place orders.
This packet must not commit.
This packet must not push.
This packet must not create PR.

PREFLIGHT
cd C:\\Dev\\Ai.Os
pwd
git status --short --branch
git branch --show-current
git log -1 --oneline

READ FIRST
AGENTS.md
README.md
RISK_POLICY.md
docs/governance/AI_OS_REPO_MEMORY.md
docs/governance/aios-identity-and-lane-governance.md

READ SOURCE ARTIFACTS
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json

FORBIDDEN PATHS
AGENTS.md
README.md
RISK_POLICY.md
.env
secrets
credentials
broker account identifiers
broker modules
order modules
demo execution modules
live execution modules
scheduler files
daemon files
webhook files
background loops
dashboard mutation files
unrelated docs
unrelated tests
any path outside C:\\Dev\\Ai.Os except temporary validation paths

REQUIRED BEHAVIOR
Confirm the orchestrator current stage is first read-only broker probe review.
Confirm next protected boundary remains owner approval before broker contact, credentials, .env access, account identifiers, demo action, live action, order execution, scheduler, daemon, webhook, or background loop.
Confirm all safety booleans remain false.
Report whether the next non-repo-only stage requires OWNER_WAKE_REQUIRED.

SAFE NEXT ACTION
Stop after DRY_RUN relay review. Keep protected Forex boundary locked unless Anthony provides explicit later approval in a complete tokenized packet.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
git status --short --branch

STOP POINT
Stop after DRY_RUN relay review and final report.
Do not edit files.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not authorize demo, live micro, live trading, scheduler, daemon, webhook, background loop, or order execution.
Do not commit.
Do not push.
Do not create PR.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
CURRENT_STAGE:
NEXT_PROTECTED_BOUNDARY:
OWNER_WAKE_REQUIRED:
BROKER_API_USED:
CREDENTIALS_USED:
ENV_READ:
ACCOUNT_IDENTIFIERS_USED:
ORDER_EXECUTION:
DEMO_AUTHORIZED:
LIVE_AUTHORIZED:
SCHEDULER_STARTED:
DAEMON_STARTED:
WEBHOOK_STARTED:
BACKGROUND_LOOP_STARTED:
NEXT_SAFE_ACTION:
GIT_STATUS:
"""


def _next_safe_action(result: Mapping[str, Any]) -> str:
    if result.get("owner_wake_required"):
        return (
            "Stop for Human Owner approval before any broker-facing, credential, "
            "environment, account identifier, demo, live, order, scheduler, daemon, "
            "webhook, or background-loop action."
        )
    return (
        "Continue only by executing the generated repo-only DRY_RUN packet. Stop at "
        "the next protected Forex boundary."
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _git_value(*command: str) -> str:
    try:
        return subprocess.check_output(["git", *command], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


__all__ = [
    "DEFAULT_NEXT_PACKET_OUTPUT_PATH",
    "DEFAULT_REPORT_OUTPUT_PATH",
    "DEFAULT_STATE_OUTPUT_PATH",
    "STATUS_FAIL_CLOSED",
    "STATUS_OWNER_WAKE",
    "STATUS_READY",
    "ULTIMATE_FINISH_LINE",
    "VALIDATOR_CHAIN",
    "build_next_codex_packet",
    "build_report_markdown",
    "build_stage_graph",
    "detect_current_stage",
    "protected_reasons",
    "run_forex_full_chainable_finish_line_orchestrator_v2",
    "select_next_stage",
]
