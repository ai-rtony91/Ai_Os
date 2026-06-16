from __future__ import annotations

from pathlib import Path

from automation.forex_engine import broker_paper_presecurity_gate
from automation.forex_engine import run_broker_paper_presecurity_gate_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_presecurity_gate.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_presecurity_gate_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PRESECURITY_READY"}
FORBIDDEN_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}
REQUIRED_SECRET_PATTERNS = {
    ".env",
    "*.env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
    "*.pfx",
    "*.p12",
    "*secret*",
    "*secrets*",
}


def test_presecurity_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_presecurity_requirements_include_all_required_controls() -> None:
    requirements = broker_paper_presecurity_gate.build_presecurity_requirements()

    assert requirements["credential_boundary_required"] is True
    assert requirements["env_secret_read_allowed"] is False
    assert requirements["broker_sdk_allowed"] is False
    assert requirements["network_api_allowed"] is False
    assert requirements["webhook_allowed"] is False
    assert requirements["scheduler_allowed"] is False
    assert requirements["daemon_allowed"] is False
    assert requirements["broker_paper_orders_allowed"] is False
    assert requirements["live_orders_allowed"] is False
    assert requirements["manual_approval_required"] is True
    assert requirements["kill_switch_required"] is True
    assert requirements["max_loss_guard_required"] is True
    assert requirements["daily_stop_required"] is True
    assert requirements["audit_log_required"] is True
    assert requirements["rustdesk_operator_hygiene_required"] is True
    assert REQUIRED_SECRET_PATTERNS.issubset(set(requirements["secrets_exclusion_patterns"]))
    assert requirements["blocked_capabilities"]


def test_presecurity_gate_can_be_ready_without_enabling_broker_or_orders() -> None:
    result = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate()
    summary = broker_paper_presecurity_gate.summarize_presecurity_gate(result)

    assert result["classification"] == "PRESECURITY_READY"
    assert summary["classification"] == "PRESECURITY_READY"
    assert result["classification"] in ALLOWED_CLASSIFICATIONS
    assert result["classification"] not in FORBIDDEN_CLASSIFICATIONS
    assert result["env_secret_read_allowed"] is False
    assert result["broker_sdk_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["webhook_allowed"] is False
    assert result["scheduler_allowed"] is False
    assert result["daemon_allowed"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["broker_paper_contract_ready"] is False
    assert result["live_ready"] is False
    assert result["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT"


def test_presecurity_gate_blocks_missing_or_forbidden_controls() -> None:
    missing = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate(
        {"kill_switch_required": False}
    )
    forbidden = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate(
        {"network_api_allowed": True}
    )

    assert missing["classification"] == "WATCHLIST"
    assert "missing_required_control:kill_switch_required" in missing["blockers"]
    assert forbidden["classification"] == "FAIL"
    assert "forbidden_capability_enabled:network_api_allowed" in forbidden["blockers"]


def test_boundary_summary_blocks_broker_live_network_orders_scheduler_and_daemon() -> None:
    boundary = broker_paper_presecurity_gate.broker_paper_presecurity_boundary_summary()

    assert boundary["readiness_contract_only"] is True
    assert boundary["broker_sdk_allowed"] is False
    assert boundary["broker_paper_orders_allowed"] is False
    assert boundary["network_api_allowed"] is False
    assert boundary["webhook_allowed"] is False
    assert boundary["env_secret_read_allowed"] is False
    assert boundary["live_orders_allowed"] is False
    assert boundary["live_ready"] is False
    assert boundary["scheduler_allowed"] is False
    assert boundary["daemon_allowed"] is False
    assert boundary["worker_dispatch"] is False
    assert boundary["queue_mutation"] is False
    assert boundary["approval_mutation"] is False


def test_demo_module_imports_and_prints_required_lines(capsys) -> None:
    assert run_broker_paper_presecurity_gate_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Presecurity Gate Demo" in output
    assert "Mode: PAPER_ONLY_CONTRACT" in output
    assert "Classification: PRESECURITY_READY" in output
    assert "Credential boundary required: true" in output
    assert "Env secret read allowed: false" in output
    assert "Broker SDK allowed: false" in output
    assert "Network/API allowed: false" in output
    assert "Webhook allowed: false" in output
    assert "Broker-paper orders allowed: false" in output
    assert "Live orders allowed: false" in output
    assert "Kill switch required: true" in output
    assert "Max loss guard required: true" in output
    assert "Daily stop required: true" in output
    assert "Audit log required: true" in output
    assert "Manual approval required: true" in output
    assert "Safety: no broker/API/network/orders/secrets/live execution." in output


def test_presecurity_modules_have_no_forbidden_imports_or_execution_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "schedule", "daemon"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "oanda",
            "schedule.every",
            "daemon.daemoncontext",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
        ):
            assert forbidden_call not in source
