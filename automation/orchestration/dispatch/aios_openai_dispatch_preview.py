#!/usr/bin/env python3
"""Local-only AI_OS OpenAI dispatch preview runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = ROOT / "docs/AI_OS/dispatch/fixtures/OPENAI_PACKET_DRAFT_EXAMPLE_001.json"
OUTPUT_DIR = ROOT / "docs/AI_OS/dispatch/preview_outputs"
RESULT_PATH = OUTPUT_DIR / "DISPATCH_PREVIEW_RESULT_001.json"
REPORT_PATH = OUTPUT_DIR / "DISPATCH_PREVIEW_REPORT_001.md"

REQUIRED_FALSE = [
    "live_openai_api_call",
    "api_key_required",
    "network_required",
    "package_install_required",
    "repo_mutation_allowed",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
]

BLOCK_TERMS = [
    "openai live call",
    "live openai call",
    "api key required",
    ".env",
    "package install",
    "network required",
    "broker execution",
    "oanda execution",
    "live trading",
    "real order",
    "pi gpio",
    "pi motor",
    "night supervisor runtime start",
    "telemetry write",
    "control write",
    "approval inbox write",
    "secret access",
    "commit allowed",
    "push allowed",
    "merge allowed",
]


def load_packet(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise SystemExit(f"SAFETY_FAIL: {message}")


def validate_packet(packet: dict) -> None:
    missing = [field for field in REQUIRED_FALSE if field not in packet]
    if missing:
        fail(f"missing required safety fields: {', '.join(missing)}")
    for field in REQUIRED_FALSE:
        if packet[field] is not False:
            fail(f"{field} must be false")
    for field in ["live_trading_status", "broker_execution_status", "oanda_status", "pi_gpio_motor_status"]:
        if packet.get(field) != "BLOCKED":
            fail(f"{field} must be BLOCKED")
    if packet.get("human_approval_required") is not True:
        fail("human_approval_required must be true")
    if packet.get("profitability_priority") != "TRUSTED_PROVEN_PROFITABILITY":
        fail("profitability priority missing")
    if packet.get("fail_closed") is not True:
        fail("fail_closed must be true")
    raw = json.dumps(packet, sort_keys=True).lower()
    for term in BLOCK_TERMS:
        if term in raw and term not in {"live trading", ".env"}:
            fail(f"blocked term requested: {term}")


def build_decision(packet: dict) -> dict:
    route = packet.get("requested_route", "BLOCKED")
    allowed_routes = {
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
    }
    if route not in allowed_routes:
        fail(f"unknown route: {route}")
    if route == "NIGHT_SUPERVISOR_RUNTIME_PENDING_APPROVAL":
        route = "NIGHT_SUPERVISOR_PREVIEW"
    return {
        "packet_id": packet["packet_id"],
        "mode": "DRY_RUN",
        "local_fixture_only": True,
        "live_openai_api_call": False,
        "api_key_required": False,
        "network_required": False,
        "package_install_required": False,
        "repo_mutation_allowed": False,
        "dispatcher_route": route,
        "night_supervisor_dispatch_allowed": route == "NIGHT_SUPERVISOR_PREVIEW",
        "night_supervisor_runtime_start_allowed": False,
        "validator_chain": [
            "git status --short --branch",
            "parse dispatch JSON fixtures",
            "confirm no forbidden paths touched",
            "confirm no Night Supervisor runtime start",
            "confirm human approval required",
        ],
        "human_approval_required": True,
        "commit_allowed": False,
        "push_allowed": False,
        "merge_allowed": False,
        "live_trading_status": "BLOCKED",
        "broker_execution_status": "BLOCKED",
        "oanda_status": "BLOCKED",
        "pi_gpio_motor_status": "BLOCKED",
        "profitability_priority": "TRUSTED_PROVEN_PROFITABILITY",
        "fail_closed": True,
        "stop_point": "Preview route only. Do not start Night Supervisor runtime.",
    }


def write_outputs(decision: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Dispatch Preview Report",
        "",
        f"Packet: `{decision['packet_id']}`",
        f"Route: `{decision['dispatcher_route']}`",
        "",
        "## Safety",
        "",
        "- local fixture only",
        "- no live OpenAI API call",
        "- no API key required",
        "- no network required",
        "- no Night Supervisor runtime start",
        "- no broker/OANDA/live trading",
        "- no Pi GPIO/motor",
        "- human approval required",
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    packet = load_packet(INPUT_PATH)
    validate_packet(packet)
    decision = build_decision(packet)
    if args.validate_only:
        print("VALIDATE_ONLY_PASS")
        print(json.dumps(decision, sort_keys=True))
        return 0
    write_outputs(decision)
    print("DISPATCH_PREVIEW_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
