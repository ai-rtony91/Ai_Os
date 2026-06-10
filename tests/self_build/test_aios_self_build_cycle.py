from __future__ import annotations

from pathlib import Path

from automation.self_build.aios_self_build_cycle import decide_self_build_cycle


def test_self_build_cycle_fails_closed_when_inputs_missing(tmp_path: Path) -> None:
    payload = decide_self_build_cycle(tmp_path, output_root=Path("Reports/self_build_cycle"))

    assert payload["decision_label"] == "BLOCKED_MISSING_INPUTS"
    assert payload["requires_human"] is True
    assert payload["safety_status"] == "SAFE_OBSERVE_ONLY"
    assert payload["emitted_actions"] == []
    assert payload["missing_inputs"]
    assert Path(payload["evidence_path"]).exists()
    assert Path(payload["report_path"]).exists()


def test_self_build_cycle_emits_no_action_commands(tmp_path: Path) -> None:
    input_root = tmp_path / "Reports/generated/phase_0_to_4_bridge"
    input_root.mkdir(parents=True)
    for name in (
        "phase0_infrastructure_inventory.json",
        "phase1_wiring_map.json",
        "phase2_approval_compressor_result.json",
        "phase3_governance_enforcement.json",
    ):
        (input_root / name).write_text("{}", encoding="utf-8")

    payload = decide_self_build_cycle(tmp_path, output_root=Path("Reports/self_build_cycle"))

    assert payload["decision_label"] == "PROTECTED_ACTION_REQUIRED"
    assert payload["requires_human"] is True
    assert payload["safety_status"] == "SAFE_OBSERVE_ONLY"
    assert payload["emitted_actions"] == []
    forbidden = ("powershell", "merge", "apply", "broker", "live", "secret", "order")
    assert not any(
        token in str(action).lower()
        for action in payload["emitted_actions"]
        for token in forbidden
    )
