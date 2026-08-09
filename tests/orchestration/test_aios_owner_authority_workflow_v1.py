import json

import pytest

from automation.orchestration.aios_owner_authority_workflow_v1 import (
    OwnerAuthorityManifestError,
    build_owner_authority_plan,
    first_pending_owner_bundle,
    load_manifest,
    phase_execution_mode,
    validate_manifest,
)


def test_manifest_is_exactly_17_phases_and_at_most_four_owner_checkpoints():
    manifest = load_manifest()
    plan = build_owner_authority_plan(manifest)

    assert [phase["phase_id"] for phase in manifest["phases"]] == list(range(1, 18))
    assert plan["phase_count"] == 17
    assert plan["owner_checkpoint_count"] == 4
    assert plan["owner_checkpoint_count"] <= plan["maximum_owner_checkpoints"]
    assert plan["protected_actions_remain_blocked"] is True


def test_owner_phases_are_consolidated_without_hiding_non_delegable_actions():
    plan = build_owner_authority_plan(load_manifest())
    bundles = {bundle["bundle_id"]: bundle for bundle in plan["bundles"]}

    assert 9 in bundles["OWNER-BUNDLE-2-DEVICE-IDENTITY"]["phase_ids"]
    assert "PHYSICAL_DEVICE" in bundles["OWNER-BUNDLE-2-DEVICE-IDENTITY"]["authorities"]
    assert 16 in bundles["OWNER-BUNDLE-3-RUNTIME-SECRETS"]["phase_ids"]
    assert "SECRET_ACCESS" in bundles["OWNER-BUNDLE-3-RUNTIME-SECRETS"]["authorities"]
    assert bundles["OWNER-BUNDLE-4-LOCATION-PRIVACY"]["phase_ids"] == [17]


def test_unapproved_owner_phase_is_prepare_only_and_approved_bundle_can_resume_ai():
    manifest = load_manifest()
    phase9 = manifest["phases"][8]

    assert phase_execution_mode(phase9) == "AI_PREPARE_ONLY"
    assert phase_execution_mode(
        phase9, approved_bundle_ids={"OWNER-BUNDLE-2-DEVICE-IDENTITY"}
    ) == "AI_EXECUTE_AFTER_OWNER_RECEIPT"


def test_ai_only_phases_do_not_require_owner_checkpoint():
    manifest = load_manifest()
    for phase_id in (1, 12, 13):
        phase = manifest["phases"][phase_id - 1]
        assert phase_execution_mode(phase) == "AI_EXECUTE"


def test_first_pending_owner_bundle_skips_approved_batches():
    plan = build_owner_authority_plan(load_manifest())
    first = first_pending_owner_bundle(
        plan, approved_bundle_ids={"OWNER-BUNDLE-1-POLICY"}
    )
    assert first["bundle_id"] == "OWNER-BUNDLE-2-DEVICE-IDENTITY"


def test_manifest_rejects_missing_or_parallel_phase_identity():
    manifest = load_manifest()
    broken = json.loads(json.dumps(manifest))
    broken["phases"][3]["phase_id"] = 99

    with pytest.raises(OwnerAuthorityManifestError):
        validate_manifest(broken)
