"""Display-only AI_OS dashboard state projector.

This module maps caller-supplied evidence dictionaries into the canonical
dashboard state contract. It does not discover live files, execute commands,
write outputs, launch workers, mutate approvals, or create dashboard truth.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


CONTRACT_SCHEMA = "AIOS_DASHBOARD_STATE_CONTRACT.v1"
CONTRACT_VERSION = "1.0"
DISPLAY_MODE = "DISPLAY_ONLY_READ_MODEL"

DEFAULT_BLOCKED_ACTIONS = [
    "APPLY",
    "approval mutation",
    "broker execution",
    "dashboard mutation",
    "git add",
    "git commit",
    "git push",
    "live trading",
    "merge",
    "scheduler launch",
    "worker launch",
]

UNSAFE_POSITIVE_KEYS = {
    "approval_mutation",
    "approval_mutation_allowed",
    "broker",
    "broker_access",
    "broker_allowed",
    "broker_execution",
    "button_authority",
    "control_authority",
    "dashboard_creates_truth",
    "dashboard_mutation",
    "dashboard_mutation_allowed",
    "daemon",
    "daemon_activation",
    "daemon_allowed",
    "daemon_performed",
    "dispatch_authorized",
    "execution_allowed",
    "live_order_execution",
    "live_orders_submitted",
    "live_trading",
    "live_trading_allowed",
    "mutation_allowed",
    "mutation_performed",
    "order_submission_allowed",
    "paper_orders_submitted",
    "production_allowed",
    "production_mutation",
    "queue_mutation_authorized",
    "real_order_execution",
    "real_orders_submitted",
    "scheduler",
    "scheduler_activation",
    "scheduler_allowed",
    "scheduler_performed",
    "worker_dispatch",
    "worker_launch",
    "worker_launch_allowed",
    "worker_launch_performed",
}

FAIL_CLOSED_EVIDENCE_STATES = {"MISSING", "STALE", "UNSUPPORTED", "UNKNOWN"}

DISPLAY_STATES = {
    "READY",
    "REVIEW",
    "NEEDS_REVIEW",
    "BLOCKED",
    "UNKNOWN",
    "DISPLAY_ONLY",
    "PASS",
    "WARN",
    "FAIL",
    "CLEAR",
    "WATCH",
    "REVIEW_REQUIRED",
    "STOP",
    "SOS",
    "NO_SETUP",
    "WATCHING",
    "CANDIDATE_FOUND",
    "HIGH_PRIORITY",
    "INVALIDATED",
    "CONTINUE",
}

SECTION_ORDER = (
    "system_state",
    "security_state",
    "continuation_state",
    "governor_state",
    "watchtower_state",
    "validator_state",
    "control_plane_state",
    "active_mission_state",
    "resume_state",
    "worker_state",
)

SECTION_DEFAULTS: dict[str, dict[str, Any]] = {
    "system_state": {
        "source_path": "schemas/aios/orchestration/RUNTIME_VISIBILITY_SCHEMA.json",
        "source_schema": "RUNTIME_VISIBILITY_SCHEMA",
        "supported_schemas": {"RUNTIME_VISIBILITY_SCHEMA", "AIOS_RUNTIME_STATE_BUNDLE.v1"},
        "source_type": "canonical_schema",
    },
    "security_state": {
        "source_path": "schemas/aios/security/AIOS_PREEMPTIVE_SECURITY_STATE.v1.schema.json",
        "source_schema": "AIOS_PREEMPTIVE_SECURITY_STATE.v1",
        "supported_schemas": {"AIOS_PREEMPTIVE_SECURITY_STATE.v1"},
        "source_type": "canonical_schema",
    },
    "continuation_state": {
        "source_path": "schemas/aios/orchestration/AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1.schema.json",
        "source_schema": "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1",
        "supported_schemas": {
            "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1",
            "AIOS_AUTONOMOUS_JOB_CONTINUATION_EVIDENCE.v1",
        },
        "source_type": "canonical_schema",
    },
    "governor_state": {
        "source_path": "automation/orchestration/aios_autonomy_decision_governor.py",
        "source_schema": "AIOS_AUTONOMY_DECISION_GOVERNOR.v1",
        "supported_schemas": {"AIOS_AUTONOMY_DECISION_GOVERNOR.v1"},
        "source_type": "source_code",
    },
    "watchtower_state": {
        "source_path": "schemas/aios/trading/AIOS_TRADING_WATCHTOWER_RESULT.v1.schema.json",
        "source_schema": "AIOS_TRADING_WATCHTOWER_RESULT.v1",
        "supported_schemas": {"AIOS_TRADING_WATCHTOWER_RESULT.v1"},
        "source_type": "canonical_schema",
    },
    "validator_state": {
        "source_path": "schemas/aios/orchestration/VALIDATOR_OUTPUT_SCHEMA.json",
        "source_schema": "VALIDATOR_OUTPUT_SCHEMA",
        "supported_schemas": {
            "VALIDATOR_OUTPUT_SCHEMA",
            "AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1",
            "AIOS_VALIDATOR_OUTPUT.v1",
        },
        "source_type": "canonical_schema",
    },
    "control_plane_state": {
        "source_path": "automation/orchestration/aios_control_plane_status.py",
        "source_schema": "AIOS_CONTROL_PLANE_STATUS.v1",
        "supported_schemas": {"AIOS_CONTROL_PLANE_STATUS.v1"},
        "source_type": "source_code",
    },
    "active_mission_state": {
        "source_path": "automation/orchestration/aios_active_mission_cycle.py",
        "source_schema": "AIOS_ACTIVE_MISSION_CYCLE.v1",
        "supported_schemas": {"AIOS_ACTIVE_MISSION_CYCLE.v1"},
        "source_type": "source_code",
    },
    "resume_state": {
        "source_path": "automation/orchestration/aios_resume_state.py",
        "source_schema": "AIOS_RESUME_STATE.v1",
        "supported_schemas": {"AIOS_RESUME_STATE.v1"},
        "source_type": "source_code",
    },
    "worker_state": {
        "source_path": "schemas/aios/orchestration/WORKER_REGISTRY_SCHEMA.json",
        "source_schema": "WORKER_REGISTRY_SCHEMA",
        "supported_schemas": {"WORKER_REGISTRY_SCHEMA", "WORKER_PROFILE_SCHEMA", "WORKER_INBOX_SCHEMA"},
        "source_type": "canonical_schema",
    },
}


def project_dashboard_state(evidence: Mapping[str, Any] | None, now_utc: str | None = None) -> dict[str, Any]:
    """Project caller-supplied evidence into the dashboard display contract."""

    now = now_utc or _utc_now()
    evidence_map = evidence if isinstance(evidence, Mapping) else {}
    sections = {name: _project_section(name, evidence_map.get(name), now) for name in SECTION_ORDER}

    return {
        "schema": CONTRACT_SCHEMA,
        "schema_version": CONTRACT_VERSION,
        "generated_at_utc": now,
        "mode": DISPLAY_MODE,
        "authority_boundary": _authority_boundary(),
        "source_index": _source_index(sections),
        "freshness": _global_freshness(sections, now),
        **sections,
        "system_health": _system_health(sections),
        "system_readiness": _system_readiness(sections),
        "risk_level": _risk_level(sections),
        "blocked_actions": _blocked_actions(sections),
        "next_safe_action": _next_safe_action(sections),
    }


def _project_section(name: str, supplied: Any, now: str) -> dict[str, Any]:
    defaults = SECTION_DEFAULTS[name]
    ref = _evidence_ref(supplied, defaults)
    payload = ref["payload"]
    missing = payload is None
    unsupported = _is_unsupported(ref, defaults)
    unsafe = _has_unsafe_positive_authority(payload)
    freshness = _freshness(ref, now, missing=missing, unsupported=unsupported)
    evidence_state = freshness["evidence_state"]

    section = _base_section(
        display_state=_display_state(name, payload, evidence_state, unsupported=unsupported, unsafe=unsafe),
        authority_state="EVIDENCE_ONLY" if not missing else "UNKNOWN",
        source_path=ref["source_path"],
        source_schema=ref["source_schema"],
        source_type=ref["source_type"],
        freshness=freshness,
        evidence_state=evidence_state,
        summary=_summary(name, payload, evidence_state, unsupported=unsupported, unsafe=unsafe),
        items=_items(name, payload),
        blocked_actions=_section_blocked_actions(payload),
        next_safe_action=_section_next_safe_action(payload, evidence_state, unsupported=unsupported, unsafe=unsafe),
        approval_required=unsafe or evidence_state in FAIL_CLOSED_EVIDENCE_STATES or _approval_required(payload),
    )

    if name == "security_state":
        section.update(_security_fields(payload))
    elif name == "continuation_state":
        section.update(_continuation_fields(payload))
    elif name == "watchtower_state":
        section.update(_watchtower_fields(payload))
    elif name == "control_plane_state":
        section.update(_control_plane_fields(payload))

    return section


def _authority_boundary() -> dict[str, bool]:
    return {
        "read_only": True,
        "evidence_only": True,
        "dashboard_creates_truth": False,
        "execution_allowed": False,
        "mutation_allowed": False,
        "control_authority": False,
        "button_authority": False,
        "broker_allowed": False,
        "live_trading_allowed": False,
        "approval_mutation_allowed": False,
        "worker_launch_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
    }


def _base_section(
    *,
    display_state: str,
    authority_state: str,
    source_path: str,
    source_schema: str,
    source_type: str,
    freshness: dict[str, Any],
    evidence_state: str,
    summary: str,
    items: list[dict[str, Any]],
    blocked_actions: list[str],
    next_safe_action: str,
    approval_required: bool,
) -> dict[str, Any]:
    return {
        "display_state": display_state,
        "authority_state": authority_state,
        "source_path": source_path,
        "source_schema": source_schema,
        "source_type": source_type,
        "freshness": freshness,
        "evidence_state": evidence_state,
        "summary": summary,
        "items": items,
        "blocked_actions": blocked_actions,
        "next_safe_action": next_safe_action,
        "approval_required": approval_required,
        "execution_allowed": False,
        "mutation_allowed": False,
        "safe_for_frontend_display": True,
    }


def _evidence_ref(supplied: Any, defaults: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(supplied, Mapping) and "payload" in supplied:
        payload = supplied.get("payload")
        source_path = str(supplied.get("source_path") or defaults["source_path"])
        source_schema = str(supplied.get("source_schema") or _payload_schema(payload) or defaults["source_schema"])
        source_type = str(supplied.get("source_type") or "runtime_evidence")
        generated_at = supplied.get("generated_at") or supplied.get("generated_at_utc") or _payload_generated_at(payload)
        ttl_seconds = supplied.get("ttl_seconds")
        is_stale = supplied.get("is_stale")
        evidence_state = supplied.get("evidence_state")
    else:
        payload = supplied if isinstance(supplied, Mapping) else None
        source_path = str(defaults["source_path"])
        source_schema = str(_payload_schema(payload) or defaults["source_schema"])
        source_type = str(defaults["source_type"])
        generated_at = _payload_generated_at(payload)
        ttl_seconds = None
        is_stale = None
        evidence_state = None

    return {
        "payload": payload if isinstance(payload, Mapping) else None,
        "source_path": source_path,
        "source_schema": source_schema,
        "source_type": source_type if source_type else "unknown",
        "generated_at": generated_at,
        "ttl_seconds": ttl_seconds,
        "is_stale": is_stale,
        "evidence_state": evidence_state,
    }


def _freshness(ref: Mapping[str, Any], now: str, *, missing: bool, unsupported: bool) -> dict[str, Any]:
    generated_at = _string_or_none(ref.get("generated_at"))
    ttl_seconds = _ttl(ref.get("ttl_seconds"))
    explicit_state = _upper_string(ref.get("evidence_state"))
    explicit_stale = ref.get("is_stale") is True

    if missing:
        state = "MISSING"
        is_stale = True
    elif unsupported:
        state = "UNSUPPORTED"
        is_stale = True
    elif explicit_state in FAIL_CLOSED_EVIDENCE_STATES:
        state = explicit_state
        is_stale = explicit_state == "STALE" or explicit_stale
    elif explicit_stale or _is_stale(generated_at, ttl_seconds, now):
        state = "STALE"
        is_stale = True
    else:
        state = "CURRENT"
        is_stale = False

    return {
        "checked_at": now,
        "generated_at": generated_at,
        "ttl_seconds": ttl_seconds,
        "is_stale": is_stale,
        "evidence_state": state,
    }


def _display_state(name: str, payload: Mapping[str, Any] | None, evidence_state: str, *, unsupported: bool, unsafe: bool) -> str:
    if unsafe:
        return "BLOCKED"
    if unsupported or evidence_state in FAIL_CLOSED_EVIDENCE_STATES:
        return "NEEDS_REVIEW"
    if payload is None:
        return "NEEDS_REVIEW"

    if name == "security_state":
        return _known_display(payload.get("overall_state"), default="CLEAR")
    if name == "continuation_state":
        return _known_display(payload.get("state"), default="CONTINUE")
    if name == "watchtower_state":
        return _known_display(payload.get("watchtower_status"), default="NO_SETUP")
    if name == "control_plane_state":
        return _status_display(payload.get("loop_status") or payload.get("status"))
    if name == "active_mission_state":
        return _mission_display(payload.get("mission_status"))
    if name == "resume_state":
        return "READY" if payload.get("resume_ready") is True else "REVIEW"
    if name == "validator_state":
        return _validator_display(payload.get("overall_result") or payload.get("status") or payload.get("validator_status"))
    if name == "governor_state":
        return _governor_display(payload)
    if name == "worker_state":
        return _status_display(payload.get("status") or payload.get("worker_status"))
    return _status_display(payload.get("overall_status") or payload.get("status"))


def _summary(name: str, payload: Mapping[str, Any] | None, evidence_state: str, *, unsupported: bool, unsafe: bool) -> str:
    if unsafe:
        return f"{name} evidence contains unsafe positive authority flags; dashboard projection is blocked."
    if unsupported:
        return f"{name} evidence schema is unsupported by the dashboard projector."
    if evidence_state == "MISSING":
        return f"{name} evidence was not supplied."
    if evidence_state == "STALE":
        return f"{name} evidence is stale and needs review."
    if payload is None:
        return f"{name} evidence is unavailable."

    for key in ("summary", "security_status", "next_highest_value_task", "mission_status", "loop_status", "status"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"{name} projected from caller-supplied evidence."


def _items(name: str, payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload.get("items"), list):
        return _object_list(payload["items"])
    if name == "security_state":
        return _object_list(payload.get("events"))
    if name == "watchtower_state":
        return _object_list(payload.get("market_radar"))
    if name == "continuation_state" and isinstance(payload.get("selected_task"), Mapping):
        return [dict(payload["selected_task"])]
    if name == "active_mission_state" and isinstance(payload.get("input_records"), Mapping):
        return [{"name": key, **value} for key, value in payload["input_records"].items() if isinstance(value, Mapping)]
    if name == "worker_state" and isinstance(payload.get("workers"), list):
        return _object_list(payload["workers"])
    return []


def _section_blocked_actions(payload: Mapping[str, Any] | None) -> list[str]:
    actions = list(DEFAULT_BLOCKED_ACTIONS)
    if payload is not None and isinstance(payload.get("blocked_actions"), list):
        actions.extend(str(item) for item in payload["blocked_actions"] if str(item).strip())
    return sorted(set(actions))


def _section_next_safe_action(
    payload: Mapping[str, Any] | None,
    evidence_state: str,
    *,
    unsupported: bool,
    unsafe: bool,
) -> str:
    if unsafe:
        return "Stop and review unsafe authority flags before displaying this evidence."
    if unsupported:
        return "Review source schema support before using this evidence in the dashboard projector."
    if evidence_state == "MISSING":
        return "Supply schema-backed evidence before presenting this dashboard section as current."
    if evidence_state == "STALE":
        return "Refresh or review source evidence before presenting this dashboard section as current."
    if payload is not None and isinstance(payload.get("next_safe_action"), str) and payload["next_safe_action"].strip():
        return payload["next_safe_action"].strip()
    return "Review source evidence before any protected action."


def _approval_required(payload: Mapping[str, Any] | None) -> bool:
    if payload is None:
        return True
    value = payload.get("approval_required")
    if isinstance(value, bool):
        return value
    if isinstance(value, Mapping):
        return any(_is_positive(item) for item in value.values())
    return False


def _security_fields(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        "shield_state": _known(payload, "shield_state", {"GREEN", "YELLOW", "RED", "BLACK", "UNKNOWN"}, "UNKNOWN"),
        "vault_lock_state": _known(
            payload,
            "vault_lock_state",
            {"LOCKED", "LOCKED_READ_ONLY", "LOCKED_REVIEW", "SEALED", "UNKNOWN"},
            "UNKNOWN",
        ),
        "radar_events": _object_list(payload.get("radar_events") if payload else None),
        "tripwire_events": _object_list(payload.get("tripwire_events") if payload else None),
        "boss_alert": _boss_alert(payload),
    }


def _continuation_fields(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    current_task = payload.get("selected_task") if payload else None
    if not isinstance(current_task, Mapping):
        current_task = payload.get("current_task") if payload else None
    return {
        "current_task": dict(current_task) if isinstance(current_task, Mapping) else None,
        "repair_count": _nonnegative_int(payload.get("repair_count") if payload else None),
        "resume_status": _resume_status(payload),
        "approval_status": _approval_status(payload),
    }


def _watchtower_fields(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        "market_radar": _object_list(payload.get("market_radar") if payload else None),
        "candidate_targets": _object_list(payload.get("candidate_targets") if payload else None),
        "priority_targets": _object_list(payload.get("priority_targets") if payload else None),
        "market_regime": _known(
            payload,
            "market_regime",
            {"TREND_UP", "TREND_DOWN", "RANGE", "HIGH_VOL", "LOW_VOL", "UNKNOWN"},
            "UNKNOWN",
        ),
        "watchtower_status": _known(
            payload,
            "watchtower_status",
            {"NO_SETUP", "WATCHING", "CANDIDATE_FOUND", "HIGH_PRIORITY", "INVALIDATED", "REVIEW_REQUIRED", "UNKNOWN"},
            "UNKNOWN",
        ),
        "next_best_setup": dict(payload["next_best_setup"])
        if payload and isinstance(payload.get("next_best_setup"), Mapping)
        else None,
    }


def _control_plane_fields(payload: Mapping[str, Any] | None) -> dict[str, str]:
    return {
        "control_plane_status": _string_value(payload.get("loop_status") if payload else None, "unknown"),
        "validator_status": _string_value(payload.get("validator_status") if payload else None, "unknown"),
        "governor_status": _string_value(payload.get("governor_status") if payload else None, "unknown"),
        "mission_status": _string_value(payload.get("mission_status") if payload else None, "unknown"),
    }


def _source_index(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, list[dict[str, str]]]:
    primary: list[dict[str, str]] = [
        {
            "source_path": "schemas/aios/orchestration/STATE_PROJECTION_RULES.md",
            "source_schema": "STATE_PROJECTION_RULES",
            "source_type": "canonical_doc",
            "authority_state": "CANONICAL_AUTHORITY",
        }
    ]
    backing: list[dict[str, str]] = [
        {
            "source_path": "schemas/aios/orchestration/AIOS_DASHBOARD_STATE_CONTRACT.v1.schema.json",
            "source_schema": CONTRACT_SCHEMA,
            "source_type": "canonical_schema",
            "authority_state": "CANONICAL_AUTHORITY",
        }
    ]

    for section in sections.values():
        source = {
            "source_path": str(section["source_path"]),
            "source_schema": str(section["source_schema"]),
            "source_type": _source_ref_type(str(section.get("source_type") or "unknown")),
            "authority_state": str(section["authority_state"]),
        }
        if source not in primary:
            primary.append(source)

        default = SECTION_DEFAULTS[_section_name_for_schema(str(section["source_schema"]))]
        schema_source = {
            "source_path": str(default["source_path"]),
            "source_schema": str(default["source_schema"]),
            "source_type": _source_ref_type(str(default["source_type"])),
            "authority_state": "CANONICAL_AUTHORITY",
        }
        if schema_source not in backing:
            backing.append(schema_source)

    return {"primary_sources": primary, "backing_schemas": backing}


def _global_freshness(sections: Mapping[str, Mapping[str, Any]], now: str) -> dict[str, Any]:
    evidence_states = [section["freshness"]["evidence_state"] for section in sections.values()]
    stale = any(section["freshness"]["is_stale"] for section in sections.values())
    state = "STALE" if "STALE" in evidence_states else "MISSING" if "MISSING" in evidence_states else "CURRENT"
    if any(state in {"UNSUPPORTED", "UNKNOWN"} for state in evidence_states):
        state = "UNKNOWN"
    return {
        "checked_at": now,
        "generated_at": now,
        "ttl_seconds": 300,
        "is_stale": stale,
        "evidence_state": state,
    }


def _system_health(sections: Mapping[str, Mapping[str, Any]]) -> str:
    states = {section["display_state"] for section in sections.values()}
    if states & {"BLOCKED", "STOP", "SOS"}:
        return "BLOCKED"
    if states & {"FAIL"}:
        return "FAIL"
    if states & {"NEEDS_REVIEW", "REVIEW", "REVIEW_REQUIRED", "WARN", "UNKNOWN"}:
        return "WARN"
    return "PASS"


def _system_readiness(sections: Mapping[str, Mapping[str, Any]]) -> str:
    health = _system_health(sections)
    if health == "BLOCKED":
        return "BLOCKED"
    if health in {"WARN", "FAIL"}:
        return "NEEDS_REVIEW"
    return "READY"


def _risk_level(sections: Mapping[str, Mapping[str, Any]]) -> str:
    states = {section["display_state"] for section in sections.values()}
    if states & {"BLOCKED", "STOP", "SOS"}:
        return "BLOCKED"
    if states & {"FAIL", "REVIEW_REQUIRED"}:
        return "HIGH"
    if states & {"NEEDS_REVIEW", "REVIEW", "WARN", "UNKNOWN"}:
        return "MEDIUM"
    return "LOW"


def _blocked_actions(sections: Mapping[str, Mapping[str, Any]]) -> list[str]:
    actions = list(DEFAULT_BLOCKED_ACTIONS)
    for section in sections.values():
        actions.extend(str(item) for item in section.get("blocked_actions", []))
    return sorted(set(actions))


def _next_safe_action(sections: Mapping[str, Mapping[str, Any]]) -> str:
    for section in sections.values():
        if section["display_state"] == "BLOCKED":
            return section["next_safe_action"]
    for section in sections.values():
        if section["approval_required"]:
            return section["next_safe_action"]
    return "Review source evidence before any protected action."


def _is_unsupported(ref: Mapping[str, Any], defaults: Mapping[str, Any]) -> bool:
    payload = ref["payload"]
    if payload is None:
        return False
    schema = str(ref.get("source_schema") or _payload_schema(payload) or "")
    return bool(schema and schema not in defaults["supported_schemas"])


def _has_unsafe_positive_authority(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in UNSAFE_POSITIVE_KEYS and _is_positive(item):
                return True
            if _has_unsafe_positive_authority(item):
                return True
    elif isinstance(value, list):
        return any(_has_unsafe_positive_authority(item) for item in value)
    return False


def _payload_schema(payload: Any) -> str | None:
    if isinstance(payload, Mapping):
        value = payload.get("schema")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _payload_generated_at(payload: Any) -> Any:
    if not isinstance(payload, Mapping):
        return None
    for key in ("generated_at_utc", "generated_utc", "generated_at", "generatedAt"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    freshness = payload.get("freshness")
    if isinstance(freshness, Mapping):
        return freshness.get("generated_at")
    return None


def _is_stale(generated_at: str | None, ttl_seconds: int | None, now: str) -> bool:
    if not generated_at or ttl_seconds is None:
        return False
    generated = _parse_utc(generated_at)
    checked = _parse_utc(now)
    if generated is None or checked is None:
        return True
    return (checked - generated).total_seconds() > ttl_seconds


def _parse_utc(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_value(value: Any, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _upper_string(value: Any) -> str:
    return str(value or "").strip().upper()


def _ttl(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def _known(payload: Mapping[str, Any] | None, key: str, allowed: set[str], default: str) -> str:
    if payload is None:
        return default
    value = _upper_string(payload.get(key))
    return value if value in allowed else default


def _known_display(value: Any, default: str) -> str:
    text = _upper_string(value)
    return text if text in DISPLAY_STATES else default


def _status_display(value: Any) -> str:
    text = _upper_string(value).replace("-", "_")
    if text in {"PASS", "PASSED", "OK", "SUCCESS", "READY", "DASHBOARD_READY"}:
        return "READY"
    if text in {"WARN", "WARNING", "REVIEW", "WAITING_FOR_REVIEW", "REQUIRES_REVIEW"}:
        return "REVIEW"
    if text in {"NEEDS_REVIEW", "REVIEW_REQUIRED"}:
        return "NEEDS_REVIEW"
    if text in {"FAIL", "FAILED", "ERROR"}:
        return "FAIL"
    if text in {"BLOCKED", "STOP", "SOS"}:
        return "BLOCKED"
    return "UNKNOWN"


def _validator_display(value: Any) -> str:
    text = _upper_string(value).replace("-", "_")
    if text in {"PASS", "PASSED", "OK", "SUCCESS", "GREEN"}:
        return "PASS"
    if text in {"WARN", "WARNING", "REVIEW", "REVIEW_REQUIRED"}:
        return "WARN"
    if text in {"FAIL", "FAILED", "ERROR", "INVALID"}:
        return "FAIL"
    if text in {"BLOCKED", "STOP", "SOS"}:
        return "BLOCKED"
    return "UNKNOWN"


def _mission_display(value: Any) -> str:
    text = _upper_string(value).replace("-", "_")
    if text in {"READY", "READY_FOR_NEXT_PACKET"}:
        return "READY"
    if text in {"BLOCKED", "STOP", "SOS"}:
        return "BLOCKED"
    if text in {"REQUIRES_APPROVAL", "REQUIRES_CLEANUP", "RUNNING_PREVIEW", "WAITING_FOR_REVIEW"}:
        return "REVIEW"
    return "UNKNOWN"


def _governor_display(payload: Mapping[str, Any]) -> str:
    category = _upper_string(payload.get("decision_category") or payload.get("category"))
    if "BLOCKED" in category or "STOP" in category:
        return "BLOCKED"
    if "REPAIR" in category or "REVIEW" in category or "STATUS_RECON" in category:
        return "REVIEW"
    if category:
        return "READY"
    return _status_display(payload.get("status"))


def _object_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, Mapping):
            result.append(dict(item))
    return result


def _boss_alert(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is not None and isinstance(payload.get("boss_alert"), Mapping):
        alert = dict(payload["boss_alert"])
        return {
            "active": bool(alert.get("active")),
            "level": str(alert.get("level") or "UNKNOWN"),
            "reason": str(alert.get("reason") or ""),
        }
    return {"active": False, "level": "UNKNOWN", "reason": ""}


def _resume_status(payload: Mapping[str, Any] | None) -> str:
    if payload is None:
        return "unknown"
    resume = payload.get("resume")
    if isinstance(resume, Mapping):
        if resume.get("can_resume") is True:
            return "can_resume"
        if resume.get("requested") is True:
            return "review_required"
        return str(resume.get("reason") or "not_requested")
    return str(payload.get("resume_status") or "unknown")


def _approval_status(payload: Mapping[str, Any] | None) -> str:
    if payload is None:
        return "unknown"
    approval = payload.get("approval_snapshot") or payload.get("approval")
    if isinstance(approval, Mapping):
        return str(
            approval.get("approval_gate_status")
            or approval.get("approval_status")
            or approval.get("approval_inbox_status")
            or "unknown"
        )
    return str(payload.get("approval_status") or "unknown")


def _nonnegative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value >= 0:
        return value
    return 0


def _is_positive(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "allowed", "enabled", "performed", "authorized"}
    return False


def _source_ref_type(value: str) -> str:
    allowed = {
        "canonical_schema",
        "canonical_doc",
        "source_code",
        "generated_projection",
        "runtime_evidence",
        "api_read_model",
        "fixture",
        "unknown",
    }
    return value if value in allowed else "unknown"


def _section_name_for_schema(source_schema: str) -> str:
    for name, defaults in SECTION_DEFAULTS.items():
        if source_schema == defaults["source_schema"] or source_schema in defaults["supported_schemas"]:
            return name
    return "system_state"


__all__ = ["project_dashboard_state"]
