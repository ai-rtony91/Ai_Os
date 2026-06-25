from __future__ import annotations

import importlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from automation.forex_engine.supervised_demo_broker_snapshot_intake_epic_v1 import (
    SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION,
    SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW,
    build_sample_supervised_demo_snapshot_intake_blocked_input,
    build_sample_supervised_demo_snapshot_intake_ready_input,
    run_supervised_demo_broker_snapshot_intake_epic,
    supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict,
    supervised_demo_broker_snapshot_intake_epic_to_markdown,
)


NEW_SOURCE_PATHS = (
    Path("automation/forex_engine/sanitized_broker_snapshot_redaction_guard_v1.py"),
    Path("automation/forex_engine/sanitized_broker_snapshot_intake_v1.py"),
    Path("automation/forex_engine/demo_broker_snapshot_review_packet_v1.py"),
    Path("automation/forex_engine/supervised_demo_broker_snapshot_intake_epic_v1.py"),
    Path("scripts/forex_delivery/run_sanitized_broker_snapshot_intake_v1.py"),
    Path("scripts/forex_delivery/run_demo_broker_snapshot_review_packet_v1.py"),
    Path("scripts/forex_delivery/run_supervised_demo_broker_snapshot_intake_epic_v1.py"),
)


def _source_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in NEW_SOURCE_PATHS)


def _import_lines() -> str:
    return "\n".join(
        line.lower()
        for path in NEW_SOURCE_PATHS
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )


def test_epic_ready_sample_is_ready_for_review() -> None:
    result = run_supervised_demo_broker_snapshot_intake_epic(
        build_sample_supervised_demo_snapshot_intake_ready_input()
    )
    assert result.classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW


def test_epic_blocked_sample_is_blocked() -> None:
    result = run_supervised_demo_broker_snapshot_intake_epic(
        build_sample_supervised_demo_snapshot_intake_blocked_input()
    )
    assert result.classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION


@pytest.mark.parametrize(
    "key",
    [
        "selected_strategy_context",
        "instrument_context",
        "guard_status",
        "intake_status",
        "broker_snapshot_status",
        "account_status",
        "operator_answer",
        "next_safe_action",
    ],
)
def test_epic_json_has_required_keys(key: str) -> None:
    data = supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
        run_supervised_demo_broker_snapshot_intake_epic()
    )
    assert key in data


def test_epic_includes_selected_strategy_context() -> None:
    result = run_supervised_demo_broker_snapshot_intake_epic()
    assert result.selected_strategy_context == "Supertrend"


def test_epic_includes_instrument_context() -> None:
    result = run_supervised_demo_broker_snapshot_intake_epic()
    assert result.instrument_context == "EUR_USD"


def test_epic_markdown_has_title() -> None:
    assert supervised_demo_broker_snapshot_intake_epic_to_markdown().startswith(
        "# Supervised Demo Broker Snapshot Intake Epic V1"
    )


def test_epic_json_has_required_top_level_keys() -> None:
    data = supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
        run_supervised_demo_broker_snapshot_intake_epic()
    )
    assert data["snapshot_review_allowed"] is True
    assert data["account_review_allowed"] is True
    assert data["demo_execution_allowed"] is False
    json.dumps(data)


def test_repeated_ready_output_deterministic() -> None:
    first = supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
        run_supervised_demo_broker_snapshot_intake_epic()
    )
    second = supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
        run_supervised_demo_broker_snapshot_intake_epic()
    )
    assert first == second


def test_repeated_blocked_output_deterministic() -> None:
    first = supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
        run_supervised_demo_broker_snapshot_intake_epic(
            build_sample_supervised_demo_snapshot_intake_blocked_input()
        )
    )
    second = supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
        run_supervised_demo_broker_snapshot_intake_epic(
            build_sample_supervised_demo_snapshot_intake_blocked_input()
        )
    )
    assert first == second


@pytest.mark.parametrize(
    ("module_name", "args", "expected"),
    [
        (
            "scripts.forex_delivery.run_sanitized_broker_snapshot_intake_v1",
            ["--sample-ready"],
            "Sanitized broker snapshot intake is review-ready.",
        ),
        (
            "scripts.forex_delivery.run_demo_broker_snapshot_review_packet_v1",
            ["--sample-ready"],
            "Broker snapshot review is ready",
        ),
        (
            "scripts.forex_delivery.run_supervised_demo_broker_snapshot_intake_epic_v1",
            ["--sample-ready"],
            "Supervised demo broker snapshot intake status:",
        ),
    ],
)
def test_runners_emit_plain_text(module_name: str, args: list[str], expected: str) -> None:
    module = importlib.import_module(module_name)
    output = io.StringIO()
    with redirect_stdout(output):
        assert module.main(args) == 0
    assert expected in output.getvalue()


@pytest.mark.parametrize(
    ("module_name", "args"),
    [
        ("scripts.forex_delivery.run_sanitized_broker_snapshot_intake_v1", ["--sample-ready", "--json"]),
        ("scripts.forex_delivery.run_demo_broker_snapshot_review_packet_v1", ["--sample-ready", "--json"]),
        ("scripts.forex_delivery.run_supervised_demo_broker_snapshot_intake_epic_v1", ["--sample-ready", "--json"]),
    ],
)
def test_runners_emit_valid_json(module_name: str, args: list[str]) -> None:
    module = importlib.import_module(module_name)
    output = io.StringIO()
    with redirect_stdout(output):
        assert module.main(args) == 0
    assert isinstance(json.loads(output.getvalue()), dict)


@pytest.mark.parametrize(
    ("module_name", "args", "title"),
    [
        (
            "scripts.forex_delivery.run_sanitized_broker_snapshot_intake_v1",
            ["--sample-ready", "--markdown"],
            "# Sanitized Broker Snapshot Intake V1",
        ),
        (
            "scripts.forex_delivery.run_demo_broker_snapshot_review_packet_v1",
            ["--sample-ready", "--markdown"],
            "# Demo Broker Snapshot Review Packet V1",
        ),
        (
            "scripts.forex_delivery.run_supervised_demo_broker_snapshot_intake_epic_v1",
            ["--sample-ready", "--markdown"],
            "# Supervised Demo Broker Snapshot Intake Epic V1",
        ),
    ],
)
def test_runners_emit_markdown(module_name: str, args: list[str], title: str) -> None:
    module = importlib.import_module(module_name)
    output = io.StringIO()
    with redirect_stdout(output):
        assert module.main(args) == 0
    assert title in output.getvalue()


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
def test_no_forbidden_imports(forbidden_import: str) -> None:
    assert forbidden_import not in _import_lines()


def test_no_oanda_import() -> None:
    assert "oanda" not in _import_lines()


def test_no_credential_import() -> None:
    imports = _import_lines()
    assert "credential" not in imports
    assert "keyring" not in imports


def test_no_network_call_markers() -> None:
    text = _source_text().lower()
    for marker in ("requests.", "httpx.", "socket.", "urlopen(", "create_connection("):
        assert marker not in text


def test_no_dotenv_usage() -> None:
    text = _source_text().lower()
    assert "load_dotenv" not in text
    assert "dotenv" not in _import_lines()


def test_no_subprocess_in_module_logic() -> None:
    assert "subprocess" not in _source_text().lower()


def test_no_broker_execution_import() -> None:
    imports = _import_lines()
    assert "broker_execution" not in imports
    assert "broker_mutation" not in imports


def test_no_order_placement_function() -> None:
    text = _source_text().lower()
    for marker in ("def place_order", "def submit_order", "create_order(", "place_trade("):
        assert marker not in text


def test_no_live_trading_approval() -> None:
    compact = _source_text().replace(" ", "").lower()
    assert "live_trading_allowed=true" not in compact
    assert "demo_execution_allowed=true" not in compact


def test_no_secret_or_account_persistence_write() -> None:
    text = _source_text().lower()
    assert "write_text(" not in text
    assert "secret_persistence" not in text
    assert "account_id_persistence_allowed=true" not in text.replace(" ", "")


@pytest.mark.parametrize("marker", ["scheduler", "daemon", "webhook"])
def test_no_scheduler_daemon_or_webhook(marker: str) -> None:
    assert marker not in _source_text().lower()


def test_manual_finalization_report_includes_exact_git_add_commands() -> None:
    report = Path("Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_MANUAL_FINALIZATION_V1.md")
    text = report.read_text(encoding="utf-8")
    assert "git add automation/forex_engine/sanitized_broker_snapshot_redaction_guard_v1.py" in text
    assert "git add tests/forex_engine/test_supervised_demo_broker_snapshot_intake_epic_v1.py" in text


def test_manual_finalization_report_says_no_git_add_dot() -> None:
    report = Path("Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_MANUAL_FINALIZATION_V1.md")
    text = report.read_text(encoding="utf-8")
    assert "No broad add-dot staging is allowed." in text
    assert "git add ." not in text


def test_epic_report_says_no_trade_placed() -> None:
    report = Path("Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_EPIC_REPORT_V1.md")
    assert "No trade was placed." in report.read_text(encoding="utf-8")
