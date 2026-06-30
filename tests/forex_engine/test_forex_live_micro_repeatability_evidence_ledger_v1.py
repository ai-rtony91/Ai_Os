from __future__ import annotations

import json
from pathlib import Path

from scripts.forex_delivery import (
    run_forex_live_micro_repeatability_evidence_ledger_v1 as ledger,
)


def _write_state(path: Path, *, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _state_snapshot(
    *,
    pnl: float | int = -0.0002,
    classification: str = "negative",
    open_trade_found: bool = True,
    open_position_found: bool = False,
    sltp_complete: bool = True,
    risk_controls_observed: bool = True,
    input_overrides: dict | None = None,
) -> dict:
    payload = {
        "module": "run_forex_live_micro_evidence_review_v1",
        "packet_id": "PKT-FOREX-LIVE-MICRO-EVIDENCE-REVIEW-V1",
        "input": {
            "evidence_mode": "readonly",
            "order_endpoint_called": False,
            "post_request_called": False,
            "trade_close_called": False,
            "position_close_called": False,
            "live_order_execution": False,
            "demo_order_execution": False,
            "money_movement": False,
            "scheduler_started": False,
            "daemon_started": False,
            "webhook_started": False,
            "broker_api_called": False,
            "bitwarden_called": False,
        },
        "result": {"repeatability_status": "READY"},
        "runtime_summary": {
            "open_trade_found": open_trade_found,
            "open_position_found": open_position_found,
            "unrealized_pl_value": pnl,
            "pnl_classification": classification,
            "risk_controls_observed": risk_controls_observed,
            "sltp_evidence_complete": sltp_complete,
            "trade_fingerprints": ["sha256:trade-fp"],
            "position_fingerprints": [],
            "sl_fingerprint": "sha256:sl-fp",
            "tp_fingerprint": "sha256:tp-fp",
            "trailing_sl_fingerprint": None,
        },
    }
    if input_overrides:
        payload["input"].update(input_overrides)
    return payload


def _run(
    *,
    tmp_path: Path,
    state_paths: list[Path],
    min_snapshots: int = 1,
    **kwargs: object,
) -> dict:
    state_output = tmp_path / "ledger_state.json"
    report_output = tmp_path / "ledger_report.md"
    if state_output.exists():
        state_output.unlink()
    if report_output.exists():
        report_output.unlink()
    return ledger.run_forex_live_micro_repeatability_evidence_ledger_v1(
        evidence_state_paths=state_paths,
        min_snapshots=min_snapshots,
        state_output=state_output,
        report_output=report_output,
        write_report=False,
        **kwargs,
    )


def test_default_local_only_mode_does_not_call_broker_or_bitwarden(tmp_path):
    local_state = tmp_path / "state.json"
    _write_state(local_state, payload=_state_snapshot())
    payload = _run(
        tmp_path=tmp_path,
        state_paths=[local_state],
    )
    assert payload["input"]["local_only"] is True
    assert payload["input"]["bitwarden_called"] is False
    assert payload["input"]["broker_api_called"] is False


def test_missing_evidence_file_returns_insufficient_snapshots(tmp_path):
    missing = tmp_path / "missing.json"
    payload = _run(tmp_path=tmp_path, state_paths=[missing])
    assert payload["result"]["repeatability_status"] == ledger.LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS
    assert payload["input"]["evidence_files_missing"] == [str(missing)]
    assert payload["runtime_summary"]["snapshot_count"] == 0


def test_negative_snapshot_returns_open_trade_still_negative(tmp_path):
    state = tmp_path / "state.json"
    _write_state(state, payload=_state_snapshot(pnl=-0.1, classification="negative"))
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    assert payload["runtime_summary"]["latest_pnl_classification"] == "negative"
    assert payload["runtime_summary"]["latest_pnl_value"] == -0.1
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE
    )


def test_flat_snapshot_returns_open_trade_flat(tmp_path):
    state = tmp_path / "state.json"
    _write_state(state, payload=_state_snapshot(pnl=0.0, classification="flat"))
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    assert payload["runtime_summary"]["latest_pnl_classification"] == "flat"
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT
    )


def test_positive_snapshot_returns_open_trade_positive(tmp_path):
    state = tmp_path / "state.json"
    _write_state(state, payload=_state_snapshot(pnl=0.3, classification="positive"))
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    assert payload["runtime_summary"]["latest_pnl_classification"] == "positive"
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE
    )


def test_sltp_missing_returns_sltp_evidence_missing(tmp_path):
    state = tmp_path / "state.json"
    _write_state(state, payload=_state_snapshot(sltp_complete=False, classification="positive"))
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING
    )
    assert payload["runtime_summary"]["sltp_latest_complete"] is False


def test_forbidden_action_true_returns_forbidden_flag(tmp_path):
    state = tmp_path / "state.json"
    _write_state(
        state,
        payload=_state_snapshot(input_overrides={"trade_close_called": True}),
    )
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED
    )
    assert payload["runtime_summary"]["forbidden_action_flags_clear"] is False


def test_money_movement_true_returns_money_movement_flag(tmp_path):
    state = tmp_path / "state.json"
    _write_state(state, payload=_state_snapshot(input_overrides={"money_movement": True}))
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED
    )
    assert payload["runtime_summary"]["money_movement_clear"] is False
    assert payload["result"]["current_stage"] == ledger.CURRENT_STAGE


def test_min_snapshots_greater_than_available_is_insufficient(tmp_path):
    state = tmp_path / "state.json"
    _write_state(state, payload=_state_snapshot())
    payload = _run(tmp_path=tmp_path, state_paths=[state], min_snapshots=3)
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS
    )
    assert payload["runtime_summary"]["snapshot_count"] == 1


def test_multiple_snapshots_aggregate_pnl_and_counts(tmp_path):
    first = tmp_path / "state1.json"
    second = tmp_path / "state2.json"
    _write_state(first, payload=_state_snapshot(pnl=-0.5, classification="negative"))
    _write_state(second, payload=_state_snapshot(pnl=0.25, classification="positive"))
    payload = _run(tmp_path=tmp_path, state_paths=[first, second], min_snapshots=2)
    assert payload["runtime_summary"]["snapshot_count"] == 2
    assert payload["runtime_summary"]["open_trade_seen_count"] == 2
    assert payload["runtime_summary"]["profit_positive_count"] == 1
    assert payload["runtime_summary"]["profit_negative_count"] == 1
    assert payload["runtime_summary"]["pnl_values"] == [-0.5, 0.25]
    assert payload["runtime_summary"]["latest_pnl_value"] == 0.25
    assert payload["result"]["repeatability_status"] == (
        ledger.LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE
    )


def test_output_contains_fingerprints_no_raw_secrets(tmp_path):
    token = "EXAMPLE_TOKEN_PLACEHOLDER"
    account = "ACC-000-111111-001"
    session = "SESSION-XYZ-999"
    state = tmp_path / "state.json"
    payload = _state_snapshot()
    payload["runtime_summary"]["trade_fingerprints"] = [f"sha256:{token}"]
    payload["input"]["token"] = token
    payload["input"]["broker_account_id"] = account
    payload["input"]["bw_session"] = session
    _write_state(state, payload=payload)
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    state_text = (tmp_path / "ledger_state.json").read_text(encoding="utf-8")
    assert token not in state_text
    assert account not in state_text
    assert session not in state_text
    assert "Bearer " + token not in state_text
    assert "Authorization" not in state_text
    assert all(fp.startswith("sha256:") for fp in payload["runtime_summary"]["evidence_fingerprints"])


def test_no_live_or_money_or_scheduler_flags(tmp_path):
    state = tmp_path / "state.json"
    _write_state(state, payload=_state_snapshot())
    payload = _run(tmp_path=tmp_path, state_paths=[state])
    assert payload["input"]["live_order_execution"] is False
    assert payload["input"]["money_movement"] is False
    assert payload["input"]["scheduler_started"] is False
    assert payload["input"]["daemon_started"] is False
    assert payload["input"]["webhook_started"] is False

