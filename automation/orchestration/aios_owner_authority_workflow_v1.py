"""Consolidated owner-authority checkpoint planning for the AIOS 17-phase gateway program.

This module is deliberately non-authoritative. It does not grant approvals, enroll
devices, handle secrets, deploy runtimes, or execute protected actions. It turns
the canonical phase manifest into a small set of owner-action bundles so AI work
can be prepared behind protected gates without repeated operator interruptions.
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable, Mapping

MANIFEST_SCHEMA = "aios.owner_authority_phases.v1"
PLAN_SCHEMA = "aios.owner_authority_plan.v1"
EXPECTED_PHASE_IDS = tuple(range(1, 18))
DEFAULT_MANIFEST_PATH = Path(__file__).with_name("AIOS_OWNER_AUTHORITY_PHASES_V1.json")

ALLOWED_OWNER_AUTHORITIES = frozenset(
    {
        "NONE",
        "POLICY_ACCEPTANCE",
        "RISK_ACCEPTANCE",
        "EXTERNAL_ACCOUNT",
        "PHYSICAL_DEVICE",
        "DEPLOYMENT",
        "AUTHORITY_BOUNDARY",
        "SECRET_ACCESS",
        "PRIVACY_CONSENT",
    }
)


class OwnerAuthorityManifestError(ValueError):
    """Raised when the Part B manifest is structurally unsafe or inconsistent."""


def _as_nonempty_string(value: Any, field: str) -> str:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise OwnerAuthorityManifestError(f"{field} must be a non-empty string")
    return text


def load_manifest(path: str | Path | None = None) -> dict[str, Any]:
    manifest_path = Path(path) if path is not None else DEFAULT_MANIFEST_PATH
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    validate_manifest(manifest)
    return manifest


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise OwnerAuthorityManifestError("unexpected manifest schema")
    if manifest.get("program") != "AIOS_17_PHASE_OWNER_AUTHORITY_WORKFLOW":
        raise OwnerAuthorityManifestError("unexpected program identity")
    if manifest.get("mode") != "PREPARE_BEHIND_GATE":
        raise OwnerAuthorityManifestError("owner workflow must remain PREPARE_BEHIND_GATE")

    phases = manifest.get("phases")
    if not isinstance(phases, list):
        raise OwnerAuthorityManifestError("phases must be a list")

    phase_ids: list[int] = []
    seen_bundles: set[str] = set()
    for phase in phases:
        if not isinstance(phase, Mapping):
            raise OwnerAuthorityManifestError("each phase must be an object")

        phase_id = phase.get("phase_id")
        if not isinstance(phase_id, int):
            raise OwnerAuthorityManifestError("phase_id must be an integer")
        phase_ids.append(phase_id)

        _as_nonempty_string(phase.get("name"), f"phase {phase_id} name")
        authority = _as_nonempty_string(
            phase.get("owner_authority"), f"phase {phase_id} owner_authority"
        )
        if authority not in ALLOWED_OWNER_AUTHORITIES:
            raise OwnerAuthorityManifestError(
                f"phase {phase_id} has unsupported owner_authority {authority}"
            )

        bundle_id = phase.get("owner_bundle")
        owner_action = phase.get("owner_action")
        if authority == "NONE":
            if bundle_id is not None or owner_action is not None:
                raise OwnerAuthorityManifestError(
                    f"phase {phase_id} cannot define owner bundle/action when authority is NONE"
                )
        else:
            bundle = _as_nonempty_string(bundle_id, f"phase {phase_id} owner_bundle")
            _as_nonempty_string(owner_action, f"phase {phase_id} owner_action")
            seen_bundles.add(bundle)

    if tuple(phase_ids) != EXPECTED_PHASE_IDS:
        raise OwnerAuthorityManifestError("phases must be exactly 1 through 17 in order")

    maximum = manifest.get("maximum_owner_checkpoints")
    if not isinstance(maximum, int) or maximum < 1:
        raise OwnerAuthorityManifestError("maximum_owner_checkpoints must be a positive integer")
    if len(seen_bundles) > maximum:
        raise OwnerAuthorityManifestError("manifest exceeds maximum_owner_checkpoints")


def build_owner_authority_plan(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Group protected phases into the smallest declared owner-action bundles."""

    validate_manifest(manifest)
    automated_phase_ids: list[int] = []
    owner_phase_ids: list[int] = []
    bundles: "OrderedDict[str, dict[str, Any]]" = OrderedDict()

    for phase in manifest["phases"]:
        phase_id = int(phase["phase_id"])
        authority = str(phase["owner_authority"])
        if authority == "NONE":
            automated_phase_ids.append(phase_id)
            continue

        owner_phase_ids.append(phase_id)
        bundle_id = str(phase["owner_bundle"])
        bundle = bundles.setdefault(
            bundle_id,
            {"bundle_id": bundle_id, "phase_ids": [], "authorities": [], "actions": []},
        )
        bundle["phase_ids"].append(phase_id)
        if authority not in bundle["authorities"]:
            bundle["authorities"].append(authority)
        action = str(phase["owner_action"])
        if action not in bundle["actions"]:
            bundle["actions"].append(action)

    return {
        "schema": PLAN_SCHEMA,
        "program": manifest["program"],
        "mode": "PREPARE_BEHIND_GATE",
        "phase_count": len(manifest["phases"]),
        "automated_phase_ids": automated_phase_ids,
        "owner_phase_ids": owner_phase_ids,
        "owner_checkpoint_count": len(bundles),
        "maximum_owner_checkpoints": manifest["maximum_owner_checkpoints"],
        "bundles": list(bundles.values()),
        "protected_actions_remain_blocked": True,
    }


def phase_execution_mode(
    phase: Mapping[str, Any],
    approved_bundle_ids: Iterable[str] = (),
) -> str:
    """Return the permitted mode for one phase using trusted upstream approvals.

    The caller is responsible for validating that an approval receipt is genuine.
    This function never validates identity or grants authority by itself.
    """

    authority = str(phase.get("owner_authority", ""))
    if authority not in ALLOWED_OWNER_AUTHORITIES:
        raise OwnerAuthorityManifestError("phase owner_authority is invalid")
    if authority == "NONE":
        return "AI_EXECUTE"

    bundle_id = _as_nonempty_string(phase.get("owner_bundle"), "owner_bundle")
    approved = {str(item) for item in approved_bundle_ids}
    if bundle_id in approved:
        return "AI_EXECUTE_AFTER_OWNER_RECEIPT"
    return "AI_PREPARE_ONLY"


def first_pending_owner_bundle(
    plan: Mapping[str, Any],
    approved_bundle_ids: Iterable[str] = (),
) -> dict[str, Any] | None:
    if plan.get("schema") != PLAN_SCHEMA:
        raise OwnerAuthorityManifestError("unexpected plan schema")
    approved = {str(item) for item in approved_bundle_ids}
    for bundle in plan.get("bundles", []):
        if str(bundle.get("bundle_id")) not in approved:
            return dict(bundle)
    return None
