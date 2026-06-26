from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine.supervised_demo_manual_execution_exception_epic_v1 import (
    SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_BLOCKED,
    SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_READY_FOR_OWNER_REVIEW,
    build_sample_supervised_demo_manual_execution_exception_blocked_input,
    build_sample_supervised_demo_manual_execution_exception_ready_input,
    run_supervised_demo_manual_execution_exception_epic,
    supervised_demo_manual_execution_exception_epic_to_jsonable_dict,
    supervised_demo_manual_execution_exception_epic_to_markdown,
    supervised_demo_manual_execution_exception_epic_to_operator_text,
)
from scripts.forex_delivery import run_demo_manual_execution_exception_scope_gate_v1 as scope_runner
from scripts.forex_delivery import run_supervised_demo_manual_execution_exception_epic_v1 as epic_runner
from scripts.forex_delivery import run_supervised_demo_manual_execution_exception_packet_v1 as packet_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATHS = (
    "automation/forex_engine/demo_manual_execution_exception_scope_gate_v1.py",
    "automation/forex_engine/demo_manual_execution_exception_checklist_v1.py",
    "automation/forex_engine/supervised_demo_manual_execution_exception_packet_v1.py",
    "automation/forex_engine/supervised_demo_manual_execution_exception_epic_v1.py",
    "scripts/forex_delivery/run_demo_manual_execution_exception_scope_gate_v1.py",
    "scripts/forex_delivery/run_supervised_demo_manual_execution_exception_packet_v1.py",
    "scripts/forex_delivery/run_supervised_demo_manual_execution_exception_epic_v1.py",
)
REPORT_PATHS = (
    "Reports/forex_delivery/AIOS_FOREX_DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_GATE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_EPIC_REPORT_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_MANUAL_FINALIZATION_V1.md",
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
    result = run_supervised_demo_manual_execution_exception_epic(
        build_sample_supervised_demo_manual_execution_exception_ready_input()
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_READY_FOR_OWNER_REVIEW


def test_epic_blocked_sample_blocks() -> None:
    result = run_supervised_demo_manual_execution_exception_epic(
        build_sample_supervised_demo_manual_execution_exception_blocked_input()
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_BLOCKED


@pytest.mark.parametrize(
    "field_name",
    (
        "exception_packet_status",
        "owner_approval_status",
        "scope_status",
        "checklist_status",
        "selected_strategy",
        "candidate_id",
        "instrument",
        "direction",
        "entry_type",
        "proposed_units",
        "entry_price",
        "stop_loss",
        "take_profit",
        "max_loss",
        "expected_reward",
        "reward_to_risk",
        "owner_warning",
        "exception_warning",
        "required_phrase",
    ),
)
def test_epic_includes_required_field(field_name: str) -> None:
    result = run_supervised_demo_manual_execution_exception_epic()

    assert getattr(result, field_name) not in ("", None)


def test_epic_operator_answer_is_plain_english() -> None:
    text = supervised_demo_manual_execution_exception_epic_to_operator_text(
        run_supervised_demo_manual_execution_exception_epic()
    )

    assert "manual execution exception status" in text
    assert "No trade was placed" in text


def test_epic_next_safe_action_present() -> None:
    result = run_supervised_demo_manual_execution_exception_epic()

    assert result.next_safe_action
    assert "review" in result.next_safe_action.lower()


def test_epic_markdown_has_title() -> None:
    markdown = supervised_demo_manual_execution_exception_epic_to_markdown(
        run_supervised_demo_manual_execution_exception_epic()
    )

    assert markdown.startswith("# Supervised Demo Manual Execution Exception Epic V1")


def test_epic_json_has_required_keys() -> None:
    payload = supervised_demo_manual_execution_exception_epic_to_jsonable_dict(
        run_supervised_demo_manual_execution_exception_epic()
    )

    for key in (
        "classification",
        "exception_packet_status",
        "owner_approval_status",
        "scope_status",
        "checklist_status",
        "selected_strategy",
        "candidate_id",
        "instrument",
        "direction",
        "entry_type",
        "proposed_units",
        "entry_price",
        "stop_loss",
        "take_profit",
        "max_loss",
        "expected_reward",
        "reward_to_risk",
        "owner_warning",
        "exception_warning",
        "required_phrase",
        "operator_answer",
        "next_safe_action",
    ):
        assert key in payload
    assert json.loads(json.dumps(payload))["classification"] == (
        SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_READY_FOR_OWNER_REVIEW
    )


def test_ready_output_deterministic() -> None:
    first = supervised_demo_manual_execution_exception_epic_to_jsonable_dict(
        run_supervised_demo_manual_execution_exception_epic()
    )
    second = supervised_demo_manual_execution_exception_epic_to_jsonable_dict(
        run_supervised_demo_manual_execution_exception_epic()
    )

    assert first == second


def test_blocked_output_deterministic() -> None:
    first = supervised_demo_manual_execution_exception_epic_to_jsonable_dict(
        run_supervised_demo_manual_execution_exception_epic(
            build_sample_supervised_demo_manual_execution_exception_blocked_input()
        )
    )
    second = supervised_demo_manual_execution_exception_epic_to_jsonable_dict(
        run_supervised_demo_manual_execution_exception_epic(
            build_sample_supervised_demo_manual_execution_exception_blocked_input()
        )
    )

    assert first == second


@pytest.mark.parametrize("runner_module", (scope_runner, packet_runner, epic_runner))
def test_runners_emit_plain_text(
    runner_module: object,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", [runner_module.__file__, "--sample-ready"])

    assert runner_module.main() == 0
    assert "No trade was placed" in capsys.readouterr().out


@pytest.mark.parametrize("runner_module", (scope_runner, packet_runner, epic_runner))
def test_runners_emit_json(
    runner_module: object,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", [runner_module.__file__, "--sample-ready", "--json"])

    assert runner_module.main() == 0
    assert json.loads(capsys.readouterr().out)["classification"]


@pytest.mark.parametrize("runner_module", (scope_runner, packet_runner, epic_runner))
def test_runners_emit_markdown(
    runner_module: object,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
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


def test_reports_exist() -> None:
    for path in REPORT_PATHS:
        assert (REPO_ROOT / path).exists()


def test_manual_finalization_report_includes_exact_git_add_commands() -> None:
    text = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_MANUAL_FINALIZATION_V1.md").read_text(
        encoding="utf-8"
    )

    for path in (*SOURCE_PATHS, *REPORT_PATHS):
        assert f"git add {path}" in text


def test_manual_finalization_report_says_no_git_add_dot() -> None:
    text = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_MANUAL_FINALIZATION_V1.md").read_text(
        encoding="utf-8"
    )

    assert "No git add dot" in text
    assert "git add ." not in text


def test_epic_report_says_no_trade_placed() -> None:
    text = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_EPIC_REPORT_V1.md").read_text(
        encoding="utf-8"
    )

    assert "No trade placed" in text


def test_protected_permissions_stay_false_in_every_top_level_output() -> None:
    result = run_supervised_demo_manual_execution_exception_epic()
    payload = supervised_demo_manual_execution_exception_epic_to_jsonable_dict(result)

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False
        assert payload[flag] is False


def test_exception_epic_never_sets_broker_action_allowed_true() -> None:
    result = run_supervised_demo_manual_execution_exception_epic()

    assert result.broker_action_allowed is False


def test_exception_epic_never_sets_demo_execution_allowed_true() -> None:
    result = run_supervised_demo_manual_execution_exception_epic()

    assert result.demo_execution_allowed is False
