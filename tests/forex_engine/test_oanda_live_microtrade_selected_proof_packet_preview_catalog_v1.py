from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import (
    oanda_live_microtrade_routed_proof_owner_decision_gate_v1 as decision_gate,
)
from automation.forex_engine import (
    oanda_live_microtrade_selected_proof_packet_preview_catalog_v1 as catalog,
)
from scripts.forex_delivery import (
    run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation/forex_engine/"
    "oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py"
)
RUNNER_PATH = (
    REPO_ROOT
    / "scripts/forex_delivery/"
    "run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py"
)
TEST_PATH = (
    REPO_ROOT
    / "tests/forex_engine/"
    "test_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_V1.md"
)
MANUAL_REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_MANUAL_FINALIZATION_V1.md"
)

SAMPLE_CASES = (
    (
        "profit",
        catalog.build_sample_profit_catalog_input,
        catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW,
        "profit_proof_candidate_review",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1",
        "Profit Proof Candidate Review Preview",
        "Review one captured profit result as a proof candidate only.",
        "This preview does not authorize trade execution or repeat trading.",
        "Anthony may approve a future proof-review packet prompt only.",
    ),
    (
        "loss",
        catalog.build_sample_loss_catalog_input,
        catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW,
        "loss_review_and_next_profit_candidate_gate",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1",
        "Loss Review And Next Profit Candidate Gate Preview",
        "Route loss result to loss review and candidate repair.",
        "This preview does not authorize revenge trading or immediate retry.",
        "Anthony may approve a future loss-review packet prompt only.",
    ),
    (
        "breakeven",
        catalog.build_sample_breakeven_catalog_input,
        catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_REQUIRE_MORE_EVIDENCE,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE,
        "more_evidence_required",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1",
        "Breakeven More Evidence Preview",
        "Require more sanitized evidence before proof promotion.",
        "This preview does not authorize another live trade.",
        "Anthony may approve a future more-evidence collection packet only.",
    ),
    (
        "missing",
        catalog.build_sample_missing_owner_result_catalog_input,
        catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_NO_OWNER_RESULT,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT,
        "owner_result_evidence_required",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1",
        "Owner Result Evidence Required Preview",
        "Require sanitized owner result evidence before proof review.",
        "This preview does not authorize broker access or result scraping.",
        "Anthony may provide sanitized owner result evidence.",
    ),
    (
        "unsafe",
        catalog.build_sample_unsafe_catalog_input,
        catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_UNSAFE,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_UNSAFE,
        "unsafe_result_repair",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1",
        "Unsafe Result Repair Preview",
        "Repair unsafe result material before any proof review.",
        "This preview blocks proof promotion and all execution.",
        "Anthony may approve an unsafe-result repair packet only.",
    ),
)

REQUIRED_RESULT_FIELDS = (
    "version",
    "packet_id",
    "classification",
    "source_decision_status",
    "source_selected_review_lane",
    "source_selected_packet_preview",
    "selected_packet_preview",
    "selected_packet_title",
    "selected_packet_purpose",
    "selected_packet_non_execution_notice",
    "selected_packet_required_owner_review",
    "selected_packet_blocked_actions",
    "selected_packet_allowed_next_human_action",
    "selected_packet_forbidden_actions",
    "preview_catalog_entry",
    "proof_warning",
    "statistical_warning",
    "owner_review_required",
    "selected_packet_preview_only",
    "preview_only",
    "catalog_only",
    "execution_blocked",
    "blocked_items",
    "exact_next_owner_action",
    "exact_next_codex_packet_policy",
    "one_sentence_answer",
    "next_safe_action",
    "protected_flags",
) + catalog.PROTECTED_FLAG_NAMES

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
    "All protected flags remain false.",
    "Selected proof packet preview catalog only.",
    "Read-only only.",
)


def _result(builder=catalog.build_sample_profit_catalog_input):
    return catalog.build_selected_proof_packet_preview_catalog(builder())


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "packet",
        "title",
        "purpose",
        "notice",
        "human_action",
    ),
    SAMPLE_CASES,
)
def test_sample_catalog_mapping(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    packet,
    title,
    purpose,
    notice,
    human_action,
):
    result = _result(builder)
    assert result.classification == classification
    assert result.source_decision_status == source_status
    assert result.source_selected_review_lane == source_lane
    assert result.source_selected_packet_preview == packet
    assert result.selected_packet_preview == packet


@pytest.mark.parametrize(
    "builder,expected",
    (
        (
            catalog.build_sample_profit_catalog_input,
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1",
        ),
        (
            catalog.build_sample_loss_catalog_input,
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1",
        ),
        (
            catalog.build_sample_breakeven_catalog_input,
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1",
        ),
        (
            catalog.build_sample_missing_owner_result_catalog_input,
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1",
        ),
        (
            catalog.build_sample_unsafe_catalog_input,
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1",
        ),
    ),
)
def test_required_route_packet_preview(builder, expected):
    assert _result(builder).selected_packet_preview == expected


@pytest.mark.parametrize(
    "builder,expected",
    (
        (
            catalog.build_sample_profit_catalog_input,
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW,
        ),
        (
            catalog.build_sample_loss_catalog_input,
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW,
        ),
        (
            catalog.build_sample_breakeven_catalog_input,
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_REQUIRE_MORE_EVIDENCE,
        ),
        (
            catalog.build_sample_missing_owner_result_catalog_input,
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_NO_OWNER_RESULT,
        ),
        (
            catalog.build_sample_unsafe_catalog_input,
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_UNSAFE,
        ),
    ),
)
def test_required_route_classification(builder, expected):
    assert _result(builder).classification == expected


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "packet",
        "title",
        "purpose",
        "notice",
        "human_action",
    ),
    SAMPLE_CASES,
)
def test_selected_packet_title_purpose_notice_and_human_action(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    packet,
    title,
    purpose,
    notice,
    human_action,
):
    result = _result(builder)
    assert result.selected_packet_title == title
    assert result.selected_packet_purpose == purpose
    assert result.selected_packet_non_execution_notice == notice
    assert result.selected_packet_allowed_next_human_action == human_action


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "packet",
        "title",
        "purpose",
        "notice",
        "human_action",
    ),
    SAMPLE_CASES,
)
def test_json_serializable_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    packet,
    title,
    purpose,
    notice,
    human_action,
):
    json.dumps(catalog.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "packet",
        "title",
        "purpose",
        "notice",
        "human_action",
    ),
    SAMPLE_CASES,
)
def test_deterministic_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    packet,
    title,
    purpose,
    notice,
    human_action,
):
    assert catalog.to_jsonable_dict(_result(builder)) == catalog.to_jsonable_dict(
        _result(builder)
    )


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "packet",
        "title",
        "purpose",
        "notice",
        "human_action",
    ),
    SAMPLE_CASES,
)
def test_markdown_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    packet,
    title,
    purpose,
    notice,
    human_action,
):
    text = catalog.to_markdown(_result(builder))
    assert "# AIOS Forex OANDA Live Microtrade Selected Proof Packet Preview Catalog V1" in text
    assert packet in text


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "packet",
        "title",
        "purpose",
        "notice",
        "human_action",
    ),
    SAMPLE_CASES,
)
def test_operator_text_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    packet,
    title,
    purpose,
    notice,
    human_action,
):
    text = catalog.to_operator_text(_result(builder))
    assert "Selected proof packet preview catalog status" in text
    assert packet in text


@pytest.mark.parametrize("field_name", REQUIRED_RESULT_FIELDS)
def test_required_result_fields_present(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", catalog.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_in_map(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize("flag_name", catalog.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_on_result(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    "flag_name",
    (
        "demo_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "live_trading_allowed",
        "live_execution_allowed",
        "credential_access_allowed",
        "account_id_persistence_allowed",
        "autonomous_execution_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "webhook_allowed",
        "live_micro_trade_exception_allowed",
        "owner_live_execution_approval_present",
        "codex_live_execution_authorized",
        "unattended_vacation_mode_allowed",
        "vacation_profit_trial_allowed",
        "repeat_live_trade_allowed",
        "next_trade_authorized",
        "result_proves_profitability",
        "statistical_profitability_confirmed",
        "selected_packet_execution_authorized",
        "selected_packet_commit_authorized",
        "selected_packet_push_authorized",
        "selected_packet_pr_authorized",
        "selected_packet_merge_authorized",
    ),
)
def test_high_risk_flags_false(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    ("field_name", "expected"),
    (
        ("preview_only", True),
        ("catalog_only", True),
        ("selected_packet_preview_only", True),
        ("owner_review_required", True),
        ("execution_blocked", True),
        ("selected_packet_required_owner_review", True),
    ),
)
def test_descriptive_flags_true(field_name: str, expected: bool):
    assert getattr(_result(), field_name) is expected


@pytest.mark.parametrize("blocked_action", catalog.SELECTED_PACKET_BLOCKED_ACTIONS)
def test_selected_packet_blocked_actions_present(blocked_action: str):
    result = _result()
    assert blocked_action in result.selected_packet_blocked_actions
    assert blocked_action in result.selected_packet_forbidden_actions
    assert blocked_action in result.blocked_items


@pytest.mark.parametrize("blocked_action", catalog.SELECTED_PACKET_BLOCKED_ACTIONS)
def test_preview_catalog_entry_blocked_actions_present(blocked_action: str):
    entry = _result().preview_catalog_entry
    assert blocked_action in entry["selected_packet_blocked_actions"]
    assert blocked_action in entry["selected_packet_forbidden_actions"]


def test_profit_catalog_selects_profit_proof_candidate_review_preview():
    result = _result(catalog.build_sample_profit_catalog_input)
    assert result.source_selected_review_lane == "profit_proof_candidate_review"
    assert result.selected_packet_title == "Profit Proof Candidate Review Preview"


def test_loss_catalog_selects_loss_review_and_next_profit_candidate_gate_preview():
    result = _result(catalog.build_sample_loss_catalog_input)
    assert result.source_selected_review_lane == "loss_review_and_next_profit_candidate_gate"
    assert result.selected_packet_title == "Loss Review And Next Profit Candidate Gate Preview"


def test_breakeven_catalog_selects_more_evidence_preview():
    result = _result(catalog.build_sample_breakeven_catalog_input)
    assert result.source_selected_review_lane == "more_evidence_required"
    assert result.selected_packet_title == "Breakeven More Evidence Preview"


def test_missing_catalog_selects_owner_result_evidence_required_preview():
    result = _result(catalog.build_sample_missing_owner_result_catalog_input)
    assert result.source_selected_review_lane == "owner_result_evidence_required"
    assert result.classification.endswith("BLOCKED_NO_OWNER_RESULT")


def test_unsafe_catalog_selects_unsafe_result_repair_preview():
    result = _result(catalog.build_sample_unsafe_catalog_input)
    assert result.source_selected_review_lane == "unsafe_result_repair"
    assert result.classification.endswith("BLOCKED_UNSAFE")


def test_exact_next_owner_action_present():
    assert _result().exact_next_owner_action == catalog.EXACT_NEXT_OWNER_ACTION


def test_exact_next_codex_packet_policy_present():
    assert _result().exact_next_codex_packet_policy == catalog.EXACT_NEXT_CODEX_PACKET_POLICY


def test_one_sentence_answer_exact():
    assert _result().one_sentence_answer == catalog.ONE_SENTENCE_ANSWER


def test_proof_warning_present():
    assert _result().proof_warning == catalog.PROOF_WARNING


def test_statistical_warning_present():
    assert _result().statistical_warning == catalog.STATISTICAL_WARNING


def test_mapping_decision_gate_output_can_be_evaluated():
    source_result = decision_gate.to_jsonable_dict(
        decision_gate.evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(
            decision_gate.build_sample_profit_decision_input()
        )
    )
    result = catalog.build_selected_proof_packet_preview_catalog(
        {"decision_gate_input": source_result}
    )
    assert result.source_selected_review_lane == "profit_proof_candidate_review"


def test_decision_gate_input_can_be_evaluated():
    result = catalog.build_selected_proof_packet_preview_catalog(
        {"decision_gate_input": decision_gate.build_sample_loss_decision_input()}
    )
    assert result.source_selected_review_lane == "loss_review_and_next_profit_candidate_gate"


def test_unsafe_owner_preview_label_does_not_authorize():
    result = catalog.build_selected_proof_packet_preview_catalog(
        {
            "decision_gate_input": decision_gate.build_sample_profit_decision_input(),
            "owner_preview_label": "approve next live trade",
        }
    )
    assert result.preview_catalog_entry["owner_preview_label"] == "pending_owner_review"
    assert result.next_trade_authorized is False


def test_owner_notes_with_sensitive_terms_are_removed():
    result = catalog.build_selected_proof_packet_preview_catalog(
        {
            "decision_gate_input": decision_gate.build_sample_profit_decision_input(),
            "owner_notes_sanitized": "account secret",
        }
    )
    assert result.preview_catalog_entry["owner_notes_sanitized"] == ""


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
        "next_trade_authorized=True",
        "selected_packet_execution_authorized=True",
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
        "# AIOS Forex OANDA Live Microtrade Selected Proof Packet Preview Catalog V1",
        "## Packet ID",
        "## Source Chain Read",
        "## Files Created",
        "## Catalog Classifications",
        "## Catalog Mapping",
        "## Profit Catalog Sample",
        "## Loss Catalog Sample",
        "## Breakeven Catalog Sample",
        "## Missing Owner Result Catalog Sample",
        "## Unsafe Catalog Sample",
        "## Exact Next Owner Action",
        "## Exact Next Codex Packet Policy",
        "## Protected Flags",
        "## Blocked Selected-Packet Actions",
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
        "python -m py_compile automation/forex_engine/oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py scripts/forex_delivery/run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py tests/forex_engine/test_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py",
        "python -m pytest tests/forex_engine/test_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py -q",
        "python scripts/forex_delivery/run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py --sample-profit --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py --sample-loss --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py --sample-breakeven --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py --sample-missing --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py --sample-unsafe --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py --sample-profit --markdown",
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
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW,
        ),
        (
            ["runner", "--sample-loss", "--json"],
            "Loss Review And Next Profit Candidate Gate Preview",
        ),
        (
            ["runner", "--sample-breakeven", "--json"],
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_REQUIRE_MORE_EVIDENCE,
        ),
        (
            ["runner", "--sample-missing", "--json"],
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_NO_OWNER_RESULT,
        ),
        (
            ["runner", "--sample-unsafe", "--json"],
            catalog.OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_UNSAFE,
        ),
        (
            ["runner", "--sample-profit", "--markdown"],
            "# AIOS Forex OANDA Live Microtrade Selected Proof Packet Preview Catalog V1",
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert run_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize(
    "phrase",
    (
        "profit_proof_candidate_review -> profit proof candidate review preview",
        "loss_review_and_next_profit_candidate_gate -> loss review and next profit candidate gate preview",
        "more_evidence_required -> breakeven more evidence preview",
        "owner_result_evidence_required -> owner result evidence required preview",
        "unsafe_result_repair -> unsafe result repair preview",
    ),
)
def test_report_catalog_mapping_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "phrase",
    (
        "Profit Proof Candidate Review Preview",
        "Review one captured profit result as a proof candidate only.",
        "Loss Review And Next Profit Candidate Gate Preview",
        "Route loss result to loss review and candidate repair.",
        "Breakeven More Evidence Preview",
        "Require more sanitized evidence before proof promotion.",
        "Owner Result Evidence Required Preview",
        "Require sanitized owner result evidence before proof review.",
        "Unsafe Result Repair Preview",
        "Repair unsafe result material before any proof review.",
    ),
)
def test_report_catalog_titles_and_purposes(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("phrase", catalog.SELECTED_PACKET_BLOCKED_ACTIONS)
def test_report_blocked_actions(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")
