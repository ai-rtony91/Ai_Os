from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from automation.forex_engine import (
    forex_autonomy_sanitized_evidence_intake_update_v1 as intake,
    supervised_autonomy_governor_v1 as governor,
)


RUNNER_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "forex_delivery"
    / "run_forex_autonomy_sanitized_evidence_intake_update_v1.py"
)
STATE_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json"
)
GOVERNOR_INPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json"
)
INPUT_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json"
)
STATE_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json"
)
REPORT_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_REPORT.md"
)
NEXT_PACKET_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_NEXT_CODEX_PACKET_V1.md"
)


def _state_mapping() -> dict[str, str]:
    return {
        "candidate_status": "AUTONOMY_BLOCKED",
        "bucket_status": "BUCKET_MAX_LOSS_HOLD",
        "next_autonomy_action": "HOLD_FOR_RISK_RESET",
    }


def _governor_ready_input(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "profitability_evidence_status": "READY",
        "sample_size": governor.MIN_SAMPLE_SIZE,
        "walk_forward_windows": governor.MIN_WALK_FORWARD_WINDOWS,
        "max_drawdown": governor.MAX_DRAWDOWN_RATIO,
        "profit_factor": governor.MIN_PROFIT_FACTOR,
        "expectancy": governor.MIN_EXPECTANCY,
        "broker_readiness": True,
        "live_bridge_eligibility": True,
        "kill_switch_state": "ARMED",
        "daily_stop_state": "ARMED",
        "max_loss_state": "ARMED",
        "order_count_last_24h": 0,
        "tp_sl_present": True,
        "monitoring_ready": True,
        "evidence_age_days": 0,
        "owner_approval_status": "APPROVED_FOR_DEMO",
        "live_exception_requested": False,
        "live_bridge_external_evidence": False,
        "owner_live_micro_exception_approved": False,
        "realized_broker_evidence": False,
    }
    payload.update(overrides)
    return payload


def _governor_ready_input_with_restricted_fields() -> dict[str, object]:
    return _governor_ready_input(
        account_id="acct-not-for-output",
        api_key="key-not-for-output",
        token="token-not-for-output",
        password="password-not-for-output",
        secret_value="secret-not-for-output",
        credential_path="credential-not-for-output",
        oanda_account="oanda-not-for-output",
        broker_id="broker-not-for-output",
    )


@pytest.mark.parametrize("candidate_id", ["candidate-safe-123", 12345])
def test_safe_candidate_id_from_base_governor_input_survives_outputs(
    tmp_path: Path, candidate_id: str | int
):
    state_output = tmp_path / "state-output.json"

    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(candidate_id=candidate_id),
        write_state=True,
        write_state_path=state_output,
    )

    assert result["updated_governor_input_preview"]["candidate_id"] == candidate_id
    assert "candidate_id" not in result["rejected_base_governor_input_fields"]

    state_payload = json.loads(state_output.read_text(encoding="utf-8"))
    assert state_payload["updated_governor_input_preview"]["candidate_id"] == candidate_id

    state_path = tmp_path / "state.json"
    base_path = tmp_path / "base.json"
    state_path.write_text(json.dumps(_state_mapping()), encoding="utf-8")
    base_path.write_text(
        json.dumps(_governor_ready_input(candidate_id=candidate_id)),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--state-json",
            str(state_path),
            "--governor-input-json",
            str(base_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stdout_payload = json.loads(completed.stdout)
    assert stdout_payload["updated_governor_input_preview"]["candidate_id"] == candidate_id


def test_safe_sample_input_candidate_id_is_preserved():
    sample_input = governor.safe_sample_input()

    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=sample_input,
    )

    assert (
        result["updated_governor_input_preview"]["candidate_id"]
        == sample_input["candidate_id"]
    )
    assert "candidate_id" not in result["rejected_base_governor_input_fields"]


@pytest.mark.parametrize(
    "candidate_id",
    [
        "candidate-account-123",
        "candidate-token-123",
        "candidate-secret-123",
        "candidate-credential-123",
        "candidate-password-123",
        "candidate-api-123",
        "candidate-oanda-123",
        "candidate-broker-123",
    ],
)
def test_candidate_id_with_sensitive_fragments_is_rejected(candidate_id: str):
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(candidate_id=candidate_id),
    )

    assert "candidate_id" not in result["updated_governor_input_preview"]
    assert "candidate_id" in result["rejected_base_governor_input_fields"]
    safe_output = json.dumps(
        intake.build_safe_output_result_payload(result),
        sort_keys=True,
    )
    assert candidate_id not in safe_output


@pytest.mark.parametrize(
    "candidate_id",
    [None, True, 1.5, ["candidate-safe-123"], {"candidate": "candidate-safe-123"}],
)
def test_non_string_non_int_candidate_id_is_rejected(candidate_id: object):
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(candidate_id=candidate_id),
    )

    assert "candidate_id" not in result["updated_governor_input_preview"]
    assert "candidate_id" in result["rejected_base_governor_input_fields"]


def test_default_run_no_evidence_applied():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_json=STATE_PATH,
        governor_input_json=GOVERNOR_INPUT_PATH,
    )

    assert result["intake_status"] == intake.INTAKE_NO_EVIDENCE
    assert result["rerun_recommended"] is False
    assert result["controller_candidate_status"] == "AUTONOMY_BLOCKED"
    assert result["controller_bucket_status"] == "BUCKET_MAX_LOSS_HOLD"
    assert result["next_safe_action"]


def test_default_run_lists_missing_fields():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_json=STATE_PATH,
        governor_input_json=GOVERNOR_INPUT_PATH,
    )

    assert "profitability_evidence_status" in result["missing_evidence_fields"]
    assert "sample_size" in result["missing_evidence_fields"]
    assert "walk_forward_windows" in result["missing_evidence_fields"]
    assert "max_drawdown" in result["missing_evidence_fields"]
    assert "profit_factor" in result["missing_evidence_fields"]
    assert "expectancy" in result["missing_evidence_fields"]
    assert "owner_approval_status" in result["missing_evidence_fields"]
    assert "evidence_age_days" in result["missing_evidence_fields"]


def test_broker_readiness_false_is_governor_gap_without_ready_rerun():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(broker_readiness=False),
        evidence_mapping={"profitability_evidence_status": "READY"},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_APPLIED
    assert "broker_readiness" in result["missing_evidence_fields"]
    assert result["blocked_evidence_fields"] == []
    assert result["rerun_recommended"] is False
    assert "Rerun the autonomy completion governor" not in result["next_safe_action"]


def test_order_count_last_24h_missing_is_governor_gap():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(order_count_last_24h=None),
    )

    assert "order_count_last_24h" in result["missing_evidence_fields"]
    assert result["rerun_recommended"] is False


@pytest.mark.parametrize("value", [10.9, -0.1])
def test_base_order_count_invalid_values_block_ready_preview(value: object):
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(order_count_last_24h=value),
        evidence_mapping={"profitability_evidence_status": "READY"},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_APPLIED
    assert "order_count_last_24h" in (
        result["missing_evidence_fields"] + result["blocked_evidence_fields"]
    )
    assert result["rerun_recommended"] is False


def test_order_count_last_24h_above_governor_max_is_blocked_gap():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(
            order_count_last_24h=governor.MAX_ORDERS_24H + 1
        ),
    )

    assert "order_count_last_24h" in result["blocked_evidence_fields"]
    assert result["missing_evidence_fields"] == []
    assert result["rerun_recommended"] is False


@pytest.mark.parametrize("value", [0, governor.MAX_ORDERS_24H])
def test_order_count_last_24h_valid_limits_remain_accepted(value: int):
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(order_count_last_24h=value),
        evidence_mapping={"profitability_evidence_status": "READY"},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_APPLIED
    assert result["missing_evidence_fields"] == []
    assert result["blocked_evidence_fields"] == []
    assert result["rerun_recommended"] is True


def test_order_count_last_24h_above_limit_blocks_ready_preview():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(
            order_count_last_24h=governor.MAX_ORDERS_24H + 1
        ),
        evidence_mapping={"profitability_evidence_status": "READY"},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_APPLIED
    assert "order_count_last_24h" in result["blocked_evidence_fields"]
    assert result["rerun_recommended"] is False


def test_owner_approval_denied_is_owner_block_gap():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(owner_approval_status="DENIED"),
        evidence_mapping={"profitability_evidence_status": "READY"},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_APPLIED
    assert "owner_approval_status" in result["blocked_evidence_fields"]
    assert result["missing_evidence_fields"] == []
    assert result["rerun_recommended"] is False


def test_owner_approval_pending_owner_review_is_owner_gap():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(
            owner_approval_status="PENDING_OWNER_REVIEW"
        ),
    )

    assert "owner_approval_status" in result["missing_evidence_fields"]
    assert result["blocked_evidence_fields"] == []
    assert result["rerun_recommended"] is False


def test_profitability_ready_with_owner_denied_still_has_evidence_gaps():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(owner_approval_status="DENIED"),
    )

    assert result["updated_governor_input_preview"]["profitability_evidence_status"] == "READY"
    assert result["missing_evidence_fields"] or result["blocked_evidence_fields"]
    assert "owner_approval_status" in result["blocked_evidence_fields"]


def test_empty_evidence_mapping_is_no_evidence_applied():
    current_governor_input = _governor_ready_input()
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=current_governor_input,
        evidence_mapping={},
    )

    assert result["intake_status"] == intake.INTAKE_NO_EVIDENCE
    assert result["applied_evidence_fields"] == []
    assert result["rejected_evidence_fields"] == []
    assert result["rerun_recommended"] is False
    assert result["updated_governor_input_preview"] == current_governor_input
    assert "Rerun the autonomy completion governor" not in result["next_safe_action"]


def test_empty_evidence_json_file_is_no_evidence_applied(tmp_path: Path):
    current_governor_input = _governor_ready_input()
    evidence_path = tmp_path / "empty-evidence.json"
    evidence_path.write_text("{}", encoding="utf-8")

    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=current_governor_input,
        evidence_json=evidence_path,
    )

    assert result["intake_status"] == intake.INTAKE_NO_EVIDENCE
    assert result["applied_evidence_fields"] == []
    assert result["rejected_evidence_fields"] == []
    assert result["rerun_recommended"] is False
    assert result["updated_governor_input_preview"] == current_governor_input


def test_critical_safety_fields_blocked_when_disarmed_or_false():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping={
            "candidate_status": "AUTONOMY_BLOCKED",
            "bucket_status": "BUCKET_MAX_LOSS_HOLD",
            "next_autonomy_action": "HOLD_FOR_RISK_RESET",
        },
        governor_input_mapping={
            "profitability_evidence_status": "READY",
            "sample_size": 45,
            "walk_forward_windows": 4,
            "max_drawdown": 0.1,
            "profit_factor": 2.2,
            "expectancy": 0.6,
            "broker_readiness": True,
            "live_bridge_eligibility": True,
            "kill_switch_state": "DISARMED",
            "daily_stop_state": "OFF",
            "max_loss_state": "UNSET",
            "order_count_last_24h": 0,
            "tp_sl_present": True,
            "monitoring_ready": False,
            "evidence_age_days": 5,
            "owner_approval_status": "APPROVED_FOR_DEMO",
            "live_exception_requested": False,
            "live_bridge_external_evidence": False,
            "owner_live_micro_exception_approved": False,
            "realized_broker_evidence": False,
        },
    )

    assert result["intake_status"] == intake.INTAKE_NO_EVIDENCE
    assert result["blocked_evidence_fields"] == [
        "kill_switch_state",
        "daily_stop_state",
        "max_loss_state",
        "monitoring_ready",
    ]
    assert result["rerun_recommended"] is False


def test_allowed_keys_merge_into_preview():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping={
            "candidate_status": "AUTONOMY_BLOCKED",
            "bucket_status": "BUCKET_MAX_LOSS_HOLD",
            "next_autonomy_action": "HOLD_FOR_RISK_RESET",
        },
        governor_input_mapping={
            "profitability_evidence_status": "PENDING",
            "sample_size": 10,
            "walk_forward_windows": 1,
            "max_drawdown": 0.21,
            "profit_factor": 1.0,
            "expectancy": -0.2,
            "broker_readiness": True,
            "live_bridge_eligibility": False,
            "kill_switch_state": "UNKNOWN",
            "daily_stop_state": "UNKNOWN",
            "max_loss_state": "UNSET",
            "order_count_last_24h": 1,
            "tp_sl_present": False,
            "monitoring_ready": True,
            "evidence_age_days": 30,
            "owner_approval_status": "PENDING",
            "live_exception_requested": False,
            "live_bridge_external_evidence": False,
            "owner_live_micro_exception_approved": False,
            "realized_broker_evidence": False,
        },
        evidence_mapping={
            "sample_size": 45,
            "walk_forward_windows": 4,
            "profitability_evidence_status": "READY",
            "max_drawdown": 0.08,
            "profit_factor": 2.2,
            "expectancy": 0.55,
            "evidence_age_days": 5,
            "owner_approval_status": "APPROVED_FOR_DEMO",
            "monitoring_ready": True,
        },
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_APPLIED
    assert result["updated_governor_input_preview"]["sample_size"] == 45
    assert result["updated_governor_input_preview"]["profitability_evidence_status"] == "READY"
    assert result["updated_governor_input_preview"]["owner_approval_status"] == "APPROVED_FOR_DEMO"
    assert "sample_size" in result["applied_evidence_fields"]
    assert result["applied_evidence_fields"]


def test_unknown_evidence_keys_are_rejected():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping={
            "candidate_status": "AUTONOMY_BLOCKED",
            "bucket_status": "BUCKET_MAX_LOSS_HOLD",
            "next_autonomy_action": "HOLD_FOR_RISK_RESET",
        },
        governor_input_mapping={"profitability_evidence_status": "PENDING"},
        evidence_mapping={"not_an_allowed_field": True},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_REJECTED
    assert "not_an_allowed_field" in result["rejected_evidence_fields"]
    assert not result["applied_evidence_fields"]


def test_forbidden_sensitive_evidence_keys_are_rejected():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping={
            "candidate_status": "AUTONOMY_BLOCKED",
            "bucket_status": "BUCKET_MAX_LOSS_HOLD",
            "next_autonomy_action": "HOLD_FOR_RISK_RESET",
        },
        governor_input_mapping={"profitability_evidence_status": "PENDING"},
        evidence_mapping={"account_id": "owner"},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_REJECTED
    assert "account_id" in result["rejected_evidence_fields"]


def test_base_input_filtering_removes_restricted_names_from_preview_and_outputs(
    tmp_path: Path,
):
    state_output = tmp_path / "state-output.json"
    report_output = tmp_path / "report-output.md"
    restricted_names = {
        "account_id",
        "api_key",
        "token",
        "password",
        "secret_value",
        "credential_path",
        "oanda_account",
        "broker_id",
    }

    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input_with_restricted_fields(),
        write_state=True,
        write_state_path=state_output,
        write_report=True,
        write_report_path=report_output,
    )

    assert restricted_names.issubset(
        set(result["rejected_base_governor_input_fields"])
    )
    for name in restricted_names:
        assert name not in result["updated_governor_input_preview"]

    state_payload = json.loads(state_output.read_text(encoding="utf-8"))
    state_text = json.dumps(state_payload, sort_keys=True)
    report_text = report_output.read_text(encoding="utf-8")
    report_lines = report_text.splitlines()
    assert state_payload["safety_boundary"]["account_identifier_persistence_allowed"] is False
    assert state_payload["safety_boundary"]["credentials_allowed"] is False
    for name in restricted_names:
        assert f'"{name}"' not in state_text
        assert f"- {name}" not in report_lines
        assert f"{name}: " not in report_text
        if name != "account_id":
            assert name not in report_text


def test_runner_stdout_omits_suppressed_base_names(tmp_path: Path):
    state_path = tmp_path / "state.json"
    base_path = tmp_path / "base.json"
    state_path.write_text(json.dumps(_state_mapping()), encoding="utf-8")
    base_path.write_text(
        json.dumps(_governor_ready_input_with_restricted_fields()),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--state-json",
            str(state_path),
            "--governor-input-json",
            str(base_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert "safety_boundary" not in payload
    for name in {
        "account_id",
        "api_key",
        "token",
        "password",
        "secret_value",
        "credential_path",
        "oanda_account",
        "broker_id",
    }:
        assert name not in completed.stdout


@pytest.mark.parametrize("value", [10.9, -0.1, -1, "1", True])
def test_evidence_mapping_order_count_invalid_values_are_rejected(value: object):
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(),
        evidence_mapping={"order_count_last_24h": value},
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_REJECTED
    assert "order_count_last_24h" in result["rejected_evidence_fields"]
    assert result["rerun_recommended"] is False


def test_evidence_json_order_count_float_is_rejected(tmp_path: Path):
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps({"order_count_last_24h": 10.9}),
        encoding="utf-8",
    )

    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping=_state_mapping(),
        governor_input_mapping=_governor_ready_input(),
        evidence_json=evidence_path,
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_REJECTED
    assert "order_count_last_24h" in result["rejected_evidence_fields"]
    assert result["rerun_recommended"] is False


def test_no_credentials_account_identifiers_env_broker_api_fields_are_not_accepted():
    result = intake.run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_mapping={
            "candidate_status": "AUTONOMY_BLOCKED",
            "bucket_status": "BUCKET_MAX_LOSS_HOLD",
            "next_autonomy_action": "HOLD_FOR_RISK_RESET",
        },
        governor_input_mapping={"profitability_evidence_status": "PENDING"},
        evidence_mapping={
            "api_key": "abc",
            "oanda_account_id": "123",
            "credential_path": "/tmp/cred",
        },
    )

    assert result["intake_status"] == intake.INTAKE_SANITIZED_REJECTED
    assert not result["applied_evidence_fields"]
    assert result["rejected_evidence_fields"]


def test_non_dict_evidence_json_is_rejected(tmp_path: Path):
    payload_path = tmp_path / "evidence-not-dict.json"
    payload_path.write_text("[\"not\", \"a\", \"dict\"]", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--state-json",
            str(STATE_PATH),
            "--governor-input-json",
            str(GOVERNOR_INPUT_PATH),
            "--evidence-json",
            str(payload_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "must be an object" in result.stderr


def test_forbidden_file_path_fragments_are_rejected(tmp_path: Path):
    state_path = tmp_path / "secret_state.json"
    state_path.write_text("{}", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--state-json",
            str(state_path),
            "--governor-input-json",
            str(GOVERNOR_INPUT_PATH),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "refusing forbidden local input path" in result.stderr

    payload = {"sample_size": 42}
    evidence_path = tmp_path / "broker_evidence.json"
    evidence_path.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--evidence-json",
            str(evidence_path),
            "--state-json",
            str(STATE_PATH),
            "--governor-input-json",
            str(GOVERNOR_INPUT_PATH),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "refusing forbidden local input path" in result.stderr


def test_no_forbidden_source_imports_in_module_and_runner() -> None:
    source = Path(
        "automation/forex_engine/forex_autonomy_sanitized_evidence_intake_update_v1.py"
    ).read_text(encoding="utf-8").lower()
    runner_source = Path(
        "scripts/forex_delivery/run_forex_autonomy_sanitized_evidence_intake_update_v1.py"
    ).read_text(encoding="utf-8").lower()

    forbidden_source = (
        "requests",
        "socket",
        "urllib",
        "dotenv",
        "os.environ",
        "import oanda",
        "from oanda",
        "import broker",
        "from broker",
    )
    assert not [fragment for fragment in forbidden_source if fragment in source + "\n" + runner_source]


def test_runner_prints_valid_json():
    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["intake_status"] in {
        intake.INTAKE_NO_EVIDENCE,
        intake.INTAKE_SANITIZED_APPLIED,
        intake.INTAKE_SANITIZED_REJECTED,
    }
    assert payload["controller_candidate_status"]
    assert payload["controller_bucket_status"]


def test_runner_writes_state_report_and_input_template_with_valid_json():
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--write-state",
            "--write-report",
            "--write-input-template",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0

    state_payload = json.loads(STATE_OUTPUT_PATH.read_text(encoding="utf-8"))
    template_payload = json.loads(INPUT_TEMPLATE_PATH.read_text(encoding="utf-8"))
    report_payload = REPORT_OUTPUT_PATH.read_text(encoding="utf-8")

    assert "intake_status" in state_payload
    assert set(intake.ALLOWED_EVIDENCE_FIELDS).issuperset(template_payload.keys())
    assert "Status:" in report_payload
    assert "Missing evidence fields:" in report_payload


def test_next_codex_packet_has_required_executable_header_sections():
    packet = NEXT_PACKET_PATH.read_text(encoding="utf-8")

    assert packet.startswith("CODEX-ONLY PROMPT\n")
    assert "AI_OS EXECUTION TOKEN" in packet
    assert "AI_OS BOOTSTRAP REQUIRED" in packet
    assert "ALLOWED PATHS" in packet
    assert "FORBIDDEN PATHS" in packet
    assert "VALIDATORS" in packet
