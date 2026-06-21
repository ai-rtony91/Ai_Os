from automation.forex_engine.read_only_probe_skeleton_i_v1 import (
    ReadOnlyProbeSkeleton,
    evaluate_read_only_probe,
)


def test_read_only_probe_is_ready():
    probe = ReadOnlyProbeSkeleton(probe_id="probe-001")

    result = evaluate_read_only_probe(probe)

    assert result.ready is True
    assert result.blocked_reasons == ()


def test_missing_probe_id_blocks_probe():
    probe = ReadOnlyProbeSkeleton(probe_id="")

    result = evaluate_read_only_probe(probe)

    assert result.ready is False
    assert "probe_id_missing" in result.blocked_reasons


def test_blocked_probe_state_is_preserved():
    probe = ReadOnlyProbeSkeleton(
        probe_id="probe-001",
        blocked_reasons=("manual_probe_block",),
    )

    result = evaluate_read_only_probe(probe)

    assert result.ready is False
    assert "manual_probe_block" in result.blocked_reasons


def test_replay_and_evidence_references_are_preserved():
    probe = ReadOnlyProbeSkeleton(
        probe_id="probe-001",
        replay_references=("replay-002", "replay-001"),
        evidence_references=("evidence-001",),
    )

    result = evaluate_read_only_probe(probe)

    assert result.replay_references == ("replay-001", "replay-002")
    assert result.evidence_references == ("evidence-001",)


def test_prohibited_probe_capability_is_rejected():
    probe = ReadOnlyProbeSkeleton(
        probe_id="probe-001",
        capabilities=("read_only_probe_planning", "network_transport"),
    )

    result = evaluate_read_only_probe(probe)

    assert result.ready is False
    assert "prohibited_probe_capability:network_transport" in result.blocked_reasons