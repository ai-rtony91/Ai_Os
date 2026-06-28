"""Tests for the full overnight work runner module."""

from pathlib import Path

from automation.forex_engine import forex_full_overnight_work_runner_v1 as module


def test_default_owner_input_returns_expected_defaults():
    result = module.evaluate_forex_full_overnight_work_runner()
    assert result["runner_status"] == "FULL_OVERNIGHT_RUNNER_READY_FOR_OWNER_HOST_EXECUTION"
    assert result["runner_mode"] == "HOST_LOOP_READY"
    assert result["active_anchor"] == "PR_1196_OVERNIGHT_CONTRACT_MERGED"
    assert result["flow1_anchor"] == "PR_1194_FLOW1_MERGED"
    assert result["owner_live_capital_intent_usd"] == 1000
    assert result["requested_max_open_positions"] == 4
    assert result["requested_quantity_scale"] == 4.0
    assert result["target_return_band"] == "100_TO_120_PERCENT"
    assert result["runtime_objective"] == "22_HOURS_PER_DAY_6_DAYS_PER_WEEK"
    assert result["next_packet_id"] == "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1"
    assert result["untracked_file_policy"] == "CLASSIFY_AND_ALLOW_ONLY_ACTIVE_SCOPE"
    assert result["max_runner_cycles_default"] == 12
    assert result["max_runner_minutes_default"] == 480


def test_continue_action_sets_ready_mode():
    result = module.evaluate_forex_full_overnight_work_runner(
        {"runner_action": "CONTINUE", "owner_attestation": True}
    )
    assert result["runner_status"] == "FULL_OVERNIGHT_RUNNER_READY_TO_CONTINUE"
    assert result["runner_mode"] == "CONTINUE_READY"
    assert result["overnight_loop_status"] == "READY_FOR_HOST_LOOP"
    assert result["publish_status"] == "READY_AFTER_HOST_VALIDATION"


def test_pause_action():
    result = module.evaluate_forex_full_overnight_work_runner({"runner_action": "PAUSE"})
    assert result["runner_status"] == "FULL_OVERNIGHT_RUNNER_PAUSED_BY_OWNER"
    assert result["runner_mode"] == "PAUSED"


def test_stop_action():
    result = module.evaluate_forex_full_overnight_work_runner({"runner_action": "STOP"})
    assert result["runner_status"] == "FULL_OVERNIGHT_RUNNER_STOPPED_BY_OWNER"
    assert result["runner_mode"] == "STOPPED"


def test_classify_action():
    result = module.evaluate_forex_full_overnight_work_runner(
        {
            "runner_action": "CLASSIFY",
            "git_status_lines": ["?? scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py"],
        }
    )
    assert result["runner_status"] == "FULL_OVERNIGHT_RUNNER_CLASSIFIED_WORKTREE"
    assert result["runner_mode"] == "CLASSIFY_READY"
    assert "can_continue" in result["path_classification"]


def test_select_next_packet_action():
    queue = module.build_active_packet_queue()
    result = module.evaluate_forex_full_overnight_work_runner(
        {"runner_action": "SELECT_NEXT", "completed_packets": [queue[0]["packet_id"]]}
    )
    assert result["runner_status"] == "FULL_OVERNIGHT_RUNNER_NEXT_PACKET_SELECTED"
    assert result["runner_mode"] == "SELECT_NEXT_READY"
    assert result["selected_next_packet"]["packet_id"] == queue[1]["packet_id"]


def test_external_gate_stop_action():
    result = module.evaluate_forex_full_overnight_work_runner(
        {"runner_action": "EXTERNAL_GATE_STOP"}
    )
    assert result["runner_status"] == "FULL_OVERNIGHT_RUNNER_STOPPED_AT_EXTERNAL_GATE"
    assert result["runner_mode"] == "EXTERNAL_GATE_STOP"
    assert result["external_gate_stop"] is not None


def test_render_next_action_queue_handles_null_external_gate_stop():
    result = module.evaluate_forex_full_overnight_work_runner()
    result["external_gate_stop"] = None
    queue_text = module.render_next_action_queue(result)
    assert "NOT_TRIGGERED" in queue_text


def test_build_active_packet_queue_order():
    queue = module.build_active_packet_queue()
    assert len(queue) == 3
    assert queue[0]["packet_id"] == "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1"
    assert queue[0]["flow_id"] == "FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE"
    assert queue[1]["packet_id"] == "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1"
    assert queue[1]["flow_id"] == "FLOW_3_PROFIT_LOOP_LIVE_WEEK_VACATION_GATE"
    assert queue[2]["packet_id"] == "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1"


def test_landed_anchor_map_contains_required_keys():
    anchor_map = module.build_known_landed_anchor_map()
    for key in {
        "PR_1192_P14_FINAL_REHEARSAL",
        "PR_1193_CONTINUOUS_BRIDGE_CONTROLLER",
        "PR_1194_FLOW1_ACTIVE_EXECUTION_AUTHORITY",
        "PR_1196_OVERNIGHT_END_TO_END_CONTRACT",
    }:
        assert key in anchor_map


def test_external_gate_stop_map_contains_all_gates():
    gates = {entry["gate_id"] for entry in module.build_external_gate_stop_map()}
    required = {
        "OWNER_INPUT_REQUIRED",
        "BROKER_SNAPSHOT_REQUIRED",
        "BROKER_CONNECTION_REQUIRED",
        "CREDENTIAL_GATE_REQUIRED",
        "DEMO_EXECUTION_AUTHORITY_REQUIRED",
        "TRADE_EVIDENCE_REQUIRED",
        "REALIZED_PL_REQUIRED",
        "LIVE_EXCEPTION_REQUIRED",
        "REAL_MONEY_APPROVAL_REQUIRED",
        "RUNTIME_SUPERVISOR_REQUIRED",
        "SOS_ALERT_PROOF_REQUIRED",
        "VACATION_MODE_PROOF_REQUIRED",
    }
    assert required.issubset(gates)

def test_classify_git_status_paths_allows_and_blocks_scope():
    allowed = [
        "scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py",
        "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json",
    ]
    allowed_result = module.classify_git_status_paths(
        ["?? scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py"],
        allowed,
    )
    assert allowed_result["can_continue"]
    assert allowed_result["action"] == "CONTINUE_VALIDATE"
    assert allowed_result["blocked_paths"] == []

    disallowed_result = module.classify_git_status_paths(
        ["?? outside/path.py", " M bad.py"],
        allowed,
    )
    assert not disallowed_result["can_continue"]
    assert disallowed_result["action"] == "STOP_DIRTY_SCOPE"
    assert "outside/path.py" in disallowed_result["blocked_paths"]
    assert "bad.py" in disallowed_result["blocked_paths"]

    secret_result = module.classify_git_status_paths(
        ["?? scripts/.env"],
        allowed,
    )
    assert not secret_result["can_continue"]
    assert "scripts/.env" in secret_result["blocked_secret_like_paths"]


def test_select_next_packet_skips_completed():
    queue = module.build_active_packet_queue()
    selected, index = module.select_next_packet(queue, [queue[0]["packet_id"]])
    assert selected["packet_id"] == queue[1]["packet_id"]
    assert index == 1


def test_checkpoint_includes_next_packet_id():
    result = module.evaluate_forex_full_overnight_work_runner()
    checkpoint = module.build_checkpoint(result)
    assert checkpoint["next_packet_id"] == result["next_packet_id"]


def test_generated_artifacts_exist_and_no_banned_tokens():
    module.generate_artifacts()
    expected_paths = [
        module.JSON_REPORT_PATH,
        module.REPORT_PATH,
        module.QUEUE_PATH,
        module.CHECKPOINT_PATH,
        module.ACTIVE_PACKET_QUEUE_PATH,
        module.EXTERNAL_GATE_STOP_PATH,
        module.OWNER_HANDOFF_PATH,
        module.NEXT_CODEX_PROMPT_PATH,
    ]
    for path in expected_paths:
        assert path.exists()

    for path in expected_paths:
        text = path.read_text(encoding="utf-8")
        assert not module.contains_banned_output_tokens(text)

    for token in module.BANNED_OUTPUT_TOKENS:
        assert token.lower() not in module.JSON_REPORT_PATH.read_text(
            encoding="utf-8"
        ).lower()
    assert not module.contains_banned_output_tokens(module.JSON_REPORT_PATH.read_text(encoding="utf-8"))


def test_required_supporting_artifacts_exist():
    assert Path(
        "scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py"
    ).exists()
    assert Path(
        "scripts/forex_delivery/validate_forex_full_overnight_work_runner_v1.ps1"
    ).exists()
    assert Path(
        "scripts/forex_delivery/publish_forex_full_overnight_work_runner_v1.ps1"
    ).exists()
    assert Path(
        "scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1"
    ).exists()
    assert Path("docs/governance/programs/contracts/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.md").exists()


def test_next_codex_prompt_default_flow2():
    module.generate_artifacts()
    prompt_text = module.NEXT_CODEX_PROMPT_PATH.read_text(encoding="utf-8")
    assert "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1" in prompt_text
