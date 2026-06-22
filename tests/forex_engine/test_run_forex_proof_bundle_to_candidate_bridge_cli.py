from __future__ import annotations

from io import StringIO
import json
from typing import Any

import scripts.run_forex_proof_bundle_to_candidate_bridge as cli


def _payload() -> dict[str, Any]:
    return {
        "selected_candidate_id": "c1-eur-buy",
        "source_proof_bundle_status": "PROOF_BUNDLE_COMPLETE",
        "source_candidate_verdict": "PAPER_CONTINUE",
        "candidate_bridge_verdict": "DEMO_REVIEW_READY",
        "closed_blockers": ["missing_replay_proof", "missing_reconciliation_proof"],
        "remaining_blockers": ["walk_forward_failed"],
        "safety": {
            "paper_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "account_id_present": False,
            "network_used": False,
            "order_execution": False,
            "demo_trading": False,
            "live_trading": False,
            "live_trading_authorized": False,
        },
        "next_safe_action": "continue",
        "enriched_candidate": {},
        "canonical_review_bundle": {},
        "strategy_quality_gaps": ["walk_forward_failed"],
        "demo_contract_gaps": [],
        "review_package_gaps": [],
        "human_review_gaps": [],
        "safety_gaps": [],
        "report_path": None,
    }


def test_human_output_includes_title_and_verdict(monkeypatch: Any) -> None:
    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", lambda write_reports=True, proof_bundle_payload=None: _payload())
    output = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", output)
    cli.main([])
    text = output.getvalue()
    assert "AIOS Forex Proof Bundle To Candidate Bridge" in text
    assert "candidate_bridge_verdict: DEMO_REVIEW_READY" in text


def test_json_output_parsable(monkeypatch: Any) -> None:
    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", lambda write_reports=True, proof_bundle_payload=None: _payload())
    output = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", output)
    code = cli.main(["--json"])
    parsed = json.loads(output.getvalue())
    assert code == 0
    assert parsed["selected_candidate_id"] == "c1-eur-buy"
    assert parsed["candidate_bridge_verdict"] == "DEMO_REVIEW_READY"


def test_write_report_calls_bridge_with_write_reports_true(monkeypatch: Any) -> None:
    captured: dict[str, bool | None] = {"write_reports": None}

    def fake_bridge(*, write_reports: bool = True, proof_bundle_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        captured["write_reports"] = write_reports
        return _payload()

    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", fake_bridge)
    output = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", output)
    cli.main(["--write-report"])
    assert captured["write_reports"] is True


def test_default_calls_bridge_without_report(monkeypatch: Any) -> None:
    captured: dict[str, bool | None] = {"write_reports": None}

    def fake_bridge(*, write_reports: bool = True, proof_bundle_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        captured["write_reports"] = write_reports
        return _payload()

    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", fake_bridge)
    output = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", output)
    cli.main([])
    assert captured["write_reports"] is False


def test_exit_code_zero_when_blocker_closed_and_no_safety_gap(monkeypatch: Any) -> None:
    payload = _payload()
    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", lambda write_reports=True, proof_bundle_payload=None: payload)
    code = cli.main(["--json"])
    assert code == 0


def test_exit_code_one_when_no_blocker_closed(monkeypatch: Any) -> None:
    payload = _payload()
    payload["closed_blockers"] = []
    payload["safety"]["broker_connected"] = False
    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", lambda write_reports=True, proof_bundle_payload=None: payload)
    code = cli.main(["--json"])
    assert code == 1


def test_exit_code_two_when_safety_gap_exists(monkeypatch: Any) -> None:
    payload = _payload()
    payload["safety"]["broker_connected"] = True
    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", lambda write_reports=True, proof_bundle_payload=None: payload)
    code = cli.main(["--json"])
    assert code == 2


def test_repo_root_import_bootstrap() -> None:
    import runpy
    module = runpy.run_path("scripts/run_forex_proof_bundle_to_candidate_bridge.py")
    assert "main" in module


def test_no_live_trading_authorized_true(monkeypatch: Any) -> None:
    payload = _payload()
    monkeypatch.setattr(cli, "run_proof_bundle_to_candidate_bridge", lambda write_reports=True, proof_bundle_payload=None: payload)
    output = StringIO()
    monkeypatch.setattr(cli.sys, "stdout", output)
    cli.main(["--json"])
    parsed = json.loads(output.getvalue())
    assert parsed["safety"]["live_trading_authorized"] is False
