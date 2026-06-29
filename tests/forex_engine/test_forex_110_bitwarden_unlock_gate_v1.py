from __future__ import annotations

import ast
import json
from pathlib import Path

from automation.forex_engine import forex_110_bitwarden_unlock_gate_v1 as gate


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "automation" / "forex_engine" / "forex_110_bitwarden_unlock_gate_v1.py"
RUNNER_PATH = ROOT / "scripts" / "forex_delivery" / "run_forex_110_bitwarden_unlock_gate_v1.py"


def test_output_is_deterministic_and_json_serializable() -> None:
    first = gate.run_forex_110_bitwarden_unlock_gate_v1()
    second = gate.run_forex_110_bitwarden_unlock_gate_v1()

    assert first == second
    json.dumps(first)


def test_all_required_forex_artifacts_are_checked_and_present() -> None:
    result = gate.run_forex_110_bitwarden_unlock_gate_v1()

    assert result["required_forex_artifacts"] == list(gate.REQUIRED_FOREX_ARTIFACTS)
    assert set(result["required_forex_artifacts_present"]) == set(gate.REQUIRED_FOREX_ARTIFACTS)
    assert all(result["required_forex_artifacts_present"].values())
    assert result["missing_forex_artifacts"] == []


def test_completion_percentages_and_110_gate_logic() -> None:
    result = gate.run_forex_110_bitwarden_unlock_gate_v1()

    assert result["forex_repo_safe_completion_percent"] == 100
    assert result["dashboard_extra_completion_percent"] == 10
    assert result["total_forex_completion_percent"] == 110
    assert result["forex_110_complete"] is True
    assert result["gate_status"] == "FOREX_110_REPO_SAFE_GATE_COMPLETE"


def test_bitwarden_and_secret_work_remain_locked() -> None:
    result = gate.run_forex_110_bitwarden_unlock_gate_v1()

    assert result["bitwarden_unlocked"] is False
    assert result["bitwarden_started"] is False
    assert result["vaultwarden_started"] is False
    assert result["secrets_migration_started"] is False
    assert result["token_storage_started"] is False
    assert "merged to main and owner confirms" in result["bitwarden_blocked_reason"]


def test_dashboard_emoji_windows_and_rules_exist() -> None:
    result = gate.run_forex_110_bitwarden_unlock_gate_v1()
    labels = {item["label"] for item in result["dashboard_emoji_windows"]}

    assert labels == set(gate.DASHBOARD_EMOJI_WINDOWS)
    assert result["dashboard_critical_display_rules"]
    assert result["dashboard_hidden_heavy_data_rules"]
    assert result["dashboard_overwhelm_prevention_rules"]
    assert result["dashboard_end_user_contract_status"]["status"] == "DEFINED"


def test_protected_broker_boundary_and_action_booleans_remain_false() -> None:
    result = gate.run_forex_110_bitwarden_unlock_gate_v1()

    assert result["protected_broker_boundary_status"] == "PROTECTED_AND_SEPARATE"
    assert result["protected_broker_boundary_handoff"]["status"] == "OWNER_GATED"
    for field in gate.PROTECTED_FALSE_FIELDS:
        assert result[field] is False


def test_source_contains_no_forbidden_runtime_network_or_secret_access() -> None:
    forbidden_imports = {"subprocess", "requests", "urllib", "dotenv", "os"}
    forbidden_phrases = (
        "os.environ",
        "load_dotenv",
        "requests.",
        "urllib.",
        "subprocess.",
        "account identifier access",
        "place_order(",
        "submit_order(",
        "execute_order(",
        "authorize_demo(",
        "authorize_live(",
        "scheduler start",
        "daemon start",
        "webhook start",
        "background loop start",
        "bitwarden implementation",
        "vaultwarden implementation",
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
