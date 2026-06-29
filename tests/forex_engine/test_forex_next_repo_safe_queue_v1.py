from __future__ import annotations

import json

from automation.forex_engine import forex_next_repo_safe_queue_v1 as module
from automation.forex_engine.evidence_depth_walkforward_sufficiency_v1 import (
    PROTECTED_FALSE_FIELDS,
)


def test_queue_is_finite_non_empty_and_json_serializable():
    result = module.run_forex_next_repo_safe_queue_v1()

    assert result["queue_status"] == "FINITE_REPO_SAFE_QUEUE_READY"
    assert 0 < len(result["next_repo_safe_buckets"]) < 10
    json.dumps(result)


def test_queue_prioritizes_repo_safe_work_before_protected_boundary():
    result = module.run_forex_next_repo_safe_queue_v1()

    assert all(bucket["protected"] is False for bucket in result["next_repo_safe_buckets"])
    assert "broker contact" in result["protected_boundaries"]
    assert "credentials" in result["protected_boundaries"]


def test_next_packet_is_dry_run_and_blocks_protected_actions():
    result = module.run_forex_next_repo_safe_queue_v1()
    packet = module.build_next_codex_packet(result)

    assert packet.startswith("CODEX-ONLY PROMPT")
    assert "MODE\nDRY_RUN" in packet
    assert "does not approve APPLY" in packet
    assert "broker contact" in packet
    assert "credentials" in packet


def test_protected_booleans_remain_false():
    result = module.run_forex_next_repo_safe_queue_v1()

    for field in PROTECTED_FALSE_FIELDS:
        assert result[field] is False
