from __future__ import annotations

from pathlib import Path

import pytest

from automation.forex_engine import broker_paper_adapter_plan_approval_gate
from automation.forex_engine import broker_paper_dryrun_replay_evidence_gate


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_adapter_plan_approval_gate.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_adapter_plan_approval_gate_demo.py"
DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "trading_lab"
    / "AIOS_FOREX_BUILDER_BROKER_PAPER_ADAPTER_PLAN_APPROVAL_GATE.md"
)
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "ADAPTER_PLAN_APPROVAL_READY"}


def _approved_plan_only_artifact() -> dict[str, object]:
    return broker_paper_adapter_plan_approval_gate.build_example_plan_only_approval()


def test_gate_doc_and_module_exist() -> None:
    assert DOC_PATH.exists()
    assert MODULE_PATH.exists()


def test_contract_blocks_broker_network_credentials_orders_and_live() -> None:
    contract = broker_paper_adapter_plan_approval_gate.build_broker_paper_adapter_plan_approval_gate_contract()

    assert contract["mode"] == "PAPER_ONLY_ADAPTER_PLAN_APPROVAL_GATE"
    assert contract["approval_scope_required"] == "broker_paper_adapter_plan_only"
    assert contract["plan_mode_required"] == "PLAN_ONLY"
    assert contract["paper_demo_adapter_planning_allowed"] is False
    for field in (
        "adapter_implementation_allowed",
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "live_trade_ready",
        "real_order_ready",
    ):
        assert contract[field] is False


def test_missing_approval_blocks_broker_paper_adapter_plan_progression() -> None:
    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate()

    assert result["classification"] == "WATCHLIST"
    assert result["source_evidence_ready"] is True
    assert result["approval_complete"] is False
    assert result["broker_paper_adapter_plan_approval_gate_ready"] is False
    assert result["paper_demo_adapter_planning_allowed"] is False
    assert "missing_approval:broker_selection_approval" in result["blockers"]
    assert "approval_field_must_equal:approval_scope:broker_paper_adapter_plan_only" in result["blockers"]
    assert "approved_by_human_owner_must_be_Anthony_Meza" in result["blockers"]
    assert result["broker_sdk_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["credentials_allowed"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["live_orders_allowed"] is False


def test_incomplete_approval_blocks_progression() -> None:
    approval = {
        "approval_scope": "broker_paper_adapter_plan_only",
        "plan_mode": "PLAN_ONLY",
        "broker_selection_approval": True,
        "approved_by_human_owner": "Anthony Meza",
    }

    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=approval
    )

    assert result["classification"] == "WATCHLIST"
    assert result["approval_complete"] is False
    assert result["broker_paper_adapter_plan_approval_gate_ready"] is False
    assert "missing_approval:external_auth_boundary_approval" in result["blockers"]
    assert "missing_approval:human_owner_confirmation" in result["blockers"]
    assert result["paper_demo_adapter_planning_allowed"] is False
    assert result["live_orders_allowed"] is False


def test_approved_broker_paper_adapter_plan_allows_paper_demo_planning_only() -> None:
    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=_approved_plan_only_artifact()
    )
    summary = broker_paper_adapter_plan_approval_gate.summarize_broker_paper_adapter_plan_approval_gate(
        result
    )

    assert result["classification"] == "ADAPTER_PLAN_APPROVAL_READY"
    assert result["approval_complete"] is True
    assert result["broker_paper_adapter_plan_approval_gate_ready"] is True
    assert result["paper_demo_adapter_planning_allowed"] is True
    assert summary["paper_demo_adapter_planning_allowed"] is True
    assert result["adapter_implementation_allowed"] is False
    assert result["broker_sdk_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["credentials_allowed"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["would_place_order"] is False
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["live_orders_allowed"] is False


def test_live_execution_remains_blocked_even_when_plan_ready() -> None:
    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=_approved_plan_only_artifact()
    )

    assert result["classification"] == "ADAPTER_PLAN_APPROVAL_READY"
    assert result["live_ready"] is False
    assert result["live_trade_ready"] is False
    assert result["real_order_ready"] is False
    assert result["live_orders_allowed"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["credentials_used"] is False


@pytest.mark.parametrize(
    "forbidden_field",
    (
        "api_key",
        "access_token",
        "refresh_token",
        "token",
        "password",
        "secret",
        "private_key",
        "credential",
        "credentials",
        "account_id",
        "account_number",
        "live_account_id",
    ),
)
def test_repo_side_approval_artifact_rejects_credential_or_account_fields(
    forbidden_field: str,
) -> None:
    approval = _approved_plan_only_artifact()
    approval[forbidden_field] = "NOT_A_REAL_VALUE"

    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=approval
    )

    assert result["classification"] == "FAIL"
    assert forbidden_field in result["forbidden_approval_fields"]
    assert f"forbidden_approval_field:{forbidden_field}" in result["blockers"]
    assert result["paper_demo_adapter_planning_allowed"] is False
    assert result["live_orders_allowed"] is False


def test_nested_forbidden_approval_fields_fail_closed() -> None:
    approval = _approved_plan_only_artifact()
    approval["broker_boundary"] = {"api_key": "NOT_A_REAL_VALUE"}

    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=approval
    )

    assert result["classification"] == "FAIL"
    assert "broker_boundary.api_key" in result["forbidden_approval_fields"]
    assert result["paper_demo_adapter_planning_allowed"] is False


def test_live_permission_attempt_in_approval_fails_closed() -> None:
    approval = _approved_plan_only_artifact()
    approval["live_orders_allowed"] = True

    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=approval
    )

    assert result["classification"] == "FAIL"
    assert "approval_artifact_attempts_execution_or_live_permission" in result["blockers"]
    assert result["paper_demo_adapter_planning_allowed"] is False
    assert result["live_orders_allowed"] is False


def test_source_replay_evidence_must_be_ready() -> None:
    replay = broker_paper_dryrun_replay_evidence_gate.build_default_replay_evidence_gate_result()
    replay["classification"] = "WATCHLIST"
    replay["broker_paper_dryrun_replay_evidence_gate_classification"] = "WATCHLIST"
    replay["evidence_ready"] = False

    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        replay_evidence=replay,
        approval=_approved_plan_only_artifact(),
    )

    assert result["classification"] == "WATCHLIST"
    assert result["source_evidence_ready"] is False
    assert "source_replay_evidence_gate_must_be_ready" in result["blockers"]
    assert result["paper_demo_adapter_planning_allowed"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["live_orders_allowed"] is False


def test_classification_set_never_emits_broker_live_order_or_auto_ready() -> None:
    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=_approved_plan_only_artifact()
    )
    summary = broker_paper_adapter_plan_approval_gate.summarize_broker_paper_adapter_plan_approval_gate(
        result
    )

    assert broker_paper_adapter_plan_approval_gate.classify_broker_paper_adapter_plan_approval_gate(
        summary
    ) in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] not in {"LIVE_READY", "BROKER_READY", "ORDER_READY", "AUTO_TRADE_READY"}


def test_boundary_summary_blocks_execution_capabilities() -> None:
    summary = broker_paper_adapter_plan_approval_gate.broker_paper_adapter_plan_approval_gate_boundary_summary()

    assert summary["approval_gate_only"] is True
    assert summary["adapter_plan_only"] is True
    assert summary["paper_demo_adapter_planning_allowed_if_approved"] is True
    assert summary["adapter_implementation_allowed"] is False
    assert summary["broker_integration_active"] is False
    assert summary["broker_sdk_allowed"] is False
    assert summary["network_api_allowed"] is False
    assert summary["credentials_allowed"] is False
    assert summary["broker_paper_orders_allowed"] is False
    assert summary["live_orders_allowed"] is False
    assert summary["approval_scope_required"] == "broker_paper_adapter_plan_only"
    assert summary["plan_mode_required"] == "PLAN_ONLY"


def test_demo_imports_and_prints_required_lines(capsys) -> None:
    from automation.forex_engine import run_broker_paper_adapter_plan_approval_gate_demo

    assert run_broker_paper_adapter_plan_approval_gate_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Adapter Plan Approval Gate Demo" in output
    assert "Mode: PAPER_ONLY_ADAPTER_PLAN_APPROVAL_GATE" in output
    assert "Classification: ADAPTER_PLAN_APPROVAL_READY" in output
    assert "Source evidence ready: true" in output
    assert "Approval complete: true" in output
    assert "Paper/demo adapter planning allowed: true" in output
    assert "Adapter implementation allowed: false" in output
    assert "Broker SDK allowed: false" in output
    assert "Network/API allowed: false" in output
    assert "Credentials allowed: false" in output
    assert "Broker-paper orders allowed: false" in output
    assert "Live orders allowed: false" in output
    assert "Safety: approval gate only; no broker/API/network/orders/secrets/live execution." in output


def test_modules_have_no_forbidden_imports_or_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "dotenv", "mt5", "ibkr"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
            "schedule.every",
            "daemon.daemoncontext",
        ):
            assert forbidden_call not in source
