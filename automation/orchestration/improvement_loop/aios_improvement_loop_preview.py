#!/usr/bin/env python3
"""AI_OS Phase 18 improvement loop preview runner.

Local-only, standard-library-only DRY_RUN preview. It reads fixture evidence,
validates JSON shape, and writes deterministic preview outputs only in normal
mode. Validate-only mode writes nothing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "docs" / "AI_OS" / "improvement_loop" / "fixtures"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "AI_OS" / "improvement_loop" / "preview_outputs"

FORBIDDEN_TERMS = [
    "real api key",
    ".env",
    "live openai call",
    "network call",
    "package install",
    "broker execution",
    "oanda execution",
    "live trading execution",
    "real order",
    "webhook execution",
    "automatic merge",
    "automatic push",
    "runtime telemetry write",
    "real approval inbox write",
    "night supervisor modification",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def assert_local_safety(payloads: list[dict[str, Any]]) -> None:
    text = json.dumps(payloads, sort_keys=True).lower()
    # The fixture may name blocked categories; fail only on active/allowed forms.
    active_patterns = [
        '"live_openai_api_call": true',
        '"api_key_required": true',
        '"network_required": true',
        '"package_install_required": true',
        '"live_trading_status": "allowed"',
        '"broker_execution_status": "allowed"',
        '"oanda_status": "allowed"',
    ]
    for pattern in active_patterns:
        if pattern in text:
            raise ValueError(f"Blocked active safety pattern found: {pattern}")


def require_fields(name: str, payload: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if field not in payload]
    if missing:
        raise ValueError(f"{name} missing required fields: {', '.join(missing)}")


def build_outputs(trace: dict[str, Any], feedback: dict[str, Any], eval_case: dict[str, Any], recommendation: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    ranked = {
        "mode": "DRY_RUN",
        "local_fixture_only": True,
        "live_openai_api_call": False,
        "api_key_required": False,
        "network_required": False,
        "package_install_required": False,
        "auto_merge": False,
        "auto_push": False,
        "live_trading_status": "BLOCKED",
        "broker_execution_status": "BLOCKED",
        "oanda_status": "BLOCKED",
        "ranked_improvements": [
            {
                "rank": 1,
                "recommendation_id": recommendation["recommendation_id"],
                "title": recommendation["title"],
                "priority_score": recommendation["priority_score"],
                "risk_class": recommendation["risk_class"],
                "evidence": recommendation["evidence"],
                "next_handoff": "CODEX_HANDOFF_PREVIEW_001.md",
            }
        ],
    }

    report = f"""# Improvement Loop Preview Report 001

Status: PASS

Mode: DRY_RUN
Local fixture only: true
OpenAI call: false
API key required: false
Network required: false
Package install required: false
Automatic merge: false
Automatic push: false
Live trading: BLOCKED
Broker execution: BLOCKED
OANDA: BLOCKED

## Evidence Used

- Trace: {trace['trace_id']} ({trace['result']})
- Human feedback: {feedback['feedback_id']} ({feedback['severity']})
- Eval case: {eval_case['eval_id']}
- Recommendation: {recommendation['recommendation_id']}

## Ranked Improvement

{recommendation['title']}

## Next Safe Action

Create a human-approved APPLY packet for the highest-ranked improvement. Do not commit, push, merge, call OpenAI, install packages, write telemetry, write approval inbox state, touch Night Supervisor, or touch broker/OANDA/live trading.
"""

    handoff = """🧩 CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: DRAFT_ONLY_DO_NOT_EXECUTE

TITLE
Draft APPLY Packet: Merge Confirmation Rule and Runtime Path Verification

DRAFT_ONLY
NO_EXECUTION_AUTHORITY
NO_COMMIT
NO_PUSH

MISSION
Create a future scoped APPLY packet that adds a merge-confirmation decision rule and runtime worker path-verification precheck.

VALIDATION
- Confirm allowed paths before edit.
- Confirm no runtime paths touched.
- Confirm no commit or push.

STOP POINT
Stop after drafting. This preview has no execution authority.
"""
    return ranked, report, handoff


def run(validate_only: bool, output_dir: Path) -> None:
    trace = load_json(FIXTURE_DIR / "TRACE_EVENT_EXAMPLE_001.json")
    feedback = load_json(FIXTURE_DIR / "HUMAN_FEEDBACK_EXAMPLE_001.json")
    eval_case = load_json(FIXTURE_DIR / "EVAL_CASE_EXAMPLE_001.json")
    recommendation = load_json(FIXTURE_DIR / "IMPROVEMENT_RECOMMENDATION_EXAMPLE_001.json")

    require_fields("trace", trace, ["trace_id", "expected_worktree", "actual_worktree", "lesson", "safety_flags"])
    require_fields("feedback", feedback, ["feedback_id", "feedback_text", "severity", "required_fix"])
    require_fields("eval_case", eval_case, ["eval_id", "expected_behavior", "blocked_behavior", "pass_fail_criteria"])
    require_fields("recommendation", recommendation, ["recommendation_id", "title", "scores", "priority_score", "recommended_next_action"])
    assert_local_safety([trace, feedback, eval_case, recommendation])

    ranked, report, handoff = build_outputs(trace, feedback, eval_case, recommendation)

    if validate_only:
        print("AIOS_IMPROVEMENT_LOOP_VALIDATE_ONLY: PASS")
        print("NO_OUTPUT_FILES_WRITTEN")
        return

    output_dir = output_dir.resolve()
    allowed_root = DEFAULT_OUTPUT_DIR.resolve()
    if output_dir != allowed_root:
        raise ValueError(f"Output directory must be {allowed_root}")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "RANKED_IMPROVEMENTS_001.json").write_text(json.dumps(ranked, indent=2) + "\n", encoding="utf-8")
    (output_dir / "IMPROVEMENT_LOOP_PREVIEW_REPORT_001.md").write_text(report, encoding="utf-8")
    (output_dir / "CODEX_HANDOFF_PREVIEW_001.md").write_text(handoff, encoding="utf-8")
    print("AIOS_IMPROVEMENT_LOOP_PREVIEW: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    run(validate_only=args.validate_only, output_dir=Path(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
