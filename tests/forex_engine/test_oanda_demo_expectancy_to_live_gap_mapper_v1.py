from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine.oanda_demo_expectancy_to_live_gap_mapper_v1 import (
    CLASSIFICATION_BLOCKED_EXPECTANCY,
    CLASSIFICATION_BLOCKED_UNSAFE,
    CLASSIFICATION_MISSING,
    CLASSIFICATION_PARTIAL,
    CLASSIFICATION_READY,
    LIVE_GAP_WARNING,
    OWNER_WARNING,
    PERMISSION_DEFAULTS,
    VERSION,
    build_sample_blocked_expectancy_gap_mapper_input,
    build_sample_missing_live_evidence_gap_mapper_input,
    build_sample_partial_live_evidence_gap_mapper_input,
    build_sample_ready_gap_mapper_input,
    build_sample_rejected_expectancy_blocked_input,
    build_sample_strong_expectancy_missing_live_evidence_input,
    build_sample_strong_expectancy_partial_live_evidence_input,
    build_sample_unsafe_expectancy_blocked_input,
    build_sample_unsafe_gap_mapper_input,
    build_sample_weak_expectancy_blocked_input,
    map_oanda_demo_expectancy_to_live_evidence_gaps,
    oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict,
    oanda_demo_expectancy_to_live_gap_mapper_to_markdown,
    oanda_demo_expectancy_to_live_gap_mapper_to_operator_text,
)
from automation.forex_engine.oanda_demo_live_evidence_requirement_matrix_v1 import (
    build_default_oanda_demo_live_evidence_requirements,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILES = (
    REPO_ROOT / "automation/forex_engine/oanda_demo_live_evidence_requirement_matrix_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_demo_expectancy_to_live_gap_mapper_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_demo_live_evidence_bundle_gap_gate_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py",
)
REQUIRED_ITEM_IDS = tuple(
    requirement.item_id for requirement in build_default_oanda_demo_live_evidence_requirements()
)


def _map(builder):
    return map_oanda_demo_expectancy_to_live_evidence_gaps(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (build_sample_missing_live_evidence_gap_mapper_input, CLASSIFICATION_MISSING),
        (build_sample_partial_live_evidence_gap_mapper_input, CLASSIFICATION_PARTIAL),
        (build_sample_ready_gap_mapper_input, CLASSIFICATION_READY),
        (build_sample_blocked_expectancy_gap_mapper_input, CLASSIFICATION_BLOCKED_EXPECTANCY),
        (build_sample_unsafe_gap_mapper_input, CLASSIFICATION_BLOCKED_UNSAFE),
    ),
)
def test_mapper_sample_classifications(builder, classification: str):
    assert _map(builder).classification == classification


def test_mapper_version_constant():
    assert VERSION == "oanda_demo_expectancy_to_live_gap_mapper_v1"


def test_mapper_counts_present_items():
    assert _map(build_sample_partial_live_evidence_gap_mapper_input).present_count == 8


def test_mapper_counts_missing_items():
    assert _map(build_sample_partial_live_evidence_gap_mapper_input).missing_count == 14


def test_mapper_counts_blocked_items():
    assert _map(build_sample_partial_live_evidence_gap_mapper_input).blocked_count == 2


def test_mapper_counts_owner_action_required_items():
    assert _map(build_sample_partial_live_evidence_gap_mapper_input).owner_action_required_count == 4


def test_mapper_lists_missing_items():
    assert _map(build_sample_partial_live_evidence_gap_mapper_input).missing_items


def test_mapper_lists_owner_action_required_items():
    assert _map(build_sample_partial_live_evidence_gap_mapper_input).owner_action_required_items


def test_mapper_lists_blocked_items():
    assert _map(build_sample_partial_live_evidence_gap_mapper_input).blocked_items


def test_mapper_preview_produced():
    assert _map(build_sample_missing_live_evidence_gap_mapper_input).live_evidence_bundle_preview[
        "preview_only"
    ] is True


def test_mapper_never_approves_live_execution():
    preview = _map(build_sample_ready_gap_mapper_input).live_evidence_bundle_preview
    assert preview["live_execution_allowed"] is False


def test_mapper_json_serializable():
    json.dumps(oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(_map(build_sample_ready_gap_mapper_input)))


def test_mapper_markdown_title():
    markdown = oanda_demo_expectancy_to_live_gap_mapper_to_markdown(
        _map(build_sample_missing_live_evidence_gap_mapper_input)
    )
    assert markdown.startswith("# OANDA Demo Expectancy To Live Gap Mapper V1")


def test_mapper_operator_text_plain():
    text = oanda_demo_expectancy_to_live_gap_mapper_to_operator_text(
        _map(build_sample_missing_live_evidence_gap_mapper_input)
    )
    assert "Expectancy-to-live gap map status" in text


@pytest.mark.parametrize("flag", sorted(PERMISSION_DEFAULTS))
def test_mapper_permissions_false(flag: str):
    assert _map(build_sample_ready_gap_mapper_input).protected_permission_flags[flag] is False


def test_mapper_owner_warning_present():
    assert _map(build_sample_missing_live_evidence_gap_mapper_input).owner_warning == OWNER_WARNING


def test_mapper_live_gap_warning_present():
    assert _map(build_sample_missing_live_evidence_gap_mapper_input).live_gap_warning == LIVE_GAP_WARNING


def test_mapper_ready_gap_review_is_still_not_live_approval():
    text = oanda_demo_expectancy_to_live_gap_mapper_to_operator_text(_map(build_sample_ready_gap_mapper_input))
    assert "Ready gap review is not live approval." in text


def test_mapper_repeated_expectancy_ready_does_not_imply_live_ready():
    assert _map(build_sample_missing_live_evidence_gap_mapper_input).classification == CLASSIFICATION_MISSING


def test_mapper_all_present_evidence_keeps_live_false():
    result = _map(build_sample_ready_gap_mapper_input)
    assert result.classification == CLASSIFICATION_READY
    assert result.live_evidence_bundle_preview["live_evidence_bundle_approved"] is False


@pytest.mark.parametrize(
    "item_id",
    (
        "human_owner_live_exception_approval",
        "credential_boundary_verified",
        "live_account_boundary_verified",
        "demo_account_boundary_verified",
        "kill_switch_verified",
        "timeout_abort_verified",
        "rollback_plan_verified",
        "final_disarm_plan_verified",
        "reconciliation_plan_verified",
        "one_shot_only_scope_verified",
        "no_compounding_scope_verified",
        "no_bank_movement_scope_verified",
        "no_autonomous_loop_scope_verified",
    ),
)
def test_mapper_missing_required_item_blocks_ready_gap_review(item_id: str):
    sample = build_sample_ready_gap_mapper_input()
    statuses = dict(sample.evidence_statuses)
    statuses[item_id] = "MISSING"
    changed = type(sample)(
        expectancy_epic_result=sample.expectancy_epic_result,
        requirement_matrix_result=sample.requirement_matrix_result,
        evidence_statuses=statuses,
        config=sample.config,
    )
    assert map_oanda_demo_expectancy_to_live_evidence_gaps(changed).classification == CLASSIFICATION_PARTIAL


def test_mapper_duplicate_order_guard_requirement_present():
    assert "duplicate_order_guard_verified" in REQUIRED_ITEM_IDS


def test_mapper_monitoring_plan_requirement_present():
    assert "monitoring_plan_verified" in REQUIRED_ITEM_IDS


def test_mapper_audit_log_requirement_present():
    assert "audit_log_plan_verified" in REQUIRED_ITEM_IDS


def test_mapper_post_trade_journal_plan_requirement_present():
    assert "post_trade_journal_plan_verified" in REQUIRED_ITEM_IDS


def test_mapper_order_ticket_review_requirement_present():
    assert "order_ticket_review_verified" in REQUIRED_ITEM_IDS


def test_mapper_read_only_reconciliation_requirement_present():
    assert "read_only_reconciliation_verified" in REQUIRED_ITEM_IDS


def test_mapper_unknown_status_normalizes_to_blocked():
    sample = build_sample_missing_live_evidence_gap_mapper_input()
    item_id = REQUIRED_ITEM_IDS[0]
    statuses = dict(sample.evidence_statuses)
    statuses[item_id] = "UNKNOWN_STATUS"
    changed = type(sample)(
        expectancy_epic_result=sample.expectancy_epic_result,
        requirement_matrix_result=sample.requirement_matrix_result,
        evidence_statuses=statuses,
        config=sample.config,
    )
    result = map_oanda_demo_expectancy_to_live_evidence_gaps(changed)
    assert result.evidence_statuses[item_id] == "BLOCKED"


def test_mapper_output_deterministic_for_missing_sample():
    first = oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
        _map(build_sample_missing_live_evidence_gap_mapper_input)
    )
    second = oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
        _map(build_sample_missing_live_evidence_gap_mapper_input)
    )
    assert first == second


def test_mapper_output_deterministic_for_partial_sample():
    first = oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
        _map(build_sample_partial_live_evidence_gap_mapper_input)
    )
    second = oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
        _map(build_sample_partial_live_evidence_gap_mapper_input)
    )
    assert first == second


def test_mapper_output_deterministic_for_ready_sample():
    first = oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
        _map(build_sample_ready_gap_mapper_input)
    )
    second = oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
        _map(build_sample_ready_gap_mapper_input)
    )
    assert first == second


def test_mapper_unsafe_sample_never_ready():
    assert _map(build_sample_unsafe_gap_mapper_input).classification == CLASSIFICATION_BLOCKED_UNSAFE


def test_mapper_blocked_expectancy_sample_never_ready():
    assert _map(build_sample_blocked_expectancy_gap_mapper_input).classification == CLASSIFICATION_BLOCKED_EXPECTANCY


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
def test_mapper_global_sample_builders_exist(builder):
    assert builder()


@pytest.mark.parametrize(
    "forbidden",
    (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "import subprocess",
        "from subprocess",
        "git add .",
    ),
)
def test_new_module_sources_do_not_use_forbidden_imports_or_git_add_dot(forbidden: str):
    combined = "\n".join(path.read_text(encoding="utf-8") for path in SOURCE_FILES)
    assert forbidden not in combined
