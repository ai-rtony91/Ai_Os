from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine.forex_p1_supervised_paper_evidence_pipeline_v1 import (
    SAFETY_FLAGS,
    run_pipeline,
)


def trade(trade_id: str = "paper-001", evidence_type: str = "paper") -> dict:
    return {
        "trade_id": trade_id,
        "evidence_type": evidence_type,
        "strategy_id": "strategy-c1",
        "instrument": "EUR_USD",
        "direction": "buy",
        "entry_timestamp_utc": "2026-08-01T10:00:00Z",
        "exit_timestamp_utc": "2026-08-01T11:00:00Z",
        "entry_price": 1.1,
        "exit_price": 1.101,
        "stop_price": 1.099,
        "target_price": 1.101,
        "quantity_or_units": 100,
        "realized_pl": 10,
        "fees": 1,
        "risk_amount": 10,
        "exit_reason": "target",
        "entry_rationale": "bounded paper review",
        "evidence_source": "sanitized_local_review",
        "reviewed_by": "human_owner",
        "review_timestamp_utc": "2026-08-01T12:00:00Z",
    }


@pytest.fixture
def paths(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    return tuple(tmp_path / name for name in ("input.json", "ledger.json", "state.json", "report.md"))


def run(paths: tuple[Path, Path, Path, Path], records: object) -> dict:
    input_path, ledger, state, report = paths
    input_path.write_text(json.dumps(records), encoding="utf-8")
    return run_pipeline(input_path, ledger, state, report)


def test_empty_input_stays_no_evidence_and_writes_outputs(paths):
    result = run(paths, [])
    assert result["p1_status_after"] == "NO_EVIDENCE"
    assert result["accepted_records"] == result["rejected_records"] == 0
    assert all(path.exists() for path in paths[1:])


@pytest.mark.parametrize("evidence_type", ["paper", "supervised_demo"])
def test_accepts_qualifying_sanitized_types(paths, evidence_type):
    result = run(paths, [trade(evidence_type=evidence_type)])
    assert result["accepted_records"] == 1
    assert result["qualifying_trade_count"] == 1
    assert result["evidence_type_counts"] == {evidence_type: 1}


def test_preserves_supertrend_identity_and_paper_only_metadata(paths):
    record = {
        **trade(),
        "strategy_id": "supertrend_pullback_v1",
        "strategy_name": "supertrend_pullback_v1",
        "mode": "PAPER_ONLY",
        "paper_only": True,
        "strategy_config": {"atr_period": 3, "multiplier": 2.0},
    }
    result = run(paths, [record])
    ledger = json.loads(paths[1].read_text(encoding="utf-8"))
    accepted = ledger["records"][0]
    assert result["accepted_records"] == 1
    assert accepted["strategy_name"] == "supertrend_pullback_v1"
    assert accepted["mode"] == "PAPER_ONLY"
    assert accepted["paper_only"] is True
    assert accepted["strategy_config"] == {"atr_period": 3, "multiplier": 2.0}


@pytest.mark.parametrize("evidence_type", ["fixture", "synthetic", "live", "broker_raw"])
def test_rejects_nonqualifying_evidence_types(paths, evidence_type):
    result = run(paths, [trade(evidence_type=evidence_type)])
    assert result["accepted_records"] == 0
    assert "unsupported_evidence_type" in result["rejections"][0]["reasons"]


def test_duplicate_id_is_rejected_and_prior_evidence_is_unchanged(paths):
    first = run(paths, [trade()])
    ledger_before = paths[1].read_text(encoding="utf-8")
    second = run(paths, [trade()])
    assert first["accepted_records"] == 1
    assert second["duplicate_records"] == 1
    assert paths[1].read_text(encoding="utf-8") == ledger_before


def test_duplicate_within_one_input_is_rejected(paths):
    result = run(paths, [trade(), trade()])
    assert result["accepted_records"] == 1
    assert result["duplicate_records"] == 1


def test_missing_field_is_not_inferred(paths):
    record = trade()
    del record["strategy_id"]
    result = run(paths, [record])
    assert "missing_strategy_id" in result["rejections"][0]["reasons"]


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ({"exit_timestamp_utc": "not-a-time"}, "invalid_exit_timestamp_utc"),
        ({"exit_timestamp_utc": "2026-08-01T09:00:00Z"}, "invalid_timestamp_order"),
        ({"entry_price": float("nan")}, "non_finite_or_invalid_entry_price"),
        ({"api_key": "not-recorded"}, "secret_or_private_identifier_rejected"),
        ({"account_id": "private"}, "secret_or_private_identifier_rejected"),
        ({"order_id": "private"}, "secret_or_private_identifier_rejected"),
        ({"raw_broker_payload": {}}, "raw_broker_payload_rejected"),
        ({"entry_rationale": "password=do-not-store"}, "secret_or_private_identifier_rejected"),
        ({"strategy_name": "different"}, "strategy_identity_mismatch"),
        ({"mode": "LIVE"}, "paper_only_mode_required"),
        ({"paper_only": False}, "paper_only_true_required"),
    ],
)
def test_fail_closed_rejections(paths, mutation, reason):
    record = trade()
    record.update(mutation)
    result = run(paths, [record])
    assert reason in result["rejections"][0]["reasons"]


def test_append_order_is_deterministic(paths):
    later = trade("later")
    earlier = trade("earlier")
    earlier.update({
        "entry_timestamp_utc": "2026-07-31T10:00:00Z",
        "exit_timestamp_utc": "2026-07-31T11:00:00Z",
        "review_timestamp_utc": "2026-07-31T12:00:00Z",
    })
    run(paths, [later, earlier])
    ledger = json.loads(paths[1].read_text(encoding="utf-8"))
    assert [item["trade_id"] for item in ledger["records"]] == ["earlier", "later"]


def test_evaluator_is_triggered(monkeypatch, paths):
    import automation.forex_engine.forex_p1_supervised_paper_evidence_pipeline_v1 as module

    original = module.evaluate_strategy_evidence
    calls = []

    def tracked(*args, **kwargs):
        calls.append(args[0])
        return original(*args, **kwargs)

    monkeypatch.setattr(module, "evaluate_strategy_evidence", tracked)
    run(paths, [trade()])
    assert len(calls) == 2
    assert len(calls[-1]) == 1


def test_all_outputs_deny_execution_authority(paths):
    result = run(paths, [trade()])
    ledger = json.loads(paths[1].read_text(encoding="utf-8"))
    state = json.loads(paths[2].read_text(encoding="utf-8"))
    for key in SAFETY_FLAGS:
        assert result[key] is False
        assert ledger[key] is False
        assert state[key] is False
    report = paths[3].read_text(encoding="utf-8")
    assert "Live execution allowed: false" in report


def test_invalid_existing_authority_claim_fails_closed(paths):
    paths[1].write_text(json.dumps({"records": [], "live_execution_allowed": True}), encoding="utf-8")
    paths[0].write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="execution_authority"):
        run_pipeline(*paths)
