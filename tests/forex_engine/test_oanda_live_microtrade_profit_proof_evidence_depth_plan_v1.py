from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import (
    oanda_live_microtrade_profit_proof_evidence_depth_plan_v1 as depth_plan,
)
from scripts.forex_delivery import (
    run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation/forex_engine/"
    "oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py"
)
RUNNER_PATH = (
    REPO_ROOT
    / "scripts/forex_delivery/"
    "run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py"
)
TEST_PATH = (
    REPO_ROOT
    / "tests/forex_engine/"
    "test_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_V1.md"
)
MANUAL_REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_MANUAL_FINALIZATION_V1.md"
)

SAMPLE_CASES = (
    (
        "profit",
        depth_plan.build_sample_profit_depth_plan_input,
        depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_READY_FOR_OWNER_REVIEW,
        "evidence_depth_plan_ready_for_owner_review",
        "weak_profit_candidate_needs_depth_plan",
        "One profit result is not enough to prove repeatability.",
        30,
        10,
        3,
        depth_plan.EVIDENCE_DEPTH_COLLECTION_PACKET_PREVIEW,
        True,
        True,
    ),
    (
        "loss",
        depth_plan.build_sample_loss_depth_plan_input,
        depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_NOT_PROFIT_CANDIDATE,
        "blocked_not_profit_candidate",
        "not_profit_candidate",
        "The source review is not a profit candidate and cannot become proof.",
        0,
        0,
        0,
        depth_plan.LOSS_PACKET_PREVIEW,
        False,
        False,
    ),
    (
        "breakeven",
        depth_plan.build_sample_breakeven_depth_plan_input,
        depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE,
        "more_evidence_required_before_depth_plan",
        "breakeven_more_evidence_required",
        "The source review needs more evidence before a depth plan can advance.",
        0,
        0,
        0,
        depth_plan.BREAKEVEN_PACKET_PREVIEW,
        False,
        True,
    ),
    (
        "missing",
        depth_plan.build_sample_missing_owner_result_depth_plan_input,
        depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE,
        "owner_result_required_before_depth_plan",
        "owner_result_required",
        "Sanitized owner result evidence is required before depth planning.",
        0,
        0,
        0,
        depth_plan.MISSING_OWNER_RESULT_PACKET_PREVIEW,
        False,
        True,
    ),
    (
        "unsafe",
        depth_plan.build_sample_unsafe_depth_plan_input,
        depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_UNSAFE,
        "unsafe_result_repair_required_before_depth_plan",
        "unsafe_result_repair_required",
        "Unsafe result material must be repaired before any evidence-depth plan.",
        0,
        0,
        0,
        depth_plan.UNSAFE_PACKET_PREVIEW,
        False,
        False,
    ),
)

REQUIRED_RESULT_FIELDS = (
    "version",
    "packet_id",
    "classification",
    "source_profit_review_status",
    "source_candidate_review_lane",
    "source_candidate_strength_label",
    "source_statistical_validity_status",
    "source_evidence_depth_status",
    "source_evidence_depth_next_packet_preview",
    "evidence_depth_plan_status",
    "evidence_depth_plan_label",
    "evidence_depth_reason",
    "minimum_sanitized_result_count",
    "minimum_independent_session_count",
    "minimum_market_condition_buckets",
    "required_evidence_categories",
    "required_quality_gates",
    "required_risk_controls",
    "required_blocker_checks",
    "blocked_claims",
    "blocked_actions",
    "allowed_next_human_action",
    "next_packet_preview",
    "owner_review_required",
    "single_result_candidate",
    "evidence_depth_required",
    "preview_only",
    "plan_only",
    "execution_blocked",
    "statistical_claim_blocked",
    "proof_warning",
    "statistical_warning",
    "exact_next_owner_action",
    "exact_next_codex_packet_policy",
    "one_sentence_answer",
    "next_safe_action",
    "protected_flags",
) + depth_plan.PROTECTED_FLAG_NAMES

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
    "Evidence depth plan does not authorize trading.",
    "All protected flags remain false.",
    "Profit proof evidence-depth plan only.",
    "Read-only only.",
)


def _result(builder=depth_plan.build_sample_profit_depth_plan_input):
    return depth_plan.build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
        builder()
    )


def test_profit_sample_creates_evidence_depth_plan_ready_for_owner_review():
    assert (
        _result().classification
        == depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_READY_FOR_OWNER_REVIEW
    )


def test_profit_sample_labels_one_profit_result_as_weak_evidence():
    assert _result().evidence_depth_plan_label == "weak_profit_candidate_needs_depth_plan"


def test_profit_sample_requires_evidence_depth():
    assert _result().evidence_depth_required is True


def test_profit_sample_blocks_statistical_profitability_claim():
    result = _result()
    assert "statistical_profitability" in result.blocked_claims
    assert result.statistical_claim_blocked is True


def test_profit_sample_blocks_future_profit_claim():
    assert "future_profit" in _result().blocked_claims


def test_profit_sample_requires_minimum_sanitized_result_count_30():
    assert _result().minimum_sanitized_result_count == 30


def test_profit_sample_requires_minimum_independent_session_count_10():
    assert _result().minimum_independent_session_count == 10


def test_profit_sample_requires_minimum_market_condition_buckets_3():
    assert _result().minimum_market_condition_buckets == 3


def test_profit_sample_routes_to_evidence_depth_collection_packet():
    assert _result().next_packet_preview == depth_plan.EVIDENCE_DEPTH_COLLECTION_PACKET_PREVIEW


def test_loss_route_blocks_not_profit_candidate():
    result = _result(depth_plan.build_sample_loss_depth_plan_input)
    assert (
        result.classification
        == depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_NOT_PROFIT_CANDIDATE
    )
    assert "profit_proof_candidate" in result.blocked_claims


def test_breakeven_route_requires_more_evidence():
    result = _result(depth_plan.build_sample_breakeven_depth_plan_input)
    assert (
        result.classification
        == depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE
    )
    assert result.evidence_depth_plan_status == "more_evidence_required_before_depth_plan"


def test_missing_route_requires_owner_result_evidence():
    result = _result(depth_plan.build_sample_missing_owner_result_depth_plan_input)
    assert (
        result.classification
        == depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE
    )
    assert result.evidence_depth_plan_status == "owner_result_required_before_depth_plan"


def test_unsafe_route_blocks_unsafe():
    result = _result(depth_plan.build_sample_unsafe_depth_plan_input)
    assert (
        result.classification
        == depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_UNSAFE
    )
    assert result.evidence_depth_plan_status == "unsafe_result_repair_required_before_depth_plan"


def test_exact_next_owner_action_present():
    assert _result().exact_next_owner_action == depth_plan.EXACT_NEXT_OWNER_ACTION


def test_exact_next_codex_packet_policy_present():
    assert _result().exact_next_codex_packet_policy == depth_plan.EXACT_NEXT_CODEX_PACKET_POLICY


def test_one_sentence_answer_exact():
    assert _result().one_sentence_answer == depth_plan.ONE_SENTENCE_ANSWER


def test_proof_warning_present():
    assert _result().proof_warning == depth_plan.PROOF_WARNING


def test_statistical_warning_present():
    assert _result().statistical_warning == depth_plan.STATISTICAL_WARNING


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "status",
        "label",
        "reason",
        "min_results",
        "min_sessions",
        "min_buckets",
        "next_packet",
        "single_result",
        "evidence_required",
    ),
    SAMPLE_CASES,
)
def test_depth_plan_mapping(
    name,
    builder,
    classification,
    status,
    label,
    reason,
    min_results,
    min_sessions,
    min_buckets,
    next_packet,
    single_result,
    evidence_required,
):
    result = _result(builder)
    assert result.classification == classification
    assert result.evidence_depth_plan_status == status
    assert result.evidence_depth_plan_label == label
    assert result.evidence_depth_reason == reason


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "status",
        "label",
        "reason",
        "min_results",
        "min_sessions",
        "min_buckets",
        "next_packet",
        "single_result",
        "evidence_required",
    ),
    SAMPLE_CASES,
)
def test_depth_plan_minimums_and_next_packet(
    name,
    builder,
    classification,
    status,
    label,
    reason,
    min_results,
    min_sessions,
    min_buckets,
    next_packet,
    single_result,
    evidence_required,
):
    result = _result(builder)
    assert result.minimum_sanitized_result_count == min_results
    assert result.minimum_independent_session_count == min_sessions
    assert result.minimum_market_condition_buckets == min_buckets
    assert result.next_packet_preview == next_packet


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "status",
        "label",
        "reason",
        "min_results",
        "min_sessions",
        "min_buckets",
        "next_packet",
        "single_result",
        "evidence_required",
    ),
    SAMPLE_CASES,
)
def test_depth_plan_descriptive_booleans(
    name,
    builder,
    classification,
    status,
    label,
    reason,
    min_results,
    min_sessions,
    min_buckets,
    next_packet,
    single_result,
    evidence_required,
):
    result = _result(builder)
    assert result.single_result_candidate is single_result
    assert result.evidence_depth_required is evidence_required
    assert result.owner_review_required is True
    assert result.preview_only is True
    assert result.plan_only is True
    assert result.execution_blocked is True
    assert result.statistical_claim_blocked is True


@pytest.mark.parametrize("item", depth_plan.REQUIRED_EVIDENCE_CATEGORIES)
def test_profit_sample_includes_required_evidence_categories(item: str):
    assert item in _result().required_evidence_categories


@pytest.mark.parametrize("item", depth_plan.REQUIRED_QUALITY_GATES)
def test_profit_sample_includes_required_quality_gates(item: str):
    assert item in _result().required_quality_gates


@pytest.mark.parametrize("item", depth_plan.REQUIRED_RISK_CONTROLS)
def test_profit_sample_includes_required_risk_controls(item: str):
    assert item in _result().required_risk_controls


@pytest.mark.parametrize("item", depth_plan.REQUIRED_BLOCKER_CHECKS)
def test_profit_sample_includes_required_blocker_checks(item: str):
    assert item in _result().required_blocker_checks


@pytest.mark.parametrize("item", depth_plan.BLOCKED_CLAIMS)
def test_profit_sample_includes_blocked_claims(item: str):
    assert item in _result().blocked_claims


@pytest.mark.parametrize("item", depth_plan.BLOCKED_ACTIONS)
def test_profit_sample_includes_blocked_actions(item: str):
    assert item in _result().blocked_actions


@pytest.mark.parametrize("builder", tuple(case[1] for case in SAMPLE_CASES))
def test_json_serializable_outputs(builder):
    json.dumps(depth_plan.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize("builder", tuple(case[1] for case in SAMPLE_CASES))
def test_deterministic_outputs(builder):
    assert depth_plan.to_jsonable_dict(_result(builder)) == depth_plan.to_jsonable_dict(
        _result(builder)
    )


def test_markdown_output():
    text = depth_plan.to_markdown(_result())
    assert "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Plan V1" in text
    assert depth_plan.EVIDENCE_DEPTH_COLLECTION_PACKET_PREVIEW in text


def test_operator_text_output():
    text = depth_plan.to_operator_text(_result())
    assert "Evidence-depth plan status" in text
    assert depth_plan.ONE_SENTENCE_ANSWER in text


@pytest.mark.parametrize("field_name", REQUIRED_RESULT_FIELDS)
def test_required_result_fields_present(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", depth_plan.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_in_map(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize("flag_name", depth_plan.PROTECTED_FLAG_NAMES)
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
        "evidence_depth_plan_authorizes_trading",
        "evidence_depth_plan_authorizes_execution",
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
        ("plan_only", True),
        ("owner_review_required", True),
        ("single_result_candidate", True),
        ("evidence_depth_required", True),
        ("execution_blocked", True),
        ("statistical_claim_blocked", True),
    ),
)
def test_profit_descriptive_flags(field_name: str, expected: bool):
    assert getattr(_result(), field_name) is expected


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
        "evidence_depth_plan_authorizes_trading=True",
        "evidence_depth_plan_authorizes_execution=True",
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
        "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Plan V1",
        "## Packet ID",
        "## Source Chain Read",
        "## Files Created",
        "## Evidence Depth Classifications",
        "## Evidence Depth Mapping",
        "## Profit Depth Plan Sample",
        "## Loss Route Sample",
        "## Breakeven Route Sample",
        "## Missing Owner Result Sample",
        "## Unsafe Route Sample",
        "## Minimum Evidence Requirements",
        "## Required Evidence Categories",
        "## Required Quality Gates",
        "## Required Risk Controls",
        "## Required Blocker Checks",
        "## Blocked Claims",
        "## Blocked Actions",
        "## Exact Next Owner Action",
        "## Exact Next Codex Packet Policy",
        "## Protected Flags",
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
        "python -m py_compile automation/forex_engine/oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py tests/forex_engine/test_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py",
        "python -m pytest tests/forex_engine/test_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py -q",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py --sample-profit --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py --sample-loss --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py --sample-breakeven --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py --sample-missing --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py --sample-unsafe --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py --sample-profit --markdown",
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
            depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_READY_FOR_OWNER_REVIEW,
        ),
        (
            ["runner", "--sample-loss", "--json"],
            depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_NOT_PROFIT_CANDIDATE,
        ),
        (
            ["runner", "--sample-breakeven", "--json"],
            depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE,
        ),
        (
            ["runner", "--sample-missing", "--json"],
            "owner_result_required_before_depth_plan",
        ),
        (
            ["runner", "--sample-unsafe", "--json"],
            depth_plan.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_UNSAFE,
        ),
        (
            ["runner", "--sample-profit", "--markdown"],
            "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Plan V1",
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert run_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize("phrase", depth_plan.REQUIRED_EVIDENCE_CATEGORIES)
def test_report_required_evidence_categories(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", depth_plan.REQUIRED_QUALITY_GATES)
def test_report_required_quality_gates(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", depth_plan.REQUIRED_RISK_CONTROLS)
def test_report_required_risk_controls(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", depth_plan.REQUIRED_BLOCKER_CHECKS)
def test_report_required_blocker_checks(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", depth_plan.BLOCKED_CLAIMS + ("profit_proof_candidate",))
def test_report_blocked_claims(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", depth_plan.BLOCKED_ACTIONS)
def test_report_blocked_actions(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", depth_plan.PROTECTED_FLAG_NAMES)
def test_report_protected_flags(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "builder",
    (
        depth_plan.build_sample_profit_depth_plan_input,
        depth_plan.build_sample_loss_depth_plan_input,
        depth_plan.build_sample_breakeven_depth_plan_input,
        depth_plan.build_sample_missing_owner_result_depth_plan_input,
        depth_plan.build_sample_unsafe_depth_plan_input,
    ),
)
@pytest.mark.parametrize("flag_name", depth_plan.PROTECTED_FLAG_NAMES)
def test_all_sample_routes_keep_protected_flags_false(builder, flag_name: str):
    result = _result(builder)
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "builder",
    (
        depth_plan.build_sample_profit_depth_plan_input,
        depth_plan.build_sample_loss_depth_plan_input,
        depth_plan.build_sample_breakeven_depth_plan_input,
        depth_plan.build_sample_missing_owner_result_depth_plan_input,
        depth_plan.build_sample_unsafe_depth_plan_input,
    ),
)
@pytest.mark.parametrize(
    "field_name",
    (
        "preview_only",
        "plan_only",
        "owner_review_required",
        "execution_blocked",
        "statistical_claim_blocked",
    ),
)
def test_all_sample_routes_keep_core_descriptive_flags_true(builder, field_name: str):
    assert getattr(_result(builder), field_name) is True
