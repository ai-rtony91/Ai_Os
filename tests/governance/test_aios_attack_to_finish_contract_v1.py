from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/governance/AIOS_ATTACK_TO_FINISH_CONTRACT_V1.md"
SCHEMA_PATH = ROOT / "schemas/aios/orchestration/AIOS_ATTACK_TO_FINISH_CONTRACT.v1.schema.json"


REQUIRED_FIELDS = {
    "blocker_id",
    "blocker_status",
    "exact_blocker",
    "canonical_owner_file",
    "test_file",
    "runner_script",
    "missing_evidence_field",
    "unlock_status_required",
    "next_packet_name",
    "owner_action_required",
    "stop_condition",
    "no_bloat_guard",
}


REQUIRED_STATUSES = {
    "PROVEN",
    "PARTIAL",
    "NOT_PROVEN",
    "BLOCKED",
    "REVIEW_REQUIRED",
    "READY_FOR_OWNER_REVIEW",
    "OWNER_APPROVED",
    "COMPLETE",
}


def test_contract_doc_has_required_sections_and_fields():
    text = CONTRACT_PATH.read_text(encoding="utf-8")

    for section_number in range(1, 14):
        assert f"## {section_number}." in text

    for field in REQUIRED_FIELDS:
        assert f"- {field}" in text or f"- `{field}`" in text

    for status in REQUIRED_STATUSES:
        assert f"`{status}`" in text

    assert "Do not create a second source-of-truth map." in text
    assert "ATTACK_TO_FINISH:" in text


def test_schema_declares_required_fields_and_status_values():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    attack = schema["properties"]["ATTACK_TO_FINISH"]

    assert set(attack["required"]) == REQUIRED_FIELDS
    assert set(schema["$defs"]["status"]["enum"]) == REQUIRED_STATUSES
    assert schema["additionalProperties"] is False
    assert attack["additionalProperties"] is False


def test_existing_orchestration_owners_point_to_contract():
    expected_path = "docs/governance/AIOS_ATTACK_TO_FINISH_CONTRACT_V1.md"
    expected_schema = "schemas/aios/orchestration/AIOS_ATTACK_TO_FINISH_CONTRACT.v1.schema.json"

    checked_files = [
        ROOT / "docs/governance/source-of-truth-map.md",
        ROOT / "automation/orchestration/README.md",
        ROOT / "docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md",
    ]

    for path in checked_files:
        text = path.read_text(encoding="utf-8")
        assert expected_path in text

    schema_index = (ROOT / "schemas/aios/orchestration/ORCHESTRATION_SCHEMA_INDEX.json").read_text(
        encoding="utf-8"
    )
    assert expected_schema in schema_index
