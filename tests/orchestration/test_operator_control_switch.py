from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "operator" / "aios_operator_control_switch.py"
HUMAN_GATE_REPORT = REPO_ROOT / "Reports" / "human_gate" / "human_gate_packet_dogfood_report.json"
AUTONOMY_GAP_REPORT = REPO_ROOT / "Reports" / "autonomy_gap" / "autonomy_gap_reassessment_report.json"
P2_BRIDGE_REPORT = REPO_ROOT / "Reports" / "p2_enqueue_bridge" / "p2_enqueue_bridge_preview.json"
COMMAND_QUEUE = REPO_ROOT / "automation" / "orchestration" / "command_queue" / "AIOS_COMMAND_QUEUE.json"
WORKER_INBOX = REPO_ROOT / "automation" / "orchestration" / "workers" / "inbox" / "AIOS_WORKER_INBOX.json"
ACTIVE_PACKETS = REPO_ROOT / "automation" / "orchestration" / "work_packets" / "active"
APPROVAL_INBOX = REPO_ROOT / "automation" / "orchestration" / "approval_inbox"


def _load():
    spec = importlib.util.spec_from_file_location("aios_operator_control_switch_for_tests", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fingerprint(path: Path):
    if path.is_file():
        return ("file", path.read_bytes())
    if path.is_dir():
        entries = sorted(str(item.relative_to(path)) for item in path.rglob("*"))
        return ("dir", entries)
    return ("missing", None)


def _ready_evidence() -> dict:
    false_flags = {
        "approval_granted": False,
        "execution_allowed": False,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_launch_allowed": False,
        "runtime_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "worker_inbox_mutation_allowed": False,
        "active_packet_mutation_allowed": False,
        "command_queue_mutation_allowed": False,
        "telemetry_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "service_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
    }
    return {
        "human_gate_report": {
            "dogfood_status": "PASS",
            "mutation_check_status": "PASS",
            "queue_validation_summary": {"queue_validation_status": "PASS"},
            "runtime_proof_gate_summary": {"final_verdict": "READY_FOR_HUMAN_GATE"},
            "human_gate_packet_summary": {"packet_status": "READY_FOR_HUMAN_REVIEW"},
            "safe_next_action": "Operator review only.",
            "stop_condition": "Do not execute.",
            **false_flags,
        },
        "autonomy_gap_report": {
            "reassessment_status": "PASS",
            "p2_enqueue_bridge_readiness": {"status": "READY"},
            "live_execution_readiness": {"status": "BLOCKED"},
            "recommended_next_lanes": [{"lane_id": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1"}],
            "summary": {
                "recommended_next_lane": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
                "p2_enqueue_bridge_ready": "READY",
            },
            "safe_next_action": "Operator review only.",
            **false_flags,
        },
        "p2_bridge_report": {
            "bridge_status": "READY_FOR_DRY_RUN_PREVIEW",
            "validation": {"status": "PASS"},
            "summary": {"recommended_next_lane": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1"},
            "proposed_queue_item_preview": {
                "recommended_next_lane": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
                "enqueue_allowed": False,
                "canonical_queue_write_allowed": False,
                "worker_inbox_write_allowed": False,
                "active_packet_write_allowed": False,
                "dispatch_allowed": False,
                "apply_allowed": False,
                "runtime_execution_allowed": False,
                "scheduler_creation_allowed": False,
                "sos_allowed": False,
                "live_trading_allowed": False,
            },
            "safe_next_action": "Review the P2 preview.",
            "stop_condition": "Do not enqueue.",
            **false_flags,
        },
    }


def test_module_imports_cleanly():
    mod = _load()
    assert mod.SCHEMA == "AIOS_OPERATOR_CONTROL_SWITCH_REPORT.v1"
    assert mod.MODE == "DRY_RUN"
    assert mod.CONTROL_SURFACE == "operator_control_switch"


def test_current_repo_evidence_builds_blocked_operator_report(tmp_path):
    mod = _load()
    report = mod.build_operator_control_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "operator_control",
        now="2026-01-02T03:04:05Z",
        action="status",
    )
    assert report["control_status"] == "BLOCKED"
    assert report["validation"]["status"] == "PASS"
    assert report["action_allowed"] is True
    assert report["next_blocked_lane"]
    assert report["queue_mutation_allowed"] is False
    assert report["runtime_launch_allowed"] is False
    assert report["scheduler_creation_allowed"] is False
    assert report["sos_allowed"] is False
    assert report["live_trading_allowed"] is False
    assert report["protected_boundaries"]["canonical_queue_write_allowed"] is False
    assert report["protected_boundaries"]["worker_inbox_write_allowed"] is False


def test_safe_actions_are_allowed_without_mutation(tmp_path):
    mod = _load()
    for action in mod.SAFE_ACTIONS:
        report = mod.build_operator_control_report(
            repo_root=REPO_ROOT,
            output_dir=tmp_path / action,
            now="2026-01-02T03:04:05Z",
            action=action,
            evidence=_ready_evidence(),
        )
        assert report["control_status"] == "READY_FOR_OPERATOR_REVIEW"
        assert report["requested_action"] == action
        assert report["action_allowed"] is True
        assert report["action_mutates_state"] is False
        assert report["validation"]["status"] == "PASS"


def test_unsafe_actions_are_explicitly_rejected(tmp_path):
    mod = _load()
    for action in mod.UNSAFE_ACTIONS:
        report = mod.build_operator_control_report(
            repo_root=REPO_ROOT,
            output_dir=tmp_path / action,
            now="2026-01-02T03:04:05Z",
            action=action,
            evidence=_ready_evidence(),
        )
        assert report["control_status"] == "INVALID"
        assert report["requested_action"] == action
        assert report["action_allowed"] is False
        assert report["unsafe_action_rejected"] is True
        assert report["validation"]["status"] == "PASS"
        assert any(f"unsafe action rejected: {action}" == item for item in report["invalid_reasons"])


def test_missing_evidence_is_invalid_not_ready(tmp_path):
    mod = _load()
    report = mod.build_operator_control_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "Reports" / "operator_control",
        now="2026-01-02T03:04:05Z",
        action="inspect",
    )
    assert report["control_status"] == "INVALID"
    assert report["evidence_missing"] == ["human_gate_report", "autonomy_gap_report", "p2_bridge_report"]
    assert report["validation"]["status"] == "PASS"
    assert report["action_allowed"] is True


def test_control_switch_writes_only_operator_report_files(tmp_path):
    mod = _load()
    output_dir = tmp_path / "Reports" / "operator_control"
    report = mod.run_operator_control_switch(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-01-02T03:04:05Z",
        action="report",
    )
    json_path = output_dir / mod.REPORT_JSON_NAME
    md_path = output_dir / mod.REPORT_MD_NAME
    assert json_path.exists()
    assert md_path.exists()
    assert sorted(path.name for path in output_dir.iterdir()) == [
        mod.REPORT_JSON_NAME,
        mod.REPORT_MD_NAME,
    ]
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["summary"]["control_status"] == report["control_status"]
    assert "This report does not enqueue" in md_path.read_text(encoding="utf-8")


def test_control_switch_does_not_mutate_protected_runtime_paths(tmp_path):
    mod = _load()
    protected_paths = [COMMAND_QUEUE, WORKER_INBOX, ACTIVE_PACKETS, APPROVAL_INBOX]
    before = {str(path): _fingerprint(path) for path in protected_paths}
    report = mod.run_operator_control_switch(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "operator_control",
        now="2026-01-02T03:04:05Z",
        action="preview",
    )
    after = {str(path): _fingerprint(path) for path in protected_paths}
    assert before == after
    protected = report["protected_boundaries"]
    assert protected["canonical_queue_write_allowed"] is False
    assert protected["worker_inbox_write_allowed"] is False
    assert protected["active_packet_write_allowed"] is False
    assert protected["command_queue_write_allowed"] is False
    assert protected["approval_inbox_write_allowed"] is False


def test_validation_blocks_dangerous_tamper(tmp_path):
    mod = _load()
    report = mod.build_operator_control_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "operator_control",
        now="2026-01-02T03:04:05Z",
        action="status",
        evidence=_ready_evidence(),
    )
    tampered = deepcopy(report)
    tampered["queue_mutation_allowed"] = True
    tampered["protected_boundaries"]["runtime_launch_allowed"] = True
    validation = mod.validate_operator_control_report(tampered)
    assert validation["status"] == "BLOCK"
    assert any("queue_mutation_allowed" in blocker for blocker in validation["blockers"])
    assert any("protected_boundaries.runtime_launch_allowed" in blocker for blocker in validation["blockers"])


def test_cli_defaults_to_status_and_writes_report(tmp_path, monkeypatch, capsys):
    mod = _load()
    outdir = tmp_path / "Reports" / "operator_control"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aios_operator_control_switch",
            "--repo-root",
            str(REPO_ROOT),
            "--output-dir",
            str(outdir),
            "--now",
            "2026-01-02T03:04:05Z",
        ],
    )
    rc = mod.main()
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert rc == 0
    assert parsed["control_status"] == "BLOCKED"
    assert parsed["requested_action"] == "status"
    assert parsed["action_allowed"] is True
    assert (outdir / mod.REPORT_JSON_NAME).exists()
    assert (outdir / mod.REPORT_MD_NAME).exists()


def test_cli_rejects_unsafe_action_without_mutation(tmp_path, monkeypatch, capsys):
    mod = _load()
    outdir = tmp_path / "Reports" / "operator_control"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aios_operator_control_switch",
            "execute",
            "--repo-root",
            str(REPO_ROOT),
            "--output-dir",
            str(outdir),
            "--now",
            "2026-01-02T03:04:05Z",
        ],
    )
    rc = mod.main()
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert rc == 2
    assert parsed["control_status"] == "INVALID"
    assert parsed["requested_action"] == "execute"
    assert parsed["action_allowed"] is False
    assert parsed["unsafe_action_rejected"] is True
    assert (outdir / mod.REPORT_JSON_NAME).exists()


def test_required_evidence_files_exist():
    assert HUMAN_GATE_REPORT.exists()
    assert AUTONOMY_GAP_REPORT.exists()
    assert P2_BRIDGE_REPORT.exists()
