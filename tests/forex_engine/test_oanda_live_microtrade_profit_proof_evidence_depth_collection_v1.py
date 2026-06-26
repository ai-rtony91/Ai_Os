from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import (
    oanda_live_microtrade_profit_proof_evidence_depth_collection_v1 as collection,
)
from scripts.forex_delivery import (
    run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation/forex_engine/"
    "oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py"
)
RUNNER_PATH = (
    REPO_ROOT
    / "scripts/forex_delivery/"
    "run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py"
)
TEST_PATH = (
    REPO_ROOT
    / "tests/forex_engine/"
    "test_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_V1.md"
)
MANUAL_REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_MANUAL_FINALIZATION_V1.md"
)

SAMPLE_CASES = (
    (
        "complete",
        collection.build_sample_complete_collection_input,
        collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW,
        "sanitized_evidence_depth_collection_ready_for_owner_review",
        30,
        10,
        3,
        True,
    ),
    (
        "partial",
        collection.build_sample_partial_collection_input,
        collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE,
        "more_sanitized_evidence_required",
        12,
        10,
        3,
        False,
    ),
    (
        "empty",
        collection.build_sample_empty_collection_input,
        collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE,
        "more_sanitized_evidence_required",
        0,
        0,
        0,
        False,
    ),
    (
        "unsafe",
        collection.build_sample_unsafe_collection_input,
        collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE,
        "blocked_unsafe_collection",
        1,
        1,
        1,
        False,
    ),
    (
        "schema-invalid",
        collection.build_sample_schema_invalid_collection_input,
        collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID,
        "blocked_schema_invalid_collection",
        1,
        0,
        1,
        False,
    ),
)

REQUIRED_RESULT_FIELDS = (
    "version",
    "packet_id",
    "classification",
    "source_depth_plan_status",
    "source_next_packet_preview",
    "source_minimum_sanitized_result_count",
    "source_minimum_independent_session_count",
    "source_minimum_market_condition_buckets",
    "collection_status",
    "collection_label",
    "sanitized_result_count",
    "independent_session_count",
    "market_condition_bucket_count",
    "market_condition_buckets",
    "outcome_bucket_counts",
    "total_net_pnl_after_costs",
    "average_r_multiple",
    "minimum_counts_met",
    "required_controls_met",
    "required_persistence_absence_met",
    "unsafe_payload_absent",
    "rejected_result_references",
    "missing_required_fields",
    "unsafe_fragments_detected",
    "blocker_flags",
    "evidence_categories_present",
    "quality_gate_readiness",
    "risk_control_readiness",
    "blocked_claims",
    "blocked_actions",
    "allowed_next_human_action",
    "next_packet_preview",
    "owner_review_required",
    "preview_only",
    "collection_only",
    "execution_blocked",
    "statistical_claim_blocked",
    "proof_warning",
    "statistical_warning",
    "exact_next_owner_action",
    "exact_next_codex_packet_policy",
    "one_sentence_answer",
    "next_safe_action",
    "protected_flags",
) + collection.PROTECTED_FLAG_NAMES

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
    "Evidence depth collection does not prove statistical profitability.",
    "Evidence depth collection does not authorize trading.",
    "All protected flags remain false.",
    "Profit proof evidence-depth collection only.",
    "Read-only only.",
)


def _result(builder=collection.build_sample_complete_collection_input):
    return collection.evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection(
        builder()
    )


def test_complete_sample_reaches_ready_for_owner_review():
    assert (
        _result().classification
        == collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW
    )


def test_partial_sample_requires_more_evidence():
    assert (
        _result(collection.build_sample_partial_collection_input).classification
        == collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE
    )


def test_empty_sample_requires_more_evidence():
    assert (
        _result(collection.build_sample_empty_collection_input).classification
        == collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE
    )


def test_unsafe_sample_blocks_unsafe():
    assert (
        _result(collection.build_sample_unsafe_collection_input).classification
        == collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE
    )


def test_schema_invalid_sample_blocks_schema_invalid():
    assert (
        _result(collection.build_sample_schema_invalid_collection_input).classification
        == collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID
    )


def test_complete_sample_has_30_sanitized_results():
    assert _result().sanitized_result_count == 30


def test_complete_sample_has_10_independent_sessions():
    assert _result().independent_session_count == 10


def test_complete_sample_has_3_market_condition_buckets():
    assert _result().market_condition_bucket_count == 3


def test_complete_sample_has_sorted_market_condition_buckets():
    assert _result().market_condition_buckets == ("ranging", "trending", "volatile")


def test_complete_sample_has_outcome_bucket_counts():
    assert _result().outcome_bucket_counts == {
        "profit": 20,
        "loss": 5,
        "breakeven": 5,
    }


def test_complete_sample_calculates_total_net_pnl_after_costs():
    assert _result().total_net_pnl_after_costs == "30.00"


def test_complete_sample_calculates_average_r_multiple():
    assert _result().average_r_multiple == "0.10"


def test_complete_sample_meets_required_controls():
    assert _result().required_controls_met is True


def test_complete_sample_meets_persistence_absence_checks():
    assert _result().required_persistence_absence_met is True


def test_complete_sample_has_unsafe_payload_absent():
    assert _result().unsafe_payload_absent is True


def test_complete_sample_routes_to_quality_gate_preview():
    assert _result().next_packet_preview == collection.QUALITY_GATE_PACKET_PREVIEW


def test_partial_sample_fails_minimum_counts():
    assert _result(collection.build_sample_partial_collection_input).minimum_counts_met is False


def test_unsafe_sample_detects_unsafe_fragments():
    fragments = _result(collection.build_sample_unsafe_collection_input).unsafe_fragments_detected
    assert any("Authorization" in item for item in fragments)
    assert any("Bearer" in item for item in fragments)


def test_unsafe_sample_detects_unsafe_payload_absent_false():
    assert _result(collection.build_sample_unsafe_collection_input).unsafe_payload_absent is False


def test_schema_invalid_sample_reports_missing_fields():
    assert _result(collection.build_sample_schema_invalid_collection_input).missing_required_fields


def test_schema_invalid_sample_reports_invalid_decimal():
    result = _result(collection.build_sample_schema_invalid_collection_input)
    assert result.blocker_flags["invalid_decimal_values"] is True
    assert any("invalid_decimal" in item for item in result.missing_required_fields)


def test_exact_next_owner_action_present():
    assert _result().exact_next_owner_action == collection.EXACT_NEXT_OWNER_ACTION


def test_exact_next_codex_packet_policy_present():
    assert _result().exact_next_codex_packet_policy == collection.EXACT_NEXT_CODEX_PACKET_POLICY


def test_one_sentence_answer_exact():
    assert _result().one_sentence_answer == collection.ONE_SENTENCE_ANSWER


def test_proof_warning_present():
    assert _result().proof_warning == collection.PROOF_WARNING


def test_statistical_warning_present():
    assert _result().statistical_warning == collection.STATISTICAL_WARNING


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "status",
        "result_count",
        "session_count",
        "bucket_count",
        "minimum_counts_met",
    ),
    SAMPLE_CASES,
)
def test_sample_classification_mapping(
    name,
    builder,
    classification,
    status,
    result_count,
    session_count,
    bucket_count,
    minimum_counts_met,
):
    result = _result(builder)
    assert result.classification == classification
    assert result.collection_status == status


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "status",
        "result_count",
        "session_count",
        "bucket_count",
        "minimum_counts_met",
    ),
    SAMPLE_CASES,
)
def test_sample_counts(
    name,
    builder,
    classification,
    status,
    result_count,
    session_count,
    bucket_count,
    minimum_counts_met,
):
    result = _result(builder)
    assert result.sanitized_result_count == result_count
    assert result.independent_session_count == session_count
    assert result.market_condition_bucket_count == bucket_count
    assert result.minimum_counts_met is minimum_counts_met


@pytest.mark.parametrize("item", collection.REQUIRED_EVIDENCE_CATEGORIES)
def test_complete_sample_includes_evidence_categories_present(item: str):
    assert item in _result().evidence_categories_present


@pytest.mark.parametrize("item", collection.REQUIRED_QUALITY_GATES)
def test_complete_sample_includes_quality_gate_readiness(item: str):
    assert item in _result().quality_gate_readiness


@pytest.mark.parametrize("item", collection.REQUIRED_RISK_CONTROLS)
def test_complete_sample_includes_risk_control_readiness(item: str):
    assert item in _result().risk_control_readiness


@pytest.mark.parametrize("item", collection.REQUIRED_BLOCKER_CHECKS)
def test_required_blocker_checks_are_available(item: str):
    assert item in collection.REQUIRED_BLOCKER_CHECKS


@pytest.mark.parametrize("item", collection.BLOCKED_CLAIMS)
def test_complete_sample_includes_blocked_claims(item: str):
    assert item in _result().blocked_claims


@pytest.mark.parametrize("item", collection.BLOCKED_ACTIONS)
def test_complete_sample_includes_blocked_actions(item: str):
    assert item in _result().blocked_actions


@pytest.mark.parametrize("builder", tuple(case[1] for case in SAMPLE_CASES))
def test_json_serializable_outputs(builder):
    json.dumps(collection.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize("builder", tuple(case[1] for case in SAMPLE_CASES))
def test_deterministic_outputs(builder):
    assert collection.to_jsonable_dict(_result(builder)) == collection.to_jsonable_dict(
        _result(builder)
    )


def test_markdown_output():
    text = collection.to_markdown(_result())
    assert "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Collection V1" in text
    assert collection.QUALITY_GATE_PACKET_PREVIEW in text


def test_operator_text_output():
    text = collection.to_operator_text(_result())
    assert "Evidence-depth collection status" in text
    assert collection.ONE_SENTENCE_ANSWER in text


@pytest.mark.parametrize("field_name", REQUIRED_RESULT_FIELDS)
def test_required_result_fields_present(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", collection.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_in_map(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize("flag_name", collection.PROTECTED_FLAG_NAMES)
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
        "evidence_depth_collection_authorizes_trading",
        "evidence_depth_collection_authorizes_execution",
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
        ("collection_only", True),
        ("owner_review_required", True),
        ("execution_blocked", True),
        ("statistical_claim_blocked", True),
    ),
)
def test_descriptive_flags_true(field_name: str, expected: bool):
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
        "evidence_depth_collection_authorizes_trading=True",
        "evidence_depth_collection_authorizes_execution=True",
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


def test_load_collection_json_supports_local_schema_valid_json(tmp_path):
    source = collection.build_sample_partial_collection_input()
    path = tmp_path / "sanitized_collection.json"
    path.write_text(
        json.dumps({"sanitized_results": list(source.sanitized_results)}),
        encoding="utf-8",
    )
    loaded = collection.load_collection_json(str(path))
    result = collection.evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection(
        loaded
    )
    assert result.classification == (
        collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE
    )


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
        "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Collection V1",
        "## Packet ID",
        "## Source Chain Read",
        "## Files Created",
        "## Collection Classifications",
        "## Collection Schema",
        "## Classification Logic",
        "## Complete Collection Sample",
        "## Partial Collection Sample",
        "## Empty Collection Sample",
        "## Unsafe Collection Sample",
        "## Schema Invalid Sample",
        "## Minimum Evidence Requirements",
        "## Result Count",
        "## Session Count",
        "## Market Condition Bucket Count",
        "## Outcome Counts",
        "## Total Net PnL After Costs",
        "## Average R Multiple",
        "## Required Controls",
        "## Persistence Absence Checks",
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
        "python -m py_compile automation/forex_engine/oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py tests/forex_engine/test_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py",
        "python -m pytest tests/forex_engine/test_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py -q",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py --sample-complete --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py --sample-partial --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py --sample-empty --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py --sample-unsafe --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py --sample-schema-invalid --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py --sample-complete --markdown",
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
            ["runner", "--sample-complete", "--json"],
            collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW,
        ),
        (
            ["runner", "--sample-partial", "--json"],
            collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE,
        ),
        (
            ["runner", "--sample-empty", "--json"],
            "more_sanitized_evidence_required",
        ),
        (
            ["runner", "--sample-unsafe", "--json"],
            collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE,
        ),
        (
            ["runner", "--sample-schema-invalid", "--json"],
            collection.OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID,
        ),
        (
            ["runner", "--sample-complete", "--markdown"],
            "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Collection V1",
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert run_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize("phrase", collection.REQUIRED_RESULT_FIELDS)
def test_report_schema_fields(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", collection.BLOCKED_CLAIMS)
def test_report_blocked_claims(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", collection.BLOCKED_ACTIONS)
def test_report_blocked_actions(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", collection.PROTECTED_FLAG_NAMES)
def test_report_protected_flags(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "builder",
    (
        collection.build_sample_complete_collection_input,
        collection.build_sample_partial_collection_input,
        collection.build_sample_empty_collection_input,
        collection.build_sample_unsafe_collection_input,
        collection.build_sample_schema_invalid_collection_input,
    ),
)
@pytest.mark.parametrize("flag_name", collection.PROTECTED_FLAG_NAMES)
def test_all_sample_routes_keep_protected_flags_false(builder, flag_name: str):
    result = _result(builder)
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "builder",
    (
        collection.build_sample_complete_collection_input,
        collection.build_sample_partial_collection_input,
        collection.build_sample_empty_collection_input,
        collection.build_sample_unsafe_collection_input,
        collection.build_sample_schema_invalid_collection_input,
    ),
)
@pytest.mark.parametrize(
    "field_name",
    (
        "preview_only",
        "collection_only",
        "owner_review_required",
        "execution_blocked",
        "statistical_claim_blocked",
    ),
)
def test_all_sample_routes_keep_core_descriptive_flags_true(builder, field_name: str):
    assert getattr(_result(builder), field_name) is True
