from __future__ import annotations

from automation.bridge.aios_phase_bridge import phase2


def test_phase2_generates_ready_and_blocked_samples(tmp_path):
    payload = phase2(tmp_path, "2026-06-08T00:00:00Z")
    assert payload["valid_sample"]["status"] == "APPLY_READY"
    assert payload["blocked_sample"]["status"] == "BLOCKED"
    assert (tmp_path / "Reports/phase_0_to_4_bridge/phase2_approval_compressor_result.json").exists()

