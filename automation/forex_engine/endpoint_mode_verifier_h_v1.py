"""AIOS Forex Packet H: endpoint mode verifier.

Local-only validation. No broker SDK, no endpoint calls, no network access,
no credentials, no account identifiers, and no execution behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class EndpointMode(str, Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"


@dataclass(frozen=True)
class EndpointModeVerification:
    allowed: bool
    normalized_mode: str
    blocked_reasons: Tuple[str, ...]


def verify_endpoint_mode(mode: str | None) -> EndpointModeVerification:
    if mode is None:
        return EndpointModeVerification(False, "", ("endpoint_mode_missing",))

    normalized = str(mode).strip().upper()
    if not normalized:
        return EndpointModeVerification(False, "", ("endpoint_mode_missing",))

    if "," in normalized or "|" in normalized or "/" in normalized:
        return EndpointModeVerification(False, normalized, ("endpoint_mode_ambiguous",))

    if normalized == EndpointMode.LIVE.value:
        return EndpointModeVerification(False, normalized, ("live_endpoint_prohibited",))

    if normalized != EndpointMode.DEMO.value:
        return EndpointModeVerification(False, normalized, ("endpoint_mode_unknown",))

    return EndpointModeVerification(True, normalized, ())