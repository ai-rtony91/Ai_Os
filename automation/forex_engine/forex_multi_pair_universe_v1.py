"""Validate the governed multi-pair Forex universe for burst evaluation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_MULTI_PAIR_UNIVERSE_V1"
MODE = "READ_ONLY_METADATA_ONLY_MULTI_PAIR_UNIVERSE"

MULTI_PAIR_UNIVERSE_READY = "MULTI_PAIR_UNIVERSE_READY"
BLOCKED_BY_EMPTY_PAIR_UNIVERSE = "BLOCKED_BY_EMPTY_PAIR_UNIVERSE"
BLOCKED_BY_UNSUPPORTED_PAIR = "BLOCKED_BY_UNSUPPORTED_PAIR"
BLOCKED_BY_EXCLUDED_PAIR = "BLOCKED_BY_EXCLUDED_PAIR"
BLOCKED_BY_PAIR_LIMIT = "BLOCKED_BY_PAIR_LIMIT"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_GOVERNED_MULTI_PAIR_BURST_VACATION_MODE_V1"

HARD_FALSE_FIELDS = (
    "live_trade_executed_by_this_module",
    "demo_trade_executed_by_this_module",
    "broker_api_called_by_this_module",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "money_moved",
    "bank_access_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
    "live_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
    "password",
    "master_password",
    "vault_password",
    "account_number",
    "routing_number",
    "card_number",
    "debit_card_number",
    "cvv",
    "account_id",
    "oanda_account_id",
    "bearer",
    "broker_token",
    "access_token",
    "private_key",
)

SAFE_SENSITIVE_FALSE_FIELDS = frozenset(
    {
        "account_id_in_payload",
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
    }
)
SAFE_SENSITIVE_TRUE_FIELDS = frozenset({"no_account_ids"})

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer",
    "api key",
    "token value",
    "broker token",
    "access token",
    "private key",
    "password",
    "secret",
    "-----begin",
)

BANKING_KEY_PARTS = (
    "bank",
    "banking",
    "withdraw",
    "withdrawal",
    "transfer",
    "debit",
    "card",
    "rail",
    "ach",
    "wire",
    "sweep",
    "bucket_purge",
    "money_movement",
    "deposit",
)

BANKING_ALLOWED_FALSE_FIELDS = frozenset(
    {
        "money_moved",
        "money_movement_allowed",
        "bank_access_used",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
    }
)

REQUIRED_FIELDS = (
    "allowed_pairs",
    "excluded_pairs",
    "max_pairs_to_scan",
    "all_pairs_scan_requested",
    "only_trade_allowed_pairs",
    "unsupported_pairs_block",
    "pair_universe_source",
    "owner_review_required",
)


def evaluate_forex_multi_pair_universe_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate declared Forex pairs without discovering pairs externally."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return build_common_result(
            schema=SCHEMA,
            mode=MODE,
            status=BLOCKED_BY_SENSITIVE_DATA,
            ready=False,
            governed_burst_requested=_governed_requested(source),
            multi_pair_enabled=False,
            blockers=sensitive_blockers,
            next_best_packet=NEXT_BEST_PACKET,
            safe_manual_next_action="Remove sensitive keys or values before universe review.",
            extra=_universe_extra(),
        )

    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return build_common_result(
            schema=SCHEMA,
            mode=MODE,
            status=BLOCKED_BY_BANKING_FOCUS,
            ready=False,
            governed_burst_requested=_governed_requested(source),
            multi_pair_enabled=False,
            blockers=banking_blockers,
            next_best_packet=NEXT_BEST_PACKET,
            safe_manual_next_action="Remove banking, withdrawal, transfer, or money-movement focus fields.",
            extra=_universe_extra(),
        )

    pair_universe = _mapping(source.get("pair_universe"))
    if not pair_universe:
        return _blocked_universe(source, INCOMPLETE_INPUTS, ("pair_universe_missing",))

    missing = _missing_fields(pair_universe, REQUIRED_FIELDS)
    if missing:
        return _blocked_universe(
            source,
            INCOMPLETE_INPUTS,
            tuple(f"missing_{field}" for field in missing),
            pair_universe=pair_universe,
        )

    allowed_pairs = _pair_list(pair_universe.get("allowed_pairs"))
    excluded_pairs = _pair_list(pair_universe.get("excluded_pairs"))
    candidate_pairs = _candidate_pairs(pair_universe, allowed_pairs)
    max_pairs_to_scan = _int(pair_universe.get("max_pairs_to_scan"))
    all_pairs_scan_requested = _bool(pair_universe.get("all_pairs_scan_requested"))

    if not allowed_pairs:
        return _blocked_universe(
            source,
            BLOCKED_BY_EMPTY_PAIR_UNIVERSE,
            ("allowed_pairs_empty",),
            pair_universe=pair_universe,
        )
    if max_pairs_to_scan < 1 or max_pairs_to_scan > len(allowed_pairs):
        return _blocked_universe(
            source,
            BLOCKED_BY_PAIR_LIMIT,
            ("max_pairs_to_scan_outside_declared_universe",),
            pair_universe=pair_universe,
        )

    required_true = {
        "only_trade_allowed_pairs": _bool(pair_universe.get("only_trade_allowed_pairs")),
        "unsupported_pairs_block": _bool(pair_universe.get("unsupported_pairs_block")),
        "pair_universe_source_present": _present(pair_universe.get("pair_universe_source")),
        "owner_review_required": _bool(pair_universe.get("owner_review_required")),
    }
    false_gates = tuple(key for key, value in required_true.items() if not value)
    if false_gates:
        return _blocked_universe(
            source,
            INCOMPLETE_INPUTS,
            false_gates,
            pair_universe=pair_universe,
        )

    unsupported_pairs = tuple(pair for pair in candidate_pairs if pair not in allowed_pairs)
    if unsupported_pairs:
        return _blocked_universe(
            source,
            BLOCKED_BY_UNSUPPORTED_PAIR,
            tuple(f"unsupported_pair_{pair}" for pair in unsupported_pairs),
            pair_universe=pair_universe,
        )

    excluded_hits = tuple(pair for pair in candidate_pairs if pair in excluded_pairs)
    if excluded_hits:
        return _blocked_universe(
            source,
            BLOCKED_BY_EXCLUDED_PAIR,
            tuple(f"excluded_pair_{pair}" for pair in excluded_hits),
            pair_universe=pair_universe,
        )

    scan_pair_count = len(allowed_pairs) if all_pairs_scan_requested else len(candidate_pairs[:max_pairs_to_scan])
    summary = {
        "allowed_pair_count": len(allowed_pairs),
        "excluded_pair_count": len(excluded_pairs),
        "candidate_pair_count": len(candidate_pairs),
        "max_pairs_to_scan": max_pairs_to_scan,
        "all_pairs_scan_requested": all_pairs_scan_requested,
        "only_trade_allowed_pairs": True,
        "unsupported_pairs_block": True,
        "pair_universe_source": _text(pair_universe.get("pair_universe_source")),
    }
    extra = _universe_extra(
        pair_universe_summary=summary,
        scan_pair_count=scan_pair_count,
        allowed_pairs_sanitized=allowed_pairs,
        excluded_pairs_sanitized=excluded_pairs,
        all_pairs_scan_requested=all_pairs_scan_requested,
        ready_for_opportunity_batch=True,
    )
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=MULTI_PAIR_UNIVERSE_READY,
        ready=True,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=True,
        blockers=(),
        next_best_packet="AIOS_FOREX_MULTI_PAIR_OPPORTUNITY_BATCH_V1",
        safe_manual_next_action="Route declared allowed pairs into opportunity batch scoring.",
        extra=extra,
    )


def _blocked_universe(
    source: Mapping[str, Any],
    status: str,
    blockers: Sequence[str],
    *,
    pair_universe: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = _mapping(pair_universe)
    extra = _universe_extra(
        pair_universe_summary={
            "allowed_pair_count": len(_pair_list(data.get("allowed_pairs"))),
            "excluded_pair_count": len(_pair_list(data.get("excluded_pairs"))),
            "max_pairs_to_scan": _int(data.get("max_pairs_to_scan")),
            "all_pairs_scan_requested": _bool(data.get("all_pairs_scan_requested")),
        }
    )
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=False,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=False,
        blockers=tuple(blockers),
        next_best_packet=NEXT_BEST_PACKET,
        safe_manual_next_action=_safe_manual_next_action(status),
        extra=extra,
    )


def _safe_manual_next_action(status: str) -> str:
    if status == BLOCKED_BY_EMPTY_PAIR_UNIVERSE:
        return "Declare at least one owner-reviewed allowed pair."
    if status == BLOCKED_BY_UNSUPPORTED_PAIR:
        return "Remove candidates outside the declared allowed pair universe."
    if status == BLOCKED_BY_EXCLUDED_PAIR:
        return "Remove candidate pairs listed in excluded_pairs."
    if status == BLOCKED_BY_PAIR_LIMIT:
        return "Set max_pairs_to_scan between one and the declared allowed pair count."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values before universe review."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, or money-movement focus fields."
    return "Provide complete pair_universe metadata."


def _universe_extra(
    *,
    pair_universe_summary: Mapping[str, Any] | None = None,
    scan_pair_count: int = 0,
    allowed_pairs_sanitized: Sequence[str] = (),
    excluded_pairs_sanitized: Sequence[str] = (),
    all_pairs_scan_requested: bool = False,
    ready_for_opportunity_batch: bool = False,
) -> dict[str, Any]:
    return {
        "pair_universe_summary": dict(pair_universe_summary or {}),
        "scan_pair_count": scan_pair_count,
        "allowed_pairs_sanitized": list(allowed_pairs_sanitized),
        "excluded_pairs_sanitized": list(excluded_pairs_sanitized),
        "all_pairs_scan_requested": bool(all_pairs_scan_requested),
        "ready_for_opportunity_batch": bool(ready_for_opportunity_batch),
    }


def build_common_result(
    *,
    schema: str,
    mode: str,
    status: str,
    ready: bool,
    governed_burst_requested: bool,
    multi_pair_enabled: bool,
    blockers: Sequence[str],
    next_best_packet: str,
    safe_manual_next_action: str,
    extra: Mapping[str, Any] | None = None,
    audit_extra: Mapping[str, Any] | None = None,
    safety_extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    blocker_list = list(_unique(blockers))
    safety = {
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        **{field: False for field in HARD_FALSE_FIELDS},
    }
    if safety_extra:
        safety.update(dict(safety_extra))
    audit_record = {
        "schema": schema,
        "mode": mode,
        "status": status,
        "ready": bool(ready),
        "governed_burst_requested": bool(governed_burst_requested),
        "multi_pair_enabled": bool(multi_pair_enabled),
        "blockers": blocker_list,
        "next_best_packet": next_best_packet,
        "read_only": True,
        "metadata_only": True,
    }
    if audit_extra:
        audit_record.update(dict(audit_extra))
    result = {
        "schema": schema,
        "mode": mode,
        "status": status,
        "ready": bool(ready),
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "governed_burst_requested": bool(governed_burst_requested),
        "multi_pair_enabled": bool(multi_pair_enabled),
        "blockers": blocker_list,
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": safe_manual_next_action,
        "audit_record": audit_record,
        "safety": safety,
        **{field: False for field in HARD_FALSE_FIELDS},
    }
    if extra:
        result.update(dict(extra))
    return result


def sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in SAFE_SENSITIVE_FALSE_FIELDS and child is False:
                continue
            if normalized in SAFE_SENSITIVE_TRUE_FIELDS and child is True:
                continue
            if _sensitive_key_blocked(normalized):
                blockers.append(f"{child_path}:sensitive_key")
                continue
            blockers.extend(sensitive_data_blockers(child, child_path))
        return tuple(_unique(blockers))

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))

    if isinstance(value, str) and _has_secret_value(value):
        blockers.append(f"{path}:secret_like_value")
    elif isinstance(value, int) and not isinstance(value, bool) and _has_long_digit_run(str(value)):
        blockers.append(f"{path}:long_digit_run")
    return tuple(_unique(blockers))


def banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in BANKING_ALLOWED_FALSE_FIELDS and child is False:
                continue
            if any(part in normalized for part in BANKING_KEY_PARTS):
                blockers.append(f"{child_path}:banking_focus")
                continue
            blockers.extend(banking_focus_blockers(child, child_path))
        return tuple(_unique(blockers))

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(banking_focus_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    return tuple(_unique(blockers))


def _sensitive_key_blocked(normalized_key: str) -> bool:
    return any(part in normalized_key for part in SENSITIVE_KEY_PARTS)


def _has_secret_value(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS) or _has_long_digit_run(lowered)


def _has_long_digit_run(text: str, minimum: int = 8) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _candidate_pairs(pair_universe: Mapping[str, Any], allowed_pairs: Sequence[str]) -> list[str]:
    explicit = pair_universe.get("candidate_pairs")
    if isinstance(explicit, Sequence) and not isinstance(explicit, (str, bytes, bytearray)):
        return _pair_list(explicit)
    if _bool(pair_universe.get("all_pairs_scan_requested")):
        return list(allowed_pairs)
    max_pairs_to_scan = _int(pair_universe.get("max_pairs_to_scan"))
    return list(allowed_pairs[:max_pairs_to_scan])


def _pair_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    pairs: list[str] = []
    for item in value:
        text = _pair_text(item)
        if text:
            pairs.append(text)
    return _unique(pairs)


def _pair_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().upper().replace("/", "_").replace("-", "_")


def _governed_requested(source: Mapping[str, Any]) -> bool:
    return _bool(source.get("governed_burst_requested")) or _bool(
        _mapping(source.get("permission")).get("governed_burst_requested")
    )


def _missing_fields(source: Mapping[str, Any], required_fields: Sequence[str]) -> tuple[str, ...]:
    return tuple(field for field in required_fields if field not in source)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _int(value: Any) -> int:
    if isinstance(value, bool) or value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return 0
    return 0


def _number(value: Any) -> float:
    if isinstance(value, bool) or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return 0.0
    return 0.0


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result
