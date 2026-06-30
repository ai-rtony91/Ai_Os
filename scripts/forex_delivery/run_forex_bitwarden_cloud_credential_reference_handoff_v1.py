"""Runner for the Bitwarden cloud credential reference handoff packet."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_bitwarden_cloud_credential_reference_handoff_v1 import (  # noqa: E402
    BitwardenCloudCredentialReferenceInput,
    evaluate_bitwarden_cloud_credential_reference_handoff,
    input_as_dict,
    result_as_dict,
)


STATE_JSON_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_BITWARDEN_CLOUD_CREDENTIAL_REFERENCE_HANDOFF_V1_STATE.json"
)
REPORT_MD_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_BITWARDEN_CLOUD_CREDENTIAL_REFERENCE_HANDOFF_V1_REPORT.md"
)


def build_default_handoff_input() -> BitwardenCloudCredentialReferenceInput:
    return BitwardenCloudCredentialReferenceInput(
        broker_read_only_probe_landed=True,
        bitwarden_provider="Bitwarden",
        broker_runtime_item_ref="AIOS / OANDA / Practice Demo / Broker Runtime",
        credential_reference_map_item_ref="AIOS / Bitwarden / Credential Reference Map",
        broker_api_token_field_ref="broker_api_token",
        broker_account_id_field_ref="broker_account_id",
        endpoint_field_ref="endpoint",
        environment_field_ref="environment",
        allowed_mode_field_ref="allowed_mode",
        expected_broker="OANDA",
        expected_environment="practice_demo",
        expected_endpoint="https://api-fxpractice.oanda.com",
        expected_allowed_mode="read_only_until_owner_demo_approval",
        owner_reference_map_created=True,
        item_reference_declared=True,
        field_references_declared=True,
        secret_values_present_in_repo=False,
        bitwarden_cli_called=False,
        bitwarden_vault_read=False,
        credentials_read=False,
        env_read=False,
        broker_api_called=False,
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        session_window_hours=22,
        session_window_days_per_week=6,
    )


def build_report_markdown(result_payload: dict[str, object]) -> str:
    blockers = result_payload["blockers"]
    blockers_rendered = (
        "\n".join(f"- {item}" for item in blockers)
        if blockers
        else "- (none)"
    )
    return f"""# Forex Bitwarden Cloud Credential Reference Handoff V1 Report

## Packet evaluation

Input:
- broker_runtime_item_ref: {result_payload['broker_runtime_item_ref']}
- credential_reference_map_item_ref: {result_payload['credential_reference_map_item_ref']}

Result:
- handoff_status: {result_payload['handoff_status']}
- current_stage: {result_payload['current_stage']}
- next_stage: {result_payload['next_stage']}
- safe_next_action: {result_payload['safe_next_action']}
- blockers:
{blockers_rendered}

## Boundary flags

- bitwarden_cli_called: {result_payload['bitwarden_cli_called']}
- bitwarden_vault_read: {result_payload['bitwarden_vault_read']}
- credentials_read: {result_payload['credentials_read']}
- env_read: {result_payload['env_read']}
- broker_api_called: {result_payload['broker_api_called']}
- order_execution: {result_payload['order_execution']}
- demo_authorized: {result_payload['demo_authorized']}
- live_authorized: {result_payload['live_authorized']}
"""


def run_handoff(
    state_output: Path = STATE_JSON_PATH,
    report_output: Path = REPORT_MD_PATH,
) -> tuple[dict[str, object], dict[str, object]]:
    handoff_input = build_default_handoff_input()
    handoff_result = evaluate_bitwarden_cloud_credential_reference_handoff(handoff_input)
    input_payload = input_as_dict(handoff_input)
    result_payload = result_as_dict(handoff_result)

    artifact = {
        "input": input_payload,
        "result": result_payload,
    }
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    report_output.write_text(build_report_markdown(result_payload), encoding="utf-8")

    print(json.dumps(result_payload, separators=(",", ":")))
    return input_payload, result_payload


def main() -> None:
    run_handoff()


if __name__ == "__main__":
    main()
