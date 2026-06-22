from __future__ import annotations

import json
from io import StringIO
from typing import Any

import scripts.run_forex_journey_status as cli


def _payload_fixture(final_verdict: str, safe: bool = True) -> dict[str, Any]:
    return {
        "selected_candidate_id": "c1-eur-buy",
        "selected_strategy": "ema_rsi",
        "selected_direction": "LONG",
        "candidate_demo_review_verdict": "PAPER_CONTINUE",
        "review_chain_status": "REVIEW_CHAIN_INCOMPLETE",
        "final_verdict": final_verdict,
        "live_trading_authorized": False,
        "candidate_demo_review_blockers": ["proof_not_ready"],
        "review_chain_blockers": ["cert_missing"],
        "final_next_safe_action": "collect_more",
        "safety": {
            "paper_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "account_id_present": False,
            "network_used": False,
            "order_execution": False,
            "demo_trading": False,
            "live_trading": False,
        } | ({} if safe else {"broker_connected": True}),
    }


def test_format_human_status_includes_required_fields() -> None:
    payload = _payload_fixture("JOURNEY_INCOMPLETE")
    output = cli.format_human_status(payload)
    assert "AIOS Forex Journey Status" in output
    assert "selected_candidate_id: c1-eur-buy" in output
    assert "candidate_demo_review_verdict: PAPER_CONTINUE" in output
    assert "review_chain_status: REVIEW_CHAIN_INCOMPLETE" in output
    assert "final_verdict: JOURNEY_INCOMPLETE" in output
    assert "final_next_safe_action: collect_more" in output
    assert "candidate_demo_review_blockers: proof_not_ready" in output
    assert "review_chain_blockers: cert_missing" in output
    assert "safety:" in output


def test_exit_code_mapping_review_ready() -> None:
    assert cli.exit_code_for_final_verdict(cli.JOURNEY_REVIEW_READY) == 0


def test_exit_code_mapping_incomplete() -> None:
    assert cli.exit_code_for_final_verdict(cli.JOURNEY_INCOMPLETE) == 0


def test_exit_code_mapping_rejected() -> None:
    assert cli.exit_code_for_final_verdict(cli.JOURNEY_REJECTED) == 1


def test_exit_code_mapping_blocked() -> None:
    assert cli.exit_code_for_final_verdict(cli.JOURNEY_BLOCKED) == 2


def test_cli_default_calls_journey_with_no_report(monkeypatch: Any) -> None:
    captured: dict[str, bool] = {"write_reports": None}

    def _fake_journey(*, write_reports: bool = True) -> dict[str, Any]:
        captured["write_reports"] = write_reports
        return _payload_fixture(cli.JOURNEY_INCOMPLETE)

    monkeypatch.setattr(cli, "run_review_chain_end_to_end_candidate_journey", _fake_journey)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main([])
    assert code == 0
    assert captured["write_reports"] is False


def test_cli_write_report_passes_true(monkeypatch: Any) -> None:
    captured: dict[str, bool] = {"write_reports": None}

    def _fake_journey(*, write_reports: bool = True) -> dict[str, Any]:
        captured["write_reports"] = write_reports
        return _payload_fixture(cli.JOURNEY_INCOMPLETE)

    monkeypatch.setattr(cli, "run_review_chain_end_to_end_candidate_journey", _fake_journey)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main(["--write-report"])
    assert code == 0
    assert captured["write_reports"] is True


def test_cli_json_prints_valid_json(monkeypatch: Any) -> None:
    payload = _payload_fixture(cli.JOURNEY_REVIEW_READY)

    def _fake_journey(*, write_reports: bool = True) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_review_chain_end_to_end_candidate_journey", _fake_journey)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main(["--json"])
    assert code == 0
    parsed = json.loads(stdout.getvalue())
    assert parsed["selected_candidate_id"] == "c1-eur-buy"
    assert parsed["selected_strategy"] == "ema_rsi"
    assert parsed["selected_direction"] == "LONG"
    assert parsed["candidate_demo_review_verdict"] == "PAPER_CONTINUE"
    assert parsed["review_chain_status"] == "REVIEW_CHAIN_INCOMPLETE"
    assert parsed["final_verdict"] == cli.JOURNEY_REVIEW_READY
    assert parsed["live_trading_authorized"] is False
    assert parsed["candidate_demo_review_blockers"] == ["proof_not_ready"]
    assert parsed["review_chain_blockers"] == ["cert_missing"]
    assert parsed["final_next_safe_action"] == "collect_more"
    assert "safety" in parsed


def test_cli_json_contains_required_fields(monkeypatch: Any) -> None:
    payload = _payload_fixture(cli.JOURNEY_INCOMPLETE)

    def _fake_journey(*, write_reports: bool = True) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_review_chain_end_to_end_candidate_journey", _fake_journey)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main(["--json"])
    assert code == 0
    parsed = json.loads(stdout.getvalue())
    required = {
        "selected_candidate_id",
        "selected_strategy",
        "selected_direction",
        "candidate_demo_review_verdict",
        "review_chain_status",
        "final_verdict",
        "live_trading_authorized",
        "candidate_demo_review_blockers",
        "review_chain_blockers",
        "final_next_safe_action",
        "safety",
    }
    assert required.issubset(parsed.keys())


def test_cli_does_not_authorize_live_trading(monkeypatch: Any) -> None:
    payload = _payload_fixture(cli.JOURNEY_INCOMPLETE)

    def _fake_journey(*, write_reports: bool = True) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_review_chain_end_to_end_candidate_journey", _fake_journey)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    monkeypatch.setattr(cli.sys, "argv", ["run_forex_journey_status.py"])
    code = cli.main([])
    parsed = json.loads(json.dumps(cli._build_required_json_keys(_payload_fixture(cli.JOURNEY_INCOMPLETE))))
    assert parsed["live_trading_authorized"] is False
    assert code in {0, 1, 2}


def test_cli_handles_missing_blocker_lists(monkeypatch: Any) -> None:
    payload = _payload_fixture(cli.JOURNEY_INCOMPLETE)
    payload["candidate_demo_review_blockers"] = None
    payload["review_chain_blockers"] = None

    def _fake_journey(*, write_reports: bool = True) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_review_chain_end_to_end_candidate_journey", _fake_journey)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main([])
    assert code == 0
    out = stdout.getvalue()
    assert "candidate_demo_review_blockers: " in out
    assert "review_chain_blockers: " in out


def test_default_safety_flags_safe(monkeypatch: Any) -> None:
    payload = _payload_fixture(cli.JOURNEY_INCOMPLETE)

    def _fake_journey(*, write_reports: bool = True) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_review_chain_end_to_end_candidate_journey", _fake_journey)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main([])
    assert code == 0
    output = stdout.getvalue()
    assert "broker_connected: False" in output
    assert "network_used: False" in output
    assert "demo_trading: False" in output
    assert "live_trading: False" in output

