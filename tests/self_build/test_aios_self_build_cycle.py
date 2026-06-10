from __future__ import annotations

from pathlib import Path

from automation.self_build.aios_self_build_cycle import decide_self_build_cycle


def test_self_build_cycle_wrapper_uses_canonical_modules(tmp_path: Path) -> None:
    payload = decide_self_build_cycle(tmp_path, output_root=Path("Reports/self_build_cycle"))

    assert payload["canonical_modules"]["composer"].endswith("aios_self_build_cycle_composer.py")
    assert payload["canonical_modules"]["persister"].endswith("aios_self_build_evidence_persister.py")
    assert payload["cycle_id"]
    assert payload["decision"]
    assert payload["requires_human"] is True
    assert payload["safety_status"] == "SAFE_OBSERVE_ONLY"
    assert payload["emitted_actions"] == []
    assert Path(payload["evidence_path"]).exists()
    assert Path(payload["report_path"]).exists()
    assert Path(payload["canonical_persist_result"]["json_path"]).exists()


def test_self_build_cycle_wrapper_emits_no_action_commands(tmp_path: Path) -> None:
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

    assert payload["requires_human"] is True
    assert payload["safety_status"] == "SAFE_OBSERVE_ONLY"
    assert payload["emitted_actions"] == []
    forbidden = ("powershell", "merge", "apply", "broker", "live", "secret", "order")
    assert not any(
        token in str(action).lower()
        for action in payload["emitted_actions"]
        for token in forbidden
    )
