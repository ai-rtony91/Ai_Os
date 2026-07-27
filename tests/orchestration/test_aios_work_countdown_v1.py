from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "automation" / "orchestration" / "aios_work_countdown_v1.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_work_countdown_v1", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def packet(packet_id: str, status: str, **extra: object) -> dict[str, object]:
    value: dict[str, object] = {
        "packet_id": packet_id, "title": packet_id, "status": status,
        "priority": "medium", "milestone_value": 10, "risk_level": "low",
        "required_files": [f"automation/orchestration/{packet_id.lower()}.py"],
        "validators": ["python -m pytest test.py -q"],
    }
    value.update(extra)
    return value


def inventory(*packets: dict[str, object]) -> dict[str, object]:
    return {"authoritative_packet_inventory": True, "packets": list(packets)}


@pytest.fixture
def packet_repo(tmp_path: Path) -> Path:
    for state in ("active", "blocked", "complete"):
        (tmp_path / "automation/orchestration/work_packets" / state).mkdir(parents=True)
    return tmp_path


def write_json(root: Path, state: str, name: str, payload: object) -> Path:
    path = root / "automation/orchestration/work_packets" / state / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_live_folders_are_authoritative_and_mismatch_is_reported(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "active", "a.json", packet("ACTIVE", "complete"))
    write_json(packet_repo, "blocked", "b.json", packet("BLOCKED", "active"))
    write_json(packet_repo, "complete", "c.json", packet("COMPLETE", "blocked"))
    result = module.build_work_countdown(repo_root=packet_repo)
    assert result["current_task"]["packet_id"] == "ACTIVE"
    assert result["blocked_tasks"][0]["packet_id"] == "BLOCKED"
    assert result["completed_tasks"][0]["packet_id"] == "COMPLETE"
    assert result["completed_packet_count"] == 1
    assert result["completion_percentage"] == 33.33
    assert len(result["canonical_work_packet_inventory"]["folder_status_mismatches"]) == 3


def test_json_and_markdown_ids_parse_and_legacy_without_id_is_excluded(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "complete", "z.json", packet("JSON-ID", "complete"))
    md = packet_repo / "automation/orchestration/work_packets/active/a.md"
    md.write_text("# Packet\nPACKET ID: MD-ID\nSTATUS: active\n", encoding="utf-8")
    legacy = packet_repo / "automation/orchestration/work_packets/blocked/legacy.md"
    legacy.write_text("# Historical packet without an ID\n", encoding="utf-8")
    state = module.build_work_countdown(repo_root=packet_repo)
    inv = state["canonical_work_packet_inventory"]
    assert [item["packet_id"] for item in inv["records"]] == ["MD-ID", "JSON-ID"]
    assert inv["inventory_status"] == "PARTIAL"
    assert inv["excluded_legacy_records"][0]["record_identity"].endswith("legacy.md")
    assert state["total_packet_count"] == 2
    assert state["evidence_limitation"].startswith("Scoped percentage")


def test_duplicate_ids_and_parse_failures_block_calculation(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "active", "a.json", packet("DUP", "active"))
    write_json(packet_repo, "complete", "b.json", packet("DUP", "complete"))
    (packet_repo / "automation/orchestration/work_packets/blocked/bad.json").write_text("{", encoding="utf-8")
    result = module.build_work_countdown(repo_root=packet_repo)
    inv = result["canonical_work_packet_inventory"]
    assert inv["inventory_status"] == "BLOCKED"
    assert inv["duplicate_packet_ids"] == ["DUP"]
    assert len(inv["parse_failures"]) == 1
    assert result["data_quality_status"] == "BLOCKED"
    assert result["completion_percentage"] is None
    assert result["next_task"] == "REPAIR_CANONICAL_PACKET_INVENTORY"


def test_machine_readable_missing_packet_id_blocks_calculation(packet_repo: Path) -> None:
    write_json(packet_repo, "active", "missing.json", {"title": "Missing ID", "status": "active"})
    result = load_module().build_work_countdown(repo_root=packet_repo)
    inventory_state = result["canonical_work_packet_inventory"]
    assert inventory_state["inventory_status"] == "BLOCKED"
    assert inventory_state["missing_packet_ids"] == [
        "automation/orchestration/work_packets/active/missing.json"
    ]
    assert "machine_readable_packet_ids_missing" in inventory_state["data_quality_blockers"]
    assert result["completion_percentage"] is None


def test_empty_inventory_routes_registration(packet_repo: Path) -> None:
    result = load_module().build_work_countdown(repo_root=packet_repo)
    assert result["inventory_status"] == "EMPTY"
    assert result["evidence_status"] == "INCOMPLETE"
    assert result["completion_percentage"] is None
    assert result["next_task"] == "CREATE_OR_REGISTER_CANONICAL_WORK_PACKET"


def test_counts_are_bounded_and_blocked_gets_no_credit(packet_repo: Path) -> None:
    module = load_module()
    for index in range(2):
        write_json(packet_repo, "complete", f"c{index}.json", packet(f"C{index}", "complete"))
    write_json(packet_repo, "blocked", "b.json", packet("B", "blocked"))
    result = module.build_work_countdown(repo_root=packet_repo)
    assert result["total_packet_count"] == 3
    assert result["completed_packet_count"] == 2
    assert result["completed_packet_count"] <= result["total_packet_count"]
    assert 0 <= result["completion_percentage"] <= 100
    assert result["completion_percentage"] == 66.67


def test_paths_are_deterministic_and_source_files_are_not_modified(packet_repo: Path) -> None:
    module = load_module()
    later = write_json(packet_repo, "complete", "z.json", packet("Z", "complete"))
    earlier = write_json(packet_repo, "active", "a.json", packet("A", "active"))
    before = {path: path.read_bytes() for path in (later, earlier)}
    first = module.load_canonical_work_packet_inventory(packet_repo)
    second = module.load_canonical_work_packet_inventory(packet_repo)
    assert [item["source_path"] for item in first["records"]] == sorted(item["source_path"] for item in first["records"])
    assert module.stable_json(first) == module.stable_json(second)
    assert first["source_files_modified"] is False
    assert before == {path: path.read_bytes() for path in before}


def test_explicit_evidence_precedes_repo_and_selection_is_deterministic(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "complete", "ignored.json", packet("IGNORED", "complete"))
    evidence = inventory(packet("LOW", "ready", priority="low"), packet("HIGH", "ready", priority="high"))
    result = module.build_work_countdown(evidence, repo_root=packet_repo)
    assert result["next_task"]["packet_id"] == "HIGH"
    assert result["total_packet_count"] == 2


def test_telemetry_and_campaign_percentages_do_not_override_packet_math(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "active", "a.json", packet("A", "active"))
    write_json(packet_repo, "complete", "c.json", packet("C", "complete"))
    result = module.build_work_countdown(
        repo_root=packet_repo,
        repository_state={"stale_telemetry_completion_percentage": 99},
        campaign_registry_context={"completion_percentage": 87},
    )
    assert result["completion_percentage"] == 50.0
    assert result["campaign_registry_planning_context"]["completion_percentage"] == 87
    assert result["dependency_graph"]["unified_queue_index_projection"] == "READ_ONLY_PROJECTION"
    assert result["dependency_graph"]["campaign_registry_planning_context"] == "PLANNING_CONTEXT"


def test_external_provider_and_protected_actions_remain_separate(packet_repo: Path) -> None:
    write_json(packet_repo, "complete", "c.json", packet("C", "complete"))
    result = load_module().build_work_countdown(repo_root=packet_repo)
    provider = result["first_withdrawable_dollar_state"]
    assert provider["provider_status"] == "EXTERNAL_PENDING_VERIFICATION"
    assert provider["verification_state"] == "WAITING_FOR_REMOTE_EVIDENCE"
    assert result["external_wait_state"]["excluded_from_engineering_stages"] is True
    assert result["dependency_graph"]["first_withdrawable_dollar_external_provider"] == "EXTERNAL_PENDING"
    assert result["protected_actions"] and not any(result["protected_actions"].values())


def test_stable_json_serialization(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "complete", "c.json", packet("C", "complete"))
    result = module.build_work_countdown(repo_root=packet_repo)
    assert module.stable_json(result) == module.stable_json(result)
    assert json.loads(module.stable_json(result))["schema"] == "AIOS_WORK_COUNTDOWN.v1"


def test_forecast_credits_only_merged_validated_receipts(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "complete", "landed.json", packet(
        "LANDED", "complete", engineering_hours={"low": 5, "best": 10, "high": 15},
    ))
    write_json(packet_repo, "active", "open.json", packet(
        "OPEN", "active", engineering_hours={"low": 10, "best": 20, "high": 30},
    ))
    receipts = {
        "LANDED": {"validation_status": "PASSED", "pr_status": "MERGED", "merged_at": "2026-07-01T00:00:00Z"},
        "OPEN": {"validation_status": "PASSED", "pr_status": "OPEN"},
    }
    result = module.build_work_countdown(repo_root=packet_repo, execution_receipts=receipts)
    assert result["engineering_hours_remaining"] == {"low": 10.0, "best": 20.0, "high": 30.0}
    assert result["hours_removed_by_this_workflow"] == {"low": 5.0, "best": 10.0, "high": 15.0}
    assert result["fifty_hour_work_weeks_remaining"] == {"low": 0.2, "best": 0.4, "high": 0.6}
    assert result["derived_completion_percentage"] == 33.33
    assert result["forecast_confidence"] == "HIGH"
    assert result["forecast"]["external_wait_time_included_in_engineering_hours"] is False
    assert result["hours_removed_by_latest_merged_workflow"]["packet_id"] == "LANDED"


def test_forecast_refuses_to_invent_missing_estimates(packet_repo: Path) -> None:
    write_json(packet_repo, "active", "unknown.json", packet("UNKNOWN", "active"))
    result = load_module().build_work_countdown(repo_root=packet_repo)
    assert result["engineering_hours_remaining"] is None
    assert result["derived_completion_percentage"] is None
    assert result["forecast_confidence"] == "LOW"
    assert result["forecast"]["packets_missing_engineering_hours"] == ["UNKNOWN"]
    assert result["owner_action"] == "Provide the verified First Withdrawable Dollar provider evidence."


def test_pert_shared_dependencies_versioning_and_low_confidence(packet_repo: Path) -> None:
    module = load_module()
    write_json(packet_repo, "active", "a.json", packet("A", "active"))
    write_json(packet_repo, "active", "b.json", packet("B", "active"))
    baseline = {
        "schema": "AIOS_ENGINEERING_HOUR_BASELINE.v1",
        "baseline_id": "BASELINE-1", "version": 1, "supersedes": None,
        "change_explanation": "Initial evidence-calibrated forecast.",
        "shared_dependency_catalog": {"COMMON": {"optimistic": 1, "most_likely": 2, "pessimistic": 7}},
        "packets": [
            {"packet_id": packet_id, "confidence": "LOW", "shared_dependency_ids": ["COMMON"],
             "engineering_hours": {"optimistic": 1, "most_likely": 4, "pessimistic": 7}}
            for packet_id in ("A", "B")
        ],
    }
    result = module.build_work_countdown(repo_root=packet_repo, engineering_hour_baseline=baseline)
    # Packet PERT is 4 hours each; the shared dependency PERT is 16/6 once, not once per packet.
    assert result["forecast"]["baseline_expected_engineering_hours"] == 10.67
    assert result["baseline_total_engineering_hours"] == {"low": 3.0, "best": 10.0, "high": 21.0}
    assert result["engineering_hour_baseline"]["version"] == 1
    assert result["engineering_hour_baseline"]["change_explanation"]
    assert result["forecast"]["confidence_score"] == 40.0
    assert result["forecast_confidence"] == "LOW"


def test_simulation_cannot_satisfy_anchor_and_protected_actions_stay_gated(packet_repo: Path) -> None:
    write_json(packet_repo, "active", "a.json", packet(
        "A", "active", engineering_hours={"low": 1, "best": 2, "high": 3},
    ))
    result = load_module().build_work_countdown(
        repo_root=packet_repo,
        first_withdrawable_dollar_state={"evidence_kind": "PAPER_SIMULATION", "anchor_satisfied": True},
    )
    assert result["first_withdrawable_dollar_state"]["anchor_satisfied"] is False
    assert result["next_verified_blocker"] == "GENUINE_DEMO_OR_BROKER_EVIDENCE_REQUIRED"
    assert result["protected_actions"] and not any(result["protected_actions"].values())
