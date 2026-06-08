from __future__ import annotations

from dataclasses import dataclass

from automation.operator_relief.vacation_watchdog import (
    CLASSIFICATION_NON_SOS,
    CLASSIFICATION_OK,
    CLASSIFICATION_SOS,
    build_vacation_heartbeat,
)


PROTECTED_PATH_PREFIXES = (
    "AGENTS.md",
    "README.md",
    "docs/governance/",
    "automation/orchestration/",
    "automation/operator_relief/",
    "services/",
    "apps/",
)
AUTHORITY_LANES = {"MAIN_MERGE", "PROTECTED_MAIN_PR", "AUTHORITY_APPLY", "VACATION_WATCHTOWER"}
PROTECTED_ACTIONS = {"commit", "push", "merge", "main_mutation", "protected_path_write"}


@dataclass(frozen=True)
class LockRecord:
    lane: str
    worker_id: str
    worker_role: str
    status: str = "active"
    age_minutes: int = 0
    protected_paths: tuple[str, ...] = ()
    authority_lane: bool = False
    branch: str = "feature/full-operator-relief-closed-loop-v1"


@dataclass(frozen=True)
class LockRequest:
    lane: str
    worker_id: str
    worker_role: str
    requested_action: str = "observe"
    requested_paths: tuple[str, ...] = ()
    anthony_approved: bool = False


def _is_protected_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in PROTECTED_PATH_PREFIXES)


def _classify_lock_request(
    request: LockRequest,
    locks: list[LockRecord],
    *,
    stale_after_minutes: int = 120,
    critical_stale_after_minutes: int = 720,
) -> dict[str, object]:
    matching_locks = [lock for lock in locks if lock.lane == request.lane and lock.status == "active"]
    collisions = [lock for lock in matching_locks if lock.worker_id != request.worker_id]
    owned_continuation = bool(matching_locks) and not collisions
    stale_locks = [lock for lock in matching_locks if lock.age_minutes >= stale_after_minutes]
    critical_stale_locks = [lock for lock in stale_locks if lock.age_minutes >= critical_stale_after_minutes]
    protected_collision = any(lock.protected_paths for lock in collisions) or any(
        _is_protected_path(path) for path in request.requested_paths
    )
    main_or_merge_collision = request.lane in {"MAIN_MERGE", "PROTECTED_MAIN_PR"} or any(
        lock.branch == "main" or lock.authority_lane for lock in collisions
    )
    review_only_authority_attempt = (
        request.worker_role == "Claude Code review-only"
        and (request.lane in AUTHORITY_LANES or request.requested_action in PROTECTED_ACTIONS)
    )
    approval_bypass_attempt = request.requested_action in PROTECTED_ACTIONS and not request.anthony_approved
    night_supervisor_auto_merge_attempt = (
        request.worker_role == "Night Supervisor" and request.requested_action == "merge"
    )
    watchtower_protected_action_attempt = (
        request.worker_role == "Watchtower" and request.requested_action in PROTECTED_ACTIONS
    )

    safety_state: dict[str, object] = {"trading_live_blocked": True, "secret_risk_status": "CLEAR"}
    git_state: dict[str, object] = {
        "branch": "feature/full-operator-relief-closed-loop-v1",
        "git_clean": True,
        "upstream_state": "MATCHES_ORIGIN",
    }

    sos_reasons: list[str] = []
    non_sos_reasons: list[str] = []

    if protected_collision:
        safety_state["protected_gate_bypass"] = True
        sos_reasons.append("protected path lock collision")
    if main_or_merge_collision:
        git_state["main_branch_risk"] = True
        sos_reasons.append("main branch or merge lane lock collision")
    if review_only_authority_attempt:
        safety_state["protected_gate_bypass"] = True
        sos_reasons.append("review-only worker attempted authority lane")
    if approval_bypass_attempt:
        safety_state["protected_gate_bypass"] = True
        sos_reasons.append("worker attempted protected action without Anthony approval")
    if night_supervisor_auto_merge_attempt:
        safety_state["protected_gate_bypass"] = True
        sos_reasons.append("night supervisor attempted auto-merge")
    if watchtower_protected_action_attempt:
        safety_state["protected_gate_bypass"] = True
        sos_reasons.append("watchtower attempted protected git mutation")
    if stale_locks and not critical_stale_locks and not protected_collision and not main_or_merge_collision:
        non_sos_reasons.append("stale non-critical worker lock requires review")
    if collisions and not sos_reasons and not non_sos_reasons:
        non_sos_reasons.append("worker lane collision requires review")

    if sos_reasons:
        safety_state["sos_findings"] = sos_reasons
    if non_sos_reasons:
        safety_state["non_sos_findings"] = non_sos_reasons

    heartbeat = build_vacation_heartbeat(
        repo_state={"repo_path": r"C:\Dev\Ai.Os"},
        git_state=git_state,
        validator_state={"status": "PASS"},
        approval_state={"pending_count": 0, "sos_pending_count": 0},
        notification_state={"notification_rail": "ADB_SOS", "adb_sos_available": True},
        lock_state={"lock_count": len(locks), "stale_lock_count": len(stale_locks)},
        safety_state=safety_state,
        timestamp_utc="2026-06-08T00:00:00+00:00",
    )

    return {
        "lane": request.lane,
        "worker_id": request.worker_id,
        "owned_continuation": owned_continuation,
        "collision_detected": bool(collisions),
        "stale_lock_detected": bool(stale_locks),
        "stale_lock_auto_cleanup_allowed": False,
        "protected_path_collision": protected_collision,
        "main_or_merge_collision": main_or_merge_collision,
        "review_only_authority_attempt": review_only_authority_attempt,
        "approval_bypass_attempt": approval_bypass_attempt,
        "night_supervisor_auto_merge_allowed": False,
        "watchtower_git_mutation_allowed": False,
        "safe_next_action": heartbeat["safe_next_action"],
        "do_not_wake_reason": heartbeat["do_not_wake_reason"],
        "heartbeat": heartbeat,
    }


def test_same_lane_active_lock_different_worker_detects_collision() -> None:
    report = _classify_lock_request(
        LockRequest(lane="VACATION_WATCHDOG", worker_id="OpenAI CLI", worker_role="OpenAI CLI"),
        [LockRecord(lane="VACATION_WATCHDOG", worker_id="Codex CLI", worker_role="Codex CLI")],
    )

    assert report["collision_detected"] is True
    assert report["owned_continuation"] is False
    assert report["stale_lock_auto_cleanup_allowed"] is False
    assert report["heartbeat"]["classification"] == CLASSIFICATION_NON_SOS


def test_same_lane_same_worker_active_lock_allows_owned_continuation() -> None:
    report = _classify_lock_request(
        LockRequest(lane="VACATION_WATCHDOG", worker_id="Codex CLI", worker_role="Codex CLI"),
        [LockRecord(lane="VACATION_WATCHDOG", worker_id="Codex CLI", worker_role="Codex CLI")],
    )

    assert report["owned_continuation"] is True
    assert report["collision_detected"] is False
    assert report["heartbeat"]["classification"] == CLASSIFICATION_OK


def test_stale_lock_requires_review_and_does_not_auto_clean() -> None:
    report = _classify_lock_request(
        LockRequest(lane="REPORT_REVIEW", worker_id="OpenAI CLI", worker_role="OpenAI CLI"),
        [LockRecord(lane="REPORT_REVIEW", worker_id="Codex CLI", worker_role="Codex CLI", age_minutes=180)],
    )

    assert report["stale_lock_detected"] is True
    assert report["stale_lock_auto_cleanup_allowed"] is False
    assert report["heartbeat"]["classification"] == CLASSIFICATION_NON_SOS
    assert report["heartbeat"]["sos_required"] is False


def test_protected_path_lock_collision_is_sos_required() -> None:
    report = _classify_lock_request(
        LockRequest(
            lane="OPERATOR_RELIEF_APPLY",
            worker_id="OpenAI CLI",
            worker_role="OpenAI CLI",
            requested_paths=("automation/operator_relief/vacation_watchdog.py",),
        ),
        [
            LockRecord(
                lane="OPERATOR_RELIEF_APPLY",
                worker_id="Codex CLI",
                worker_role="Codex CLI",
                protected_paths=("automation/operator_relief/vacation_watchdog.py",),
            )
        ],
    )

    assert report["protected_path_collision"] is True
    assert report["heartbeat"]["classification"] == CLASSIFICATION_SOS
    assert report["heartbeat"]["sos_required"] is True


def test_non_protected_stale_lock_below_critical_threshold_is_non_sos_attention() -> None:
    report = _classify_lock_request(
        LockRequest(lane="REPORT_ONLY", worker_id="OpenAI CLI", worker_role="OpenAI CLI"),
        [LockRecord(lane="REPORT_ONLY", worker_id="Codex CLI", worker_role="Codex CLI", age_minutes=180)],
        critical_stale_after_minutes=720,
    )

    assert report["stale_lock_detected"] is True
    assert report["heartbeat"]["classification"] == CLASSIFICATION_NON_SOS
    assert report["heartbeat"]["sos_required"] is False
    assert report["do_not_wake_reason"]


def test_main_branch_or_merge_lane_collision_is_sos_required() -> None:
    report = _classify_lock_request(
        LockRequest(lane="MAIN_MERGE", worker_id="OpenAI CLI", worker_role="OpenAI CLI"),
        [
            LockRecord(
                lane="MAIN_MERGE",
                worker_id="Codex CLI",
                worker_role="Codex CLI",
                authority_lane=True,
                branch="main",
            )
        ],
    )

    assert report["main_or_merge_collision"] is True
    assert report["heartbeat"]["classification"] == CLASSIFICATION_SOS


def test_claude_code_review_only_lock_cannot_escalate_to_authority_lane() -> None:
    report = _classify_lock_request(
        LockRequest(
            lane="AUTHORITY_APPLY",
            worker_id="Claude Code",
            worker_role="Claude Code review-only",
            requested_action="protected_path_write",
        ),
        [],
    )

    assert report["review_only_authority_attempt"] is True
    assert report["heartbeat"]["classification"] == CLASSIFICATION_SOS


def test_openai_codex_worker_lock_cannot_bypass_anthony_approval() -> None:
    report = _classify_lock_request(
        LockRequest(
            lane="VACATION_WATCHDOG",
            worker_id="OpenAI CLI",
            worker_role="OpenAI CLI",
            requested_action="commit",
            anthony_approved=False,
        ),
        [],
    )

    assert report["approval_bypass_attempt"] is True
    assert report["heartbeat"]["classification"] == CLASSIFICATION_SOS


def test_night_supervisor_observes_but_does_not_auto_merge() -> None:
    report = _classify_lock_request(
        LockRequest(
            lane="MAIN_MERGE",
            worker_id="Night Supervisor",
            worker_role="Night Supervisor",
            requested_action="merge",
        ),
        [],
    )

    assert report["night_supervisor_auto_merge_allowed"] is False
    assert report["heartbeat"]["classification"] == CLASSIFICATION_SOS


def test_watchtower_can_classify_sos_but_cannot_commit_push_or_merge() -> None:
    for action in ("commit", "push", "merge"):
        report = _classify_lock_request(
            LockRequest(
                lane="VACATION_WATCHTOWER",
                worker_id="Watchtower",
                worker_role="Watchtower",
                requested_action=action,
            ),
            [],
        )

        assert report["watchtower_git_mutation_allowed"] is False
        assert report["heartbeat"]["classification"] == CLASSIFICATION_SOS


def test_lock_report_includes_safe_next_action() -> None:
    report = _classify_lock_request(
        LockRequest(lane="REPORT_ONLY", worker_id="Codex CLI", worker_role="Codex CLI"),
        [],
    )

    assert report["safe_next_action"] == "Continue read-only monitoring or wait for Anthony approval."


def test_lock_report_includes_do_not_wake_reason_when_no_sos_exists() -> None:
    report = _classify_lock_request(
        LockRequest(lane="REPORT_ONLY", worker_id="Codex CLI", worker_role="Codex CLI"),
        [LockRecord(lane="REPORT_ONLY", worker_id="Codex CLI", worker_role="Codex CLI")],
    )

    assert report["heartbeat"]["sos_required"] is False
    assert report["do_not_wake_reason"] == (
        "No confirmed SOS condition is present; keep Anthony asleep and retain read-only status."
    )
