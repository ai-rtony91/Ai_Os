from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine.oanda_demo_expectancy_to_live_evidence_bundle_epic_v1 import (
    CLASSIFICATION_BLOCKED,
    CLASSIFICATION_READY_FOR_OWNER_REVIEW,
    CLASSIFICATION_REQUIRE_MORE_EVIDENCE,
    EXACT_NEXT_CODEX_PACKET,
    EXACT_NEXT_OWNER_ACTION,
    LIVE_GAP_WARNING,
    LIVE_PROFIT_STATUS,
    ONE_SENTENCE_ANSWER,
    OWNER_WARNING,
    PERMISSION_DEFAULTS,
    PROFIT_CLAIM_STATUS,
    VERSION,
    build_sample_blocked_expectancy_epic_input,
    build_sample_missing_live_evidence_epic_input,
    build_sample_partial_live_evidence_epic_input,
    build_sample_ready_live_gap_review_epic_input,
    build_sample_rejected_expectancy_blocked_input,
    build_sample_strong_expectancy_missing_live_evidence_input,
    build_sample_strong_expectancy_partial_live_evidence_input,
    build_sample_unsafe_expectancy_blocked_input,
    build_sample_unsafe_live_evidence_epic_input,
    build_sample_weak_expectancy_blocked_input,
    oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict,
    oanda_demo_expectancy_to_live_evidence_bundle_epic_to_markdown,
    oanda_demo_expectancy_to_live_evidence_bundle_epic_to_operator_text,
    run_oanda_demo_expectancy_to_live_evidence_bundle_epic,
)
from scripts.forex_delivery import (
    run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1 as epic_runner,
)
from scripts.forex_delivery import run_oanda_demo_expectancy_to_live_gap_mapper_v1 as mapper_runner
from scripts.forex_delivery import run_oanda_demo_live_evidence_requirement_matrix_v1 as matrix_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS = (
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAPPER_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_V1.md",
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_EPIC_REPORT_V1.md",
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_MANUAL_FINALIZATION_V1.md",
)


def _epic(builder):
    return run_oanda_demo_expectancy_to_live_evidence_bundle_epic(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (build_sample_missing_live_evidence_epic_input, CLASSIFICATION_REQUIRE_MORE_EVIDENCE),
        (build_sample_partial_live_evidence_epic_input, CLASSIFICATION_REQUIRE_MORE_EVIDENCE),
        (build_sample_ready_live_gap_review_epic_input, CLASSIFICATION_READY_FOR_OWNER_REVIEW),
        (build_sample_blocked_expectancy_epic_input, CLASSIFICATION_BLOCKED),
        (build_sample_unsafe_live_evidence_epic_input, CLASSIFICATION_BLOCKED),
    ),
)
def test_epic_sample_classifications(builder, classification: str):
    assert _epic(builder).classification == classification


def test_epic_version_constant():
    assert VERSION == "oanda_demo_expectancy_to_live_evidence_bundle_epic_v1"


@pytest.mark.parametrize(
    "field_name",
    (
        "one_sentence_answer",
        "expectancy_status",
        "requirement_matrix_status",
        "gap_mapper_status",
        "gap_gate_status",
        "requirement_count",
        "present_count",
        "missing_count",
        "blocked_count",
        "owner_action_required_count",
        "missing_items",
        "owner_action_required_items",
        "blocked_items",
        "live_evidence_bundle_preview",
        "owner_gap_review_allowed",
        "profit_claim_status",
        "live_profit_status",
        "exact_next_owner_action",
        "exact_next_codex_packet",
    ),
)
def test_epic_includes_required_top_level_fields(field_name: str):
    assert hasattr(_epic(build_sample_missing_live_evidence_epic_input), field_name)


def test_epic_missing_live_evidence_requires_more_evidence():
    assert _epic(build_sample_missing_live_evidence_epic_input).classification == CLASSIFICATION_REQUIRE_MORE_EVIDENCE


def test_epic_partial_live_evidence_requires_more_evidence():
    assert _epic(build_sample_partial_live_evidence_epic_input).classification == CLASSIFICATION_REQUIRE_MORE_EVIDENCE


def test_epic_ready_gap_review_ready_for_owner_review():
    assert _epic(build_sample_ready_live_gap_review_epic_input).classification == CLASSIFICATION_READY_FOR_OWNER_REVIEW


def test_epic_blocked_expectancy_blocked():
    assert _epic(build_sample_blocked_expectancy_epic_input).classification == CLASSIFICATION_BLOCKED


def test_epic_unsafe_blocked():
    assert _epic(build_sample_unsafe_live_evidence_epic_input).classification == CLASSIFICATION_BLOCKED


def test_epic_exact_one_sentence_answer_present():
    assert _epic(build_sample_ready_live_gap_review_epic_input).one_sentence_answer == ONE_SENTENCE_ANSWER


def test_epic_live_execution_allowed_false():
    assert _epic(build_sample_ready_live_gap_review_epic_input).live_execution_allowed is False


def test_epic_live_micro_trade_exception_allowed_false():
    assert _epic(build_sample_ready_live_gap_review_epic_input).live_micro_trade_exception_allowed is False


def test_epic_live_evidence_bundle_approved_false():
    assert _epic(build_sample_ready_live_gap_review_epic_input).live_evidence_bundle_approved is False


def test_epic_profit_claim_status_distinguishes_demo_proof_from_live_authority():
    assert _epic(build_sample_ready_live_gap_review_epic_input).profit_claim_status == PROFIT_CLAIM_STATUS


def test_epic_live_profit_status_blocked():
    assert _epic(build_sample_ready_live_gap_review_epic_input).live_profit_status == LIVE_PROFIT_STATUS


def test_epic_exact_next_owner_action_present():
    assert _epic(build_sample_ready_live_gap_review_epic_input).exact_next_owner_action == EXACT_NEXT_OWNER_ACTION


def test_epic_exact_next_codex_packet_present():
    assert _epic(build_sample_ready_live_gap_review_epic_input).exact_next_codex_packet == EXACT_NEXT_CODEX_PACKET


def test_epic_next_packet_is_assembler_not_live_execution():
    next_packet = _epic(build_sample_ready_live_gap_review_epic_input).exact_next_codex_packet
    assert next_packet == "AIOS-FOREX-OANDA-DEMO-LIVE-EVIDENCE-BUNDLE-ASSEMBLER-V1"
    assert "LIVE-EXECUTION" not in next_packet


def test_epic_says_ready_gap_review_is_not_live_approval():
    text = oanda_demo_expectancy_to_live_evidence_bundle_epic_to_operator_text(
        _epic(build_sample_ready_live_gap_review_epic_input)
    )
    assert "Ready gap review is not live approval." in text


def test_epic_says_no_broker_call_no_trade_placed():
    text = oanda_demo_expectancy_to_live_evidence_bundle_epic_to_operator_text(
        _epic(build_sample_ready_live_gap_review_epic_input)
    )
    assert "No broker call was made by this packet." in text
    assert "No trade placed by this packet." in text


def test_epic_json_serializable():
    json.dumps(oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(_epic(build_sample_ready_live_gap_review_epic_input)))


def test_epic_markdown_title():
    markdown = oanda_demo_expectancy_to_live_evidence_bundle_epic_to_markdown(
        _epic(build_sample_ready_live_gap_review_epic_input)
    )
    assert markdown.startswith("# OANDA Demo Expectancy To Live Evidence Bundle Epic Report V1")


def test_epic_operator_text_plain():
    text = oanda_demo_expectancy_to_live_evidence_bundle_epic_to_operator_text(
        _epic(build_sample_missing_live_evidence_epic_input)
    )
    assert "Expectancy-to-live evidence bundle epic status" in text


@pytest.mark.parametrize("flag", sorted(PERMISSION_DEFAULTS))
def test_epic_permissions_false(flag: str):
    assert _epic(build_sample_ready_live_gap_review_epic_input).protected_permission_flags[flag] is False


def test_epic_owner_warning_present():
    assert _epic(build_sample_missing_live_evidence_epic_input).owner_warning == OWNER_WARNING


def test_epic_live_gap_warning_present():
    assert _epic(build_sample_missing_live_evidence_epic_input).live_gap_warning == LIVE_GAP_WARNING


def test_epic_no_raw_account_data_appears_in_json():
    payload = json.dumps(oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(_epic(build_sample_ready_live_gap_review_epic_input)))
    assert "001-" not in payload


def test_epic_no_raw_credential_data_appears_in_json():
    payload = json.dumps(oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(_epic(build_sample_ready_live_gap_review_epic_input))).lower()
    assert "sk-" not in payload


def test_epic_no_raw_broker_order_id_appears_in_json():
    payload = json.dumps(oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(_epic(build_sample_ready_live_gap_review_epic_input))).lower()
    assert "orderid" not in payload


def test_epic_no_live_endpoint_text_appears_except_boundary_requirement():
    payload = json.dumps(oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(_epic(build_sample_ready_live_gap_review_epic_input))).lower()
    assert "api-fxtrade" not in payload


@pytest.mark.parametrize(
    "forbidden_true",
    (
        '"live_execution_allowed": true',
        '"live_micro_trade_exception_allowed": true',
        '"live_evidence_bundle_approved": true',
        '"real_money_allowed": true',
        '"compounding_allowed": true',
        '"bank_movement_allowed": true',
        '"autonomous_execution_allowed": true',
    ),
)
def test_epic_json_has_no_protected_true_flags(forbidden_true: str):
    payload = json.dumps(
        oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(
            _epic(build_sample_ready_live_gap_review_epic_input)
        )
    ).lower()
    assert forbidden_true not in payload


def test_epic_surfaces_evidence_gaps():
    result = _epic(build_sample_partial_live_evidence_epic_input)
    assert result.missing_items
    assert result.owner_action_required_items
    assert result.blocked_items


def test_epic_preview_is_preview_only():
    assert _epic(build_sample_ready_live_gap_review_epic_input).live_evidence_bundle_preview[
        "preview_only"
    ] is True


@pytest.mark.parametrize(
    "builder",
    (
        build_sample_strong_expectancy_missing_live_evidence_input,
        build_sample_strong_expectancy_partial_live_evidence_input,
        build_sample_weak_expectancy_blocked_input,
        build_sample_rejected_expectancy_blocked_input,
        build_sample_unsafe_expectancy_blocked_input,
    ),
)
def test_epic_global_sample_builders_exist(builder):
    assert builder()


@pytest.mark.parametrize(
    ("argv", "expected"),
    (
        (["runner"], "Live evidence requirement matrix status"),
        (["runner", "--json"], '"classification"'),
        (["runner", "--markdown"], "# OANDA Demo Live Evidence Requirement Matrix V1"),
    ),
)
def test_matrix_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert matrix_runner.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize(
    ("argv", "expected"),
    (
        (["runner"], "Expectancy-to-live gap map status"),
        (["runner", "--json"], '"classification"'),
        (["runner", "--markdown"], "# OANDA Demo Expectancy To Live Gap Mapper V1"),
    ),
)
def test_mapper_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert mapper_runner.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize(
    ("argv", "expected"),
    (
        (["runner"], "Expectancy-to-live evidence bundle epic status"),
        (["runner", "--json"], '"classification"'),
        (["runner", "--markdown"], "# OANDA Demo Expectancy To Live Evidence Bundle Epic Report V1"),
    ),
)
def test_epic_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert epic_runner.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize("report_path", REPORTS)
def test_required_reports_exist(report_path: Path):
    assert report_path.exists()


@pytest.mark.parametrize("report_path", REPORTS)
def test_reports_say_no_trade_placed(report_path: Path):
    assert "No trade placed by this packet." in report_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("report_path", REPORTS)
def test_reports_say_no_broker_call(report_path: Path):
    assert "No broker call was made by this packet." in report_path.read_text(encoding="utf-8")


def test_manual_finalization_report_has_exact_git_add_commands():
    text = REPORTS[-1].read_text(encoding="utf-8")
    assert "git add automation/forex_engine/oanda_demo_live_evidence_requirement_matrix_v1.py" in text
    assert "git add ." not in text


def test_epic_report_static_safety_says_pass():
    text = REPORTS[3].read_text(encoding="utf-8")
    assert "Static safety result: PASS" in text


def test_epic_report_records_source_files_read():
    text = REPORTS[3].read_text(encoding="utf-8")
    assert "Source files read" in text


def test_epic_report_records_source_files_missing():
    text = REPORTS[3].read_text(encoding="utf-8")
    assert "Source files missing" in text


def test_epic_report_includes_all_requirement_ids():
    text = REPORTS[3].read_text(encoding="utf-8")
    assert "human_owner_live_exception_approval" in text
    assert "evidence_bundle_owner_review_verified" in text


def test_gap_mapper_report_explains_gap_review_is_not_live_approval():
    text = REPORTS[1].read_text(encoding="utf-8")
    assert "ready gap review is still not live approval" in text.lower()


def test_gap_gate_report_says_live_approval_remains_false():
    text = REPORTS[2].read_text(encoding="utf-8")
    assert "live approval remains false" in text.lower()


def test_no_existing_evidence_bundle_file_is_mutated():
    manual = REPORTS[-1].read_text(encoding="utf-8")
    assert "docs/forex/LIVE_ARMING_EVIDENCE_BUNDLE_TEMPLATE.md" not in manual
