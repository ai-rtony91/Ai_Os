import json
from pathlib import Path

import pytest

from automation.orchestration.autonomy_chain_report.aios_operator_chain_report_entrypoint import (
    ChainReportEntrypointError,
    load_chain_result_from_text,
    main,
    render_operator_chain_report,
)

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
    result = {
        "schema": "AIOS_SELF_AUTONOMY_CHAIN_HARNESS.v1",
        "generated_at_utc": NOW,
        "component": "self_autonomy_chain_harness",
        "mode": "READ_ONLY_CHAIN_INTEGRATION_HARNESS",
        "chain_id": "chain-entrypoint-test",
        "verdict": verdict,
        "chain_state": "WAITING_FOR_HUMAN_APPROVAL",
        "goal": "Inspect safe chain status.",
        "first_blocking_component": None,
        "component_verdicts": {
            "readiness": "READY_FOR_DRY_RUN_ONLY",
            "plan": "PLAN_READY_DRY_RUN_PREVIEW",
            "dry_run_execution": "DRY_RUN_SIMULATION_COMPLETE",
            "apply_gate": "HUMAN_APPROVAL_REQUIRED",
            "review_loop": "REVIEW_COMPLETE_RECOMMENDATIONS_ONLY",
        },
        "component_states": {
            "readiness": "DRY_RUN_READY",
            "plan": "DRY_RUN_PREVIEW_READY",
            "dry_run_execution": "SIMULATION_COMPLETE",
            "apply_gate": "WAITING_FOR_HUMAN_APPROVAL",
            "review_loop": "RECOMMENDATIONS_ONLY",
        },
        "human_approval_required": True,
        "explicit_human_approval_present": False,
        "apply_review_ready": False,
        "blockers": [],
        "evidence_inputs": [],
        "next_safe_action": "Request human review before future action.",
        "safety": {"read_only": True},
    }
    if verdict.startswith("BLOCKED"):
        result["chain_state"] = "BLOCKED"
        result["first_blocking_component"] = "plan"
        result["component_verdicts"]["plan"] = "BLOCKED_SCOPE_UNKNOWN"
        result["blockers"] = ["scope_unknown"]
    for field in HARD_FALSE_FIELDS:
        result[field] = False
        result["safety"][field] = False
    return result


def _write_json(tmp_path: Path, payload):
    path = tmp_path / "chain_result.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_render_json_returns_valid_json_report_for_safe_chain_result():
    rendered = render_operator_chain_report(_chain_result(), output_format="json", now_utc=NOW)
    report = json.loads(rendered)

    assert report["schema"] == "AIOS_OPERATOR_CHAIN_REPORT.v1"
    assert report["verdict"] == "REPORT_HUMAN_APPROVAL_REQUIRED"


def test_render_markdown_returns_markdown_string():
    rendered = render_operator_chain_report(_chain_result(), output_format="markdown", now_utc=NOW)

    assert rendered.startswith("# AIOS Operator Chain Report")
    assert "Report verdict: REPORT_HUMAN_APPROVAL_REQUIRED" in rendered


def test_unsupported_format_raises_controlled_failure():
    with pytest.raises(ChainReportEntrypointError) as excinfo:
        render_operator_chain_report(_chain_result(), output_format="bad", now_utc=NOW)

    assert excinfo.value.payload["verdict"] == "BLOCKED_UNSUPPORTED_FORMAT"


def test_load_chain_result_from_text_rejects_invalid_json():
    with pytest.raises(ChainReportEntrypointError) as excinfo:
        load_chain_result_from_text("{not json")

    assert excinfo.value.payload["verdict"] == "BLOCKED_INPUT_JSON_INVALID"


def test_main_with_no_input_exits_2_and_prints_missing(capsys):
    assert main([]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "BLOCKED_INPUT_SOURCE_MISSING"


def test_main_with_stdin_and_input_exits_2_and_prints_conflict(tmp_path, capsys):
    path = _write_json(tmp_path, _chain_result())

    assert main(["--stdin", "--input", str(path)]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "BLOCKED_INPUT_SOURCE_CONFLICT"


def test_main_input_json_exits_0_and_prints_json_report(tmp_path, capsys):
    path = _write_json(tmp_path, _chain_result())

    assert main(["--input", str(path), "--format", "json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "REPORT_HUMAN_APPROVAL_REQUIRED"


def test_main_input_markdown_exits_0_and_prints_markdown(tmp_path, capsys):
    path = _write_json(tmp_path, _chain_result())

    assert main(["--input", str(path), "--format", "markdown"]) == 0

    assert capsys.readouterr().out.startswith("# AIOS Operator Chain Report")


def test_main_input_invalid_json_exits_2_and_prints_invalid_json(tmp_path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text("{not json", encoding="utf-8")

    assert main(["--input", str(path)]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "BLOCKED_INPUT_JSON_INVALID"


def test_main_bad_format_exits_2_and_prints_unsupported(capsys):
    assert main(["--format", "bad"]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "BLOCKED_UNSUPPORTED_FORMAT"


def test_entrypoint_source_never_writes_files():
    source = Path(
        "automation/orchestration/autonomy_chain_report/aios_operator_chain_report_entrypoint.py"
    ).read_text(encoding="utf-8")

    assert "write_text" not in source
    assert ".write(" not in source
    assert "open(" not in source


def test_entrypoint_source_never_calls_subprocess():
    source = Path(
        "automation/orchestration/autonomy_chain_report/aios_operator_chain_report_entrypoint.py"
    ).read_text(encoding="utf-8")

    assert "subprocess" not in source


def test_output_never_contains_codex_marker():
    chain_result = _chain_result()
    chain_result["note"] = "CODEX-ONLY PROMPT"
    rendered = render_operator_chain_report(chain_result, output_format="json", now_utc=NOW)

    assert "CODEX-ONLY PROMPT" not in rendered


def test_output_never_contains_execution_token():
    chain_result = _chain_result()
    chain_result["note"] = "AI_OS EXECUTION TOKEN"
    rendered = render_operator_chain_report(chain_result, output_format="json", now_utc=NOW)

    assert "AI_OS EXECUTION TOKEN" not in rendered


def test_blocked_m17_report_exits_2(tmp_path, capsys):
    path = _write_json(tmp_path, _chain_result("BLOCKED_CHAIN_COMPONENT_FAILURE"))

    assert main(["--input", str(path)]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "REPORT_BLOCKED_CHAIN"


def test_safe_report_preserves_hard_safety_false_fields():
    rendered = render_operator_chain_report(_chain_result(), output_format="json", now_utc=NOW)
    report = json.loads(rendered)

    for field in HARD_FALSE_FIELDS:
        assert report[field] is False
        assert report["safety"][field] is False
