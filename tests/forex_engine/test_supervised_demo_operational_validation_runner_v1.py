from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import supervised_demo_operational_validation_runner_v1 as runner
from scripts.forex_delivery import run_supervised_demo_operational_validation_runner_v1 as cli


RUNNER = (
    ROOT
    / "scripts"
    / "forex_delivery"
    / "run_supervised_demo_operational_validation_runner_v1.py"
)


def ready_input(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "candidate_id": "candidate-ready",
        "candidate_status": "REVIEW_READY",
        "selected_candidate_present": True,
        "candidate_review_ready": True,
        "owner_review_required": True,
        "risk_boundary_confirmed": True,
        "evidence_collection_ready": True,
        "operational_health_ready": True,
        "no_open_trade": True,
        "no_pending_order": True,
        "no_live_endpoint": True,
        "no_credential_access": True,
        "no_account_id_access": True,
        "no_money_movement": True,
        "no_scheduler_activation": True,
        "no_daemon_activation": True,
        "no_webhook_activation": True,
        "owner_approval_status": "APPROVED_FOR_SUPERVISED_DEMO_VALIDATION",
        "kill_switch_state": "ARMED",
    }
    base.update(overrides)
    return base


def test_ready_path_allows_supervised_demo_validation_only() -> None:
    result = runner.evaluate_supervised_demo_operational_validation(ready_input())

    assert (
        result["operational_validation_status"]
        == runner.READY_FOR_SUPERVISED_DEMO_VALIDATION
    )
    assert result["allowed_to_enter_supervised_demo_validation"] is True
    assert result["blockers"] == []
    assert result["safety_boundary"]["demo_routing_allowed"] is False
    assert result["safety_boundary"]["money_movement_allowed"] is False


def test_missing_candidate_requires_more_evidence() -> None:
    result = runner.evaluate_supervised_demo_operational_validation(
        ready_input(
            candidate_id="",
            selected_candidate_present=False,
            candidate_review_ready=None,
        )
    )

    assert result["operational_validation_status"] == runner.REQUIRE_MORE_EVIDENCE
    assert result["allowed_to_enter_supervised_demo_validation"] is False
    assert result["candidate_status"] == "REVIEW_READY"
    assert any(
        "selected_candidate_present must be true" in item
        for item in result["required_evidence"]
    )


def test_not_review_ready_candidate_is_rejected() -> None:
    result = runner.evaluate_supervised_demo_operational_validation(
        ready_input(
            candidate_status="NOT_REVIEW_READY",
            candidate_review_ready=False,
        )
    )

    assert result["operational_validation_status"] == runner.REJECTED_FOR_DEMO_VALIDATION
    assert result["allowed_to_enter_supervised_demo_validation"] is False
    assert any("not review-ready" in item for item in result["blockers"])


def test_safety_boundary_block_path() -> None:
    result = runner.evaluate_supervised_demo_operational_validation(
        ready_input(no_live_endpoint=False, no_money_movement=False)
    )

    assert result["operational_validation_status"] == runner.BLOCKED_BY_SAFETY_BOUNDARY
    assert result["allowed_to_enter_supervised_demo_validation"] is False
    assert result["safety_boundary"]["hard_boundary_status"] == "FAILED"
    assert result["safety_boundary"]["false_safety_fields"] == [
        "no_live_endpoint",
        "no_money_movement",
    ]


def test_incomplete_evidence_requires_more_evidence() -> None:
    result = runner.evaluate_supervised_demo_operational_validation(
        ready_input(evidence_collection_ready=False, operational_health_ready=False)
    )

    assert result["operational_validation_status"] == runner.REQUIRE_MORE_EVIDENCE
    assert result["safety_boundary"]["hard_boundary_status"] == "CONFIRMED"
    assert any(
        "evidence_collection_ready must be true" in item
        for item in result["required_evidence"]
    )
    assert any(
        "operational_health_ready must be true" in item
        for item in result["required_evidence"]
    )


def test_owner_approval_missing_requires_more_evidence() -> None:
    result = runner.evaluate_supervised_demo_operational_validation(
        ready_input(owner_approval_status="PENDING_OWNER_REVIEW")
    )

    assert result["operational_validation_status"] == runner.REQUIRE_MORE_EVIDENCE
    assert result["allowed_to_enter_supervised_demo_validation"] is False
    assert any("owner_approval_status" in item for item in result["required_evidence"])


def test_report_write_path(monkeypatch, tmp_path: Path) -> None:
    report_path = tmp_path / "AIOS_FOREX_SUPERVISED_DEMO_OPERATIONAL_VALIDATION_RUNNER_V1.md"
    monkeypatch.setattr(runner, "REPORT_PATH", report_path)

    result = runner.run_supervised_demo_operational_validation(write_report=True)

    assert result["operational_validation_status"] == runner.REQUIRE_MORE_EVIDENCE
    assert report_path.exists()
    report = report_path.read_text(encoding="utf-8")
    assert "# AIOS Forex Supervised Demo Operational Validation Runner V1" in report
    assert "PKT-FOREX-002 Demo Trade Evidence Collector" in report


def test_deterministic_output_keys() -> None:
    result = runner.evaluate_supervised_demo_operational_validation(ready_input())

    assert tuple(result.keys()) == runner.RESULT_KEYS


def test_no_broker_network_or_env_behavior_by_construction() -> None:
    module_source = Path(runner.__file__).read_text(encoding="utf-8").lower()
    cli_source = Path(cli.__file__).read_text(encoding="utf-8").lower()
    combined = module_source + "\n" + cli_source

    forbidden_snippets = (
        "os.environ",
        "dotenv",
        "requests",
        "urllib",
        "http.client",
        "socket",
        "import broker",
        "from broker",
        "import oanda",
        "from oanda",
    )

    assert not [snippet for snippet in forbidden_snippets if snippet in combined]


def test_cli_prints_json_for_default_safe_sample() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["packet_id"] == runner.PACKET_ID
    assert payload["operational_validation_status"] == runner.REQUIRE_MORE_EVIDENCE
    assert payload["allowed_to_enter_supervised_demo_validation"] is False


def test_cli_supports_input_json(tmp_path: Path) -> None:
    input_file = tmp_path / "validation_input.json"
    input_file.write_text(json.dumps(ready_input()), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--input-json", str(input_file)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert (
        payload["operational_validation_status"]
        == runner.READY_FOR_SUPERVISED_DEMO_VALIDATION
    )


def test_cli_write_report_uses_local_module_function(monkeypatch, tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    monkeypatch.setattr(runner, "REPORT_PATH", report_path)
    stdout = io.StringIO()

    exit_code = cli.main(["--write-report"], stdout=stdout)

    assert exit_code == 0
    assert report_path.exists()
    assert json.loads(stdout.getvalue())["operational_validation_status"] == (
        runner.REQUIRE_MORE_EVIDENCE
    )
