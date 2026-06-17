import json
from copy import deepcopy
from pathlib import Path

from automation.orchestration.autonomy_chain_report import build_operator_chain_report

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


def _chain_result(verdict="CHAIN_HUMAN_APPROVAL_REQUIRED"):
    chain_state = {
        "CHAIN_HUMAN_APPROVAL_REQUIRED": "WAITING_FOR_HUMAN_APPROVAL",
        "CHAIN_APPLY_REVIEW_READY": "HUMAN_APPLY_REVIEW_READY",
        "CHAIN_REVIEW_COMPLETE": "REVIEW_COMPLETE",
        "BLOCKED_CHAIN_COMPONENT_FAILURE": "BLOCKED",
    }.get(verdict, "REVIEW_REQUIRED")
    first_blocking_component = "plan" if verdict.startswith("BLOCKED") else None
    component_verdicts = {
        "readiness": "READY_FOR_DRY_RUN_ONLY",
        "plan": "PLAN_READY_DRY_RUN_PREVIEW",
        "dry_run_execution": "DRY_RUN_SIMULATION_COMPLETE",
        "apply_gate": "HUMAN_APPROVAL_REQUIRED",
        "review_loop": "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY",
    }
    if verdict == "CHAIN_APPLY_REVIEW_READY":
        component_verdicts["apply_gate"] = "APPLY_REVIEW_READY"
        component_verdicts["review_loop"] = "REVIEW_COMPLETE_NO_ACTION"
    if verdict == "CHAIN_REVIEW_COMPLETE":
        component_verdicts["apply_gate"] = "SCOPE_REVIEW_COMPLETE"
        component_verdicts["review_loop"] = "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY"
    if verdict.startswith("BLOCKED"):
        component_verdicts["plan"] = "BLOCKED_SCOPE_UNKNOWN"
    result = {
        "schema": "AIOS_SELF_AUTONOMY_CHAIN_HARNESS.v1",
        "generated_at_utc": NOW,
        "component": "self_autonomy_chain_harness",
        "mode": "READ_ONLY_CHAIN_INTEGRATION_HARNESS",
        "chain_id": "chain-test",
        "verdict": verdict,
        "chain_state": chain_state,
        "goal": "Inspect safe chain status.",
        "first_blocking_component": first_blocking_component,
        "component_verdicts": component_verdicts,
        "component_states": {
            "readiness": "DRY_RUN_READY",
            "plan": "DRY_RUN_PREVIEW_READY",
            "dry_run_execution": "SIMULATION_COMPLETE",
            "apply_gate": "WAITING_FOR_HUMAN_APPROVAL",
            "review_loop": "RECOMMENDATIONS_ONLY",
        },
        "human_approval_required": True,
        "explicit_human_approval_present": verdict == "CHAIN_APPLY_REVIEW_READY",
        "apply_review_ready": verdict == "CHAIN_APPLY_REVIEW_READY",
        "blockers": ["scope_unknown"] if verdict.startswith("BLOCKED") else [],
        "evidence_inputs": [],
        "next_safe_action": "Request human review before future action.",
        "safety": {"read_only": True},
    }
    for field in HARD_FALSE_FIELDS:
        result[field] = False
        result["safety"][field] = False
    return result


def _assert_hard_safety_false(result):
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_human_approval_chain_produces_human_approval_report():
    result = build_operator_chain_report(_chain_result("CHAIN_HUMAN_APPROVAL_REQUIRED"), now_utc=NOW)

    assert result["verdict"] == "REPORT_HUMAN_APPROVAL_REQUIRED"
    assert result["inherited_chain_verdict"] == "CHAIN_HUMAN_APPROVAL_REQUIRED"
    _assert_hard_safety_false(result)


def test_apply_review_ready_chain_produces_apply_review_report():
    result = build_operator_chain_report(_chain_result("CHAIN_APPLY_REVIEW_READY"), now_utc=NOW)

    assert result["verdict"] == "REPORT_APPLY_REVIEW_READY"
    assert result["apply_review_ready"] is True
    assert result["apply_allowed"] is False


def test_review_complete_chain_produces_review_complete_report():
    result = build_operator_chain_report(_chain_result("CHAIN_REVIEW_COMPLETE"), now_utc=NOW)

    assert result["verdict"] == "REPORT_CHAIN_REVIEW_COMPLETE"


def test_blocked_chain_verdict_produces_blocked_chain_report():
    result = build_operator_chain_report(_chain_result("BLOCKED_CHAIN_COMPONENT_FAILURE"), now_utc=NOW)

    assert result["verdict"] == "REPORT_BLOCKED_CHAIN"
    assert result["first_blocking_component"] == "plan"


def test_missing_chain_result_blocks():
    result = build_operator_chain_report(None, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_RESULT_MISSING"
    _assert_hard_safety_false(result)


def test_malformed_chain_result_blocks():
    result = build_operator_chain_report({}, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_CHAIN_RESULT_MALFORMED"


def test_unsafe_terms_block_content():
    chain_result = _chain_result()
    chain_result["note"] = "secret material"

    result = build_operator_chain_report(chain_result, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_UNSAFE_CONTENT"


def test_codex_marker_blocks_executable_content():
    chain_result = _chain_result()
    chain_result["note"] = "CODEX-ONLY PROMPT"

    result = build_operator_chain_report(chain_result, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"


def test_execution_token_blocks_executable_content():
    chain_result = _chain_result()
    chain_result["note"] = "AI_OS EXECUTION TOKEN"

    result = build_operator_chain_report(chain_result, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"


def test_executable_true_blocks_executable_content():
    chain_result = _chain_result()
    chain_result["executable"] = True

    result = build_operator_chain_report(chain_result, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_EXECUTABLE_CONTENT"


def test_hard_safety_true_blocks_report():
    chain_result = _chain_result()
    chain_result["apply_allowed"] = True

    result = build_operator_chain_report(chain_result, now_utc=NOW)

    assert result["verdict"] == "BLOCKED_HARD_SAFETY_VIOLATION"
    assert result["apply_allowed"] is False


def test_report_markdown_includes_required_operator_fields():
    result = build_operator_chain_report(_chain_result("BLOCKED_CHAIN_COMPONENT_FAILURE"), now_utc=NOW)
    markdown = result["report_markdown"]

    assert "Chain verdict: BLOCKED_CHAIN_COMPONENT_FAILURE" in markdown
    assert "First blocking component: plan" in markdown
    assert "Next safe action: Request human review before future action." in markdown
    assert "Hard safety all false: True" in markdown


def test_report_markdown_contains_no_executable_commands():
    markdown = build_operator_chain_report(_chain_result(), now_utc=NOW)["report_markdown"].lower()

    assert "git add" not in markdown
    assert "git commit" not in markdown
    assert "git push" not in markdown
    assert "python -m" not in markdown
    assert "powershell" not in markdown


def test_output_never_contains_executable_markers():
    chain_result = _chain_result()
    chain_result["note"] = "CODEX-ONLY PROMPT"
    result = build_operator_chain_report(chain_result, now_utc=NOW)
    rendered = json.dumps(result, sort_keys=True)

    assert "CODEX-ONLY PROMPT" not in rendered
    assert "AI_OS EXECUTION TOKEN" not in rendered


def test_hard_safety_booleans_remain_false_for_every_report_verdict():
    cases = [
        _chain_result("CHAIN_HUMAN_APPROVAL_REQUIRED"),
        _chain_result("CHAIN_APPLY_REVIEW_READY"),
        _chain_result("CHAIN_REVIEW_COMPLETE"),
        _chain_result("BLOCKED_CHAIN_COMPONENT_FAILURE"),
        None,
        {},
    ]

    for chain_result in cases:
        result = build_operator_chain_report(chain_result, now_utc=NOW)
        _assert_hard_safety_false(result)


def test_report_id_is_deterministic_for_same_input():
    chain_result = _chain_result()

    one = build_operator_chain_report(deepcopy(chain_result), now_utc=NOW)
    two = build_operator_chain_report(deepcopy(chain_result), now_utc=NOW)

    assert one["report_id"] == two["report_id"]


def test_schema_contains_required_top_level_fields():
    schema = json.loads(
        Path("schemas/aios/orchestration/AIOS_OPERATOR_CHAIN_REPORT.v1.schema.json").read_text(encoding="utf-8")
    )
    required = set(schema["required"])

    for field in (
        "schema",
        "generated_at_utc",
        "component",
        "mode",
        "report_id",
        "verdict",
        "report_state",
        "inherited_chain_id",
        "inherited_chain_verdict",
        "inherited_chain_state",
        "first_blocking_component",
        "human_approval_required",
        "explicit_human_approval_present",
        "apply_review_ready",
        "hard_safety_all_false",
        "component_verdicts",
        "component_states",
        "blockers",
        "report_json",
        "report_markdown",
        "next_safe_action",
        "safety",
    ):
        assert field in required


def test_report_json_contains_component_verdicts_and_states():
    result = build_operator_chain_report(_chain_result(), now_utc=NOW)

    assert result["report_json"]["component_verdicts"] == result["component_verdicts"]
    assert result["report_json"]["component_states"] == result["component_states"]
