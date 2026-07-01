from __future__ import annotations

import ast
import json
from pathlib import Path

from automation.forex_engine import broker_connection_proof_boundary_readiness_v1 as readiness


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "automation" / "forex_engine" / "broker_connection_proof_boundary_readiness_v1.py"
RUNNER_PATH = (
    ROOT / "scripts" / "forex_delivery" / "run_broker_connection_proof_boundary_readiness_v1.py"
)
FORBIDDEN_TEXT = (
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


def test_readiness_state_is_owner_gated_at_broker_connection_proof():
    result = readiness.run_broker_connection_proof_boundary_readiness_v1()

    assert result["readiness_status"] == "OWNER_GATED_BROKER_CONNECTION_PROOF_READY_FOR_REVIEW"
    assert result["next_protected_boundary"] == "broker connection proof"
    assert result["source_repo_only_remaining_stage_count"] == 1
    assert result["source_protected_stage_count"] == 12
    assert result["owner_wake_required"] is True


def test_protected_action_and_runtime_booleans_are_false():
    result = readiness.run_broker_connection_proof_boundary_readiness_v1()

    for field in readiness.PROTECTED_FALSE_FIELDS:
        assert result[field] is False
    assert result["stash_applied"] is False


def test_state_is_json_serializable_and_contains_reusable_pattern():
    result = readiness.run_broker_connection_proof_boundary_readiness_v1()

    json.dumps(result)
    assert result["reusable_autonomy_pattern"]["identity_chain"]


def test_generated_next_packet_is_tokenized_and_forbids_protected_actions():
    result = readiness.run_broker_connection_proof_boundary_readiness_v1()
    packet = readiness.build_next_codex_packet(result)

    assert packet.startswith("CODEX-ONLY PROMPT")
    assert "AI_OS EXECUTION TOKEN" in packet
    for phrase in [
        "Do not contact broker",
        "Do not use credentials",
        "Do not read .env",
        "Do not use account identifiers",
        "Do not place orders",
        "Do not authorize demo execution",
        "Do not authorize live execution",
        "Do not start scheduler, daemon, webhook, worker, watcher, listener, or background loop",
    ]:
        assert phrase in packet


def test_source_contains_no_forbidden_imports_or_runtime_calls():
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
        for forbidden in FORBIDDEN_TEXT:
            assert forbidden not in source.lower()
