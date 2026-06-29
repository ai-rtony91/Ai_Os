from __future__ import annotations

import ast
import json
from pathlib import Path

from automation.forex_engine import forex_overnight_repo_safe_campaign_planner_v1 as planner
from automation.forex_engine.broker_connection_proof_boundary_readiness_v1 import (
    PROTECTED_FALSE_FIELDS,
)


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "automation" / "forex_engine" / "forex_overnight_repo_safe_campaign_planner_v1.py"
RUNNER_PATH = (
    ROOT / "scripts" / "forex_delivery" / "run_forex_overnight_repo_safe_campaign_planner_v1.py"
)


def test_campaign_status_and_finite_queue_are_repo_safe():
    result = planner.run_forex_overnight_repo_safe_campaign_planner_v1()

    assert result["campaign_status"] == "REPO_SAFE_OVERNIGHT_BUILD_STAGE_READY"
    assert result["repo_safe_work_units"]
    assert isinstance(result["repo_safe_work_units"], list)
    assert result["overnight_run_limits"]["finite_queue"] is True
    assert result["overnight_run_limits"]["infinite_loop"] is False


def test_protected_boundary_and_owner_wake_are_preserved():
    result = planner.run_forex_overnight_repo_safe_campaign_planner_v1()

    assert result["next_protected_boundary"] == "broker connection proof"
    assert result["protected_boundaries"][0]["name"] == "broker connection proof"
    assert result["owner_wake_required"] is True


def test_all_broker_action_runtime_booleans_are_false_and_stash_preserved():
    result = planner.run_forex_overnight_repo_safe_campaign_planner_v1()

    for field in PROTECTED_FALSE_FIELDS:
        assert result[field] is False
    assert result["stash_policy"]["stash_preserved"] is True
    assert result["stash_policy"]["stash_applied"] is False


def test_state_is_json_serializable_and_next_packet_is_repo_safe_only():
    result = planner.run_forex_overnight_repo_safe_campaign_planner_v1()
    packet = planner.build_next_codex_packet(result)

    json.dumps(result)
    assert packet.startswith("CODEX-ONLY PROMPT")
    assert "AI_OS EXECUTION TOKEN" in packet
    assert "repo-safe" in packet.lower()
    for phrase in [
        "Do not contact broker",
        "Do not use credentials",
        "Do not read .env",
        "Do not use account identifiers",
        "Do not place orders",
        "Do not authorize demo or live execution",
        "Do not start scheduler, daemon, webhook, worker, watcher, listener, or background loop",
    ]:
        assert phrase in packet


def test_source_contains_no_forbidden_imports_or_runtime_calls():
    forbidden_text = (
        "os.environ",
        "dotenv",
        "requests",
        "urllib",
        "broker api",
        "order execution",
        "scheduler start",
        "daemon start",
        "webhook start",
        "background loop start",
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

        assert "subprocess" not in imports
        assert "requests" not in imports
        assert "urllib" not in imports
        assert "dotenv" not in imports
        for forbidden in forbidden_text:
            assert forbidden not in source.lower()
