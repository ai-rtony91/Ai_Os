"""Runner for the broker read-only state probe lane."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_broker_read_only_state_probe_v1 import (
    BrokerReadOnlyProbeInput,
    evaluate_broker_read_only_state_probe,
    input_as_dict,
    result_as_dict,
)


STATE_JSON_PATH = Path("Reports/forex_delivery/AIOS_FOREX_BROKER_READ_ONLY_STATE_PROBE_V1_STATE.json")
REPORT_MD_PATH = Path("Reports/forex_delivery/AIOS_FOREX_BROKER_READ_ONLY_STATE_PROBE_V1_REPORT.md")


def build_default_probe_input() -> BrokerReadOnlyProbeInput:
    return BrokerReadOnlyProbeInput(
        broker_name="OANDA",
        broker_environment="practice_demo",
        config_template_present=True,
        owner_runtime_config_present=False,
        credential_reference_declared=False,
        credential_material_present=False,
        account_reference_declared=False,
        read_only_capabilities_declared=True,
        mutating_capabilities_blocked=True,
        network_disabled_for_packet=True,
        broker_api_called=False,
        credentials_read=False,
        env_read=False,
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        session_window_hours=22,
        session_window_days_per_week=6,
    )


def build_report_markdown(result: dict) -> str:
    blockers = result["blockers"]
    blocker_lines = "\n".join(f"- {item}" for item in blockers) if blockers else "- (none)"
    return f"""# Forex Broker Read-Only State Probe V1 Report

## Packet evaluation

Input:
- broker_name: {result['broker_name']}
- broker_environment: {result['broker_environment']}

Result:
- probe_status: {result['probe_status']}
- current_stage: {result['current_stage']}
- next_stage: {result['next_stage']}
- safe_next_action: {result['safe_next_action']}
- blockers:
{blocker_lines}

## Hard boundaries

- broker_api_called: {result['broker_api_called']}
- credentials_read: {result['credentials_read']}
- env_read: {result['env_read']}
- order_execution: {result['order_execution']}
- demo_authorized: {result['demo_authorized']}
- live_authorized: {result['live_authorized']}
"""


def run_probe(
    state_output: Path = STATE_JSON_PATH,
    report_output: Path = REPORT_MD_PATH,
) -> tuple[dict, dict]:
    probe_input = build_default_probe_input()
    probe_result = evaluate_broker_read_only_state_probe(probe_input)
    input_payload = input_as_dict(probe_input)
    result_payload = result_as_dict(probe_result)

    payload = {
        "input": input_payload,
        "result": result_payload,
    }

    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report_output.write_text(build_report_markdown(result_payload), encoding="utf-8")

    print(json.dumps(result_payload, separators=(",", ":")))

    return input_payload, result_payload


def main() -> None:
    run_probe()


if __name__ == "__main__":
    main()
