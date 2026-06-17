import json
from copy import deepcopy
from pathlib import Path

from automation.orchestration.autonomy_packet_draft import build_human_approved_packet_draft

NOW = "2026-01-01T00:00:00Z"
HARD_FALSE_FIELDS = (
    "self_approval_allowed",
    "apply_allowed",
    "apply_performed",
    "commands_executed",
    "files_written",
    "mutations_performed",
    "executable_packet_emitted",
    "execution_token_emitted",
    "codex_prompt_emitted",
    "worker_launch_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "broker_allowed",
    "live_trading_allowed",
    "production_allowed",
    "dashboard_mutation_allowed",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
)


def _operator_report(verdict="REPORT_HUMAN_APPROVAL_REQUIRED"):
    chain_verdict = {
        "REPORT_HUMAN_APPROVAL_REQUIRED": "CHAIN_HUMAN_APPROVAL_REQUIRED",
        "REPORT_APPLY_REVIEW_READY": "CHAIN_APPLY_REVIEW_READY",
        "REPORT_CHAIN_REVIEW_COMPLETE": "CHAIN_REVIEW_COMPLETE",
        "REPORT_BLOCKED_CHAIN": "BLOCKED_CHAIN_COMPONENT_FAILURE",
    }.get(verdict, "CHAIN_HUMAN_APPROVAL_REQUIRED")
    report = {
        "schema": "AIOS_OPERATOR_CHAIN_REPORT.v1",
        "generated_at_utc": NOW,
        "component": "operator_chain_report",
        "mode": "READ_ONLY_OPERATOR_CHAIN_REPORT",
        "report_id": "operator-chain-report-test",
        "verdict": verdict,
        "report_state": "HUMAN_APPROVAL_REQUIRED_REPORTED",
        "inherited_chain_id": "chain-test",
        "inherited_chain_verdict": chain_verdict,
        "inherited_chain_state": "WAITING_FOR_HUMAN_APPROVAL",
        "first_blocking_component": None,
        "human_approval_required": True,
        "explicit_human_approval_present": verdict == "REPORT_APPLY_REVIEW_READY",
        "apply_review_ready": verdict == "REPORT_APPLY_REVIEW_READY",
        "hard_safety_all_false": True,
        "component_verdicts": {
            "readiness": "READY_FOR_DRY_RUN_ONLY",
            "plan": "PLAN_READY_DRY_RUN_PREVIEW",
            "dry_run_execution": "DRY_RUN_SIMULATION_COMPLETE",
            "apply_gate": "HUMAN_APPROVAL_REQUIRED",
            "review_loop": "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY",
        },
        "component_states": {},
        "blockers": [],
        "report_json": {
            "chain_id": "chain-test",
            "chain_verdict": chain_verdict,
            "chain_state": "WAITING_FOR_HUMAN_APPROVAL",
            "allowed_paths": ["automation/orchestration/autonomy_packet_draft/"],
            "forbidden_paths": ["Reports/", "automation/orchestration/work_packets/"],
            "validator_chain": [
                "git diff --check",
                "python -m pytest tests/orchestration/test_aios_human_approved_packet_draft_generator.py -q",
            ],
            "mission_summary": "Review a safe packet draft object.",
            "rollback_note": "No mutation is performed by this draft.",
            "stop_point": "Stop after human review.",
        },
        "report_markdown": "# AIOS Operator Chain Report\n",
        "next_safe_action": "Request human review before future action.",
        "safety": {"read_only": True},
    }
    if verdict == "REPORT_BLOCKED_CHAIN":
        report["report_state"] = "CHAIN_BLOCKED_REPORTED"
        report["first_blocking_component"] = "plan"
        report["blockers"] = ["scope_unknown"]
    for field in HARD_FALSE_FIELDS:
        report[field] = False
        report["safety"][field] = False
    return report


def _assert_hard_safety_false(result):
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_human_approval_report_with_known_scope_returns_ready():
    result = build_human_approved_packet_draft(_operator_report(), now_utc=NOW)

    assert result["verdict"] == "PACKET_DRAFT_READY"
    assert result["packet_draft_created"] is True
    assert result["packet_draft"]["approval_required"] is True


def test_apply_review_report_still_generates_non_executable_draft():
    result = build_human_approved_packet_draft(_operator_report("REPORT_APPLY_REVIEW_READY"), now_utc=NOW)

    assert result["verdict"] == "PACKET_DRAFT_READY"
    assert result["packet_draft"]["suggested_mode"] == "APPLY_REVIEW"
    assert result["packet_draft"]["executable"] is False


def test_chain_review_complete_report_with_known_scope_returns_ready():
    result = build_human_approved_packet_draft(_operator_report("REPORT_CHAIN_REVIEW_COMPLETE"), now_utc=NOW)

    assert result["verdict"] == "PACKET_DRAFT_READY"


def test_missing_report_blocks():
    result = build_human_approved_packet_draft(None, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_OPERATOR_REPORT_MISSING"
    _assert_hard_safety_false(result)


def test_malformed_report_blocks():
    result = build_human_approved_packet_draft({}, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_OPERATOR_REPORT_MALFORMED"


def test_blocked_chain_report_is_not_ready():
    result = build_human_approved_packet_draft(_operator_report("REPORT_BLOCKED_CHAIN"), now_utc=NOW)

    assert result["verdict"] == "BLOCKED_OPERATOR_REPORT_NOT_READY"


def test_hard_safety_false_blocks():
    report = _operator_report()
    report["hard_safety_all_false"] = False

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_HARD_SAFETY_VIOLATION"


def test_missing_allowed_paths_blocks_scope_unknown():
    report = _operator_report()
    report["report_json"].pop("allowed_paths")

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_PACKET_SCOPE_UNKNOWN"


def test_missing_forbidden_paths_blocks_scope_unknown():
    report = _operator_report()
    report["report_json"].pop("forbidden_paths")

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_PACKET_SCOPE_UNKNOWN"


def test_missing_validator_chain_blocks_scope_unknown():
    report = _operator_report()
    report["report_json"].pop("validator_chain")

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_PACKET_SCOPE_UNKNOWN"


def test_unsafe_terms_block_content():
    report = _operator_report()
    report["note"] = "secret scheduler scope"

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_UNSAFE_CONTENT"


def test_codex_marker_blocks_executable_content():
    report = _operator_report()
    report["note"] = "CODEX-ONLY PROMPT"

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"


def test_execution_token_blocks_executable_content():
    report = _operator_report()
    report["note"] = "AI_OS EXECUTION TOKEN"

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"


def test_executable_true_blocks_executable_content():
    report = _operator_report()
    report["executable"] = True

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"


def test_packet_draft_executable_is_false():
    result = build_human_approved_packet_draft(_operator_report(), now_utc=NOW)

    assert result["packet_draft"]["executable"] is False


def test_packet_draft_execution_token_present_is_false():
    result = build_human_approved_packet_draft(_operator_report(), now_utc=NOW)

    assert result["packet_draft"]["execution_token_present"] is False


def test_packet_draft_codex_prompt_present_is_false():
    result = build_human_approved_packet_draft(_operator_report(), now_utc=NOW)

    assert result["packet_draft"]["codex_prompt_present"] is False


def test_output_never_contains_codex_marker():
    report = _operator_report()
    report["note"] = "CODEX-ONLY PROMPT"
    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert "CODEX-ONLY PROMPT" not in json.dumps(result, sort_keys=True)


def test_output_never_contains_execution_token():
    report = _operator_report()
    report["note"] = "AI_OS EXECUTION TOKEN"
    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert "AI_OS EXECUTION TOKEN" not in json.dumps(result, sort_keys=True)


def test_hard_safety_booleans_remain_false_in_every_verdict():
    reports = [
        _operator_report(),
        _operator_report("REPORT_APPLY_REVIEW_READY"),
        _operator_report("REPORT_CHAIN_REVIEW_COMPLETE"),
        _operator_report("REPORT_BLOCKED_CHAIN"),
        None,
        {},
    ]

    for report in reports:
        result = build_human_approved_packet_draft(report, now_utc=NOW)
        _assert_hard_safety_false(result)


def test_draft_id_is_deterministic_for_same_input():
    report = _operator_report()
    one = build_human_approved_packet_draft(deepcopy(report), now_utc=NOW)
    two = build_human_approved_packet_draft(deepcopy(report), now_utc=NOW)

    assert one["draft_id"] == two["draft_id"]


def test_schema_contains_required_top_level_fields():
    schema = json.loads(
        Path("schemas/aios/orchestration/AIOS_HUMAN_APPROVED_PACKET_DRAFT.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    required = set(schema["required"])

    for field in (
        "schema",
        "generated_at_utc",
        "component",
        "mode",
        "draft_id",
        "verdict",
        "draft_state",
        "source_report_id",
        "source_report_verdict",
        "source_chain_verdict",
        "source_chain_state",
        "packet_draft",
        "packet_draft_created",
        "non_executable_draft_only",
        "human_approval_required_before_execution",
        "blockers",
        "evidence_inputs",
        "next_safe_action",
        "safety",
    ):
        assert field in required


def test_safe_blocked_actions_with_git_words_do_not_trigger_unsafe_content():
    report = _operator_report()
    report["blocked_actions"] = ["commit", "push", "merge"]
    report["safety"]["blocked_actions"] = ["git commit", "git push", "merge"]

    result = build_human_approved_packet_draft(report, now_utc=NOW)

    assert result["verdict"] == "PACKET_DRAFT_READY"


def test_generator_source_does_not_write_files():
    source = Path(
        "automation/orchestration/autonomy_packet_draft/aios_human_approved_packet_draft_generator.py"
    ).read_text(encoding="utf-8")

    assert "write_text" not in source
    assert ".write(" not in source
    assert "open(" not in source
