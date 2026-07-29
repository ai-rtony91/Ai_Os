from automation.orchestration.platform import OrchestrationPlatform, create_platform


def test_platform_consolidates_queue_and_dispatch_without_mutation(tmp_path):
    platform = create_platform(tmp_path)
    queue = platform.queue({"candidates": []})
    dispatch = platform.dispatch({"schema": "AIOS_RUNTIME_EXECUTION_QUEUE.v1", "items": []})

    assert queue["safety"]["queue_mutation"] is False
    assert dispatch["status"] == "NO_DISPATCHABLE_WORK"
    assert dispatch["safety"]["worker_launch"] is False


def test_platform_packet_generator_preserves_safety_gates(tmp_path):
    platform = OrchestrationPlatform(tmp_path)
    result = platform.generate_packet({"action_id": "unsafe_unbounded"})

    assert result["packet_ready"] is False
    assert result["reason_code"] == "allowed_paths_missing"
    assert "No live trading." in result["safety_blocks"]


def test_platform_validator_fails_closed_on_enabled_protected_action(tmp_path):
    platform = OrchestrationPlatform(tmp_path)
    state = {
        "schema": "AIOS_CANONICAL_ORCHESTRATION_SPINE.v1",
        "status": "READY",
        "permissions": {"queue_mutation": False},
        "protected_actions": {"broker_access": True},
    }

    result = platform.validate(state)

    assert result["status"] == "BLOCKED"
    assert result["defects"] == ["unsafe_protected_actions"]
    assert result["grants_approval"] is False


def test_platform_report_reuses_canonical_renderer(tmp_path):
    platform = OrchestrationPlatform(tmp_path)
    state = {
        "status": "READY",
        "coverage": {"classification_coverage_percent": 100, "discovered_item_count": 0, "classified_item_count": 0, "duplicate_item_count": 0, "unclassified_item_count": 0},
        "economic_anchor": {"first_withdrawable_dollar_status": "NOT_VERIFIED", "engineering_hours_status": "NOT_VERIFIED", "verified_engineering_hours_remaining": None, "current_highest_blocker": "NOT_VERIFIED"},
        "queue_plan": {},
        "dependency_graph": {"ready_nodes": [], "blocked_nodes": [], "cyclic_dependencies": []},
        "controller_registry": [],
        "task_catalog": [],
        "next_verified_task": None,
        "owner_action_required": False,
    }
    assert "AI_OS CANONICAL ORCHESTRATION SPINE" in platform.report(state)
