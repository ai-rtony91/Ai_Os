from __future__ import annotations

import importlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from automation.forex_engine.supervised_demo_trade_epic_v1 import (
    SUPERVISED_DEMO_TRADE_BLOCKED_ACCOUNT,
    SUPERVISED_DEMO_TRADE_REVIEW_READY,
    build_sample_supervised_demo_blocked_input,
    build_sample_supervised_demo_ready_input,
    run_supervised_demo_trade_epic,
    supervised_demo_epic_to_jsonable_dict,
    supervised_demo_epic_to_markdown,
)


NEW_MODULE_PATHS = (
    Path("automation/forex_engine/broker_read_only_snapshot_contract_v1.py"),
    Path("automation/forex_engine/demo_account_readiness_gate_v1.py"),
    Path("automation/forex_engine/demo_trade_risk_gate_v1.py"),
    Path("automation/forex_engine/demo_position_sizer_v1.py"),
    Path("automation/forex_engine/demo_order_plan_builder_v1.py"),
    Path("automation/forex_engine/demo_operator_execution_ticket_v1.py"),
    Path("automation/forex_engine/post_trade_evidence_capture_v1.py"),
    Path("automation/forex_engine/demo_trade_feedback_router_v1.py"),
    Path("automation/forex_engine/supervised_demo_trade_epic_v1.py"),
)


def _source_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in NEW_MODULE_PATHS)


def test_sample_ready_produces_review_ready_top_level_output() -> None:
    result = run_supervised_demo_trade_epic(build_sample_supervised_demo_ready_input())
    assert result.classification == SUPERVISED_DEMO_TRADE_REVIEW_READY


def test_sample_blocked_produces_blocked_output() -> None:
    result = run_supervised_demo_trade_epic(build_sample_supervised_demo_blocked_input())
    assert result.classification == SUPERVISED_DEMO_TRADE_BLOCKED_ACCOUNT


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("selected_strategy", "Supertrend"),
        ("supertrend_status", "SUPER_TREND_PROOF_REVIEW_READY"),
        ("instrument", "EUR_USD"),
        ("direction", "LONG"),
        ("proposed_units", 20000),
        ("stop_loss", "1.0950"),
        ("take_profit", "1.1100"),
        ("max_loss", "100.00"),
        ("expected_reward", "200.00"),
        ("reward_to_risk", "2.00"),
        ("next_safe_action", "Anthony may review"),
    ],
)
def test_top_level_ready_sample_has_required_trade_review_fields(field: str, expected: object) -> None:
    data = supervised_demo_epic_to_jsonable_dict(run_supervised_demo_trade_epic())
    if field == "next_safe_action":
        assert str(expected) in data[field]
    else:
        assert data[field] == expected


@pytest.mark.parametrize(
    "permission",
    [
        "demo_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
    ],
)
def test_top_level_permissions_remain_false(permission: str) -> None:
    result = run_supervised_demo_trade_epic()
    assert getattr(result, permission) is False


def test_operator_answer_is_plain_english() -> None:
    result = run_supervised_demo_trade_epic()
    assert "execution remains locked" in result.operator_answer
    assert "_" not in result.operator_answer


@pytest.mark.parametrize(
    "key",
    [
        "selected_strategy",
        "supertrend_status",
        "instrument",
        "direction",
        "proposed_units",
        "operator_answer",
    ],
)
def test_json_output_has_required_keys(key: str) -> None:
    data = supervised_demo_epic_to_jsonable_dict(run_supervised_demo_trade_epic())
    assert key in data
    json.dumps(data)


def test_markdown_output_has_title() -> None:
    assert supervised_demo_epic_to_markdown().startswith("# Supervised Demo Trade Epic V1")


def test_repeated_output_is_deterministic() -> None:
    first = supervised_demo_epic_to_jsonable_dict(run_supervised_demo_trade_epic())
    second = supervised_demo_epic_to_jsonable_dict(run_supervised_demo_trade_epic())
    assert first == second


@pytest.mark.parametrize(
    "forbidden_import",
    [
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "from requests",
        "from httpx",
        "from socket",
        "from dotenv",
        "from keyring",
    ],
)
def test_no_forbidden_imports_across_new_modules(forbidden_import: str) -> None:
    assert forbidden_import not in _source_text().lower()


@pytest.mark.parametrize(
    "forbidden_call",
    [
        "requests.",
        "httpx.",
        "socket.",
        "urlopen(",
        "create_connection(",
        "connect(",
    ],
)
def test_no_network_calls_in_module_logic(forbidden_call: str) -> None:
    assert forbidden_call not in _source_text().lower()


def test_no_subprocess_in_module_logic() -> None:
    assert "subprocess" not in _source_text().lower()


def test_no_dotenv_usage() -> None:
    text = _source_text().lower()
    assert "load_dotenv" not in text
    assert ".env" not in text


def test_no_credential_import_usage() -> None:
    text = "\n".join(
        line.lower()
        for path in NEW_MODULE_PATHS
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )
    assert "credential" not in text
    assert "keyring" not in text


def test_no_broker_execution_import() -> None:
    text = _source_text().lower()
    assert "broker_execution" not in text
    assert "oanda" not in text


def test_no_order_placement_function() -> None:
    text = _source_text().lower()
    assert "def place_order" not in text
    assert "def submit_order" not in text
    assert "create_order(" not in text


@pytest.mark.parametrize(
    ("module_name", "args"),
    [
        ("scripts.forex_delivery.run_supervised_demo_trade_epic_v1", ["--sample-ready", "--json"]),
        ("scripts.forex_delivery.run_demo_order_plan_builder_v1", ["--sample-ready", "--json"]),
        ("scripts.forex_delivery.run_post_trade_evidence_capture_v1", ["--sample-profit", "--json"]),
    ],
)
def test_runners_emit_valid_json(module_name: str, args: list[str]) -> None:
    module = importlib.import_module(module_name)
    output = io.StringIO()
    with redirect_stdout(output):
        assert module.main(args) == 0
    payload = json.loads(output.getvalue())
    assert isinstance(payload, dict)


@pytest.mark.parametrize(
    ("module_name", "args", "title"),
    [
        (
            "scripts.forex_delivery.run_supervised_demo_trade_epic_v1",
            ["--sample-ready", "--markdown"],
            "# Supervised Demo Trade Epic V1",
        ),
        (
            "scripts.forex_delivery.run_demo_order_plan_builder_v1",
            ["--sample-ready", "--markdown"],
            "# Demo Order Plan V1",
        ),
        (
            "scripts.forex_delivery.run_post_trade_evidence_capture_v1",
            ["--sample-profit", "--markdown"],
            "# Post-Trade Evidence Capture V1",
        ),
    ],
)
def test_runners_emit_markdown(module_name: str, args: list[str], title: str) -> None:
    module = importlib.import_module(module_name)
    output = io.StringIO()
    with redirect_stdout(output):
        assert module.main(args) == 0
    assert title in output.getvalue()


def test_manual_finalization_report_includes_git_add_commands() -> None:
    report = Path("Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_MANUAL_FINALIZATION_V1.md")
    text = report.read_text(encoding="utf-8")
    assert "git add automation/forex_engine/supervised_demo_trade_epic_v1.py" in text
    assert "git add tests/forex_engine/test_supervised_demo_trade_epic_v1.py" in text


def test_manual_finalization_report_says_no_git_add_dot() -> None:
    report = Path("Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_MANUAL_FINALIZATION_V1.md")
    text = report.read_text(encoding="utf-8")
    assert "No broad add-dot staging is allowed." in text
    assert "git add ." not in text
