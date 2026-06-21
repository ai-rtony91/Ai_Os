"""AIOS Forex Packet H: account metadata sanitizer.

Removes account identifiers while preserving safe governance/replay metadata.
"""

from __future__ import annotations

from typing import Mapping


FORBIDDEN_ACCOUNT_KEYS = frozenset(
    {
        "account",
        "account_id",
        "account_number",
        "account_identifier",
        "broker_account",
        "oanda_account_id",
        "mt_account",
    }
)


def sanitize_account_metadata(metadata: Mapping[str, object] | None) -> dict[str, object]:
    if not metadata:
        return {}

    sanitized: dict[str, object] = {}

    for key, value in metadata.items():
        normalized_key = str(key).strip().lower()

        if normalized_key in FORBIDDEN_ACCOUNT_KEYS:
            continue

        if "account" in normalized_key and normalized_key not in {
            "account_boundary_status",
            "account_boundary_clear",
        }:
            continue

        sanitized[str(key)] = value

    return sanitized