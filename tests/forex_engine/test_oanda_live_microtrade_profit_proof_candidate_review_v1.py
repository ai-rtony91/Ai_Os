from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import (
    oanda_live_microtrade_profit_proof_candidate_review_v1 as review,
)
from scripts.forex_delivery import (
    run_oanda_live_microtrade_profit_proof_candidate_review_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation/forex_engine/"
    "oanda_live_microtrade_profit_proof_candidate_review_v1.py"
)
RUNNER_PATH = (
    REPO_ROOT
    / "scripts/forex_delivery/"
    "run_oanda_live_microtrade_profit_proof_candidate_review_v1.py"
)
TEST_PATH = (
    REPO_ROOT
    / "tests/forex_engine/"
    "test_oanda_live_microtrade_profit_proof_candidate_review_v1.py"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_V1.md"
)
MANUAL_REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_MANUAL_FINALIZATION_V1.md"
)

SAMPLE_CASES = (
    (
        "profit",
        review.build_sample_profit_review_input,
        review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW,
        review.PROFIT_PACKET_PREVIEW,
        "profit_proof_candidate_review",
        "single_profit_result_candidate_ready_for_owner_review",
        "weak_single_result_candidate",
        review.PROFIT_PROOF_CANDIDATE_SUMMARY,
        "not_statistically_valid_single_result",
        "evidence_depth_required_before_profitability_claim",
        review.EVIDENCE_DEPTH_NEXT_PACKET_PREVIEW,
        True,
        True,
        "single_result_not_statistical_profitability_proof",
    ),
    (
        "loss",
        review.build_sample_loss_review_input,
        review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE,
        review.LOSS_PACKET_PREVIEW,
        "loss_review_and_next_profit_candidate_gate",
        "blocked_not_profit_route_loss_review_required",
        "not_profit_candidate",
        "Loss route cannot be treated as a profit proof candidate.",
        "not_profit_route_not_profitability_proof",
        "route_to_loss_review_before_profit_candidate_review",
        review.LOSS_PACKET_PREVIEW,
        False,
        False,
        "non_profit_route_loss_review",
    ),
    (
        "breakeven",
        review.build_sample_breakeven_review_input,
        review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE,
        review.BREAKEVEN_PACKET_PREVIEW,
        "more_evidence_required",
        "breakeven_requires_more_evidence",
        "insufficient_single_result_candidate",
        "Breakeven route requires more evidence before profit proof review.",
        "not_statistically_valid_more_evidence_required",
        "more_evidence_required_before_profit_candidate_review",
        review.BREAKEVEN_PACKET_PREVIEW,
        False,
        True,
        "breakeven_requires_more_evidence",
    ),
    (
        "missing",
        review.build_sample_missing_owner_result_review_input,
        review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT,
        review.MISSING_OWNER_RESULT_PACKET_PREVIEW,
        "owner_result_evidence_required",
        "blocked_no_owner_result_payload",
        "no_candidate_without_owner_result",
        "Missing owner-result evidence blocks profit proof candidate review.",
        "not_valid_no_owner_result",
        "owner_result_evidence_required_before_review",
        review.MISSING_OWNER_RESULT_PACKET_PREVIEW,
        False,
        False,
        "owner_result_payload_missing",
    ),
    (
        "unsafe",
        review.build_sample_unsafe_review_input,
        review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_UNSAFE,
        review.UNSAFE_PACKET_PREVIEW,
        "unsafe_result_repair",
        "blocked_unsafe_result_material",
        "unsafe_not_a_candidate",
        "Unsafe result material blocks profit proof candidate review.",
        "not_valid_unsafe_result_material",
        "unsafe_result_repair_required_before_review",
        review.UNSAFE_PACKET_PREVIEW,
        False,
        False,
        "unsafe_result_material_blocks_profit_proof_review",
    ),
)

REQUIRED_RESULT_FIELDS = (
    "version",
    "packet_id",
    "classification",
    "source_catalog_status",
    "source_selected_packet_preview",
    "source_selected_packet_title",
    "source_selected_packet_purpose",
    "source_selected_packet_non_execution_notice",
    "source_selected_packet_blocked_actions",
    "candidate_review_lane",
    "candidate_review_status",
    "candidate_strength_label",
    "proof_candidate_summary",
    "statistical_validity_status",
    "evidence_depth_status",
    "evidence_depth_next_packet_preview",
    "owner_review_required",
    "single_result_candidate",
    "evidence_depth_required",
    "preview_only",
    "review_only",
    "execution_blocked",
    "blocked_items",
    "proof_warning",
    "statistical_warning",
    "exact_next_owner_action",
    "exact_next_codex_packet_policy",
    "one_sentence_answer",
    "next_safe_action",
    "protected_flags",
) + review.PROTECTED_FLAG_NAMES

REPORT_SAFETY_PHRASES = (
    "No trade placed by this packet.",
    "No broker call was made by this packet.",
    "No credential access occurred.",
    "No account ID was persisted.",
    "No broker order ID was persisted.",
    "No raw broker payload was persisted.",
    "No live approval was granted.",
    "No repeat trading approval was granted.",
    "No next trade approval was granted.",
    "No selected packet execution approval was granted.",
    "No selected packet commit approval was granted.",
    "No selected packet push approval was granted.",
    "No selected packet PR approval was granted.",
    "No selected packet merge approval was granted.",
    "No real money approval was granted.",
    "No compounding approval was granted.",
    "No bank movement approval was granted.",
    "No autonomous execution was granted.",
    "Unattended vacation mode remains blocked.",
    "Vacation profit trial remains blocked unless Anthony separately approves.",
    "Profit is not guaranteed.",
    "One result does not prove statistical profitability.",
    "Single-result proof candidate is weak evidence.",
    "Evidence depth is required before any profitability claim.",
    "All protected flags remain false.",
    "Profit proof candidate review only.",
    "Read-only only.",
)


def _result(builder=review.build_sample_profit_review_input):
    return review.review_oanda_live_microtrade_profit_proof_candidate(builder())


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "packet",
        "lane",
        "status",
        "strength",
        "summary",
        "statistical_status",
        "evidence_status",
        "evidence_packet",
        "single_result",
        "evidence_required",
        "blocked_item",
    ),
    SAMPLE_CASES,
)
def test_review_mapping(
    name,
    builder,
    classification,
    packet,
    lane,
    status,
    strength,
    summary,
    statistical_status,
    evidence_status,
    evidence_packet,
    single_result,
    evidence_required,
    blocked_item,
):
    result = _result(builder)
    assert result.classification == classification
    assert result.source_selected_packet_preview == packet
    assert result.candidate_review_lane == lane
    assert result.candidate_review_status == status


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "packet",
        "lane",
        "status",
        "strength",
        "summary",
        "statistical_status",
        "evidence_status",
        "evidence_packet",
        "single_result",
        "evidence_required",
        "blocked_item",
    ),
    SAMPLE_CASES,
)
def test_candidate_details(
    name,
    builder,
    classification,
    packet,
    lane,
    status,
    strength,
    summary,
    statistical_status,
    evidence_status,
    evidence_packet,
    single_result,
    evidence_required,
    blocked_item,
):
    result = _result(builder)
    assert result.candidate_strength_label == strength
    assert result.proof_candidate_summary == summary
    assert result.statistical_validity_status == statistical_status
    assert result.evidence_depth_status == evidence_status
    assert result.evidence_depth_next_packet_preview == evidence_packet


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "packet",
        "lane",
        "status",
        "strength",
        "summary",
        "statistical_status",
        "evidence_status",
        "evidence_packet",
        "single_result",
        "evidence_required",
        "blocked_item",
    ),
    SAMPLE_CASES,
)
def test_candidate_boolean_details(
    name,
    builder,
    classification,
    packet,
    lane,
    status,
    strength,
    summary,
    statistical_status,
    evidence_status,
    evidence_packet,
    single_result,
    evidence_required,
    blocked_item,
):
    result = _result(builder)
    assert result.single_result_candidate is single_result
    assert result.evidence_depth_required is evidence_required
    assert result.owner_review_required is True
    assert result.preview_only is True
    assert result.review_only is True
    assert result.execution_blocked is True
    assert blocked_item in result.blocked_items


def test_profit_review_selects_profit_proof_candidate_review():
    assert _result().candidate_review_lane == "profit_proof_candidate_review"


def test_profit_review_classification_ready_for_owner_review():
    assert (
        _result().classification
        == review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW
    )


def test_profit_candidate_strength_is_weak_single_result():
    assert _result().candidate_strength_label == "weak_single_result_candidate"


def test_profit_candidate_not_statistically_valid():
    assert _result().statistical_validity_status == "not_statistically_valid_single_result"


def test_profit_review_routes_to_evidence_depth_plan():
    assert _result().evidence_depth_next_packet_preview == review.EVIDENCE_DEPTH_NEXT_PACKET_PREVIEW


def test_loss_route_blocks_as_not_profit_route():
    result = _result(review.build_sample_loss_review_input)
    assert (
        result.classification
        == review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE
    )
    assert "non_profit_route_loss_review" in result.blocked_items


def test_breakeven_route_requires_more_evidence():
    result = _result(review.build_sample_breakeven_review_input)
    assert (
        result.classification
        == review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE
    )
    assert "breakeven_requires_more_evidence" in result.blocked_items


def test_missing_route_blocks_no_owner_result():
    result = _result(review.build_sample_missing_owner_result_review_input)
    assert (
        result.classification
        == review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT
    )
    assert "owner_result_payload_missing" in result.blocked_items


def test_unsafe_route_blocks_unsafe():
    result = _result(review.build_sample_unsafe_review_input)
    assert (
        result.classification
        == review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_UNSAFE
    )
    assert "unsafe_result_material_blocks_profit_proof_review" in result.blocked_items


def test_exact_next_owner_action_present():
    assert _result().exact_next_owner_action == review.EXACT_NEXT_OWNER_ACTION


def test_exact_next_codex_packet_policy_present():
    assert _result().exact_next_codex_packet_policy == review.EXACT_NEXT_CODEX_PACKET_POLICY


def test_one_sentence_answer_exact():
    assert _result().one_sentence_answer == review.ONE_SENTENCE_ANSWER


def test_proof_warning_present():
    assert _result().proof_warning == review.PROOF_WARNING


def test_statistical_warning_present():
    assert _result().statistical_warning == review.STATISTICAL_WARNING


def test_evidence_depth_status_present():
    assert _result().evidence_depth_status == "evidence_depth_required_before_profitability_claim"


def test_evidence_depth_next_packet_preview_present():
    assert _result().evidence_depth_next_packet_preview == review.EVIDENCE_DEPTH_NEXT_PACKET_PREVIEW


@pytest.mark.parametrize("builder", tuple(case[1] for case in SAMPLE_CASES))
def test_json_serializable_outputs(builder):
    json.dumps(review.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize("builder", tuple(case[1] for case in SAMPLE_CASES))
def test_deterministic_outputs(builder):
    assert review.to_jsonable_dict(_result(builder)) == review.to_jsonable_dict(
        _result(builder)
    )


def test_markdown_output():
    text = review.to_markdown(_result())
    assert "# AIOS Forex OANDA Live Microtrade Profit Proof Candidate Review V1" in text
    assert review.EVIDENCE_DEPTH_NEXT_PACKET_PREVIEW in text


def test_operator_text_output():
    text = review.to_operator_text(_result())
    assert "Profit proof candidate review status" in text
    assert review.ONE_SENTENCE_ANSWER in text


@pytest.mark.parametrize("field_name", REQUIRED_RESULT_FIELDS)
def test_required_result_fields_present(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", review.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_in_map(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize("flag_name", review.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_on_result(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    "flag_name",
    (
        "next_trade_authorized",
        "selected_packet_execution_authorized",
        "selected_packet_commit_authorized",
        "selected_packet_push_authorized",
        "selected_packet_pr_authorized",
        "selected_packet_merge_authorized",
        "result_proves_profitability",
        "statistical_profitability_confirmed",
        "profit_proof_validated_as_statistical",
        "future_profit_claim_allowed",
        "live_execution_allowed",
        "repeat_live_trade_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "unattended_vacation_mode_allowed",
    ),
)
def test_high_risk_flags_false(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    ("field_name", "expected"),
    (
        ("preview_only", True),
        ("review_only", True),
        ("owner_review_required", True),
        ("single_result_candidate", True),
        ("evidence_depth_required", True),
        ("execution_blocked", True),
    ),
)
def test_profit_descriptive_flags(field_name: str, expected: bool):
    assert getattr(_result(), field_name) is expected


@pytest.mark.parametrize("blocked_item", review.BASE_BLOCKED_ITEMS)
def test_base_blocked_items_present(blocked_item: str):
    assert blocked_item in _result().blocked_items


@pytest.mark.parametrize(
    "fragment",
    (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "import subprocess",
        "from oanda",
        "import oanda",
        "broker_mutation",
        "oanda_trade_execution",
        "oanda_execution",
        "broker_execution",
        "def place_order",
        "def submit_order",
        "def execute_order",
        "live_execution_allowed=True",
        "repeat_live_trade_allowed=True",
        "next_trade_authorized=True",
        "selected_packet_execution_authorized=True",
        "selected_packet_commit_authorized=True",
        "selected_packet_push_authorized=True",
        "selected_packet_pr_authorized=True",
        "selected_packet_merge_authorized=True",
        "compounding_allowed=True",
        "bank_movement_allowed=True",
        "statistical_profitability_confirmed=True",
        "future_profit_claim_allowed=True",
    ),
)
def test_static_safety_no_forbidden_fragments_in_module(fragment: str):
    assert fragment not in MODULE_PATH.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize(
    "fragment",
    (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "import subprocess",
        "def place_order",
        "def submit_order",
        "def execute_order",
        ".env",
    ),
)
def test_static_safety_no_forbidden_fragments_in_runner(fragment: str):
    assert fragment not in RUNNER_PATH.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize(
    "path", (MODULE_PATH, RUNNER_PATH, TEST_PATH, REPORT_PATH, MANUAL_REPORT_PATH)
)
def test_created_paths_exist(path: Path):
    assert path.exists()


@pytest.mark.parametrize("phrase", REPORT_SAFETY_PHRASES)
def test_report_required_safety_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "heading",
    (
        "# AIOS Forex OANDA Live Microtrade Profit Proof Candidate Review V1",
        "## Packet ID",
        "## Source Chain Read",
        "## Files Created",
        "## Review Classifications",
        "## Review Mapping",
        "## Profit Review Sample",
        "## Loss Route Sample",
        "## Breakeven Route Sample",
        "## Missing Owner Result Sample",
        "## Unsafe Route Sample",
        "## Exact Next Owner Action",
        "## Exact Next Codex Packet Policy",
        "## Protected Flags",
        "## Blocked Actions",
        "## Evidence Depth Next Packet Preview",
        "## Safety Boundary",
        "## Validators Run",
        "## Validators Passed",
        "## Validators Failed",
        "## Git Status If Available",
        "## Next Safe Action",
    ),
)
def test_report_required_sections(heading: str):
    assert heading in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "command",
    (
        "python -m py_compile automation/forex_engine/oanda_live_microtrade_profit_proof_candidate_review_v1.py scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_candidate_review_v1.py tests/forex_engine/test_oanda_live_microtrade_profit_proof_candidate_review_v1.py",
        "python -m pytest tests/forex_engine/test_oanda_live_microtrade_profit_proof_candidate_review_v1.py -q",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_candidate_review_v1.py --sample-profit --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_candidate_review_v1.py --sample-loss --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_candidate_review_v1.py --sample-breakeven --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_candidate_review_v1.py --sample-missing --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_candidate_review_v1.py --sample-unsafe --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_candidate_review_v1.py --sample-profit --markdown",
        "git diff --check",
        "git status --short --branch",
    ),
)
def test_manual_report_commands(command: str):
    assert command in MANUAL_REPORT_PATH.read_text(encoding="utf-8")


def test_manual_report_says_do_not_compile_markdown_reports():
    assert (
        "Do not include Markdown report files in python -m py_compile."
        in MANUAL_REPORT_PATH.read_text(encoding="utf-8")
    )


@pytest.mark.parametrize(
    ("argv", "expected"),
    (
        (
            ["runner", "--sample-profit", "--json"],
            review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW,
        ),
        (
            ["runner", "--sample-loss", "--json"],
            review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE,
        ),
        (
            ["runner", "--sample-breakeven", "--json"],
            review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE,
        ),
        (
            ["runner", "--sample-missing", "--json"],
            review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT,
        ),
        (
            ["runner", "--sample-unsafe", "--json"],
            review.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_UNSAFE,
        ),
        (
            ["runner", "--sample-profit", "--markdown"],
            "# AIOS Forex OANDA Live Microtrade Profit Proof Candidate Review V1",
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert run_oanda_live_microtrade_profit_proof_candidate_review_v1.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize(
    "phrase",
    (
        "profit_proof_candidate_review -> weak single-result profit proof candidate review",
        "loss_review_and_next_profit_candidate_gate -> blocked not-profit route",
        "more_evidence_required -> breakeven requires more evidence",
        "owner_result_evidence_required -> blocked missing owner result",
        "unsafe_result_repair -> blocked unsafe result repair",
    ),
)
def test_report_review_mapping_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "phrase",
    (
        "One captured profit result can be reviewed as a proof candidate only.",
        "One profit result does not prove repeatable edge or statistical profitability.",
        "Profit candidate review does not approve another trade.",
        "Loss route cannot be treated as a profit proof candidate.",
        "Breakeven route requires more evidence before profit proof review.",
        "Missing owner-result evidence blocks profit proof candidate review.",
        "Unsafe result material blocks profit proof candidate review.",
        review.ONE_SENTENCE_ANSWER,
        review.EXACT_NEXT_OWNER_ACTION,
        review.EXACT_NEXT_CODEX_PACKET_POLICY,
    ),
)
def test_report_review_required_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", review.PROTECTED_FLAG_NAMES)
def test_report_protected_flags(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", review.BASE_BLOCKED_ITEMS)
def test_report_blocked_actions(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "builder",
    (
        review.build_sample_profit_review_input,
        review.build_sample_loss_review_input,
        review.build_sample_breakeven_review_input,
        review.build_sample_missing_owner_result_review_input,
        review.build_sample_unsafe_review_input,
    ),
)
@pytest.mark.parametrize("flag_name", review.PROTECTED_FLAG_NAMES)
def test_all_sample_routes_keep_protected_flags_false(builder, flag_name: str):
    result = _result(builder)
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "builder",
    (
        review.build_sample_profit_review_input,
        review.build_sample_loss_review_input,
        review.build_sample_breakeven_review_input,
        review.build_sample_missing_owner_result_review_input,
        review.build_sample_unsafe_review_input,
    ),
)
@pytest.mark.parametrize(
    "field_name",
    ("preview_only", "review_only", "owner_review_required", "execution_blocked"),
)
def test_all_sample_routes_keep_review_descriptive_flags_true(builder, field_name: str):
    assert getattr(_result(builder), field_name) is True
