from __future__ import annotations

from automation.bridge.aios_approval_model import ApprovalRecord, compress_approval


def record(**overrides):
    data = {
        "approval_id": "approval-1",
        "source_packet_id": "packet-1",
        "created_utc": "2026-06-08T00:00:00Z",
        "operator": "Anthony",
        "decision": "approve",
        "mode_requested": "APPLY",
        "mode_allowed": "APPLY",
        "scope_summary": "Apply bounded local bridge changes.",
        "allowed_paths": ["automation/bridge/"],
        "forbidden_paths": ["AGENTS.md"],
        "protected_actions_detected": [],
        "approval_text": "Anthony explicitly approves APPLY for bounded local bridge changes.",
        "evidence_files": ["Reports/example.json"],
        "validator_chain": ["git diff --check"],
        "expires_utc": "",
        "status": "pending",
    }
    data.update(overrides)
    return ApprovalRecord.from_dict(data)


def test_valid_non_protected_apply_is_ready():
    assert compress_approval(record()).status == "APPLY_READY"


def test_missing_approval_text_waits():
    decision = compress_approval(record(approval_text=""))
    assert decision.status == "WAIT"


def test_protected_agents_edit_requires_approval():
    decision = compress_approval(
        record(
            allowed_paths=["AGENTS.md"],
            protected_actions_detected=["commit"],
            approval_text="Anthony explicitly approves APPLY for AGENTS.md edit.",
        )
    )
    assert decision.status == "REQUIRES_APPROVAL"


def test_live_trading_blocks():
    decision = compress_approval(record(scope_summary="Apply live trading broker execution."))
    assert decision.status == "BLOCKED"


def test_secret_handling_blocks():
    decision = compress_approval(record(scope_summary="Apply credential handling."))
    assert decision.status == "BLOCKED"


def test_placeholder_path_blocks():
    placeholder_path = "path/" + "to/file"
    decision = compress_approval(record(allowed_paths=[placeholder_path]))
    assert decision.status == "BLOCKED"


def test_commit_without_separate_approval_requires_approval():
    decision = compress_approval(record(protected_actions_detected=["commit"]))
    assert decision.status == "REQUIRES_APPROVAL"


def test_push_without_separate_approval_requires_approval():
    decision = compress_approval(record(protected_actions_detected=["push"]))
    assert decision.status == "REQUIRES_APPROVAL"


def test_stale_evidence_requires_approval():
    decision = compress_approval(record(expires_utc="2000-01-01T00:00:00Z"))
    assert decision.status == "REQUIRES_APPROVAL"


def test_missing_validator_chain_requires_approval():
    decision = compress_approval(record(validator_chain=[]))
    assert decision.status == "REQUIRES_APPROVAL"
