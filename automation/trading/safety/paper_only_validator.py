"""Paper-only safety validator for completion sweep inputs and outputs."""

from __future__ import annotations

from collections.abc import Iterable


FORBIDDEN_TOKENS = {
    "webhook_url",
    "broker",
    "api_key",
    "secret_key",
    "live_order",
    "real_order",
    "account_id",
    "password",
    "token",
}


def validate_paper_payload(payload: dict) -> list[str]:
    """Return all blocking reasons; empty list means PASS."""
    blockers = []
    if payload.get("paper_only") is not True:
        blockers.append("paper_only must be true for this sweep")
    if payload.get("live_execution_status") != "BLOCKED":
        blockers.append("live_execution_status must be BLOCKED in paper mode")
    if payload.get("execution_allowed") is not False:
        blockers.append("execution_allowed must be false in paper-only mode")

    if _has_forbidden_tokens(payload):
        blockers.append("forbidden routing tokens detected in payload")
    return blockers


def _has_forbidden_tokens(value: object, *, _path: str = "root") -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_TOKENS:
                return True
            if _has_forbidden_tokens(item, _path=f"{_path}.{key}"):
                return True
    elif isinstance(value, list | tuple):
        for index, item in enumerate(value):
            if _has_forbidden_tokens(item, _path=f"{_path}[{index}]"):
                return True
    elif isinstance(value, str):
        lowered = value.lower()
        return any(token in lowered for token in FORBIDDEN_TOKENS)
    return False


def is_regime_approved(permission: str, regime: str, trend_score: float) -> bool:
    """Simple paper-only regime gate used for deterministic dry-run behavior."""
    mapping = {"bullish": "trend_up", "bearish": "trend_down", "neutral": "flat"}
    return mapping.get(permission, "flat") == regime and trend_score >= 0.5

