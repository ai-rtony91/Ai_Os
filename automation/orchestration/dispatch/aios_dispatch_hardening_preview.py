#!/usr/bin/env python3
"""Fixture-only AI_OS dispatch hardening preview runner."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = ROOT / "docs/AI_OS/dispatch/fixtures/DISPATCH_HARDENING_DECISION_EXAMPLE_001.json"
OUTPUT_DIR = ROOT / "docs/AI_OS/dispatch/hardening_outputs"
RESULT_PATH = OUTPUT_DIR / "DISPATCH_HARDENING_RESULT_001.json"
REPORT_PATH = OUTPUT_DIR / "DISPATCH_HARDENING_REPORT_001.md"

ROUTE_CONFIDENCE_THRESHOLD = 0.75
READINESS_THRESHOLD = 0.80
SAFETY_THRESHOLD = 0.90
RISK_THRESHOLD = 0.40

ROUTES = {
    "BLOCKED",
    "READ_ONLY_RECON",
    "DOCS_ONLY",
    "FIXTURE_ONLY",
    "DRY_RUN_IMPLEMENTATION",
    "APPLY_HUMAN_APPROVED",
    "PR_VALIDATION",
    "MERGE_HUMAN_APPROVED",
    "NIGHT_SUPERVISOR_PREVIEW",
    "NIGHT_SUPERVISOR_RUNTIME_PENDING_APPROVAL",
    "OPENAI_SMOKE_TEST_PENDING_APPROVAL",
    "RESPONSES_PACKET_DRAFT_PENDING_APPROVAL",
    "PROMPTFOO_RED_TEAM_PENDING_APPROVAL",
    "COMPUTER_USE_PENDING_APPROVAL",
    "PI_CAR_VOICE_PREVIEW",
    "PI_CAR_MOTOR_BLOCKED",
    "LIVE_TRADING_BLOCKED",
}

HARD_BLOCKER_FIELDS = {
    "live_openai_api_call": "LIVE_OPENAI_CALL_RISK",
    "api_key_required": "API_KEY_RISK",
    "api_key_printed": "API_KEY_RISK",
    "network_required": "NETWORK_RISK",
    "package_install_required": "UNKNOWN_RISK",
    "repo_mutation_allowed": "FORBIDDEN_PATH_RISK",
    "promptfoo_execution_allowed": "PROMPTFOO_EXECUTION_RISK",
    "computer_use_action_allowed": "COMPUTER_USE_ACTION_RISK",
    "skill_execution_allowed": "SKILL_UNREVIEWED_RISK",
    "night_supervisor_runtime_start_allowed": "NIGHT_SUPERVISOR_ACTIVE",
    "paper_sos_resume_allowed": "NIGHT_SUPERVISOR_ACTIVE",
    "controlled_run_allowed": "NIGHT_SUPERVISOR_ACTIVE",
    "commit_allowed": "APPROVAL_MISSING",
    "push_allowed": "APPROVAL_MISSING",
    "merge_allowed": "APPROVAL_MISSING",
}

BLOCKED_STATUSES = {
    "live_trading_status": "LIVE_TRADING_RISK",
    "broker_execution_status": "BROKER_RISK",
    "oanda_status": "OANDA_RISK",
    "pi_gpio_motor_status": "PI_MOTOR_RISK",
}

VALIDATORS_BY_ROUTE = {
    "NIGHT_SUPERVISOR_PREVIEW": [
        "git status check",
        "allowed-path scope check",
        "Night Supervisor lock/cycle check",
        "no runtime start check",
        "human approval check",
        "clean-state verifier",
    ],
    "BLOCKED": ["blocker report", "stop point verifier"],
}


def load_input() -> dict:
    with INPUT_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise SystemExit(f"AIOS_DISPATCH_HARDENING_FAIL_CLOSED: {message}")


def validate_packet(packet: dict) -> None:
    required = [
        "mode",
        "local_fixture_only",
        "decision_id",
        "packet_id",
        "route",
        "route_confidence",
        "risk_score",
        "readiness_score",
        "safety_score",
        "blocker_classes",
        "validators_required",
        "human_approval_required",
        "approval_threshold",
        "allowed_execution_mode",
        "fail_closed",
        "stop_point",
        "profitability_priority",
        *HARD_BLOCKER_FIELDS.keys(),
        *BLOCKED_STATUSES.keys(),
        "secrets_policy",
    ]
    missing = [field for field in required if field not in packet]
    if missing:
        fail(f"missing required fields: {', '.join(missing)}")
    if packet["route"] not in ROUTES:
        fail(f"unknown route: {packet['route']}")
    if packet["local_fixture_only"] is not True:
        fail("local_fixture_only must be true")
    if packet["profitability_priority"] != "TRUSTED_PROVEN_PROFITABILITY":
        fail("profitability priority must be TRUSTED_PROVEN_PROFITABILITY")
    if packet["fail_closed"] is not True:
        fail("fail_closed must be true")


def build_decision(packet: dict) -> dict:
    blockers = list(dict.fromkeys(packet.get("blocker_classes", [])))
    for field, blocker in HARD_BLOCKER_FIELDS.items():
        if packet.get(field) is True:
            blockers.append(blocker)
    for field, blocker in BLOCKED_STATUSES.items():
        if packet.get(field) != "BLOCKED":
            blockers.append(blocker)
    if packet.get("secrets_policy") != "NO_REAL_SECRETS":
        blockers.append("SECRET_RISK")

    route = packet["route"]
    if "UNKNOWN_RISK" in blockers:
        packet["route_confidence"] = min(packet["route_confidence"], 0.5)
    if blockers and any(
        item in blockers
        for item in {
            "SECRET_RISK",
            "API_KEY_RISK",
            "ENV_FILE_RISK",
            "SERVICE_ACCOUNT_FILE_RISK",
            "LIVE_TRADING_RISK",
            "BROKER_RISK",
            "OANDA_RISK",
            "PI_MOTOR_RISK",
            "PROFITABILITY_PRIORITY_VIOLATION",
            "UNKNOWN_RISK",
        }
    ):
        route = "BLOCKED"
    if packet["route_confidence"] < ROUTE_CONFIDENCE_THRESHOLD:
        blockers.append("UNKNOWN_RISK")
        route = "BLOCKED"
    if packet["risk_score"] > RISK_THRESHOLD:
        route = "BLOCKED"
    if packet["readiness_score"] < READINESS_THRESHOLD or packet["safety_score"] < SAFETY_THRESHOLD:
        blockers.append("VALIDATOR_MISSING")
        route = "BLOCKED"

    validators = VALIDATORS_BY_ROUTE.get(route, packet["validators_required"])
    if not validators:
        blockers.append("VALIDATOR_MISSING")
        route = "BLOCKED"
        validators = VALIDATORS_BY_ROUTE["BLOCKED"]

    return {
        **packet,
        "route": route,
        "blocker_classes": list(dict.fromkeys(blockers)),
        "validators_required": validators,
        "preview_generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "FAIL_CLOSED" if route == "BLOCKED" else "PREVIEW_PASS",
    }


def write_outputs(decision: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Dispatch Hardening Report 001",
        "",
        f"Decision: `{decision['decision_id']}`",
        f"Packet: `{decision['packet_id']}`",
        f"Route: `{decision['route']}`",
        f"Result: `{decision['result']}`",
        "",
        "## Safety",
        "",
        "- LOCAL_FIXTURE_ONLY",
        "- NO_LIVE_OPENAI_API_CALL",
        "- NO_API_KEY_REQUIRED",
        "- NO_NETWORK",
        "- NO_RUNTIME_AUTONOMY",
        "- NO_NIGHT_SUPERVISOR_RUNTIME_START",
        "- NO_PROMPTFOO_EXECUTION",
        "- NO_COMPUTER_USE_ACTIONS",
        "- NO_SKILL_EXECUTION",
        "- NO_BROKER_OANDA_LIVE_TRADING",
        "- NO_PI_GPIO_MOTOR",
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    packet = load_input()
    validate_packet(packet)
    decision = build_decision(packet)
    if args.validate_only:
        print("AI_OS_DISPATCH_HARDENING_PREVIEW")
        print("VALIDATE_ONLY_PASS")
        print(json.dumps(decision, sort_keys=True))
        return 0
    write_outputs(decision)
    print("AI_OS_DISPATCH_HARDENING_PREVIEW")
    print("LOCAL_FIXTURE_ONLY")
    print("DISPATCH_HARDENING_PREVIEW_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

