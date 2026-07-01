from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine import forex_brake_trip_proof_v1 as brake


def _safety_config() -> dict[str, object]:
    return json.loads(
        Path("control/forex/forex_safety_controls_config.json").read_text(encoding="utf-8")
    )


def test_brake_trip_proof_apply_writes_append_only_ledger(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    receipt = brake.run_forex_brake_trip_proof_v1(
        repo_root,
        safety_config_mapping=_safety_config(),
        apply=True,
    )

    assert receipt["mode"] == "APPLY"
    assert receipt["all_trips_passed"] is True
    assert receipt["ledger_entry_count_before"] == 0
    assert receipt["ledger_entry_count_after"] == 3
    assert receipt["appended_entry_count"] == 3
    assert receipt["trip_results"][0]["stop_pause_resume_status"] == "STOP_REQUIRED"
    assert receipt["trip_results"][1]["warning_intent_emitted"] is True
    assert receipt["trip_results"][1]["halt_action"] == "HALT_FOR_DAY"
    assert receipt["trip_results"][1]["blocked_trade_count_after_halt"] == 1
    assert receipt["trip_results"][1]["no_further_simulated_trades_occurred"] is True
    assert receipt["trip_results"][2]["halt_action"] == "HALT_ALL"
    assert receipt["trip_results"][2]["owner_reset_required"] is True
    assert receipt["trip_results"][2]["blocked_trade_count_after_halt"] == 1

    ledger_path = repo_root / "telemetry" / "forex" / "brake_trip_proof_ledger.jsonl"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert isinstance(ledger, list)
    assert len(ledger) == 3
    assert all(entry["ledger_label"] == brake.SIMULATED_TRIP_PROOF for entry in ledger)
    assert ledger[0]["stop_pause_resume_status"] == "STOP_REQUIRED"
    assert ledger[1]["warning_intent_emitted"] is True
    assert ledger[2]["halt_action"] == "HALT_ALL"


def test_brake_trip_proof_dry_run_does_not_write_ledger(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    receipt = brake.run_forex_brake_trip_proof_v1(
        repo_root,
        safety_config_mapping=_safety_config(),
        apply=False,
    )

    assert receipt["mode"] == "DRY_RUN"
    assert receipt["appended_entry_count"] == 0
    assert receipt["ledger_entry_count_after"] == 3
    assert not (repo_root / "telemetry" / "forex" / "brake_trip_proof_ledger.jsonl").exists()


def test_brake_trip_proof_has_no_forbidden_network_or_broker_imports() -> None:
    source = Path("automation/forex_engine/forex_brake_trip_proof_v1.py").read_text(
        encoding="utf-8"
    ).lower()
    forbidden = (
        "requests",
        "urllib",
        "socket",
        "dotenv",
        "oanda",
        "import broker",
        "from broker",
        "os.environ",
        "subprocess",
    )

    assert not [token for token in forbidden if token in source]
