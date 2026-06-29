from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "security" / "aios_security_360_baseline_v1.py"
RUNNER_PATH = REPO_ROOT / "scripts" / "security" / "run_aios_security_360_baseline_v1.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("aios_security_360_baseline_v1", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _state(repo_root: Path = REPO_ROOT) -> dict:
    return _load_module().build_security_360_baseline(repo_root)


def test_output_is_json_serializable() -> None:
    state = _state()

    dumped = json.dumps(state, sort_keys=True)

    assert "aios.security_360_baseline.v1" in dumped


def test_all_protected_actions_are_blocked() -> None:
    state = _state()

    required = {
        "broker_contact",
        "broker_api_use",
        "credential_use",
        "env_read",
        "account_identifier_use",
        "order_execution",
        "demo_authorization",
        "live_authorization",
        "scheduler_start",
        "daemon_start",
        "webhook_start",
        "watcher_start",
        "listener_start",
        "background_loop_start",
        "remote_public_exposure",
        "tunnel_start",
        "bitwarden_start",
        "vaultwarden_start",
        "secrets_migration",
        "token_storage",
        "dashboard_execution_controls",
    }

    assert set(state["protected_actions"]) == required
    assert all(item["status"] == "BLOCKED" for item in state["protected_actions"].values())


def test_no_external_bank_certification_claim_is_made() -> None:
    state = _state()

    assert state["bank_style_security_target"] == "DEFENSE_IN_DEPTH_HIGH_ASSURANCE_INTERNAL_TARGET"
    assert state["certification_claim"] == "NO_EXTERNAL_BANK_CERTIFICATION_CLAIM"


def test_remote_dashboard_gate_requires_core_protections() -> None:
    gate = _state()["required_gates_before_remote_dashboard"]
    controls = set(gate["required_controls"])

    assert "authenticated access" in controls
    assert "private route or HTTPS" in controls
    assert "read-only dashboard API" in controls
    assert "no secrets in frontend" in controls
    assert "no execution controls" in controls
    assert gate["owner_approval_required"] is True


def test_broker_readonly_gate_blocks_sensitive_broker_material() -> None:
    gate = _state()["required_gates_before_broker_readonly"]
    controls = set(gate["required_controls"])

    assert "no credentials in repo" in controls
    assert "no account identifiers in repo" in controls
    assert "no raw broker payloads in repo" in controls
    assert "no order endpoints" in controls
    assert "runtime-only credentials if ever approved" in controls


def test_bitwarden_remains_locked_until_owner_confirmation() -> None:
    state = _state()
    gate = state["required_gates_before_bitwarden"]

    assert state["protected_actions"]["bitwarden_start"]["status"] == "BLOCKED"
    assert "owner confirmation" in gate["required_controls"]
    assert "no token storage before approval" in gate["required_controls"]


def test_demo_live_remains_blocked_without_proof_and_owner_approval() -> None:
    state = _state()
    demo = set(state["required_gates_before_demo"]["required_controls"])
    live = set(state["required_gates_before_live"]["required_controls"])

    for controls in (demo, live):
        assert "profitability proof" in controls
        assert "owner approval" in controls
        assert "runtime-only credentials" in controls
        assert "post-trade evidence capture" in controls
    assert state["protected_actions"]["demo_authorization"]["status"] == "BLOCKED"
    assert state["protected_actions"]["live_authorization"]["status"] == "BLOCKED"


def test_scheduler_daemon_webhook_remains_blocked() -> None:
    state = _state()
    gate = set(state["required_gates_before_scheduler_daemon_webhook"]["required_controls"])

    assert "explicit owner approval" in gate
    assert "bounded runtime" in gate
    assert "safe shutdown" in gate
    assert state["protected_actions"]["scheduler_start"]["status"] == "BLOCKED"
    assert state["protected_actions"]["daemon_start"]["status"] == "BLOCKED"
    assert state["protected_actions"]["webhook_start"]["status"] == "BLOCKED"


def test_unknown_missing_control_becomes_review_required_or_blocked(tmp_path: Path) -> None:
    state = _state(tmp_path)
    statuses = {domain["status"] for domain in state["security_domains"]}

    assert state["overall_security_posture"] in {"REVIEW_REQUIRED", "BLOCKED"}
    assert "REVIEW_REQUIRED" in statuses or "BLOCKED_BY_DEFAULT" in statuses
    assert state["high_priority_findings"]


def test_source_code_does_not_contain_network_or_env_reading_behavior() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    runner = RUNNER_PATH.read_text(encoding="utf-8")
    combined = source + "\n" + runner
    forbidden = [
        "requests.",
        "urllib.",
        "http.client",
        "socket.",
        "subprocess",
        "os.environ",
        "getenv",
        "dotenv",
        ".env",
        "OANDA_API",
        "API_TOKEN",
    ]

    assert all(term not in combined for term in forbidden)
    assert _state()["tool_behavior"]["calls_network"] is False
