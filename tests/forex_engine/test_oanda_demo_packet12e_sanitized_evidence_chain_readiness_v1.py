from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import socket
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_packet12e_sanitized_evidence_chain_readiness_v1 import (  # noqa: E402
    INTERNAL_LEDGER_ONLY,
    NEXT_ACTION_INCOMPLETE,
    NEXT_ACTION_READY,
    PACKET12E_BLOCKED_ACCEPTANCE_NOT_CONFIRMED,
    PACKET12E_BLOCKED_UNSAFE_EVIDENCE,
    PACKET12E_OWNER_RUN_CHAIN_INCOMPLETE,
    PACKET12E_READY_TO_ADVANCE,
    run_packet12e_sanitized_evidence_chain_readiness,
)
from scripts.forex_delivery.run_oanda_demo_packet12e_sanitized_evidence_chain_readiness_v1 import (  # noqa: E402
    main as script_main,
)


def _safe_owner_read_output() -> dict:
    return {
        "evidence_type": "sanitized_owner_run_broker_read_output",
        "broker_read_performed": True,
        "broker_network_call_performed": True,
        "live_endpoint_used": False,
        "order_placement_performed": False,
        "order_mutation_performed": False,
        "order_close_performed": False,
        "position_mutation_performed": False,
        "trade_mutation_performed": False,
        "raw_broker_payload_persisted": False,
        "secrets_written": False,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "result": {
            "trade_id": "320",
            "instrument": "EUR_USD",
            "side": "long",
            "units": "1",
            "entry_price": "1.13596",
            "realized_pl": "0.0000",
            "unrealized_pl": "-0.0004",
            "open_trade_count": "1",
            "open_position_count": "1",
        },
    }


def _safe_packet09_evidence() -> dict:
    return {
        "evidence_type": "sanitized_packet09_owner_run_telemetry",
        "broker_read_performed": True,
        "broker_network_call_performed": True,
        "raw_broker_payload_persisted": False,
        "secrets_written": False,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "result": {
            "trade_id": "320",
            "instrument": "EUR_USD",
            "side": "long",
            "units": "1",
            "entry_price": "1.13596",
            "realized_pl": "0.0000",
            "unrealized_pl": "-0.0004",
            "open_trade_count": "1",
            "open_position_count": "1",
            "monitor_bucket": "OPEN_UNREALIZED_NEGATIVE",
            "result_bucket": "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE",
            "repeat_proof_lane_status": "NOT_STARTED_NO_PROFIT_EVIDENCE",
            "repeat_proof_eligible": False,
            "profit_evidence": False,
        },
    }


def _accepted_packet11_report() -> str:
    return "\n".join(
        [
            "# Packet 11 Acceptance Report",
            "",
            "- acceptance_status: SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED",
            "- sanitized_evidence_accepted: yes",
            "- raw broker payload persisted: false",
            "- no secrets written",
            "",
        ]
    )


def _not_confirmed_packet11_report() -> str:
    return "\n".join(
        [
            "# Packet 11 Acceptance Report",
            "",
            "- acceptance_status: SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED",
            "- sanitized_evidence_accepted: no",
            "- raw broker payload persisted: false",
            "- no secrets written",
            "",
        ]
    )


def _write_chain(
    tmp_path: Path,
    *,
    owner_payload: dict | None = None,
    packet09_payload: dict | None = None,
    packet11_report: str | None = None,
) -> tuple[Path, Path, Path]:
    owner_path = tmp_path / "owner.json"
    packet09_path = tmp_path / "packet09.json"
    packet11_path = tmp_path / "packet11.md"
    if owner_payload is not None:
        owner_path.write_text(json.dumps(owner_payload), encoding="utf-8")
    if packet09_payload is not None:
        packet09_path.write_text(json.dumps(packet09_payload), encoding="utf-8")
    if packet11_report is not None:
        packet11_path.write_text(packet11_report, encoding="utf-8")
    return owner_path, packet09_path, packet11_path


def _run_with_paths(owner_path: Path, packet09_path: Path, packet11_path: Path) -> dict:
    return run_packet12e_sanitized_evidence_chain_readiness(
        owner_read_output_path=owner_path,
        packet09_evidence_path=packet09_path,
        packet11_acceptance_report_path=packet11_path,
    )


def _run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_all_files_missing_returns_owner_run_chain_incomplete(tmp_path: Path) -> None:
    owner_path, packet09_path, packet11_path = _write_chain(tmp_path)

    result = _run_with_paths(owner_path, packet09_path, packet11_path)

    assert result["packet12e_status"] == PACKET12E_OWNER_RUN_CHAIN_INCOMPLETE
    assert result["missing_required_files"] == [
        owner_path.as_posix(),
        packet09_path.as_posix(),
        packet11_path.as_posix(),
    ]
    assert result["next_action"] == NEXT_ACTION_INCOMPLETE
    assert result["acceptance_confirmed"] is False


def test_sanitized_files_present_and_packet11_confirmed_is_ready(
    tmp_path: Path,
) -> None:
    owner_path, packet09_path, packet11_path = _write_chain(
        tmp_path,
        owner_payload=_safe_owner_read_output(),
        packet09_payload=_safe_packet09_evidence(),
        packet11_report=_accepted_packet11_report(),
    )

    result = _run_with_paths(owner_path, packet09_path, packet11_path)

    assert result["packet12e_status"] == PACKET12E_READY_TO_ADVANCE
    assert result["missing_required_files"] == []
    assert result["unsafe_findings"] == []
    assert result["acceptance_confirmed"] is True
    assert result["next_action"] == NEXT_ACTION_READY


def test_unsafe_key_blocks_with_unsafe_evidence_status(tmp_path: Path) -> None:
    packet09 = _safe_packet09_evidence()
    packet09["account_id"] = "redacted"
    owner_path, packet09_path, packet11_path = _write_chain(
        tmp_path,
        owner_payload=_safe_owner_read_output(),
        packet09_payload=packet09,
        packet11_report=_accepted_packet11_report(),
    )

    result = _run_with_paths(owner_path, packet09_path, packet11_path)

    assert result["packet12e_status"] == PACKET12E_BLOCKED_UNSAFE_EVIDENCE
    assert any("account_id" in finding for finding in result["unsafe_findings"])


def test_unsafe_token_like_value_blocks_with_unsafe_evidence_status(
    tmp_path: Path,
) -> None:
    owner_payload = _safe_owner_read_output()
    owner_payload["diagnostic_note"] = "Bearer abcdefghijklmnopqrstuvwxyz1234567890"
    owner_path, packet09_path, packet11_path = _write_chain(
        tmp_path,
        owner_payload=owner_payload,
        packet09_payload=_safe_packet09_evidence(),
        packet11_report=_accepted_packet11_report(),
    )

    result = _run_with_paths(owner_path, packet09_path, packet11_path)

    assert result["packet12e_status"] == PACKET12E_BLOCKED_UNSAFE_EVIDENCE
    assert any("bearer-token-like value" in finding for finding in result["unsafe_findings"])


def test_missing_packet11_acceptance_blocks_when_files_are_present(
    tmp_path: Path,
) -> None:
    owner_path, packet09_path, packet11_path = _write_chain(
        tmp_path,
        owner_payload=_safe_owner_read_output(),
        packet09_payload=_safe_packet09_evidence(),
        packet11_report=_not_confirmed_packet11_report(),
    )

    result = _run_with_paths(owner_path, packet09_path, packet11_path)

    assert result["packet12e_status"] == PACKET12E_BLOCKED_ACCEPTANCE_NOT_CONFIRMED
    assert result["missing_required_files"] == []
    assert result["unsafe_findings"] == []
    assert result["acceptance_confirmed"] is False


def test_cli_json_works_without_writing_report(tmp_path: Path) -> None:
    owner_path, packet09_path, packet11_path = _write_chain(
        tmp_path,
        owner_payload=_safe_owner_read_output(),
        packet09_payload=_safe_packet09_evidence(),
        packet11_report=_accepted_packet11_report(),
    )
    report_path = tmp_path / "packet12e_report.md"

    code, payload = _run_script(
        [
            "--owner-read-output-path",
            str(owner_path),
            "--packet09-evidence-path",
            str(packet09_path),
            "--packet11-acceptance-report-path",
            str(packet11_path),
            "--report-path",
            str(report_path),
            "--json",
        ]
    )

    assert code == 0
    assert payload["packet12e_status"] == PACKET12E_READY_TO_ADVANCE
    assert payload["report_path"] is None
    assert not report_path.exists()


def test_cli_write_report_writes_report(tmp_path: Path) -> None:
    owner_path, packet09_path, packet11_path = _write_chain(
        tmp_path,
        owner_payload=_safe_owner_read_output(),
        packet09_payload=_safe_packet09_evidence(),
        packet11_report=_accepted_packet11_report(),
    )
    report_path = tmp_path / "packet12e_report.md"

    code, payload = _run_script(
        [
            "--owner-read-output-path",
            str(owner_path),
            "--packet09-evidence-path",
            str(packet09_path),
            "--packet11-acceptance-report-path",
            str(packet11_path),
            "--report-path",
            str(report_path),
            "--write-report",
            "--json",
        ]
    )

    assert code == 0
    assert payload["packet12e_status"] == PACKET12E_READY_TO_ADVANCE
    assert payload["report_path"] == str(report_path)
    assert "packet12e_status: PACKET12E_READY_TO_ADVANCE" in report_path.read_text(
        encoding="utf-8"
    )


def test_no_broker_network_or_helper_call_is_required_or_performed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def fail_network(*args, **kwargs):
        raise AssertionError("network call must not be performed")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    owner_path, packet09_path, packet11_path = _write_chain(
        tmp_path,
        owner_payload=_safe_owner_read_output(),
        packet09_payload=_safe_packet09_evidence(),
        packet11_report=_accepted_packet11_report(),
    )

    result = _run_with_paths(owner_path, packet09_path, packet11_path)

    assert result["broker_network_call_performed"] is False
    assert result["broker_helper_call_required"] is False
    assert result["broker_helper_call_performed"] is False
    assert result["network_call_performed"] is False
    assert result["no_new_order_placed"] is True
    assert result["no_live_trade_placed"] is True
    assert result["no_broker_state_modified"] is True
    assert result["no_secrets_written"] is True
    assert result["raw_broker_payload_persisted"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == INTERNAL_LEDGER_ONLY
