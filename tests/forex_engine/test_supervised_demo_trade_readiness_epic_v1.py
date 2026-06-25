from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine.supervised_demo_trade_readiness_epic_v1 import (
    SUPERVISED_DEMO_TRADE_READINESS_BLOCKED,
    SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW,
    build_sample_supervised_demo_trade_readiness_blocked_input,
    build_sample_supervised_demo_trade_readiness_ready_input,
    run_supervised_demo_trade_readiness_epic,
    supervised_demo_trade_readiness_epic_to_jsonable_dict,
    supervised_demo_trade_readiness_epic_to_markdown,
    supervised_demo_trade_readiness_epic_to_operator_text,
)
from scripts.forex_delivery import run_demo_trade_readiness_bridge_v1 as bridge_runner
from scripts.forex_delivery import run_supervised_demo_trade_readiness_epic_v1 as epic_runner
from scripts.forex_delivery import run_supervised_demo_trade_review_bundle_v1 as bundle_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATHS = (
    "automation/forex_engine/demo_trade_candidate_context_v1.py",
    "automation/forex_engine/demo_trade_readiness_bridge_v1.py",
    "automation/forex_engine/supervised_demo_trade_review_bundle_v1.py",
    "automation/forex_engine/supervised_demo_trade_readiness_epic_v1.py",
    "scripts/forex_delivery/run_demo_trade_readiness_bridge_v1.py",
    "scripts/forex_delivery/run_supervised_demo_trade_review_bundle_v1.py",
    "scripts/forex_delivery/run_supervised_demo_trade_readiness_epic_v1.py",
)
PERMISSION_FLAGS = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
)


def _source_text() -> str:
    return "\n".join((REPO_ROOT / path).read_text(encoding="utf-8") for path in SOURCE_PATHS)


def test_epic_ready_sample_passes() -> None:
    result = run_supervised_demo_trade_readiness_epic(
        build_sample_supervised_demo_trade_readiness_ready_input()
    )

    assert result.classification == SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW
    assert result.proposed_units > 0


def test_epic_blocked_sample_blocks() -> None:
    result = run_supervised_demo_trade_readiness_epic(
        build_sample_supervised_demo_trade_readiness_blocked_input()
    )

    assert result.classification == SUPERVISED_DEMO_TRADE_READINESS_BLOCKED
    assert "blocked" in result.operator_answer.lower()


@pytest.mark.parametrize(
    "field_name",
    (
        "readiness_bridge_status",
        "review_bundle_status",
        "snapshot_intake_status",
        "account_status",
        "candidate_status",
        "risk_status",
        "position_size_status",
        "order_plan_status",
        "operator_ticket_status",
        "selected_strategy",
        "candidate_id",
        "instrument",
        "direction",
        "proposed_units",
        "entry_price",
        "stop_loss",
        "take_profit",
        "max_loss",
        "expected_reward",
        "reward_to_risk",
    ),
)
def test_epic_includes_required_field(field_name: str) -> None:
    result = run_supervised_demo_trade_readiness_epic()

    assert getattr(result, field_name) not in ("", None)


def test_epic_operator_answer_is_plain_english() -> None:
    text = supervised_demo_trade_readiness_epic_to_operator_text(run_supervised_demo_trade_readiness_epic())

    assert "Supervised demo trade readiness status" in text
    assert "No trade was placed" in text


def test_epic_next_safe_action_present() -> None:
    result = run_supervised_demo_trade_readiness_epic()

    assert result.next_safe_action
    assert "review" in result.next_safe_action.lower()


def test_epic_markdown_has_title() -> None:
    markdown = supervised_demo_trade_readiness_epic_to_markdown(run_supervised_demo_trade_readiness_epic())

    assert markdown.startswith("# Supervised Demo Trade Readiness Epic V1")


def test_epic_json_has_required_keys() -> None:
    payload = supervised_demo_trade_readiness_epic_to_jsonable_dict(run_supervised_demo_trade_readiness_epic())

    for key in (
        "classification",
        "readiness_bridge_status",
        "review_bundle_status",
        "selected_strategy",
        "candidate_id",
        "instrument",
        "direction",
        "proposed_units",
        "entry_price",
        "stop_loss",
        "take_profit",
        "max_loss",
        "expected_reward",
        "reward_to_risk",
        "operator_answer",
        "next_safe_action",
    ):
        assert key in payload
    assert json.loads(json.dumps(payload))["classification"] == (
        SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW
    )


def test_ready_output_deterministic() -> None:
    first = supervised_demo_trade_readiness_epic_to_jsonable_dict(run_supervised_demo_trade_readiness_epic())
    second = supervised_demo_trade_readiness_epic_to_jsonable_dict(run_supervised_demo_trade_readiness_epic())

    assert first == second


def test_blocked_output_deterministic() -> None:
    first = supervised_demo_trade_readiness_epic_to_jsonable_dict(
        run_supervised_demo_trade_readiness_epic(build_sample_supervised_demo_trade_readiness_blocked_input())
    )
    second = supervised_demo_trade_readiness_epic_to_jsonable_dict(
        run_supervised_demo_trade_readiness_epic(build_sample_supervised_demo_trade_readiness_blocked_input())
    )

    assert first == second


@pytest.mark.parametrize(
    "runner_module",
    (bridge_runner, bundle_runner, epic_runner),
)
def test_runners_emit_plain_text(runner_module: object, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", [runner_module.__file__, "--sample-ready"])

    assert runner_module.main() == 0
    assert "No trade was placed" in capsys.readouterr().out


@pytest.mark.parametrize(
    "runner_module",
    (bridge_runner, bundle_runner, epic_runner),
)
def test_runners_emit_json(runner_module: object, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", [runner_module.__file__, "--sample-ready", "--json"])

    assert runner_module.main() == 0
    assert json.loads(capsys.readouterr().out)["classification"]


@pytest.mark.parametrize(
    "runner_module",
    (bridge_runner, bundle_runner, epic_runner),
)
def test_runners_emit_markdown(runner_module: object, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", [runner_module.__file__, "--sample-ready", "--markdown"])

    assert runner_module.main() == 0
    assert capsys.readouterr().out.startswith("#")


@pytest.mark.parametrize(
    "pattern",
    (
        "import " + "requests",
        "from " + "requests",
        "import " + "httpx",
        "from " + "httpx",
        "import " + "socket",
        "from " + "socket",
        "import " + "dotenv",
        "from " + "dotenv",
        "import " + "keyring",
        "from " + "keyring",
        "import " + "oanda",
        "from " + "oanda",
        "import " + "OANDA",
        "from " + "OANDA",
        "broker_" + "execution",
        "broker_" + "mutation",
        "sub" + "process",
        "place_" + "order",
        "submit_" + "order",
        "create_" + "order",
        "sched" + "uler",
        "dae" + "mon",
        "web" + "hook",
    ),
)
def test_new_source_avoids_unsafe_import_or_call_patterns(pattern: str) -> None:
    assert pattern not in _source_text()


@pytest.mark.parametrize(
    "approval_pattern",
    (
        "demo_execution_allowed=True",
        "broker_action_allowed=True",
        "real_money_allowed=True",
        "compounding_allowed=True",
        "bank_movement_allowed=True",
        "live_trading_allowed=True",
        "credential_access_allowed=True",
        "account_id_persistence_allowed=True",
    ),
)
def test_new_source_never_sets_protected_permission_true(approval_pattern: str) -> None:
    assert approval_pattern not in _source_text()


def test_manual_finalization_report_includes_exact_git_add_commands() -> None:
    text = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_MANUAL_FINALIZATION_V1.md").read_text(
        encoding="utf-8"
    )

    for path in SOURCE_PATHS:
        assert f"git add {path}" in text
    assert "git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_EPIC_REPORT_V1.md" in text


def test_manual_finalization_report_says_no_git_add_dot() -> None:
    text = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_MANUAL_FINALIZATION_V1.md").read_text(
        encoding="utf-8"
    )

    assert "No git add dot" in text
    assert "git add ." not in text


def test_epic_report_says_no_trade_placed() -> None:
    text = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_EPIC_REPORT_V1.md").read_text(
        encoding="utf-8"
    )

    assert "No trade placed" in text


def test_protected_permissions_stay_false_in_every_top_level_output() -> None:
    result = run_supervised_demo_trade_readiness_epic()
    payload = supervised_demo_trade_readiness_epic_to_jsonable_dict(result)

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False
        assert payload[flag] is False
