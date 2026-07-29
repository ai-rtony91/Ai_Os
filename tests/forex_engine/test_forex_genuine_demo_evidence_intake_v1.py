from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "automation/forex_engine/forex_genuine_demo_evidence_intake_v1.py"


def module():
    spec = importlib.util.spec_from_file_location("intake", PATH)
    value = importlib.util.module_from_spec(spec); assert spec.loader
    spec.loader.exec_module(value)
    return value


def evidence(state="OPEN"):
    value = {
        "schema": "AIOS_SANITIZED_DEMO_TRADE.v1", "evidence_timestamp": "2026-07-27T00:00:00Z",
        "broker_family": "OANDA", "environment": "PRACTICE", "session_mode": "BROKER_DEMO",
        "record_type": "SANITIZED_TRADE_RECEIPT", "trade_state": state, "trade_count": 1,
        "broker_origin_confirmation": True, "sanitized": True, "instrument": "EUR_USD", "side": "BUY",
        "units": 1, "entry_price": 1.1, "secret_values_recorded": False,
        "credential_values_recorded": False, "private_identifiers_recorded": False,
        "account_identifiers_recorded": False, "raw_broker_payload_recorded": False,
        "live_trading_allowed": False, "money_movement_allowed": False,
    }
    if state == "CLOSED":
        value.update(realized_pnl=0.1, drawdown=0.01, post_trade_review=True,
                     trades=[{"realized_pnl": 0.1, "entry_price": 1.1, "exit_price": 1.2}])
    return value


def classify(payload, path="Reports/forex_delivery/evidence.json"):
    return module().classify_genuine_demo_source(path, payload, as_of_date="2026-07-27")


def test_required_exclusions_receive_no_credit():
    for marker in ("INITIAL_STUB", "PAPER_SIMULATION_DAY", "paper_signal_execution_loop", "offline fixture", "command_package_only", "telemetry_blocked", "telemetry_rejected", "evidence_not_supplied"):
        value = evidence(); value["marker"] = marker
        item = classify(value)
        assert not item["accepted_for_genuine_demo"]
    value = evidence(); value.update(record_type="REAL_DEMO_DAY", session_mode="PAPER_SIMULATION")
    assert not classify(value)["accepted_for_genuine_demo"]


def test_markdown_prose_and_stale_evidence_fail_closed():
    assert not classify(evidence(), "Reports/forex_delivery/story.md")["accepted_for_genuine_demo"]
    value = evidence(); value["evidence_timestamp"] = "2026-01-01T00:00:00Z"
    item = classify(value)
    assert item["classification"] == "STALE" and not item["accepted_for_genuine_demo"]


def test_open_and_closed_evidence_are_distinguished():
    opened = classify(evidence())
    assert opened["classification"] == "GENUINE_SANITIZED_OPEN_DEMO_TRADE"
    assert opened["accepted_for_genuine_demo"] and not opened["accepted_for_metrics"]
    closed = classify(evidence("CLOSED"))
    assert closed["classification"] == "GENUINE_SANITIZED_CLOSED_DEMO_TRADE"
    assert closed["accepted_for_metrics"]


def test_incomplete_nonfinite_and_live_flags_fail_closed():
    closed = evidence("CLOSED"); closed["trades"] = [{}]
    assert not classify(closed)["accepted_for_metrics"]
    for key, value in (("entry_price", float("nan")), ("live_trading_allowed", True), ("money_movement_allowed", True)):
        payload = evidence(); payload[key] = value
        assert not classify(payload)["accepted_for_genuine_demo"]


def test_sensitive_account_and_raw_values_fail_without_echo():
    for key in ("api_key", "account_id", "raw_response", "broker_order_id", "authorization_header", "balance", "private_screenshot"):
        payload = evidence(); payload[key] = "DO-NOT-ECHO"
        item = classify(payload)
        assert not item["accepted_for_genuine_demo"]
        assert "DO-NOT-ECHO" not in json.dumps(item)


def test_every_safety_flag_must_be_explicitly_false():
    m = module()
    for key in m.FALSE_SAFETY_FLAGS:
        payload = evidence(); payload.pop(key)
        assert not classify(payload)["accepted_for_genuine_demo"]
        payload = evidence(); payload[key] = True
        assert not classify(payload)["accepted_for_genuine_demo"]


def test_inventory_reads_only_approved_json_directory(tmp_path: Path):
    root = tmp_path
    approved = root / module().SANITIZED_INTAKE_DIRECTORY
    approved.mkdir(parents=True)
    (approved / "receipt.json").write_text(json.dumps(evidence()), encoding="utf-8")
    (approved / "ignored.md").write_text(json.dumps(evidence()), encoding="utf-8")
    elsewhere = root / "Reports/forex_delivery"; elsewhere.mkdir(parents=True)
    (elsewhere / "OANDA_DEMO.json").write_text(json.dumps(evidence()), encoding="utf-8")
    inventory = module().load_genuine_demo_source_inventory(root, as_of_date="2026-07-27")
    assert len(inventory) == 1
    assert inventory[0]["source_path"].startswith(module().SANITIZED_INTAKE_DIRECTORY)


def test_non_evidence_example_receives_zero_credit():
    path = ROOT / "telemetry/forex/sanitized_oanda_practice_evidence/NON_EVIDENCE_SCHEMA_EXAMPLE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    item = classify(payload, path.relative_to(ROOT).as_posix())
    assert not item["accepted_for_genuine_demo"]
    state = module().build_genuine_demo_evidence_bundle([item], as_of_date="2026-07-27")
    assert not any(criterion["counted_for_progress"] for criterion in state["criteria_evidence"])


def test_bundle_open_receipt_passes_only_nonterminal_criteria():
    state = module().build_genuine_demo_evidence_bundle([classify(evidence())], as_of_date="2026-07-27")
    criteria = {item["criterion_id"]: item for item in state["criteria_evidence"]}
    assert criteria["DEMO_GENUINE_MARKET_EVIDENCE"]["status"] == "PASS"
    assert criteria["DEMO_RECEIPT_READY"]["status"] == "PASS"
    assert criteria["DEMO_METRICS_COMPLETE"]["status"] != "PASS"
    assert criteria["POST_TRADE_REVIEW_READY"]["status"] != "PASS"


def test_absent_evidence_returns_exact_owner_requirement():
    state = module().build_genuine_demo_evidence_bundle([], as_of_date="2026-07-27")
    assert state["status"] == "BLOCKED_GENUINE_DEMO_EVIDENCE_NOT_FOUND"
    assert state["next_verified_task"] == "CAPTURE_ONE_SANITIZED_OANDA_PRACTICE_TRADE_RECEIPT"
    assert state["owner_evidence_requirement"]["owner_evidence_status"] == "OWNER_SANITIZED_DEMO_EVIDENCE_REQUIRED"


def test_deterministic_serialization_emoji_headings_and_no_actions():
    m = module(); state = m.build_genuine_demo_evidence_bundle([], as_of_date="2026-07-27")
    assert m.stable_json(state) == m.stable_json(state)
    report = m.render_genuine_demo_evidence_report(state)
    assert report.startswith("# 🧪 AIOS FOREX — GENUINE DEMO EVIDENCE")
    assert "## 📉 EFFECT ON FIRST-TRADE COUNTDOWN" in report
    assert not any(state["permissions"].values()) and not any(state["protected_actions"].values())
    source = PATH.read_text(encoding="utf-8").lower()
    for forbidden in ("requests", "urllib", "socket", "subprocess", "os.environ"):
        assert forbidden not in source
