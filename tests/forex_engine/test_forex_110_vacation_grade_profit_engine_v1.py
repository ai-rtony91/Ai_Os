from __future__ import annotations

import ast
import json
from pathlib import Path

from automation.forex_engine import forex_110_vacation_grade_profit_engine_v1 as engine
from scripts.forex_delivery import run_forex_110_vacation_grade_profit_engine_v1 as runner


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT / "automation" / "forex_engine" / "forex_110_vacation_grade_profit_engine_v1.py"
)
RUNNER_PATH = (
    ROOT / "scripts" / "forex_delivery" / "run_forex_110_vacation_grade_profit_engine_v1.py"
)


def test_state_output_is_json_serializable_and_deterministic() -> None:
    first = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)
    second = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert first == second
    json.dumps(first)


def test_only_approved_readiness_values_are_used() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    for key, value in result.items():
        if key.endswith("_status") and isinstance(value, str):
            assert value in engine.READINESS_VALUES
    for lane in result["five_lane_completion_map"]:
        assert lane["current_status"] in engine.READINESS_VALUES


def test_blocked_actions_remain_blocked() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert result["blocked_actions"] == engine.BLOCKED_ACTIONS
    assert all(result["blocked_actions"].values())


def test_five_lane_map_has_exactly_five_lanes() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert [lane["lane_name"] for lane in result["five_lane_completion_map"]] == [
        "Profit Proof",
        "Return Target Validation",
        "Broker + Runtime Evidence",
        "Safety / Real-Money Gate",
        "Dashboard Truth / Owner Control",
    ]


def test_shortest_packet_chain_has_no_more_than_seven_packets() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert len(result["shortest_packet_chain"]) <= 7
    assert len(result["shortest_packet_chain"]) == 7


def test_vacation_grade_not_proven_without_complete_evidence() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert result["vacation_grade_status"] != "PROVEN"


def test_profitability_not_proven_without_evidence() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert result["profitability_status"] != "PROVEN"


def test_good_day_return_target_not_proven_without_evidence() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert result["good_day_return_target_status"] != "PROVEN"


def test_phenomenal_return_target_not_proven_without_evidence() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert result["phenomenal_day_return_target_status"] != "PROVEN"


def test_22h_6d_not_proven_without_evidence() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert result["twenty_two_hour_six_day_status"] != "PROVEN"


def test_live_real_money_not_proven_without_evidence() -> None:
    result = engine.run_forex_110_vacation_grade_profit_engine_v1(ROOT)

    assert result["live_real_money_status"] != "PROVEN"


def test_tool_does_not_call_broker_network_env_or_credentials() -> None:
    forbidden_imports = {
        "http",
        "os",
        "requests",
        "socket",
        "subprocess",
        "urllib",
    }
    forbidden_phrases = (
        "os.environ",
        "getenv",
        "load_dotenv",
        "requests.",
        "urllib.",
        "socket.",
        "subprocess.",
        "place_order(",
        "submit_order(",
        "execute_order(",
        "start_server(",
        "start_scheduler(",
        "start_daemon(",
    )

    for path in (MODULE_PATH, RUNNER_PATH):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )

        assert not (imports & forbidden_imports)
        lowered = source.lower()
        for phrase in forbidden_phrases:
            assert phrase not in lowered


def test_runner_writes_report_and_state_deterministically(tmp_path, monkeypatch) -> None:
    state_path = tmp_path / "state.json"
    report_path = tmp_path / "report.md"
    monkeypatch.setattr(runner, "STATE_PATH", state_path)
    monkeypatch.setattr(runner, "REPORT_PATH", report_path)

    assert runner.main(["--repo-root", str(ROOT), "--write-state", "--write-report"]) == 0
    first_state = state_path.read_text(encoding="utf-8")
    first_report = report_path.read_text(encoding="utf-8")
    assert runner.main(["--repo-root", str(ROOT), "--write-state", "--write-report"]) == 0

    assert state_path.read_text(encoding="utf-8") == first_state
    assert report_path.read_text(encoding="utf-8") == first_report
    json.loads(first_state)
