from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_forex_builder_roadmap.py"
ADAPTER_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_candidate_packet_evidence_adapter.py"
PLANNER_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_packet_queue_planner.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def roadmap_result() -> dict[str, object]:
    module = load_module("aios_forex_builder_roadmap", MODULE_PATH)
    return module.build_forex_builder_roadmap({})


def roadmap_candidates() -> list[dict[str, object]]:
    result = roadmap_result()
    candidates = result["roadmap_candidates"]
    assert isinstance(candidates, list)
    return candidates


def assert_preview_only(result: dict[str, object]) -> None:
    assert result["commands_executed"] == []
    assert result["files_written"] == []
    assert result["workers_dispatched"] is False
    assert result["queues_mutated"] is False
    assert result["approvals_mutated"] is False
    safety = result["safety"]
    assert isinstance(safety, dict)
    assert safety["preview_only"] is True
    assert safety["evidence_only"] is True
    assert safety["command_execution"] is False
    assert safety["filesystem_writes"] is False
    assert safety["reports_written"] is False
    assert safety["network_access"] is False


def test_roadmap_status_is_ready() -> None:
    result = roadmap_result()

    assert result["schema"] == "AIOS_FOREX_BUILDER_ROADMAP_CANDIDATE_SOURCE.v1"
    assert result["roadmap_status"] == "ready"


def test_today_goal_alignment_is_present_and_aligned() -> None:
    result = roadmap_result()

    alignment = result["today_goal_alignment"]
    assert isinstance(alignment, dict)
    assert alignment["aligned"] is True
    assert "industrial-grade forex trading bot builder" in alignment["milestone"]
    assert alignment["non_live_only"] is True


def test_roadmap_candidates_are_emitted() -> None:
    candidates = roadmap_candidates()

    assert len(candidates) == 5


def test_first_candidate_is_canonical_spec_packet() -> None:
    candidates = roadmap_candidates()

    assert candidates[0]["packet_id"] == "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
    assert candidates[0]["title"] == "Create canonical forex builder product spec"
    assert candidates[0]["lane"] == "forex-builder-spec"


def test_all_candidates_are_non_live() -> None:
    for candidate in roadmap_candidates():
        assert candidate["non_live_only"] is True
        assert candidate["broker_allowed"] is False
        assert candidate["live_trading_allowed"] is False
        assert candidate["credentials_allowed"] is False
        assert candidate["orders_allowed"] is False
        assert candidate["webhooks_allowed"] is False


def test_all_candidates_have_required_planner_fields() -> None:
    required_fields = {
        "packet_id",
        "title",
        "lane",
        "priority",
        "milestone_value",
        "risk_level",
        "status",
        "required_files",
        "validators",
    }

    for candidate in roadmap_candidates():
        assert required_fields.issubset(candidate)
        assert candidate["required_files"]
        assert candidate["validators"]


def test_forbidden_lanes_include_protected_boundaries() -> None:
    result = roadmap_result()
    forbidden_text = " ".join(result["forbidden_lanes"]).lower()

    for term in ("broker", "live", "orders", "secrets", "webhooks", "scheduler", "daemon"):
        assert term in forbidden_text


def test_next_recommended_candidate_is_canonical_spec_packet() -> None:
    result = roadmap_result()
    next_candidate = result["next_recommended_candidate"]

    assert isinstance(next_candidate, dict)
    assert next_candidate["packet_id"] == "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"


def test_output_is_compatible_with_candidate_adapter_and_packet_queue_planner() -> None:
    adapter = load_module("aios_candidate_packet_evidence_adapter", ADAPTER_PATH)
    planner = load_module("aios_packet_queue_planner", PLANNER_PATH)
    result = roadmap_result()

    adapter_result = adapter.build_candidate_packet_evidence(
        {"candidate_packets": result["roadmap_candidates"]}
    )
    plan = planner.build_packet_queue_planner(adapter_result["candidate_packets"])

    assert adapter_result["candidate_packets"][0]["packet_id"] == "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
    assert plan["queue_status"] == "selected"
    assert plan["selected_packet"]["packet_id"] == "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
    assert plan["codex_ready_packet_preview"]["packet_ready"] is True


def test_no_candidate_writes_to_broker_trading_credentials_order_webhook_paths() -> None:
    forbidden_segments = {"broker", "trading", "credentials", "credential", "order", "orders", "webhook", "webhooks"}

    for candidate in roadmap_candidates():
        for path in candidate["required_files"]:
            parts = str(path).replace("\\", "/").lower().split("/")
            assert not forbidden_segments.intersection(parts)


def test_no_candidate_allows_network() -> None:
    for candidate in roadmap_candidates():
        assert candidate["network_allowed"] is False


def test_no_candidate_allows_scheduler_or_daemon() -> None:
    for candidate in roadmap_candidates():
        assert candidate["scheduler_allowed"] is False
        assert candidate["daemon_allowed"] is False


def test_commands_executed_is_empty() -> None:
    assert roadmap_result()["commands_executed"] == []


def test_files_written_is_empty() -> None:
    assert roadmap_result()["files_written"] == []


def test_workers_dispatched_false() -> None:
    assert roadmap_result()["workers_dispatched"] is False


def test_queues_mutated_false() -> None:
    assert roadmap_result()["queues_mutated"] is False


def test_approvals_mutated_false() -> None:
    assert roadmap_result()["approvals_mutated"] is False


def test_safety_preview_only_true() -> None:
    assert_preview_only(roadmap_result())


def test_source_does_not_import_subprocess_network_or_file_write_tools() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden in ("subprocess", "socket", "urllib", "requests", "http", "pathlib", "os", "shutil"):
        assert forbidden not in import_lines
    for forbidden_call in ("open(", "Path(", "write_text(", "write_bytes("):
        assert forbidden_call not in source
