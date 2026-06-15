from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_STOP_REPORT_RESUME.v1"


def _summarize_validators(validators: list[Any]) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    for validator in validators:
        if not isinstance(validator, dict):
            continue
        normalized.append(
            {
                "name": validator.get("name", "validator"),
                "command": validator.get("command", ""),
                "passed": bool(validator.get("passed", False)),
                "returncode": validator.get("returncode"),
            }
        )
    passed = sum(1 for validator in normalized if validator["passed"])
    return {
        "count": len(normalized),
        "passed_count": passed,
        "failed_count": len(normalized) - passed,
        "validators": normalized,
    }


def build_stop_report_resume(run_state: dict[str, Any] | None) -> dict[str, Any]:
    state = run_state if isinstance(run_state, dict) else {}
    validators = state.get("validators_run", state.get("validators", []))
    if not isinstance(validators, list):
        validators = []
    result = str(state.get("result", "unknown"))
    stop_reason = str(state.get("stop_reason", state.get("blocked_reason", "none")))
    validators_summary = _summarize_validators(validators)
    resume_ready = result in {"DONE_FOR_CURRENT_GOAL", "REVIEW_REQUIRED", "preview_only"} and stop_reason in {
        "none",
        "",
        "review_required",
    }
    run_id = str(state.get("run_id") or f"AIOS-DRY-RUN-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "result": result,
        "stop_reason": stop_reason,
        "completed_steps": list(state.get("completed_steps", [])) if isinstance(state.get("completed_steps", []), list) else [],
        "failed_steps": list(state.get("failed_steps", [])) if isinstance(state.get("failed_steps", []), list) else [],
        "validators_summary": validators_summary,
        "next_safe_action": state.get("next_safe_action", "Review stop report before resuming AIOS self-build work."),
        "resume_ready": resume_ready,
        "morning_summary": (
            f"AIOS self-build run {run_id}: result={result}, stop_reason={stop_reason}, "
            f"validators_passed={validators_summary['passed_count']}/{validators_summary['count']}."
        ),
        "output_paths_preview": {
            "stop_report": "Reports/aios_self_build/AIOS_STOP_REPORT_preview.json",
            "resume_summary": "Reports/aios_self_build/AIOS_RESUME_SUMMARY_preview.json",
        },
        "files_written": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview AIOS stop/report/resume summary.")
    parser.add_argument("--run-state", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state = json.loads(args.run_state)
    print(json.dumps(build_stop_report_resume(state), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
