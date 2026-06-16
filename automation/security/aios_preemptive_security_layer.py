"""AI_OS Preemptive Security Layer v1.

Read-only scanner that summarizes security risk before orchestration chooses a
next action. It does not mutate files, call external services, launch workers,
or print matched secret-like values.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVENT_SCHEMA = "AIOS_PREEMPTIVE_SECURITY_EVENT.v1"
STATE_SCHEMA = "AIOS_PREEMPTIVE_SECURITY_STATE.v1"
COMPONENT = "preemptive_security_layer"

EVENT_CATEGORIES = (
    "CANARY_TRIP",
    "SECRET_EXPOSURE_RISK",
    "BROKER_AUTHORITY_RISK",
    "LIVE_TRADING_RISK",
    "REAL_ORDER_RISK",
    "WEBHOOK_RISK",
    "PRODUCTION_DEPLOY_RISK",
    "DASHBOARD_MUTATION_RISK",
    "SCHEDULER_DAEMON_RISK",
    "WORKER_LAUNCH_RISK",
    "PROTECTED_AUTHORITY_RISK",
    "UNKNOWN_SECURITY_RISK",
)

SAFE_GENERATED_PREFIXES = (
    "reports/",
    "automation/orchestration/work_packets/preview/",
)
REVIEW_ARTIFACT_PREFIXES = (
    "control/review_bridge/",
)
PROTECTED_PREFIXES = (
    "agents.md",
    "readme.md",
    "docs/governance/",
    "docs/security/",
    "automation/orchestration/",
    "automation/runtime/",
    "automation/security/",
    "schemas/aios/",
)

SECRET_PATH_RE = re.compile(
    r"(^|[/\\])(\.env|secrets?|credentials?|private[-_ ]?keys?|api[-_ ]?keys?|tokens?)([/\\.]|$)",
    re.IGNORECASE,
)
SECRET_TEXT_RE = re.compile(
    r"\b(api[_-]?key|client[_-]?secret|secret|token|password|passwd|credential|private[_-]?key)\b\s*[:=]",
    re.IGNORECASE,
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE)
OPENAI_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b")

CANARY_RE = re.compile(r"\b(AIOS_CANARY|TRIPWIRE_DO_NOT_TOUCH|DECOY_SECRET_DO_NOT_USE)\b", re.IGNORECASE)
ENABLEMENT_RE = re.compile(
    r"\b(enable|enabled|connect|connected|submit|send|place|placed|execute|executed|activate|activated|"
    r"launch|launched|deploy|deployed|mutate|mutation|write|start|started|register|registered|authorize|authorized)\b",
    re.IGNORECASE,
)
BROKER_RE = re.compile(r"\b(broker|oanda|broker[_-]?auth|broker[_-]?authority|broker[_-]?execution)\b", re.IGNORECASE)
LIVE_TRADING_RE = re.compile(r"\b(live[_-]?trading|live broker|live execution|live account)\b", re.IGNORECASE)
REAL_ORDER_RE = re.compile(
    r"\b(real[\s_-]?orders?|live[\s_-]?orders?|order[\s_-]?execution|place[\s_-]?order|place real order)\b",
    re.IGNORECASE,
)
WEBHOOK_RE = re.compile(r"\b(webhook|webhook[_-]?url|external[_-]?hook)\b", re.IGNORECASE)
PRODUCTION_RE = re.compile(r"\b(production|prod[_-]?deploy|deploy[_-]?production|release[_-]?deploy)\b", re.IGNORECASE)
DASHBOARD_MUTATION_RE = re.compile(
    r"\b(dashboard[\s_-]?(mutation|mutate|write|control|execute)|apps/dashboard)\b", re.IGNORECASE
)
SCHEDULER_RE = re.compile(r"\b(scheduler|scheduledtask|daemon|background[_-]?service|cron)\b", re.IGNORECASE)
WORKER_RE = re.compile(
    r"\b(worker[\s_-]?launch|launch[\s_-]?worker|start[\s_-]?worker|spawn[\s_-]?worker)\b", re.IGNORECASE
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_id(*parts: str) -> str:
    seed = "\n".join(parts)
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def _norm_path(path: str | Path) -> str:
    text = str(path).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text.lower()


def _source_role(path: str) -> str:
    normalized = _norm_path(path)
    if any(normalized.startswith(prefix) for prefix in SAFE_GENERATED_PREFIXES):
        return "generated_evidence"
    if any(normalized.startswith(prefix) for prefix in REVIEW_ARTIFACT_PREFIXES):
        return "review_bridge"
    if normalized.startswith("tests/"):
        return "test_fixture"
    if normalized.startswith("docs/"):
        return "documentation"
    return "repo_file"


def _is_generated_or_report(path: str, source_role: str) -> bool:
    normalized = _norm_path(path)
    return source_role in {"generated_evidence", "sandbox_preview", "report"} or any(
        normalized.startswith(prefix) for prefix in SAFE_GENERATED_PREFIXES
    )


def _is_protected_path(path: str) -> bool:
    normalized = _norm_path(path)
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def build_security_event(
    category: str,
    *,
    source_type: str,
    source_path: str,
    reason: str,
    severity: str,
    confidence: float,
    indicators: list[str] | None = None,
    action: str | None = None,
    source_role: str | None = None,
    contributes_to_stop: bool | None = None,
) -> dict[str, Any]:
    if category not in EVENT_CATEGORIES:
        category = "UNKNOWN_SECURITY_RISK"
    normalized_severity = severity.upper()
    return {
        "schema": EVENT_SCHEMA,
        "event_id": _stable_id(category, source_type, source_path, reason),
        "category": category,
        "severity": normalized_severity,
        "source_type": source_type,
        "source_path": str(source_path).replace("\\", "/"),
        "source_role": source_role or _source_role(source_path),
        "reason": reason,
        "indicators": sorted(set(indicators or [])),
        "confidence": round(float(confidence), 3),
        "action": action or ("SOS" if normalized_severity == "SOS" else normalized_severity),
        "matched_values_printed": False,
        "values_redacted": True,
        "contributes_to_stop": normalized_severity in {"SOS", "STOP"} if contributes_to_stop is None else bool(contributes_to_stop),
        "blocked_actions": _blocked_actions_for(category),
        "next_safe_action": _next_safe_action_for(category, normalized_severity),
        "safety": {
            "read_only": True,
            "secret_values_redacted": True,
            "network_access": False,
            "broker_access": False,
            "live_trading": False,
            "production_mutation": False,
            "dashboard_mutation": False,
            "scheduler_activation": False,
            "worker_launch": False,
        },
    }


def _blocked_actions_for(category: str) -> list[str]:
    common = ["APPLY", "git add", "git commit", "git push"]
    category_actions = {
        "SECRET_EXPOSURE_RISK": ["secret printing", "credential use"],
        "BROKER_AUTHORITY_RISK": ["broker access", "broker credential use"],
        "LIVE_TRADING_RISK": ["live trading", "broker execution"],
        "REAL_ORDER_RISK": ["real order execution"],
        "WEBHOOK_RISK": ["external webhook call"],
        "PRODUCTION_DEPLOY_RISK": ["production deploy"],
        "DASHBOARD_MUTATION_RISK": ["dashboard mutation controls"],
        "SCHEDULER_DAEMON_RISK": ["scheduler activation", "daemon activation"],
        "WORKER_LAUNCH_RISK": ["worker launch"],
        "PROTECTED_AUTHORITY_RISK": ["protected authority mutation"],
        "CANARY_TRIP": ["canary handling", "secret access"],
        "UNKNOWN_SECURITY_RISK": ["unreviewed mutation"],
    }
    return common + category_actions.get(category, ["unreviewed mutation"])


def _next_safe_action_for(category: str, severity: str) -> str:
    if severity == "WATCH":
        return "Continue READ_ONLY/DRY_RUN only; do not APPLY from this state."
    if severity == "REVIEW":
        return "Stop for human review of the exact listed files before APPLY."
    if severity == "STOP":
        return "Stop before mutation and run protected-action/security review."
    if severity == "SOS":
        return "SOS: stop immediately and escalate without printing secret-like values."
    return "Continue read-only evidence collection."


def _event_from_path(path: str, status: str = "") -> list[dict[str, Any]]:
    role = _source_role(path)
    normalized = _norm_path(path)
    events: list[dict[str, Any]] = []

    if CANARY_RE.search(path):
        events.append(
            build_security_event(
                "CANARY_TRIP",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Canary or decoy tripwire marker appeared in a file path.",
                severity="SOS",
                confidence=0.98,
                indicators=["canary_tripwire"],
            )
        )
    if SECRET_PATH_RE.search(path):
        events.append(
            build_security_event(
                "SECRET_EXPOSURE_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Path resembles a secret, credential, token, private key, or environment file.",
                severity="SOS",
                confidence=0.96,
                indicators=["secret_path"],
            )
        )
    if ("broker" in normalized or "oanda" in normalized) and not _is_generated_or_report(path, role):
        events.append(
            build_security_event(
                "BROKER_AUTHORITY_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Path points at broker/OANDA authority outside generated evidence.",
                severity="SOS",
                confidence=0.9,
                indicators=["broker_path"],
            )
        )
    if "live" in normalized and "trading" in normalized and not _is_generated_or_report(path, role):
        events.append(
            build_security_event(
                "LIVE_TRADING_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Path points at live-trading authority outside generated evidence.",
                severity="SOS",
                confidence=0.9,
                indicators=["live_trading_path"],
            )
        )
    if "real_order" in normalized or "real-orders" in normalized:
        events.append(
            build_security_event(
                "REAL_ORDER_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Path references real order execution.",
                severity="SOS",
                confidence=0.92,
                indicators=["real_order_path"],
            )
        )
    if WEBHOOK_RE.search(path) and not _is_generated_or_report(path, role):
        events.append(
            build_security_event(
                "WEBHOOK_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Path references external webhook authority.",
                severity="STOP",
                confidence=0.86,
                indicators=["webhook_path"],
            )
        )
    if PRODUCTION_RE.search(path) and not _is_generated_or_report(path, role):
        events.append(
            build_security_event(
                "PRODUCTION_DEPLOY_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Path references production or deploy authority.",
                severity="STOP",
                confidence=0.86,
                indicators=["production_path"],
            )
        )
    if DASHBOARD_MUTATION_RE.search(path) and not _is_generated_or_report(path, role):
        events.append(
            build_security_event(
                "DASHBOARD_MUTATION_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Path references dashboard mutation/control authority.",
                severity="STOP",
                confidence=0.88,
                indicators=["dashboard_mutation_path"],
            )
        )
    if SCHEDULER_RE.search(path) and status:
        events.append(
            build_security_event(
                "SCHEDULER_DAEMON_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Dirty path references scheduler or daemon authority.",
                severity="STOP",
                confidence=0.84,
                indicators=["scheduler_daemon_path"],
            )
        )
    if WORKER_RE.search(path) and status:
        events.append(
            build_security_event(
                "WORKER_LAUNCH_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Dirty path references worker launch authority.",
                severity="STOP",
                confidence=0.84,
                indicators=["worker_launch_path"],
            )
        )
    if _is_protected_path(path) and status:
        events.append(
            build_security_event(
                "PROTECTED_AUTHORITY_RISK",
                source_type="path",
                source_path=path,
                source_role=role,
                reason="Dirty path is inside protected authority scope.",
                severity="STOP",
                confidence=0.8,
                indicators=["protected_path"],
            )
        )

    return events


def classify_text(text: str, *, source_path: str = "", source_role: str | None = None) -> list[dict[str, Any]]:
    role = source_role or _source_role(source_path)
    generated_context = _is_generated_or_report(source_path, role)
    events: list[dict[str, Any]] = []

    if CANARY_RE.search(text):
        events.append(
            build_security_event(
                "CANARY_TRIP",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason="Canary or decoy tripwire marker appeared in content.",
                severity="SOS",
                confidence=0.98,
                indicators=["canary_tripwire"],
            )
        )

    if SECRET_TEXT_RE.search(text) or PRIVATE_KEY_RE.search(text) or OPENAI_KEY_RE.search(text):
        events.append(
            build_security_event(
                "SECRET_EXPOSURE_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason="Content contains a secret-like assignment or private key pattern; values are redacted.",
                severity="SOS",
                confidence=0.96,
                indicators=["secret_pattern"],
            )
        )

    actionable = ENABLEMENT_RE.search(text) is not None
    watch_only = generated_context and not actionable
    severity_for_safety_mention = "WATCH" if watch_only else "SOS"
    stop_for_safety_mention = not watch_only

    if BROKER_RE.search(text):
        events.append(
            build_security_event(
                "BROKER_AUTHORITY_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason=(
                    "Generated safety/report content mentions broker authority without enablement."
                    if watch_only
                    else "Content implies broker/OANDA authority, enablement, or execution."
                ),
                severity=severity_for_safety_mention,
                confidence=0.74 if watch_only else 0.9,
                indicators=["broker_oanda"],
                contributes_to_stop=stop_for_safety_mention,
            )
        )
    if LIVE_TRADING_RE.search(text):
        events.append(
            build_security_event(
                "LIVE_TRADING_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason=(
                    "Generated safety/report content mentions live-trading risk without enablement."
                    if watch_only
                    else "Content implies live-trading authority or execution."
                ),
                severity=severity_for_safety_mention,
                confidence=0.74 if watch_only else 0.91,
                indicators=["live_trading"],
                contributes_to_stop=stop_for_safety_mention,
            )
        )
    if REAL_ORDER_RE.search(text):
        events.append(
            build_security_event(
                "REAL_ORDER_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason=(
                    "Generated safety/report content mentions real-order risk without enablement."
                    if watch_only
                    else "Content implies real-order execution."
                ),
                severity=severity_for_safety_mention,
                confidence=0.76 if watch_only else 0.92,
                indicators=["real_order"],
                contributes_to_stop=stop_for_safety_mention,
            )
        )
    if WEBHOOK_RE.search(text) and actionable:
        events.append(
            build_security_event(
                "WEBHOOK_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason="Content implies external webhook execution or authority.",
                severity="STOP",
                confidence=0.86,
                indicators=["webhook"],
            )
        )
    if PRODUCTION_RE.search(text) and actionable:
        events.append(
            build_security_event(
                "PRODUCTION_DEPLOY_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason="Content implies production deploy authority.",
                severity="STOP",
                confidence=0.86,
                indicators=["production_deploy"],
            )
        )
    if DASHBOARD_MUTATION_RE.search(text) and actionable:
        events.append(
            build_security_event(
                "DASHBOARD_MUTATION_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason="Content implies dashboard mutation/control authority.",
                severity="STOP",
                confidence=0.86,
                indicators=["dashboard_mutation"],
            )
        )
    if SCHEDULER_RE.search(text) and actionable:
        events.append(
            build_security_event(
                "SCHEDULER_DAEMON_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason="Content implies scheduler or daemon activation.",
                severity="STOP",
                confidence=0.86,
                indicators=["scheduler_daemon"],
            )
        )
    if WORKER_RE.search(text) and actionable:
        events.append(
            build_security_event(
                "WORKER_LAUNCH_RISK",
                source_type="content",
                source_path=source_path,
                source_role=role,
                reason="Content implies unauthorized worker launch.",
                severity="STOP",
                confidence=0.86,
                indicators=["worker_launch"],
            )
        )
    return events


def events_from_dirty_tree(dirty_tree: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(dirty_tree, dict):
        return []

    events: list[dict[str, Any]] = []
    files = dirty_tree.get("dirty_files")
    if not isinstance(files, list):
        files = dirty_tree.get("files")
    if not isinstance(files, list):
        files = []

    for item in files:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or item.get("file") or "")
        classification = str(item.get("classification") or "UNKNOWN_DIRTY")
        status = str(item.get("git_code") or item.get("status") or "")
        reason = str(item.get("reason") or "")
        role = _source_role(path)
        indicators = [str(value) for value in item.get("security_indicators") or [] if value]

        events.extend(_event_from_path(path, status=status))

        if classification == "SECURITY_SOS_DIRTY":
            content_blob = " ".join([path, reason, " ".join(indicators)])
            content_events = classify_text(content_blob, source_path=path, source_role=role)
            if _is_generated_or_report(path, role):
                for event in content_events:
                    if event["category"] in {
                        "BROKER_AUTHORITY_RISK",
                        "LIVE_TRADING_RISK",
                        "REAL_ORDER_RISK",
                        "WEBHOOK_RISK",
                        "PRODUCTION_DEPLOY_RISK",
                    } and event["category"] != "SECRET_EXPOSURE_RISK":
                        event["severity"] = "WATCH"
                        event["action"] = "WATCH"
                        event["contributes_to_stop"] = False
                        event["reason"] = "Generated evidence mentions security risk; no enablement, secret exposure, executable authority, or live action is implied."
                        event["next_safe_action"] = _next_safe_action_for(event["category"], "WATCH")
            events.extend(content_events)
        elif classification == "PROTECTED_AUTHORITY_DIRTY":
            events.append(
                build_security_event(
                    "PROTECTED_AUTHORITY_RISK",
                    source_type="dirty_tree",
                    source_path=path,
                    source_role=role,
                    reason="Dirty Tree Classifier marked this file as protected authority dirty.",
                    severity="STOP",
                    confidence=0.9,
                    indicators=["protected_authority_dirty"],
                )
            )
        elif classification in {"UNKNOWN_DIRTY", "REVIEW_REQUIRED_DIRTY"}:
            events.append(
                build_security_event(
                    "UNKNOWN_SECURITY_RISK",
                    source_type="dirty_tree",
                    source_path=path,
                    source_role=role,
                    reason=f"Dirty Tree Classifier marked this file as {classification}; review is required.",
                    severity="REVIEW",
                    confidence=0.72,
                    indicators=["dirty_tree_review_required"],
                    action="REVIEW_REQUIRED",
                    contributes_to_stop=False,
                )
            )

    return _dedupe_events(events)


def _dedupe_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for event in events:
        event_id = str(event.get("event_id") or "")
        if event_id in seen:
            continue
        seen.add(event_id)
        deduped.append(event)
    return deduped


def _category_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    counts = {category: 0 for category in EVENT_CATEGORIES}
    for event in events:
        category = str(event.get("category") or "UNKNOWN_SECURITY_RISK")
        counts[category] = counts.get(category, 0) + 1
    return {key: value for key, value in counts.items() if value}


def _aggregate_state(events: list[dict[str, Any]]) -> tuple[str, str, bool, bool, bool]:
    stop_events = [event for event in events if event.get("contributes_to_stop") is True]
    if any(event.get("severity") == "SOS" for event in stop_events):
        return "SOS", "SECURITY_SOS", True, True, True
    if any(event.get("severity") == "STOP" for event in stop_events):
        return "STOP", "SECURITY_STOP", False, True, True
    if any(event.get("severity") == "REVIEW" for event in events):
        return "REVIEW_REQUIRED", "SECURITY_REVIEW_REQUIRED", False, False, True
    if any(event.get("severity") == "WATCH" for event in events):
        return "WATCH", "SECURITY_WATCH", False, False, False
    return "CLEAR", "SECURITY_CLEAR", False, False, False


def _hud_state(overall_state: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    if overall_state == "SOS":
        shield_state = "BLACK"
        vault_lock_state = "SEALED"
    elif overall_state == "STOP":
        shield_state = "RED"
        vault_lock_state = "LOCKED"
    elif overall_state == "REVIEW_REQUIRED":
        shield_state = "YELLOW"
        vault_lock_state = "LOCKED_REVIEW"
    elif overall_state == "WATCH":
        shield_state = "YELLOW"
        vault_lock_state = "LOCKED_READ_ONLY"
    else:
        shield_state = "GREEN"
        vault_lock_state = "LOCKED"

    radar_events = [
        {
            "event_id": event["event_id"],
            "category": event["category"],
            "severity": event["severity"],
            "source_path": event["source_path"],
            "reason": event["reason"],
        }
        for event in events
        if event.get("category") != "CANARY_TRIP"
    ]
    tripwire_events = [
        {
            "event_id": event["event_id"],
            "category": event["category"],
            "severity": event["severity"],
            "source_path": event["source_path"],
            "reason": event["reason"],
        }
        for event in events
        if event.get("category") == "CANARY_TRIP"
    ]

    return {
        "shield_state": shield_state,
        "vault_lock_state": vault_lock_state,
        "radar_events": radar_events,
        "tripwire_events": tripwire_events,
        "boss_alert": {
            "active": overall_state in {"SOS", "STOP"},
            "level": overall_state,
            "reason": events[0]["reason"] if events and overall_state in {"SOS", "STOP"} else "",
        },
    }


def build_security_state(
    *,
    repo_root: str | Path = ".",
    dirty_tree: dict[str, Any] | None = None,
    evidence_items: list[dict[str, Any]] | None = None,
    generated_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    events: list[dict[str, Any]] = []
    events.extend(events_from_dirty_tree(dirty_tree))

    for item in evidence_items or []:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "")
        content = str(item.get("content") or item.get("summary") or "")
        if path:
            events.extend(_event_from_path(path))
        if content:
            events.extend(classify_text(content, source_path=path))

    events = _dedupe_events(events)
    overall_state, security_status, sos_required, stop_required, review_required = _aggregate_state(events)
    safe_for_dry_run = overall_state in {"CLEAR", "WATCH"}
    safe_for_apply = overall_state == "CLEAR"
    hud = _hud_state(overall_state, events)
    blocked_actions = sorted({action for event in events for action in event.get("blocked_actions", [])})
    if overall_state in {"WATCH", "REVIEW_REQUIRED", "STOP", "SOS"}:
        blocked_actions = sorted(set(blocked_actions + ["APPLY"]))
    next_safe_action = {
        "CLEAR": "Continue with normal approved workflow; protected actions still require approval.",
        "WATCH": "Continue READ_ONLY/DRY_RUN only; do not APPLY from this state.",
        "REVIEW_REQUIRED": "Stop for human review of listed security events before APPLY.",
        "STOP": "Stop before mutation and run protected-action/security review.",
        "SOS": "SOS: stop immediately and escalate without printing secret-like values.",
    }[overall_state]

    return {
        "schema": STATE_SCHEMA,
        "generated_utc": generated_utc or _utc_now(),
        "repo_root": str(root),
        "component": COMPONENT,
        "overall_state": overall_state,
        "security_status": security_status,
        "safe_for_dry_run": safe_for_dry_run,
        "safe_for_apply": safe_for_apply,
        "sos_required": sos_required,
        "stop_required": stop_required,
        "review_required": review_required,
        "event_count": len(events),
        "events": events,
        "category_counts": _category_counts(events),
        "shield_state": hud["shield_state"],
        "vault_lock_state": hud["vault_lock_state"],
        "radar_events": hud["radar_events"],
        "tripwire_events": hud["tripwire_events"],
        "boss_alert": hud["boss_alert"],
        "blocked_actions": blocked_actions,
        "next_safe_action": next_safe_action,
        "safety": {
            "read_only": True,
            "stdout_only_by_default": True,
            "secret_values_printed": False,
            "writes_reports_by_default": False,
            "network_access": False,
            "broker_access": False,
            "live_trading": False,
            "real_order_execution": False,
            "production_mutation": False,
            "dashboard_mutation": False,
            "scheduler_activation": False,
            "daemon_activation": False,
            "worker_launch": False,
        },
    }


def _load_dirty_tree_classifier(repo_root: Path) -> Any | None:
    path = repo_root / "automation" / "orchestration" / "continuation" / "aios_dirty_tree_classifier.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("aios_dirty_tree_classifier", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def build_state_from_repo(repo_root: str | Path, dirty_tree_json_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root)
    dirty_tree: dict[str, Any] | None = None
    if dirty_tree_json_path:
        dirty_tree = _load_json(Path(dirty_tree_json_path))
    else:
        classifier = _load_dirty_tree_classifier(root)
        if classifier is not None:
            dirty_tree = classifier.build_dirty_tree_classification(repo_root=root)
    return build_security_state(repo_root=root, dirty_tree=dirty_tree)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit read-only AI_OS preemptive security state JSON.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--dirty-tree-json", default="", help="Optional Dirty Tree Classifier JSON file to consume.")
    args = parser.parse_args(argv)

    state = build_state_from_repo(args.repo_root, args.dirty_tree_json or None)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
