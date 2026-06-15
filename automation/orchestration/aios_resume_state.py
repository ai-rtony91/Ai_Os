from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_RESUME_STATE.v1"
INPUT_SCHEMA = "AIOS_WAKE_CONTINUE.v1"
DEFAULT_OUTPUT_DIR = Path("Reports/aios_resume")
LATEST_FILENAME = "AIOS_RESUME_STATE_latest.json"

SENSITIVE_KEYS = {
    "api_key",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "credentials",
    "credential",
    "broker_credentials",
}


def safety_flags() -> dict[str, bool]:
    return {
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "runtime_launch": False,
        "scheduler": False,
        "daemon": False,
        "broker": False,
        "credentials": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if key_lower in {"stdout", "stderr"}:
                continue
            if key_lower in SENSITIVE_KEYS:
                sanitized[key_text] = "[redacted]"
                continue
            sanitized[key_text] = _sanitize(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def summarize_validators(wake_report: dict[str, Any]) -> dict[str, Any]:
    validators = wake_report.get("validators_run", [])
    if not isinstance(validators, list):
        validators = []

    summarized = []
    for validator in validators:
        if not isinstance(validator, dict):
            continue
        summarized.append(
            {
                "name": validator.get("name", "validator"),
                "command": validator.get("command", ""),
                "returncode": validator.get("returncode"),
                "passed": bool(validator.get("passed", False)),
            }
        )

    passed_count = sum(1 for validator in summarized if validator["passed"])
    return {
        "count": len(summarized),
        "passed_count": passed_count,
        "failed_count": len(summarized) - passed_count,
        "validators": summarized,
    }


def resume_readiness(wake_report: dict[str, Any]) -> tuple[bool, str]:
    result = wake_report.get("result")
    handoff = wake_report.get("bounded_executor_handoff")
    handoff_status = handoff.get("handoff_status") if isinstance(handoff, dict) else None
    if result != "DONE_FOR_CURRENT_GOAL":
        return False, "result_not_done_for_current_goal"
    if handoff_status != "ready":
        return False, "bounded_executor_handoff_not_ready"
    return True, "ready_for_resume"


def build_resume_state(wake_report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(wake_report, dict):
        wake_report = {}

    goal_decision = wake_report.get("goal_decision")
    if not isinstance(goal_decision, dict):
        goal_decision = {}

    next_build_plan = wake_report.get("next_build_plan")
    if not isinstance(next_build_plan, dict):
        next_build_plan = {}

    bounded_handoff = wake_report.get("bounded_executor_handoff")
    if not isinstance(bounded_handoff, dict):
        bounded_handoff = {}

    resume_ready, resume_reason_code = resume_readiness(wake_report)

    return {
        "schema": SCHEMA,
        "input_schema": wake_report.get("schema", INPUT_SCHEMA),
        "goal": wake_report.get("goal", "unknown"),
        "result": wake_report.get("result", "unknown"),
        "selected_action": wake_report.get("selected_action"),
        "last_decision": {
            "decision": goal_decision.get("decision"),
            "reason_code": goal_decision.get("reason_code"),
            "decision_reasons": goal_decision.get("decision_reasons", []),
        },
        "next_build_plan": _sanitize(next_build_plan),
        "bounded_executor_handoff": _sanitize(bounded_handoff),
        "next_safe_action": wake_report.get("next_safe_action", "Inspect wake/continue output before resuming."),
        "approval_required": _sanitize(wake_report.get("approval_required", {})),
        "safety": safety_flags(),
        "validators_summary": summarize_validators(wake_report),
        "resume_ready": resume_ready,
        "resume_reason_code": resume_reason_code,
    }


def _resolve_output_dir(repo_root: Path, output_dir: Path | str | None = None) -> Path:
    allowed_root = (repo_root / DEFAULT_OUTPUT_DIR).resolve()
    target = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target = target if target.is_absolute() else repo_root / target
    target = target.resolve()
    try:
        target.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError("resume_state_dir_outside_allowed_root") from exc
    return target


def write_resume_state(
    repo_root: Path,
    resume_state: dict[str, Any],
    *,
    output_dir: Path | str | None = None,
    generated_at_utc: datetime | None = None,
) -> dict[str, Any]:
    target_dir = _resolve_output_dir(repo_root, output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    now = generated_at_utc or datetime.now(timezone.utc)
    timestamp = now.astimezone(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    timestamped_path = target_dir / f"AIOS_RESUME_STATE_{timestamp}.json"
    latest_path = target_dir / LATEST_FILENAME
    if timestamped_path.exists():
        raise FileExistsError("timestamped_resume_state_exists")

    output_state = {
        **resume_state,
        "generated_at_utc": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "resume_state_paths": {
            "timestamped": timestamped_path.relative_to(repo_root).as_posix(),
            "latest": latest_path.relative_to(repo_root).as_posix(),
        },
    }
    serialized = json.dumps(output_state, indent=2, sort_keys=False) + "\n"
    timestamped_path.write_text(serialized, encoding="utf-8")
    latest_path.write_text(serialized, encoding="utf-8")
    return output_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build one sanitized AIOS resume-state preview.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root.")
    parser.add_argument("--write", action="store_true", help="Write resume state under Reports/aios_resume.")
    parser.add_argument("--output-dir", default=None, help="Optional output dir under Reports/aios_resume.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    resume_state = build_resume_state({"schema": INPUT_SCHEMA, "goal": "forex-paper-bot", "result": "preview_only"})
    if args.write:
        resume_state = write_resume_state(repo_root, resume_state, output_dir=args.output_dir)
    print(json.dumps(resume_state, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
