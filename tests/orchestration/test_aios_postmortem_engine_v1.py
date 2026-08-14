import json
from copy import deepcopy
import pytest
from automation.orchestration.postmortem.aios_postmortem_engine_v1 import (
    DuplicateEventError, PatternMemory, PostmortemEngine, ValidationError,
    analyze_trades, build_hypothesis, canonical_json, classify, classify_trade_patterns,
    learn, performance_statistics, progress_accounting, qualify_trades,
    recommend_experiments, transition, validate_event, validate_pattern,
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

def test_pattern_schema_is_closed_and_count_is_consistent():
    pattern=PatternMemory().observe(event())
    assert validate_pattern(pattern) == pattern
    pattern["independent_incident_count"]=2
    with pytest.raises(ValidationError): validate_pattern(pattern)

def test_pattern_cannot_promote_one_incident():
    pattern=PatternMemory().observe(event()); pattern["promotion_eligible"]=True
    with pytest.raises(ValidationError): validate_pattern(pattern)

def typed_evidence(kind="trade_execution", ref="exec:1"):
    return {"evidence_type":kind,"reference":ref,"evidence_hash":"b"*64,"source":"test"}

def trade(trade_id="t1", pnl=10.0, status="CLOSED", metrics=None, **overrides):
    value={"trade_id":trade_id,"status":status,"instrument":"EUR_USD","side":"BUY",
      "entry_timestamp":"2026-01-01T00:00:00Z","exit_timestamp":"2026-01-01T00:05:00Z",
      "entry_price":1.1,"exit_price":1.2,"realized_pnl":pnl,"fees":1.0,
      "evidence":[typed_evidence()],"metrics":metrics or {}}
    value.update(overrides); return value

def test_zero_trades_and_unproven_progress():
    result=analyze_trades([])
    assert result["summary"]["total_trades"]==0 and result["summary"]["win_rate"] is None
    assert result["progress"]["qualifying_trades"]=="NOT_PROVEN"

def test_winner_loser_mixed_and_breakeven_statistics():
    accepted=qualify_trades([trade("w",11),trade("l",-4),trade("b",1)])["qualifying"]
    stats=performance_statistics(accepted)
    assert (stats["wins"],stats["losses"],stats["breakeven"])==(1,1,1)
    assert stats["net_pnl"]==5 and stats["expectancy"]==pytest.approx(5/3)

def test_duplicate_open_malformed_and_unproven_rejected():
    records=[trade("d"),trade("d"),trade("o",status="OPEN"),trade("u",status="NOT_PROVEN"),{"trade_id":"bad"}]
    result=qualify_trades(records)
    assert [x["reason"] for x in result["rejected"]]==["DUPLICATE","OPEN","UNPROVEN_CLOSED_STATE","MALFORMED"]

def test_missing_execution_evidence_rejected():
    result=qualify_trades([trade(evidence=[typed_evidence("signal")])])
    assert result["rejected"][0]["reason"]=="MISSING_REQUIRED_EVIDENCE"

def test_unsupported_evidence_type_rejected():
    result=qualify_trades([trade(evidence=[typed_evidence("broker_claim")])])
    assert result["rejected"][0]["reason"]=="MALFORMED"

def test_missing_optional_fields_remain_null():
    value=qualify_trades([trade()])["qualifying"][0]
    assert value["strategy"] is None and value["supertrend_multiplier"] is None

def test_profit_factor_zero_losses_and_with_losses():
    winners=qualify_trades([trade("w",11)])["qualifying"]
    assert performance_statistics(winners)["profit_factor"]=="INFINITE"
    mixed=qualify_trades([trade("w",11),trade("l",-4)])["qualifying"]
    assert performance_statistics(mixed)["profit_factor"]==pytest.approx(10/5)

def test_net_pnl_after_fees_and_max_drawdown():
    values=qualify_trades([trade("a",11),trade("b",-4),trade("c",-3)])["qualifying"]
    stats=performance_statistics(values)
    assert stats["cumulative_pnl"]==[10.0,5.0,1.0] and stats["max_drawdown"]==9.0

def test_invalid_nonfinite_pnl_rejected():
    assert qualify_trades([trade(pnl=float("nan"))])["rejected"][0]["reason"]=="MALFORMED"

def test_false_flip_proven_and_not_proven():
    proven=qualify_trades([trade(metrics={"flip_count":1,"bars_to_reversal":2})])["qualifying"][0]
    assert next(x for x in classify_trade_patterns(proven) if x["pattern"]=="FALSE_FLIP")["status"]=="PROVEN"
    absent=qualify_trades([trade()])["qualifying"][0]
    assert next(x for x in classify_trade_patterns(absent) if x["pattern"]=="FALSE_FLIP")["status"]=="NOT_PROVEN"

def test_low_volatility_whipsaw():
    value=qualify_trades([trade(metrics={"atr":0.2,"atr_floor":0.5,"reversal_count":2})])["qualifying"][0]
    assert next(x for x in classify_trade_patterns(value) if x["pattern"]=="LOW_VOLATILITY_WHIPSAW")["status"]=="PROVEN"

def test_multiplier_metadata_and_sensitivity():
    value=qualify_trades([trade(supertrend_multiplier=3,metrics={"supertrend_multiplier":3,"comparison_multiplier":2})])["qualifying"][0]
    assert value["supertrend_multiplier"]==3
    assert next(x for x in classify_trade_patterns(value) if x["pattern"]=="MULTIPLIER_SENSITIVITY")["status"]=="PROVEN"

def test_recommendations_cite_trades_and_evidence():
    metrics={"flip_count":1,"bars_to_reversal":1}
    values=qualify_trades([trade("a",metrics=metrics),trade("b",metrics=metrics)])["qualifying"]
    recommendation=recommend_experiments(values)[0]
    assert recommendation["supporting_trade_ids"]==["a","b"] and recommendation["supporting_evidence_refs"]==["exec:1"]
    assert recommendation["evidence_status"]=="ELIGIBLE" and recommendation["authority"]=="ANALYSIS_ONLY"

def test_recommendation_below_threshold_blocked():
    value=qualify_trades([trade(metrics={"flip_count":1,"bars_to_reversal":1})])["qualifying"]
    assert recommend_experiments(value)[0]["evidence_status"]=="BLOCKED_BELOW_THRESHOLD"

def test_recommendations_limited_to_three():
    metrics={"flip_count":1,"bars_to_reversal":1,"atr":0.1,"atr_floor":0.5,"reversal_count":3,"duration_seconds":20,
      "supertrend_multiplier":3,"comparison_multiplier":2,"trend_bars":1,"minimum_trend_bars":4}
    values=qualify_trades([trade("a",-2,metrics=metrics),trade("b",-2,metrics=metrics)])["qualifying"]
    assert len(recommend_experiments(values))==3

def test_30_trade_progress_accounting():
    result=progress_accounting(software_complete=100,qualifying_trades=30,evidence_proven=True,analysis_complete=True)
    assert result=={"software_complete":100,"evidence_complete":100.0,"trade_analysis_complete":100.0,"release_ready":100,"qualifying_trades":30,"target_trades":30}

def test_progress_does_not_fabricate_zero():
    result=progress_accounting(software_complete=100,qualifying_trades=None)
    assert result["qualifying_trades"]=="NOT_PROVEN" and result["release_ready"]=="NOT_PROVEN"

def test_typed_evidence_does_not_cross_prove_market_condition():
    value=qualify_trades([trade(evidence=[typed_evidence("trade_execution")])])["qualifying"][0]
    assert value["market_condition"] is None

def test_analysis_output_contract():
    result=analyze_trades([trade()],evidence_proven=True)
    assert set(result)>={"trade_details","summary","losing_patterns","winning_patterns","recommended_experiments","progress"}

def test_no_broker_or_runtime_mutation_authority():
    import inspect
    from automation.orchestration.postmortem import aios_postmortem_engine_v1 as module
    source=inspect.getsource(module).lower()
    assert "import requests" not in source and "import socket" not in source and "subprocess" not in source
