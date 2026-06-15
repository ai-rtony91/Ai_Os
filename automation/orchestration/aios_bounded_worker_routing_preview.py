from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_BOUNDED_WORKER_ROUTING_PREVIEW.v1"
VALIDATOR = "automation/orchestration/validators/Test-AiOsRecommendedCommand.ps1"

NO_ROUTE_STATUSES = {"none", "no command recommended", "no_command_recommended"}
PASS_STATUSES = {"PASS", "SAFE", "VALIDATED", "VALID"}
FAILED_STATUSES = {"FAIL", "FAILED", "BLOCKED", "REJECTED", "UNSAFE"}

PROTECTED_COMMAND_TERMS = (
    "git add",
    "git commit",
    "git push",
    "git merge",
    "git reset",
    "git clean",
    "git checkout",
    "git switch",
    "gh pr create",
    "gh pr merge",
    "remove-item",
    "rm ",
    "del ",
    "erase ",
    "start-process",
    "schtasks",
    "invoke-expression",
    "iex",
    "set-content",
    "add-content",
    "out-file",
    "move-item",
    "copy-item",
    "rename-item",
    "new-item",
)

HIGH_RISK_TERMS = (
    "secret",
    "secrets",
    "credential",
    "credentials",
    "api_key",
    "apikey",
    "token",
    "password",
    ".env",
    "broker",
    "oanda",
    "webhook",
    "live trading",
    "live_trading",
    "real order",
    "real_orders",
    "place order",
    "submit order",
    "buy",
    "sell",
    "scheduler",
    "daemon",
    "startup task",
)


def _safety() -> dict[str, bool]:
    return {
        "preview_only": True,
        "command_execution": False,
        "codex_launch": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "scheduler_activation": False,
        "daemon_activation": False,
        "network_access": False,
        "reports_written": False,
        "file_writes": False,
        "broker": False,
        "credentials": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "runtime_supervisor_consumable_status": True,
    }


def _required_approvals() -> dict[str, bool]:
    return {
        "human_owner_review_before_execution": True,
        "worker_dispatch": True,
        "queue_mutation": True,
        "approval_mutation": True,
        "local_apply": True,
        "commit": True,
        "push": True,
        "merge": True,
        "scheduler_or_daemon": True,
        "broker_or_trading": True,
    }


def _blocked_actions(extra: list[str] | None = None) -> list[str]:
    actions = [
        "execute_recommended_command",
        "launch_codex",
        "dispatch_worker",
        "mutate_runtime_queue",
        "mutate_worker_inbox",
        "mutate_approval_state",
        "start_scheduler",
        "start_daemon",
        "access_network",
        "write_reports",
        "touch_broker_trading_credentials_orders_or_webhooks",
        "git_add",
        "git_commit",
        "git_push",
        "git_merge",
    ]
    if extra:
        actions.extend(extra)
    return list(dict.fromkeys(actions))


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _get_command(source_recommendation: dict[str, Any]) -> str:
    for key in ("recommended_command", "command", "next_safe_action"):
        value = source_recommendation.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    contract = _as_dict(source_recommendation.get("orchestration_result_contract"))
    value = contract.get("next_safe_action")
    return value.strip() if isinstance(value, str) else ""


def _no_action_command(command: str) -> bool:
    normalized = command.strip().lower().rstrip(".")
    return not normalized or any(normalized.startswith(status) for status in NO_ROUTE_STATUSES)


def _validation_status(source_recommendation: dict[str, Any], validated_command: Any) -> str:
    if isinstance(validated_command, dict):
        for key in ("validation_status", "command_validation_status", "status", "result"):
            value = validated_command.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip().upper()
        if validated_command.get("validated") is True:
            return "PASS"
        if validated_command.get("safe") is True:
            return "PASS"
    if isinstance(validated_command, str) and validated_command.strip():
        return validated_command.strip().upper()
    value = source_recommendation.get("command_validation_status")
    return value.strip().upper() if isinstance(value, str) else "NOT_RUN"


def _validated_command(command: str, validation_status: str, validated_command: Any) -> dict[str, Any]:
    validation = _as_dict(validated_command)
    return {
        "command": command,
        "validator": str(validation.get("validator") or VALIDATOR),
        "validation_status": validation_status,
        "validated": validation_status in PASS_STATUSES,
        "execution_allowed": False,
    }


def _contains_any(text: str, terms: tuple[str, ...]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term in lower]


def _recommendation_protected(source_recommendation: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    contract = _as_dict(source_recommendation.get("orchestration_result_contract"))
    safety = _as_dict(source_recommendation.get("safety"))
    flags = _as_dict(source_recommendation.get("protected_action_flags"))

    if source_recommendation.get("protected_action_recommended") is True:
        reasons.append("protected_action_recommended")
    if contract.get("approval_required") is True:
        reasons.append("recommendation_requires_approval")
    if str(contract.get("status") or "").upper() == "BLOCKED":
        reasons.append("recommendation_contract_blocked")
    for key, value in {**safety, **flags}.items():
        if value is True and str(key) in {
            "command_execution",
            "command_execution_requested",
            "codex_launch",
            "worker_dispatch",
            "launches_workers",
            "queue_mutation",
            "approval_mutation",
            "scheduler",
            "daemon",
            "network",
            "network_access",
            "broker",
            "credentials",
            "live_trading",
            "real_orders",
            "real_webhooks",
            "git_add",
            "git_commit",
            "git_push",
            "merge",
        }:
            reasons.append(f"unsafe_flag:{key}")
    return reasons


def _propose_worker(command: str, source_recommendation: dict[str, Any]) -> tuple[str, str]:
    contract = _as_dict(source_recommendation.get("orchestration_result_contract"))
    worker_identity = str(contract.get("worker_identity") or "").strip()
    if worker_identity and worker_identity.upper() != "UNKNOWN":
        return worker_identity, "recommendation-contract-lane"

    command_lower = command.lower()
    if "commit_packages/" in command_lower or "commit_packages\\" in command_lower:
        return "save_git", "commit-package-preview"
    if (
        "validators/" in command_lower
        or "validators\\" in command_lower
        or command_lower.startswith("git status")
        or command_lower.startswith("git diff")
        or command_lower.startswith("git log")
        or command_lower.startswith("git show")
    ):
        return "check_audit", "validation-audit-preview"
    if (
        "work_packets/" in command_lower
        or "work_packets\\" in command_lower
        or "workers/" in command_lower
        or "workers\\" in command_lower
        or "dispatch" in command_lower
        or "campaign_registry/" in command_lower
        or "campaign_registry\\" in command_lower
    ):
        return "route_dispatch", "bounded-routing-preview"
    return "orchestration_codex", "bounded-orchestration-preview"


def _write_scope(command: str, source_recommendation: dict[str, Any]) -> list[str]:
    contract = _as_dict(source_recommendation.get("orchestration_result_contract"))
    evidence = _as_dict(contract.get("evidence"))
    level5 = _as_dict(evidence.get("level5_commit_package_preview"))
    scope = _as_list(source_recommendation.get("allowed_paths"))
    scope.extend(_as_list(contract.get("allowed_paths")))
    scope.extend(_as_list(level5.get("exact_changed_files")))
    if scope:
        return list(dict.fromkeys(scope))
    if " -File " in command:
        script = command.split(" -File ", 1)[1].split()[0].strip("\"'")
        if script:
            return [script]
    return []


def _task_summary(command: str, source_recommendation: dict[str, Any], routing_status: str) -> str:
    reason = source_recommendation.get("reason")
    if isinstance(reason, str) and reason.strip():
        return f"Preview worker route for validated recommendation: {reason.strip()}"
    if routing_status == "no_route":
        return "No worker route available because there is no actionable recommendation."
    return f"Preview worker route for validated command: {command}"


def _base_preview(
    *,
    routing_status: str,
    source_recommendation: Any,
    validated_command: dict[str, Any],
    proposed_worker_identity: str | None,
    proposed_lane: str | None,
    proposed_task_summary: str,
    proposed_write_scope: list[str],
    reasons: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "routing_status": routing_status,
        "source_recommendation": source_recommendation,
        "validated_command": validated_command,
        "proposed_worker_identity": proposed_worker_identity,
        "proposed_lane": proposed_lane,
        "proposed_task_summary": proposed_task_summary,
        "proposed_write_scope": proposed_write_scope,
        "required_approvals": _required_approvals(),
        "blocked_actions": _blocked_actions(reasons),
        "commands_executed": [],
        "queues_mutated": False,
        "approvals_mutated": False,
        "workers_dispatched": False,
        "files_written": [],
        "safety": _safety(),
        "runtime_supervisor_blocker": None if routing_status == "route_ready" else ";".join(reasons),
        "next_safe_action": next_safe_action,
    }


def build_bounded_worker_routing_preview(source_recommendation: Any, validated_command: Any = None) -> dict[str, Any]:
    if not isinstance(source_recommendation, dict) or not source_recommendation:
        return _base_preview(
            routing_status="no_route",
            source_recommendation=source_recommendation,
            validated_command=_validated_command("", "NOT_RUN", validated_command),
            proposed_worker_identity=None,
            proposed_lane=None,
            proposed_task_summary="No worker route available because the recommendation is missing.",
            proposed_write_scope=[],
            reasons=["missing_recommendation"],
            next_safe_action="Stop and generate a validated next-action recommendation before routing preview.",
        )

    command = _get_command(source_recommendation)
    validation_status = _validation_status(source_recommendation, validated_command)
    validation = _validated_command(command, validation_status, validated_command)

    if _no_action_command(command):
        return _base_preview(
            routing_status="no_route",
            source_recommendation=source_recommendation,
            validated_command=validation,
            proposed_worker_identity=None,
            proposed_lane=None,
            proposed_task_summary=_task_summary(command, source_recommendation, "no_route"),
            proposed_write_scope=[],
            reasons=["no_actionable_recommendation"],
            next_safe_action="Stop or idle; no worker route is available without an actionable validated recommendation.",
        )

    protected_reasons = _recommendation_protected(source_recommendation)
    protected_terms = _contains_any(command, PROTECTED_COMMAND_TERMS)
    high_risk_terms = _contains_any(command, HIGH_RISK_TERMS)
    if protected_terms:
        protected_reasons.append("protected_command_term:" + ",".join(protected_terms))
    if high_risk_terms:
        protected_reasons.append("high_risk_command_term:" + ",".join(high_risk_terms))

    if protected_reasons:
        worker, lane = _propose_worker(command, source_recommendation)
        return _base_preview(
            routing_status="blocked",
            source_recommendation=source_recommendation,
            validated_command=validation,
            proposed_worker_identity=worker,
            proposed_lane=lane,
            proposed_task_summary=_task_summary(command, source_recommendation, "blocked"),
            proposed_write_scope=_write_scope(command, source_recommendation),
            reasons=protected_reasons,
            next_safe_action="Stop before routing. Protected or high-risk recommendations require explicit Anthony approval and a separate packet.",
        )

    if validation_status in FAILED_STATUSES:
        worker, lane = _propose_worker(command, source_recommendation)
        return _base_preview(
            routing_status="rejected",
            source_recommendation=source_recommendation,
            validated_command=validation,
            proposed_worker_identity=worker,
            proposed_lane=lane,
            proposed_task_summary=_task_summary(command, source_recommendation, "rejected"),
            proposed_write_scope=_write_scope(command, source_recommendation),
            reasons=["recommended_command_failed_validation"],
            next_safe_action="Stop and repair the recommendation before routing preview.",
        )

    if validation_status not in PASS_STATUSES:
        worker, lane = _propose_worker(command, source_recommendation)
        return _base_preview(
            routing_status="blocked",
            source_recommendation=source_recommendation,
            validated_command=validation,
            proposed_worker_identity=worker,
            proposed_lane=lane,
            proposed_task_summary=_task_summary(command, source_recommendation, "blocked"),
            proposed_write_scope=_write_scope(command, source_recommendation),
            reasons=["recommended_command_not_validated"],
            next_safe_action="Run the recommended-command validator first; do not route or execute unvalidated commands.",
        )

    worker, lane = _propose_worker(command, source_recommendation)
    return _base_preview(
        routing_status="route_ready",
        source_recommendation=source_recommendation,
        validated_command=validation,
        proposed_worker_identity=worker,
        proposed_lane=lane,
        proposed_task_summary=_task_summary(command, source_recommendation, "route_ready"),
        proposed_write_scope=_write_scope(command, source_recommendation),
        reasons=[],
        next_safe_action="Use this as worker routing preview evidence only; do not execute, dispatch, queue, approve, or write from this preview.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a preview-only AIOS bounded worker routing object.")
    parser.add_argument("--recommendation", default="{}", help="JSON recommendation or runtime self-route report.")
    parser.add_argument("--validated-command", default="{}", help="JSON validation evidence or status string.")
    return parser


def _load_arg(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    preview = build_bounded_worker_routing_preview(
        _load_arg(args.recommendation),
        _load_arg(args.validated_command),
    )
    print(json.dumps(preview, indent=2, sort_keys=False))
    return 0 if preview["routing_status"] in {"route_ready", "no_route"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
