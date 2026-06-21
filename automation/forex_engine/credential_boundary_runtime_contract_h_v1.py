"""AIOS Forex Packet H: credential boundary runtime contract.

Local-only contract. It never reads credentials, env vars, files, vaults,
broker SDKs, or network resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple


FORBIDDEN_CREDENTIAL_KEYS = frozenset(
    {
        "password",
        "token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "access_token",
        "refresh_token",
        "bearer",
        "credential",
    }
)


@dataclass(frozen=True)
class CredentialBoundaryResult:
    clear: bool
    blocked_reasons: Tuple[str, ...]


def validate_credential_boundary(metadata: Mapping[str, object] | None) -> CredentialBoundaryResult:
    if not metadata:
        return CredentialBoundaryResult(True, ())

    reasons = []
    for key, value in metadata.items():
        normalized_key = str(key).strip().lower()
        normalized_value = str(value).strip()

        if normalized_key in FORBIDDEN_CREDENTIAL_KEYS:
            reasons.append(f"credential_key_prohibited:{normalized_key}")

        if normalized_value.startswith(("sk-", "Bearer ", "eyJ")):
            reasons.append(f"credential_value_leak:{normalized_key}")

        if ".env" in normalized_value.lower():
            reasons.append(f"repo_env_reference_prohibited:{normalized_key}")

    return CredentialBoundaryResult(not reasons, tuple(dict.fromkeys(reasons)))