from __future__ import annotations
import json
from pathlib import Path
import pytest
from automation.orchestration.aios_delivery_receipt_instrumentation_v1 import *

START="2026-08-06T10:00:00Z"; END="2026-08-06T10:02:30Z"
def start(tmp_path):
    return start_task_timing(tmp_path/"run",task_id="TASK-1",packet_id="PACKET-1",lane="LANE-1",branch="work",starting_head="a"*40,started_utc=START)

def test_start_and_identical_duplicate(tmp_path):
    one=start(tmp_path); two=start(tmp_path); assert one==two and one["runtime_marker_only"]

def test_conflicting_start_fails(tmp_path):
    start(tmp_path)
    with pytest.raises(ValueError,match="conflicting"): start_task_timing(tmp_path/"run",task_id="TASK-1",packet_id="PACKET-1",lane="OTHER",branch="work",starting_head="a"*40,started_utc=START)

def test_complete_measures_and_is_idempotent(tmp_path):
    start(tmp_path); kw=dict(task_id="TASK-1",packet_id="PACKET-1",completed_utc=END,ending_head="b"*40)
    one=complete_task_timing(tmp_path/"run",tmp_path/"term",**kw); two=complete_task_timing(tmp_path/"run",tmp_path/"term",**kw)
    assert one==two and one["elapsed_seconds"]==150 and one["duration_measured"]

def test_missing_start_has_null_duration(tmp_path):
    value=complete_task_timing(tmp_path/"run",tmp_path/"term",task_id="T",packet_id="P",completed_utc=END)
    assert value["elapsed_seconds"] is None and value["duration_exclusion_reason"]=="START_MARKER_UNAVAILABLE"

def test_terminal_before_start_and_conflict_fail(tmp_path):
    start(tmp_path)
    with pytest.raises(ValueError,match="earlier"): complete_task_timing(tmp_path/"run",tmp_path/"term",task_id="TASK-1",packet_id="PACKET-1",completed_utc="2026-08-06T09:00:00Z")
    value=complete_task_timing(tmp_path/"run",tmp_path/"term",task_id="TASK-1",packet_id="PACKET-1",completed_utc=END)
    assert value
    with pytest.raises(ValueError,match="conflicting"): block_task_timing(tmp_path/"run",tmp_path/"term",task_id="TASK-1",packet_id="PACKET-1",blocked_utc=END,blocker_reasons=["x"])

def test_blocked_has_no_completion_credit(tmp_path):
    start(tmp_path); value=block_task_timing(tmp_path/"run",tmp_path/"term",task_id="TASK-1",packet_id="PACKET-1",blocked_utc=END,blocker_reasons=["validator failed"])
    assert value["status"]=="BLOCKED" and value["completion_credit"] is False and value["elapsed_seconds"]==150

@pytest.mark.parametrize("bad",[float("nan"),float("inf")])
def test_nonfinite_fails(bad):
    with pytest.raises(ValueError): stable_json({"x":bad})

def test_invalid_timestamp_and_sensitive_values_fail(tmp_path):
    with pytest.raises(ValueError): start_task_timing(tmp_path,task_id="T",packet_id="P",lane="L",branch="work",starting_head="a",started_utc="bad")
    with pytest.raises(ValueError,match="sensitive"): append_velocity_event(tmp_path/"e",{"schema":EVENT_SCHEMA,"event_id":"x","account_id":"123"})

def workflow(conclusion="success", prs=None, sha="a"):
    return {"repository":{"full_name":"owner/repo"},"workflow_run":{"id":1,"name":"CI","event":"pull_request","status":"completed","conclusion":conclusion,"head_sha":sha,"head_branch":"work","pull_requests":prs or []}}

def pr(merged=True, sha="a", created=None):
    return {"repository":{"full_name":"owner/repo"},"pull_request":{"number":7,"created_at":created,"closed_at":END,"merged_at":END if merged else None,"merged":merged,"base":{"ref":"main","sha":"b"},"head":{"ref":"work","sha":sha}}}

def test_github_success_failure_missing_and_self():
    assert normalize_github_event_receipt(workflow())["validation_passed"] is True
    assert normalize_github_event_receipt(workflow("failure"))["validation_passed"] is False
    assert normalize_github_event_receipt(workflow(None))["validation_available"] is False
    own=workflow(); own["workflow_run"]["name"]="AIOS Delivery Validation Receipts V1"; assert normalize_github_event_receipt(own) is None

def test_pr_reconciliation_is_fail_closed_and_creation_not_inferred():
    closed=normalize_github_event_receipt(pr()); check=normalize_github_event_receipt(workflow(prs=[{"number":7}]))
    result=rebuild_github_pr_delivery_metadata([closed,check])[0]
    assert result["completion_credit"] and result["created_at"] is None
    assert not rebuild_github_pr_delivery_metadata([normalize_github_event_receipt(pr(False)),check])[0]["completion_credit"]
    assert not rebuild_github_pr_delivery_metadata([closed,normalize_github_event_receipt(workflow(prs=[]))])[0]["completion_credit"]

def test_conflicting_receipts_and_sha_fail_closed():
    a=normalize_github_event_receipt(pr()); b={**a,"head_sha":"other"}
    with pytest.raises(ValueError,match="conflicting"): rebuild_github_pr_delivery_metadata([a,b])

def test_event_dedup_and_metadata_byte_stability(tmp_path):
    event={"schema":EVENT_SCHEMA,"event_id":"e1","event_type":"TASK_STARTED","timestamp_utc":START}
    assert append_velocity_event(tmp_path/"events",event); assert not append_velocity_event(tmp_path/"events",event)
    start(tmp_path); receipt=complete_task_timing(tmp_path/"run",tmp_path/"term",task_id="TASK-1",packet_id="PACKET-1",completed_utc=END)
    assert stable_json(rebuild_codex_delivery_metadata([receipt]))==stable_json(rebuild_codex_delivery_metadata([receipt]))

def test_workflow_is_read_only_nonrecursive_and_no_secrets():
    text=(Path(__file__).parents[2]/".github/workflows/aios_delivery_validation_receipts_v1.yml").read_text()
    for permission in ("contents: read","actions: read","pull-requests: read"): assert permission in text
    lowered=text.lower(); assert "secrets." not in lowered and "git push" not in lowered and "contents: write" not in lowered

def test_first_withdrawable_dollar_remains_separate():
    report=render_owner_report({"runtime_marker_path":".aios/runtime","codex_metadata_path":"metadata.json","status":"SAFE"})
    assert "First Withdrawable Dollar remains a separate milestone" in report
