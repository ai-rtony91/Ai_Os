from __future__ import annotations

import json
from io import StringIO
from typing import Any

import scripts.run_forex_proof_gap_closure_plan as cli


def _payload(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    base = {
        "selected_candidate_id": "c1-eur-buy",
        "source_candidate_verdict": "PAPER_CONTINUE",
        "source_review_chain_status": "REVIEW_CHAIN_INCOMPLETE",
        "source_journey_final_verdict": "JOURNEY_INCOMPLETE",
        "highest_value_next_packet": "AIOS_FOREX-CANDIDATE-EVIDENCE-REPAIR-LOOP-V1",
        "recommended_packet_sequence": [
            {"packet_id": "AIOS_FOREX-CANDIDATE-EVIDENCE-REPAIR-LOOP-V1"},
        ],
        "closure_buckets": {
            "evidence_proof_gaps": [],
            "strategy_quality_gaps": ["walk_forward_failed"],
            "demo_contract_gaps": [],
            "review_package_gaps": [],
            "safety_gaps": [],
            "human_review_gaps": [],
        },
        "next_safe_action": "collect_more",
        "safety": {
            "paper_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "network_used": False,
            "order_execution": False,
            "demo_trading": False,
            "live_trading": False,
        },
    }
    if overrides:
        base.update(overrides)
    return base


def test_human_output_contains_title_and_next_packet(monkeypatch: Any) -> None:
    payload = _payload()

    def fake_plan(*, write_reports: bool = True, journey_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_proof_gap_closure_plan", fake_plan)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main([])
    out = stdout.getvalue()
    assert "AIOS Forex Proof Gap Closure Plan" in out
    assert "highest_value_next_packet: AIOS_FOREX-CANDIDATE-EVIDENCE-REPAIR-LOOP-V1" in out
    assert code == 0


def test_json_output(monkeypatch: Any) -> None:
    payload = _payload()

    def fake_plan(*, write_reports: bool = True, journey_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_proof_gap_closure_plan", fake_plan)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main(["--json"])
    out = stdout.getvalue()
    parsed = json.loads(out)
    assert code == 0
    assert parsed["selected_candidate_id"] == "c1-eur-buy"
    assert parsed["highest_value_next_packet"] == "AIOS_FOREX-CANDIDATE-EVIDENCE-REPAIR-LOOP-V1"
    assert "closure_buckets" in parsed


def test_write_report_flag(monkeypatch: Any) -> None:
    captured = {"write_reports": None}

    def fake_plan(*, write_reports: bool = True, journey_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        captured["write_reports"] = write_reports
        return _payload()

    monkeypatch.setattr(cli, "run_proof_gap_closure_plan", fake_plan)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    cli.main(["--write-report"])
    assert captured["write_reports"] is True


def test_default_report_flag_false(monkeypatch: Any) -> None:
    captured = {"write_reports": None}

    def fake_plan(*, write_reports: bool = True, journey_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        captured["write_reports"] = write_reports
        return _payload()

    monkeypatch.setattr(cli, "run_proof_gap_closure_plan", fake_plan)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    cli.main([])
    assert captured["write_reports"] is False


def test_exit_code_zero_when_no_safety_gap(monkeypatch: Any) -> None:
    def fake_plan(*, write_reports: bool = True, journey_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return _payload()

    monkeypatch.setattr(cli, "run_proof_gap_closure_plan", fake_plan)
    assert cli.exit_code_for_final_verdict(_payload()) == 0
    assert cli.main([]) == 0


def test_exit_code_two_when_safety_gap(monkeypatch: Any) -> None:
    payload = _payload(
        {
            "closure_buckets": {
                "evidence_proof_gaps": [],
                "strategy_quality_gaps": [],
                "demo_contract_gaps": [],
                "review_package_gaps": [],
                "safety_gaps": ["unsafe_broker_connected"],
                "human_review_gaps": [],
            },
            "highest_value_next_packet": "AIOS_FOREX-SAFETY-BLOCKER-CONTAINMENT-V1",
        }
    )

    def fake_plan(*, write_reports: bool = True, journey_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_proof_gap_closure_plan", fake_plan)
    assert cli.exit_code_for_final_verdict(payload) == 2
    assert cli.main(["--json"]) == 2


def test_output_with_empty_sequence(monkeypatch: Any) -> None:
    payload = _payload(
        {
            "highest_value_next_packet": "NO_GAP_DETECTED",
            "recommended_packet_sequence": [],
        }
    )

    def fake_plan(*, write_reports: bool = True, journey_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(cli, "run_proof_gap_closure_plan", fake_plan)
    stdout = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    code = cli.main([])
    out = stdout.getvalue()
    assert "recommended_packet_sequence:" in out
    assert "NO_GAP_DETECTED" in out
    assert code == 0


def test_repo_root_bootstrap_import() -> None:
    import runpy
    module = runpy.run_path("scripts/run_forex_proof_gap_closure_plan.py")
    assert "main" in module
