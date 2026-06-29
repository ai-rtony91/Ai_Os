from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from dataclasses import asdict

from automation.forex_engine.forex_broker_read_only_state_probe_v1 import (
    BrokerReadOnlyProbeInput,
    evaluate_broker_read_only_state_probe,
)
from scripts.forex_delivery.run_forex_broker_read_only_state_probe_v1 import build_report_markdown


def _base_input() -> BrokerReadOnlyProbeInput:
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


def _ready_input() -> BrokerReadOnlyProbeInput:
    base = _base_input()
    return replace(
        base,
        owner_runtime_config_present=True,
        credential_reference_declared=True,
        account_reference_declared=True,
    )


def test_default_input_returns_owner_runtime_config_required():
    result = evaluate_broker_read_only_state_probe(_base_input())
    assert result.probe_status == "OWNER_RUNTIME_CONFIG_REQUIRED"
    assert result.current_stage == "broker_read_only_state_probe"
    assert result.next_stage == "owner_runtime_config_handoff"


def test_missing_template_returns_template_required():
    result = evaluate_broker_read_only_state_probe(
        replace(_base_input(), config_template_present=False),
    )
    assert result.probe_status == "BROKER_READ_ONLY_TEMPLATE_REQUIRED"


def test_missing_credential_reference_returns_credential_reference_required():
    result = evaluate_broker_read_only_state_probe(
        replace(_base_input(), owner_runtime_config_present=True),
    )
    assert result.probe_status == "CREDENTIAL_REFERENCE_REQUIRED"

def test_credential_material_present_returns_secret_material_rejected():
    result = evaluate_broker_read_only_state_probe(
        replace(_ready_input(), credential_material_present=True),
    )
    assert result.probe_status == "SECRET_MATERIAL_REJECTED"


def test_missing_account_reference_returns_account_reference_required():
    result = evaluate_broker_read_only_state_probe(
        replace(
            _ready_input(),
            credential_reference_declared=True,
            account_reference_declared=False,
        ),
    )
    assert result.probe_status == "ACCOUNT_REFERENCE_REQUIRED"


def test_missing_read_only_declarations_returns_read_only_capability_required():
    result = evaluate_broker_read_only_state_probe(
        replace(_ready_input(), read_only_capabilities_declared=False),
    )
    assert result.probe_status == "READ_ONLY_CAPABILITY_DECLARATION_REQUIRED"


def test_mutating_capabilities_not_blocked_returns_mutating_capability_block_required():
    result = evaluate_broker_read_only_state_probe(
        replace(_ready_input(), mutating_capabilities_blocked=False),
    )
    assert result.probe_status == "MUTATING_CAPABILITY_BLOCK_REQUIRED"


def test_network_not_disabled_returns_network_must_remain_disabled_for_this_packet():
    result = evaluate_broker_read_only_state_probe(
        replace(_ready_input(), network_disabled_for_packet=False),
    )
    assert result.probe_status == "NETWORK_MUST_REMAIN_DISABLED_FOR_THIS_PACKET"


def _violation_input() -> BrokerReadOnlyProbeInput:
    return replace(_ready_input(), broker_api_called=True)


def test_any_protected_flag_true_returns_protected_boundary_violation():
    for field_name in [
        "broker_api_called",
        "credentials_read",
        "env_read",
        "order_execution",
        "demo_authorized",
        "live_authorized",
    ]:
        result = evaluate_broker_read_only_state_probe(
            replace(_ready_input(), **{field_name: True}),
        )
        assert result.probe_status == "PROTECTED_BOUNDARY_VIOLATION"


def test_fully_complete_nonsecret_input_returns_ready():
    result = evaluate_broker_read_only_state_probe(_ready_input())
    assert result.probe_status == "BROKER_READ_ONLY_PROBE_CONTRACT_READY"
    assert result.next_stage == "credential_persistence_owner_handoff"


def test_protected_flags_are_false_in_normal_outputs():
    result = evaluate_broker_read_only_state_probe(_ready_input())
    assert result.broker_api_called is False
    assert result.credentials_read is False
    assert result.env_read is False
    assert result.order_execution is False
    assert result.demo_authorized is False
    assert result.live_authorized is False


def test_runner_writes_state_json_and_report():
    command = [
        sys.executable,
        "scripts/forex_delivery/run_forex_broker_read_only_state_probe_v1.py",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    assert completed.returncode == 0
    assert completed.stdout.startswith("{")

    state_path = Path(
        "Reports/forex_delivery/AIOS_FOREX_BROKER_READ_ONLY_STATE_PROBE_V1_STATE.json",
    )
    report_path = Path(
        "Reports/forex_delivery/AIOS_FOREX_BROKER_READ_ONLY_STATE_PROBE_V1_REPORT.md",
    )

    state_json = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_json["result"]["probe_status"] == "OWNER_RUNTIME_CONFIG_REQUIRED"
    assert report_path.exists()
    assert "OWNER_RUNTIME_CONFIG_REQUIRED" in report_path.read_text(encoding="utf-8")


def test_config_template_exists_and_is_nosecret():
    template_path = Path(
        "configs/forex/AIOS_FOREX_BROKER_READ_ONLY_STATE_PROBE_V1.example.json",
    )
    data = json.loads(template_path.read_text(encoding="utf-8"))
    assert data["broker_name"] == "OANDA"
    assert data["broker_environment"] == "practice_demo"
    assert data["credential_reference"] == "OWNER_RUNTIME_SECRET_REFERENCE_REQUIRED"
    assert data["account_reference"] == "OWNER_MASKED_ACCOUNT_REFERENCE_REQUIRED"
    assert data["network_mode_for_this_packet"] == "DISABLED"
    assert data["session_window_hours"] == 22
    assert data["session_window_days_per_week"] == 6
    assert data["contains_secret_material"] is False
    assert all(
        key in data
        for key in (
            "read_only_capabilities",
            "forbidden_mutating_capabilities",
        )
    )


def test_docs_include_autonomous_target():
    doc_path = Path(
        "docs/trading_lab/forex/FOREX_BROKER_READ_ONLY_STATE_PROBE_V1.md",
    )
    text = doc_path.read_text(encoding="utf-8")
    assert "22hr/day" in text
    assert "6day/week" in text


def test_report_includes_next_stage_for_ready_input_when_evaluated():
    ready_input = _ready_input()
    ready_result = evaluate_broker_read_only_state_probe(ready_input)
    assert ready_result.next_stage == "credential_persistence_owner_handoff"
    assert ready_result.probe_status == "BROKER_READ_ONLY_PROBE_CONTRACT_READY"
    report = build_report_markdown(asdict(ready_result))
    assert "next_stage: credential_persistence_owner_handoff" in report
