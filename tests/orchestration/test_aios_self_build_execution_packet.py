from automation.orchestration.self_development.aios_self_build_candidate_selector import (
    select_self_build_candidate,
)
from automation.orchestration.self_development.aios_self_build_execution_packet import (
    build_self_build_execution_packet,
)


def test_builds_executable_packet_from_candidate() -> None:
    candidate = select_self_build_candidate({})
    packet = build_self_build_execution_packet(candidate)

    assert packet["schema"] == "AIOS_SELF_BUILD_EXECUTION_PACKET.v1"
    assert packet["packet_id"].endswith("-EXECUTION-PACKET")
    assert packet["objective"] == candidate["objective"]
    assert packet["mode"] == "APPLY_LOCAL_SELF_BUILD"


def test_includes_identity_header() -> None:
    packet = build_self_build_execution_packet(select_self_build_candidate({}))

    assert packet["identity_marker"] == "AIOS-AUTONOMOUS-SELF-BUILD-EXECUTOR-BURN-IN-V1"
    assert packet["supervisor_identity"] == "ChatGPT Supervisor / Human-guided execution authority"
    assert packet["worker_identity"] == "Codex CLI local implementation worker"
    assert packet["zone"] == "AUTONOMOUS_SELF_BUILD_EXECUTION"
    assert packet["approval_authority"] == "Human Owner / Anthony"


def test_includes_validators_allowed_files_and_stop_conditions() -> None:
    packet = build_self_build_execution_packet(select_self_build_candidate({}))

    assert "git diff --check" in packet["validator_chain"]
    assert packet["allowed_files"]
    assert "SOS_ACTIVE" in packet["stop_conditions"]
    assert "PUSH_PR_MERGE_REQUESTED" in packet["stop_conditions"]


def test_includes_commit_push_pr_merge_policy() -> None:
    packet = build_self_build_execution_packet(select_self_build_candidate({}))

    assert packet["commit_policy"] == "LOCAL_COMMIT_ONLY_WITH_APPROVAL"
    assert packet["push_pr_merge_policy"] == "BLOCKED_IN_THIS_PACKET"
    assert packet["safety"]["pushes"] is False
    assert packet["safety"]["creates_pr"] is False
    assert packet["safety"]["merges"] is False


def test_execution_packet_is_data_only_and_does_not_mutate_registry() -> None:
    packet = build_self_build_execution_packet(select_self_build_candidate({}))

    assert packet["safety"]["data_only"] is True
    assert packet["safety"]["writes_files"] is False
    assert packet["safety"]["creates_ready_stage"] is False
    assert packet["safety"]["mutates_registry"] is False
