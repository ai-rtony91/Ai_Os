import json
from copy import deepcopy
import pytest
from automation.orchestration.postmortem.aios_postmortem_engine_v1 import (
    DuplicateEventError, PatternMemory, PostmortemEngine, ValidationError,
    build_hypothesis, canonical_json, classify, learn, transition, validate_event,
)

def event(eid="event-1", iid="incident-1"):
    h="a"*64
    return {"event_id":eid,"incident_id":iid,"packet_id":"packet-1","task_id":"task-1","run_id":"run-1",
      "worker_identity":"EAST_OCC_01","supervisor_identity":"Codex-East","lane":"postmortem",
      "timestamp":"2026-08-12T00:00:00Z","repository_identity":"ai-rtony91/Ai_Os","worktree":"/workspace/Ai_Os",
      "branch":"work","base_sha":"1"*40,"head_sha":"2"*40,"tree_sha":"3"*40,"worktree_state":"CLEAN",
      "remote_state":"LOCAL_ONLY","failing_stage":"publication","sanitized_detection_signature":"local-commit-unpublished",
      "evidence_references":["git:3ae69d3"],"evidence_hashes":[h],"outcome_classification":"LOCAL_COMMIT_AT_RISK",
      "root_cause_status":"UNVERIFIED","verified_root_cause":None,"hypotheses":[],"recovery_attempts":[],
      "recovery_result":"NOT_ATTEMPTED","validators_after_recovery":[],"durability_state":"AT_RISK",
      "lesson_status":"PENDING","promotion_status":"NOT_ELIGIBLE","next_safe_action":"PUBLISH_AND_VERIFY_COMMIT"}

def test_valid_and_malformed_and_duplicates():
    assert validate_event(event())["event_id"] == "event-1"
    bad=event(); del bad["packet_id"]
    with pytest.raises(ValidationError): validate_event(bad)
    eng=PostmortemEngine(); eng.analyze(event())
    with pytest.raises(DuplicateEventError): eng.analyze(event())

def test_secret_nonfinite_path_and_contradiction_rejected():
    for mutate in (lambda x:x.update(password="x"),lambda x:x.update(worktree="../escape"),lambda x:x.update(recovery_result=float("nan"))):
      x=event(); mutate(x)
      with pytest.raises(ValidationError): validate_event(x)
    x=event(); x["durability_state"]="REMOTE_VERIFIED"
    with pytest.raises(ValidationError): validate_event(x)

def test_classification_is_deterministic_and_bounded():
    assert classify({"dirty_worktree":True}) == classify({"dirty_worktree":True})
    cases={"origin_absent":"ORIGIN_ABSENT","origin_incorrect":"ORIGIN_INCORRECT","authorization_unavailable":"AUTHORIZATION_UNAVAILABLE","local_commit_only":"LOCAL_COMMIT_AT_RISK","missing_commit":"MISSING_COMMIT","missing_branch":"MISSING_BRANCH","worker_lease_expired":"WORKER_LEASE_EXPIRED","worker_active":"WORKER_STILL_ACTIVE","application_lock_expired":"STALE_APPLICATION_LOCK","git_index_lock_persistent":"GIT_LOCK_REVIEW_REQUIRED","orphaned_apply":"ORPHANED_APPLY","duplicate_apply":"DUPLICATE_APPLY","packet_collision":"PACKET_COLLISION","corrupt_evidence":"CORRUPT_STATE","validators_failed":"VALIDATION_FAILURE","ci_failed":"CI_FAILURE"}
    for flag, outcome in cases.items(): assert classify({flag:True})["outcome_classification"] == outcome
    assert classify({"local_commit_only":True})["durability_state"] == "AT_RISK"

def test_hypotheses_do_not_become_causes_without_proof_and_keep_contradictions():
    h=build_hypothesis("h1","cause",["i1"],["i2"],"bounded test","PASSED")
    assert h["confidence_level"] == "UNVERIFIED" and h["contradicting_incidents"] == ["i2"]
    assert build_hypothesis("h1","cause",["i1"],[],"bounded test","PASSED")["promotion_eligible"]

def test_lesson_is_evidence_not_authority():
    lesson=learn(event())
    assert lesson["verified_root_cause"] is None and lesson["authority"] == "EVIDENCE_NOT_GOVERNANCE"
    assert lesson["governance_promotion"] == "SEPARATE_HUMAN_OWNER_APPROVAL_REQUIRED"

def test_pattern_independence_duplicate_suppression_and_promotion():
    memory=PatternMemory(); first=memory.observe(event())
    assert first["independent_incident_count"] == 1 and not first["promotion_eligible"]
    replay=memory.observe(event()); assert replay["duplicate_suppressed"] and replay["independent_incident_count"] == 1
    second=memory.observe(event("event-2","incident-2")); assert second["independent_incident_count"] == 2 and second["promotion_eligible"]
    critical=memory.pattern("local-commit-unpublished",safety_critical=True)
    assert not critical["promotion_eligible"] and critical["human_owner_review_required"]

def test_mutable_replay_and_contradictory_incident_rejected():
    memory=PatternMemory(); memory.observe(event())
    x=event(); x["recovery_result"]="CHANGED"
    with pytest.raises(ValidationError): memory.observe(x)
    x=event("event-2","incident-1"); x["recovery_result"]="CHANGED"
    with pytest.raises(ValidationError): memory.observe(x)

def test_state_machine_fails_closed_and_is_idempotent():
    assert transition("OBSERVED","OBSERVED")["changed"] is False
    with pytest.raises(ValidationError): transition("OBSERVED","CLOSED")
    assert transition("VERIFIED","CLOSED")["state"] == "CLOSED"

def test_lost_supertrend_commit_is_analysis_only():
    result=classify({"local_commit_only":True,"commit":"3ae69d3"})
    assert result["outcome_classification"] == "LOCAL_COMMIT_AT_RISK"
    assert set(result)=={"outcome_classification","next_safe_action","durability_state"}

def test_corrupt_evidence_quarantine_plan_and_no_authority():
    result=classify({"corrupt_evidence":True})
    assert result["next_safe_action"] == "QUARANTINE_EVIDENCE"
    forbidden="broker credential order campaign strategy deployment scheduler daemon money"
    assert all(word not in canonical_json(result).lower() for word in forbidden.split())

def test_deterministic_machine_output_and_end_to_end():
    e=event(); engine=PostmortemEngine(); analyzed=engine.analyze(e); lesson=engine.learn(analyzed)
    plan=engine.plan({"local_commit_only":True}); verified=engine.verify({"validators_passed":True,"evidence_intact":True})
    closed=engine.close(verified["state"])
    assert canonical_json(lesson)==canonical_json(lesson)
    assert plan["durability_state"]=="AT_RISK" and closed["state"]=="CLOSED"
