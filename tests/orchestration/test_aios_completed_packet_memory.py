from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_completed_packet_memory.py"
FOREX_ROADMAP_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_forex_builder_roadmap.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_completed_packet_memory", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_forex_roadmap_module():
    spec = importlib.util.spec_from_file_location("aios_forex_builder_roadmap", FOREX_ROADMAP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "packet_id": "PKT-AIOS-NEXT-SAFE",
        "title": "Build next safe self-build packet",
        "lane": "next-safe-self-build",
        "priority": "high",
        "milestone_value": "high",
        "risk_level": "low",
        "status": "candidate",
        "required_files": ["automation/orchestration/next_safe.py"],
        "validators": ["python -m pytest -p no:cacheprovider tests/orchestration/test_next_safe.py -q"],
    }
    payload.update(overrides)
    return payload


def build_result(**overrides: object) -> dict[str, object]:
    module = load_module()
    payload: dict[str, object] = {
        "candidate_packets": [candidate()],
    }
    payload.update(overrides)
    return module.build_completed_packet_memory(payload)


def assert_preview_only(result: dict[str, object]) -> None:
    assert result["commands_executed"] == []
    assert result["files_written"] == []
    assert result["workers_dispatched"] is False
    assert result["queues_mutated"] is False
    assert result["approvals_mutated"] is False
    safety = result["safety"]
    assert isinstance(safety, dict)
    assert safety["preview_only"] is True
    assert safety["evidence_only"] is True
    assert safety["command_execution"] is False
    assert safety["filesystem_writes"] is False
    assert safety["reports_written"] is False
    assert safety["network_access"] is False


def test_empty_candidates_returns_empty_state_safely() -> None:
    module = load_module()

    result = module.build_completed_packet_memory({})

    assert result["schema"] == "AIOS_COMPLETED_PACKET_MEMORY_SUPPRESSION.v1"
    assert result["suppression_status"] == "empty"
    assert result["active_candidates"] == []
    assert result["suppressed_candidates"] == []
    assert result["next_candidate_available"] is False
    assert result["next_candidate"] is None
    assert_preview_only(result)


def test_completed_packet_id_is_suppressed() -> None:
    result = build_result(completed_packet_ids=["PKT-AIOS-NEXT-SAFE"])

    assert result["active_candidates"] == []
    assert result["suppressed_candidates"][0]["packet_id"] == "PKT-AIOS-NEXT-SAFE"
    assert "completed_packet_id:PKT-AIOS-NEXT-SAFE" in result["suppressed_candidates"][0]["suppression_reasons"]


def test_landed_pr_title_or_lane_suppresses_matching_candidate() -> None:
    result = build_result(
        landed_prs=[
            {
                "title": "Build next safe self-build packet",
                "lane": "next-safe-self-build",
                "pr_number": 732,
                "status": "merged",
            }
        ]
    )

    assert result["active_candidates"] == []
    assert any("landed_pr_match" in reason for reason in result["suppressed_candidates"][0]["suppression_reasons"])


def test_manual_suppression_rule_suppresses_matching_packet() -> None:
    result = build_result(
        manual_suppression_rules=[
            {"packet_id": "PKT-AIOS-NEXT-SAFE", "reason": "operator marked complete"}
        ]
    )

    assert result["active_candidates"] == []
    assert "manual_suppression_rule:operator marked complete" in result["suppressed_candidates"][0]["suppression_reasons"]


def test_cycle_ledger_completion_suppresses_matching_packet() -> None:
    result = build_result(
        cycle_ledger_history=[
            {
                "selected_packet": {"packet_id": "PKT-AIOS-NEXT-SAFE"},
                "status": "complete",
            }
        ]
    )

    assert result["active_candidates"] == []
    assert "cycle_ledger_complete:PKT-AIOS-NEXT-SAFE" in result["suppressed_candidates"][0]["suppression_reasons"]


def test_reopened_packet_is_not_suppressed() -> None:
    result = build_result(
        candidate_packets=[candidate(status="reopened")],
        completed_packet_ids=["PKT-AIOS-NEXT-SAFE"],
    )

    assert result["suppressed_candidates"] == []
    assert result["active_candidates"][0]["packet_id"] == "PKT-AIOS-NEXT-SAFE"


def test_candidate_with_new_required_files_is_not_suppressed() -> None:
    result = build_result(
        candidate_packets=[
            candidate(
                required_files=[
                    "automation/orchestration/old_scope.py",
                    "automation/orchestration/new_scope.py",
                ]
            )
        ],
        completed_packets=[
            {
                "packet_id": "PKT-AIOS-NEXT-SAFE",
                "required_files": ["automation/orchestration/old_scope.py"],
            }
        ],
    )

    assert result["suppressed_candidates"] == []
    assert result["active_candidates"][0]["packet_id"] == "PKT-AIOS-NEXT-SAFE"


def test_validation_failed_repair_candidate_is_not_suppressed() -> None:
    result = build_result(
        candidate_packets=[candidate(validation_status="failed")],
        completed_packet_ids=["PKT-AIOS-NEXT-SAFE"],
    )

    assert result["suppressed_candidates"] == []
    assert result["active_candidates"][0]["packet_id"] == "PKT-AIOS-NEXT-SAFE"


def test_forex_builder_scaffold_candidate_is_not_suppressed() -> None:
    result = build_result(
        candidate_packets=[
            candidate(
                packet_id="PKT-AIOS-FOREX-BUILDER-SCAFFOLD",
                title="Create forex builder scaffold",
                lane="forex-builder-scaffold",
            )
        ],
        completed_packet_ids=["PKT-AIOS-FOREX-BUILDER-SCAFFOLD"],
    )

    assert result["suppressed_candidates"] == []
    assert result["active_candidates"][0]["packet_id"] == "PKT-AIOS-FOREX-BUILDER-SCAFFOLD"


def test_active_candidates_excludes_completed_packets() -> None:
    active = candidate(packet_id="PKT-AIOS-ACTIVE", required_files=["automation/orchestration/active.py"])
    completed = candidate(packet_id="PKT-AIOS-DONE")

    result = build_result(
        candidate_packets=[completed, active],
        completed_packet_ids=["PKT-AIOS-DONE"],
    )

    active_ids = [item["packet_id"] for item in result["active_candidates"]]
    assert "PKT-AIOS-DONE" not in active_ids
    assert "PKT-AIOS-ACTIVE" in active_ids


def test_suppressed_candidates_include_suppression_reasons() -> None:
    result = build_result(completed_packet_ids=["PKT-AIOS-NEXT-SAFE"])
    suppressed = result["suppressed_candidates"][0]

    assert suppressed["packet_id"] == "PKT-AIOS-NEXT-SAFE"
    assert suppressed["candidate"]["packet_id"] == "PKT-AIOS-NEXT-SAFE"
    assert suppressed["suppression_reasons"]
    assert result["suppression_reasons"]["PKT-AIOS-NEXT-SAFE"]


def test_next_candidate_is_first_active_safe_candidate() -> None:
    first = candidate(packet_id="PKT-AIOS-FIRST", required_files=["automation/orchestration/first.py"])
    second = candidate(packet_id="PKT-AIOS-SECOND", required_files=["automation/orchestration/second.py"])

    result = build_result(candidate_packets=[first, second])

    assert result["next_candidate_available"] is True
    assert result["next_candidate"]["packet_id"] == "PKT-AIOS-FIRST"


def test_default_memory_suppresses_selfroute_candidate_evidence_integration() -> None:
    default_candidate = candidate(
        packet_id="PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION",
        title="Connect candidate packet evidence adapter into self-route",
        lane="connect-candidate-evidence-to-selfroute",
        required_files=[
            "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1",
            "tests/orchestration/test_aios_persistent_runtime_supervisor.py",
        ],
    )

    result = build_result(candidate_packets=[default_candidate])

    assert result["active_candidates"] == []
    assert result["suppressed_candidates"][0]["packet_id"] == "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION"
    assert "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION" in result["completed_packet_ids"]


def test_default_memory_includes_landed_forex_canonical_spec() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC" in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    canonical = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
    ][0]
    assert canonical["landed_pr"] == "#737"
    assert canonical["commit"] == "cd012419"
    assert canonical["completion_reason"] == "canonical forex builder spec landed on main"
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md" in canonical["completed_files"]


def test_default_memory_includes_landed_forex_data_schemas_from_pr_742() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS" in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    data_schemas = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS"
    ][0]
    assert data_schemas["landed_pr"] == "#742"
    assert data_schemas["title"] == "Add local forex builder data schema contracts"
    assert data_schemas["completion_reason"] == "local forex builder data schema contracts landed on main"
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_DATA_SCHEMAS.md" in data_schemas["completed_files"]
    assert "automation/forex_engine/schema_contracts.py" in data_schemas["completed_files"]
    assert "tests/forex_engine/test_schema_contracts.py" in data_schemas["completed_files"]


def test_default_memory_includes_completed_backtest_risk_and_dashboard_packets() -> None:
    result = build_result(candidate_packets=[])

    for packet_id in (
        "PKT-AIOS-FOREX-BUILDER-BACKTEST-HARNESS",
        "PKT-AIOS-FOREX-BUILDER-RISK-CONTRACT",
        "PKT-AIOS-FOREX-BUILDER-DASHBOARD-CONTRACT",
    ):
        assert packet_id in result["completed_packet_ids"]
        records = [
            record
            for record in load_module().DEFAULT_COMPLETED_PACKETS
            if record["packet_id"] == packet_id
        ]
        assert records[0]["landed_pr"] == "#743"


def test_default_memory_includes_paper_forward_evidence_v1_completion() -> None:
    result = build_result(candidate_packets=[])

    for packet_id in (
        "PKT-AIOS-FOREX-BUILDER-PAPER-FORWARD-SIMULATOR",
        "PKT-AIOS-FOREX-BUILDER-EVIDENCE-AGGREGATOR",
        "PKT-AIOS-FOREX-BUILDER-MONTH-END-READINESS",
        "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V1",
    ):
        assert packet_id in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    v1 = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V1"
    ][0]
    assert v1["landed_pr"] == "#744"
    assert v1["title"] == "Add paper-forward evidence expansion"
    assert (
        v1["completion_reason"]
        == "local fixture catalog, paper-forward runner, evidence bundle runner, readiness demos, and V1 evidence routing landed on main"
    )
    assert "automation/forex_engine/run_month_end_readiness_demo.py" in v1["completed_files"]
    assert "tests/forex_engine/test_evidence_bundle_runner.py" in v1["completed_files"]


def test_default_memory_includes_paper_forward_evidence_v2_completion() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V2" in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    v2 = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V2"
    ][0]
    assert v2["landed_pr"] == "#745"
    assert v2["title"] == "Add paper-forward evidence V2"
    assert v2["lane"] == "paper-forward-evidence-expansion-v2"
    assert (
        v2["completion_reason"]
        == "paper-forward evidence V2 landed with multi-fixture evidence, regime consistency, V2 demo, readiness/dashboard integration, and safe next selector"
    )
    assert "automation/forex_engine/paper_forward_evidence_v2.py" in v2["completed_files"]
    assert "automation/forex_engine/run_paper_forward_evidence_v2_demo.py" in v2["completed_files"]
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_EVIDENCE_V2.md" in v2["completed_files"]
    assert "tests/forex_engine/test_paper_forward_evidence_v2.py" in v2["completed_files"]


def test_default_memory_includes_risk_governor_completion() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-RISK-GOVERNOR-PAPER-FORWARD-THRESHOLDS" in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    risk_governor = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-RISK-GOVERNOR-PAPER-FORWARD-THRESHOLDS"
    ][0]
    assert risk_governor["landed_pr"] == "#746"
    assert risk_governor["title"] == "Add paper-forward risk governor thresholds"
    assert risk_governor["lane"] == "risk-governor-paper-forward-thresholds"
    assert (
        risk_governor["completion_reason"]
        == "risk-to-reward, expectancy, opportunity capture, cost/slippage stress, and threshold governor landed on main"
    )
    assert "automation/forex_engine/risk_governor_thresholds.py" in risk_governor["completed_files"]
    assert "automation/forex_engine/opportunity_capture.py" in risk_governor["completed_files"]
    assert "automation/forex_engine/run_risk_governor_demo.py" in risk_governor["completed_files"]
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_OPPORTUNITY_CAPTURE.md" in risk_governor["completed_files"]
    assert "tests/forex_engine/test_opportunity_capture.py" in risk_governor["completed_files"]


def test_default_memory_includes_stress_oos_completion() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-PAPER-FORWARD-STRESS-AND-OUT-OF-SAMPLE-V1" in result["completed_packet_ids"]
    records = load_module()._completed_memory_records({})
    stress_oos = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-PAPER-FORWARD-STRESS-AND-OUT-OF-SAMPLE-V1"
    ][0]
    assert stress_oos["landed_pr"] == "#747"
    assert stress_oos["title"] == "Add paper-forward stress and out-of-sample validation"
    assert stress_oos["lane"] == "paper-forward-stress-and-out-of-sample"
    assert (
        stress_oos["completion_reason"]
        == "stress scenarios, OOS validation, heldout fixtures, leave-one-regime/symbol/timeframe checks, combined stress/OOS gate, readiness/dashboard propagation, docs, and tests landed on main"
    )
    assert "automation/forex_engine/paper_forward_stress.py" in stress_oos["completed_files"]
    assert "automation/forex_engine/out_of_sample_validator.py" in stress_oos["completed_files"]
    assert "automation/forex_engine/run_stress_and_oos_demo.py" in stress_oos["completed_files"]
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_AND_OUT_OF_SAMPLE.md" in stress_oos["completed_files"]
    assert "tests/forex_engine/test_out_of_sample_validator.py" in stress_oos["completed_files"]


def test_default_memory_includes_broker_paper_sandbox_readiness_contract_completion() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-BROKER-PAPER-SANDBOX-READINESS-CONTRACT" in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    readiness = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-BROKER-PAPER-SANDBOX-READINESS-CONTRACT"
    ][0]
    assert readiness["landed_pr"] == "#748"
    assert readiness["title"] == "Add broker-paper sandbox readiness contract"
    assert readiness["lane"] == "broker-paper-sandbox-readiness-contract"
    assert (
        readiness["completion_reason"]
        == "broker-paper sandbox readiness contract landed, kept broker-paper blocked as WATCHLIST, and advanced to stress repair"
    )
    assert "automation/forex_engine/broker_paper_sandbox_readiness.py" in readiness["completed_files"]
    assert "automation/forex_engine/run_broker_paper_sandbox_readiness_demo.py" in readiness["completed_files"]
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_READINESS_CONTRACT.md" in readiness["completed_files"]
    assert "tests/forex_engine/test_broker_paper_sandbox_readiness.py" in readiness["completed_files"]


def test_default_memory_includes_stress_repair_completion() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-PAPER-FORWARD-STRESS-REPAIR-V1" in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    repair = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-PAPER-FORWARD-STRESS-REPAIR-V1"
    ][0]
    assert repair["landed_pr"] == "#749"
    assert repair["title"] == "Add paper-forward stress repair"
    assert repair["lane"] == "paper-forward-stress-repair"
    assert (
        repair["completion_reason"]
        == "stress repair diagnostics and conservative filtering/sizing policy landed, improving worst stress PnL while preserving WATCHLIST blockers honestly"
    )
    assert "automation/forex_engine/stress_repair.py" in repair["completed_files"]
    assert "automation/forex_engine/run_stress_repair_demo.py" in repair["completed_files"]
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_REPAIR.md" in repair["completed_files"]
    assert "tests/forex_engine/test_stress_repair.py" in repair["completed_files"]


def test_default_memory_includes_oos_expansion_completion() -> None:
    result = build_result(candidate_packets=[])

    assert "PKT-AIOS-PAPER-FORWARD-OOS-EXPANSION-V1" in result["completed_packet_ids"]
    records = load_module()._completed_memory_records({})
    expansion = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-PAPER-FORWARD-OOS-EXPANSION-V1"
    ][0]
    assert expansion["landed_pr"] == "#750"
    assert expansion["title"] == "Add expanded OOS validation"
    assert expansion["lane"] == "paper-forward-oos-expansion"
    assert (
        expansion["completion_reason"]
        == "expanded deterministic OOS validation landed with 14 fixtures, 29 splits, low-vol degradation blocker exposed, and broker-paper kept blocked"
    )
    assert "automation/forex_engine/oos_expansion.py" in expansion["completed_files"]
    assert "automation/forex_engine/run_oos_expansion_demo.py" in expansion["completed_files"]
    assert "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_EXPANSION.md" in expansion["completed_files"]
    assert "tests/forex_engine/test_oos_expansion.py" in expansion["completed_files"]
    assert expansion["completed_files"] == [
        "automation/forex_engine/oos_expansion.py",
        "automation/forex_engine/run_oos_expansion_demo.py",
        "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_EXPANSION.md",
        "tests/forex_engine/test_oos_expansion.py",
    ]


def test_default_memory_includes_oos_repair_and_backup_metrics_completions() -> None:
    result = build_result(candidate_packets=[])
    records = load_module()._completed_memory_records({})

    assert "PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1" in result["completed_packet_ids"]
    assert "PKT-AIOS-T9-BACKUP-DAILY-WORK-METRICS-SOS-V1" in result["completed_packet_ids"]
    repair = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1"
    ][0]
    backup = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-T9-BACKUP-DAILY-WORK-METRICS-SOS-V1"
    ][0]

    assert repair["landed_pr"] == "#751"
    assert repair["title"] == "Add OOS repair gate"
    assert "automation/forex_engine/oos_repair.py" in repair["completed_files"]
    assert "tests/forex_engine/test_oos_repair.py" in repair["completed_files"]
    assert backup["landed_pr"] == "#752"
    assert backup["title"] == "Add T9 backup daily work metrics and courtesy SOS"
    assert "automation/orchestration/backups/Get-AiOsBackupWorkDelta.ps1" in backup["completed_files"]
    assert "docs/AI_OS/operations/T9_BACKUP_DAILY_WORK_METRICS_POLICY.md" in backup["completed_files"]


def test_default_memory_includes_low_vol_edge_redesign_completion() -> None:
    result = build_result(candidate_packets=[])
    records = load_module()._completed_memory_records({})

    assert "PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1" in result["completed_packet_ids"]
    low_vol = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1"
    ][0]

    assert low_vol["landed_pr"] == "#753"
    assert low_vol["title"] == "Add low-vol edge redesign"
    assert low_vol["lane"] == "forex-low-vol-edge-redesign"
    assert (
        low_vol["completion_reason"]
        == "low-vol edge redesign landed with paper-only low-vol no-trade/reduced-size policy, audit fields, and broker/live blocked"
    )
    assert low_vol["completed_files"] == [
        "automation/forex_engine/low_vol_edge_redesign.py",
        "automation/forex_engine/run_low_vol_edge_redesign_demo.py",
        "docs/trading_lab/AIOS_FOREX_BUILDER_LOW_VOL_EDGE_REDESIGN.md",
        "tests/forex_engine/test_low_vol_edge_redesign.py",
    ]


def test_default_memory_includes_presecurity_gate_completion() -> None:
    result = build_result(candidate_packets=[])
    records = load_module()._completed_memory_records({})

    assert "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1" in result["completed_packet_ids"]
    presecurity = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1"
    ][0]

    assert presecurity["landed_pr"] == "#754"
    assert presecurity["title"] == "Add broker-paper presecurity gate"
    assert presecurity["lane"] == "broker-paper-presecurity-gate"
    assert (
        presecurity["completion_reason"]
        == "presecurity contract blocks credentials, env reads, broker SDKs, network/API, webhooks, schedulers, daemons, broker-paper orders, and live orders before adapter work"
    )
    assert presecurity["completed_files"] == [
        "automation/forex_engine/broker_paper_presecurity_gate.py",
        "automation/forex_engine/run_broker_paper_presecurity_gate_demo.py",
        "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_PRESECURITY_GATE.md",
        "tests/forex_engine/test_broker_paper_presecurity_gate.py",
    ]


def test_default_memory_includes_adapter_stub_contract_completion() -> None:
    result = build_result(candidate_packets=[])
    records = load_module()._completed_memory_records({})

    assert "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT" in result["completed_packet_ids"]
    adapter_stub = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT"
    ][0]

    assert adapter_stub["landed_pr"] == "#755"
    assert adapter_stub["title"] == "Add broker-paper adapter stub contract"
    assert adapter_stub["lane"] == "broker-paper-adapter-stub-contract"
    assert (
        adapter_stub["completion_reason"]
        == "local-only broker-paper adapter stub validates fake dry-run intents and produces simulated/rejected audit records while keeping broker SDK, credentials, network/API, broker-paper orders, and live trading blocked"
    )
    assert adapter_stub["completed_files"] == [
        "automation/forex_engine/broker_paper_adapter_stub_contract.py",
        "automation/forex_engine/run_broker_paper_adapter_stub_contract_demo.py",
        "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_ADAPTER_STUB_CONTRACT.md",
        "tests/forex_engine/test_broker_paper_adapter_stub_contract.py",
    ]


def test_default_memory_includes_dryrun_intent_ledger_completion() -> None:
    result = build_result(candidate_packets=[])
    records = load_module()._completed_memory_records({})

    assert "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1" in result["completed_packet_ids"]
    dryrun_ledger = [
        record
        for record in records
        if record["packet_id"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1"
    ][0]

    assert dryrun_ledger["landed_pr"] == "#756"
    assert dryrun_ledger["title"] == "Add broker-paper dry-run intent ledger"
    assert dryrun_ledger["lane"] == "broker-paper-dryrun-intent-ledger"
    assert (
        dryrun_ledger["completion_reason"]
        == "local-only in-memory broker-paper dry-run intent ledger records fake dry-run intents and stub simulation results while keeping broker SDK, credentials, network/API, file/Reports writes, broker-paper orders, and live trading blocked"
    )
    assert dryrun_ledger["completed_files"] == [
        "automation/forex_engine/broker_paper_dryrun_intent_ledger.py",
        "automation/forex_engine/run_broker_paper_dryrun_intent_ledger_demo.py",
        "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_DRYRUN_INTENT_LEDGER.md",
        "tests/forex_engine/test_broker_paper_dryrun_intent_ledger.py",
    ]


def test_default_memory_includes_landed_supertrend_edge_proof_builder() -> None:
    result = build_result(candidate_packets=[])

    assert "AIOS-EDGE-PROOF-BUILDER-MASTER-V1" in result["completed_packet_ids"]
    assert "PKT-AIOS-FOREX-EDGE-PROOF-SUPERTREND-V1" in result["completed_packet_ids"]
    assert "PKT-AIOS-PAPER-ONLY-SUPERTREND-EDGE-PROOF" in result["completed_packet_ids"]
    records = load_module().DEFAULT_COMPLETED_PACKETS
    supertrend = [
        record
        for record in records
        if record["packet_id"] == "AIOS-EDGE-PROOF-BUILDER-MASTER-V1"
    ][0]
    assert supertrend["landed_pr"] == "#740"
    assert supertrend["title"] == "Add paper-only Supertrend edge proof builder"
    assert supertrend["completion_reason"] == "paper-only Supertrend edge proof builder landed on main"
    assert "automation/forex_engine/indicators.py" in supertrend["completed_files"]
    assert "automation/forex_engine/strategies.py" in supertrend["completed_files"]
    assert "tests/forex_engine/test_edge_gate_policy.py" in supertrend["completed_files"]


def test_forex_canonical_spec_candidate_is_suppressed_by_default_memory() -> None:
    canonical = candidate(
        packet_id="PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC",
        title="Create canonical forex builder product spec",
        lane="forex-builder-spec",
        required_files=[
            "docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md",
            "tests/orchestration/test_aios_forex_builder_roadmap.py",
        ],
    )

    result = build_result(candidate_packets=[canonical])

    assert result["active_candidates"] == []
    assert result["suppressed_candidates"][0]["packet_id"] == "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
    assert (
        "completed_packet_id:PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
        in result["suppressed_candidates"][0]["suppression_reasons"]
    )


def test_forex_data_schemas_candidate_is_suppressed_by_pr_742_default_memory() -> None:
    data_schemas = candidate(
        packet_id="PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS",
        title="Define forex builder local data schemas",
        lane="forex-builder-data-schemas",
        required_files=[
            "docs/trading_lab/AIOS_FOREX_BUILDER_DATA_SCHEMAS.md",
            "automation/forex_engine/schema_contracts.py",
            "tests/forex_engine/test_schema_contracts.py",
        ],
    )

    result = build_result(candidate_packets=[data_schemas])

    assert result["active_candidates"] == []
    assert result["suppressed_candidates"][0]["packet_id"] == "PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS"
    assert (
        "completed_packet_id:PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS"
        in result["suppressed_candidates"][0]["suppression_reasons"]
    )


def test_supertrend_edge_proof_packet_id_is_suppressed_by_default_memory() -> None:
    supertrend = candidate(
        packet_id="AIOS-EDGE-PROOF-BUILDER-MASTER-V1",
        title="Add paper-only Supertrend edge proof builder",
        lane="paper-only-supertrend-edge-proof-builder",
        required_files=[
            "automation/forex_engine/indicators.py",
            "automation/forex_engine/strategies.py",
            "automation/forex_engine/costs.py",
            "automation/forex_engine/metrics.py",
            "automation/forex_engine/edge_gate_policy.py",
            "automation/forex_engine/daily_edge_report.py",
        ],
    )

    result = build_result(candidate_packets=[supertrend])

    assert result["active_candidates"] == []
    assert result["suppressed_candidates"][0]["packet_id"] == "AIOS-EDGE-PROOF-BUILDER-MASTER-V1"
    assert (
        "completed_packet_id:AIOS-EDGE-PROOF-BUILDER-MASTER-V1"
        in result["suppressed_candidates"][0]["suppression_reasons"]
    )


def test_supertrend_edge_proof_alternate_packet_ids_are_suppressed_by_default_memory() -> None:
    for packet_id in (
        "PKT-AIOS-FOREX-EDGE-PROOF-SUPERTREND-V1",
        "PKT-AIOS-PAPER-ONLY-SUPERTREND-EDGE-PROOF",
    ):
        result = build_result(
            candidate_packets=[
                candidate(
                    packet_id=packet_id,
                    title="Add paper-only Supertrend edge proof builder",
                    lane="paper-only-supertrend-edge-proof-builder",
                    required_files=["automation/forex_engine/indicators.py"],
                )
            ]
        )

        assert result["active_candidates"] == []
        assert result["suppressed_candidates"][0]["packet_id"] == packet_id
        assert f"completed_packet_id:{packet_id}" in result["suppressed_candidates"][0]["suppression_reasons"]


def test_forex_roadmap_advances_beyond_data_schemas_after_pr_742_and_handoffs() -> None:
    memory = load_module()
    roadmap = load_forex_roadmap_module()
    roadmap_result = roadmap.build_forex_builder_roadmap({})

    result = memory.build_completed_packet_memory(
        {"candidate_packets": roadmap_result["roadmap_candidates"]}
    )

    assert result["suppressed_candidates"][0]["packet_id"] == "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
    assert result["next_candidate"]["packet_id"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1"
    active_ids = [item["packet_id"] for item in result["active_candidates"]]
    assert "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC" not in active_ids
    assert "PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS" not in active_ids
    assert "PKT-AIOS-FOREX-BUILDER-BACKTEST-HARNESS" not in active_ids
    assert "PKT-AIOS-FOREX-BUILDER-RISK-CONTRACT" not in active_ids
    assert "PKT-AIOS-FOREX-BUILDER-DASHBOARD-CONTRACT" not in active_ids
    assert "PKT-AIOS-FOREX-BUILDER-PAPER-FORWARD-SIMULATOR" not in active_ids
    assert "PKT-AIOS-FOREX-BUILDER-EVIDENCE-AGGREGATOR" not in active_ids
    assert "PKT-AIOS-FOREX-BUILDER-MONTH-END-READINESS" not in active_ids
    assert "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V1" not in active_ids
    assert "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V2" not in active_ids
    assert "PKT-AIOS-RISK-GOVERNOR-PAPER-FORWARD-THRESHOLDS" not in active_ids
    assert "PKT-AIOS-PAPER-FORWARD-STRESS-AND-OUT-OF-SAMPLE-V1" not in active_ids
    assert "PKT-AIOS-BROKER-PAPER-SANDBOX-READINESS-CONTRACT" not in active_ids
    assert "PKT-AIOS-PAPER-FORWARD-STRESS-REPAIR-V1" not in active_ids
    assert "PKT-AIOS-PAPER-FORWARD-OOS-EXPANSION-V1" not in active_ids
    assert "PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1" not in active_ids
    assert "PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1" not in active_ids
    assert "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1" not in active_ids
    assert "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT" not in active_ids
    assert "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1" not in active_ids
    assert active_ids[0] == "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1"


def test_forex_roadmap_memory_preserves_non_live_safety_flags() -> None:
    memory = load_module()
    roadmap = load_forex_roadmap_module()
    roadmap_result = roadmap.build_forex_builder_roadmap({})

    result = memory.build_completed_packet_memory(
        {"candidate_packets": roadmap_result["roadmap_candidates"]}
    )

    for item in result["active_candidates"]:
        assert item["non_live_only"] is True
        assert item["broker_allowed"] is False
        assert item["live_trading_allowed"] is False
        assert item["credentials_allowed"] is False
        assert item["orders_allowed"] is False
        assert item["webhooks_allowed"] is False


def test_forex_builder_alignment_is_present() -> None:
    result = build_result()
    alignment = result["forex_builder_alignment"]

    assert alignment["proof_target"] == "industrial-grade forex bot builder"
    assert alignment["factory_status"] == "AIOS is the factory."
    assert alignment["proof_product"] == "forex is the first proof product"
    assert "legitimate validated repo work" in alignment["daily_contribution_policy"]
    assert "protected downstream gate" in alignment["future_gate_warning"]
    assert alignment["aligned"] is True
    assert "no broker/live/secrets" in alignment["milestone"]
    assert alignment["requires_future_gates_before_execution"] is True


def test_commands_executed_is_empty() -> None:
    assert build_result()["commands_executed"] == []


def test_files_written_is_empty() -> None:
    assert build_result()["files_written"] == []


def test_workers_dispatched_false() -> None:
    assert build_result()["workers_dispatched"] is False


def test_queues_mutated_false() -> None:
    assert build_result()["queues_mutated"] is False


def test_approvals_mutated_false() -> None:
    assert build_result()["approvals_mutated"] is False


def test_safety_preview_only_true() -> None:
    assert build_result()["safety"]["preview_only"] is True


def test_source_does_not_import_subprocess_network_or_file_write_tools() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "import subprocess",
        "from subprocess",
        "import requests",
        "import socket",
        "import urllib",
        "http.client",
        "open(",
        "write_text",
        "write_bytes",
        "with open",
        "os.system",
        "system(",
        "start-process",
    ]:
        assert forbidden not in source
