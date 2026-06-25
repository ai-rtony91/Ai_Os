from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO PACKET12E SANITIZED EVIDENCE CHAIN READINESS V1"
)
PACKET_ID = (
    "AIOS-FOREX-OANDA-DEMO-PACKET-12E-SANITIZED-EVIDENCE-CHAIN-READINESS-V1"
)

DEFAULT_OWNER_READ_OUTPUT_PATH = (
    "Reports/forex_delivery/"
    "oanda_demo_owner_run_sanitized_broker_read_output_v1.json"
)
DEFAULT_OWNER_RUN_BROKER_READ_OUTPUT_PATH = DEFAULT_OWNER_READ_OUTPUT_PATH
DEFAULT_PACKET09_EVIDENCE_PATH = (
    "Reports/forex_delivery/"
    "oanda_demo_packet09_sanitized_owner_run_telemetry_evidence_v1.json"
)
DEFAULT_PACKET11_ACCEPTANCE_REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_RUN_V1_REPORT.md"
)
DEFAULT_ACCEPTANCE_REPORT_PATH = DEFAULT_PACKET11_ACCEPTANCE_REPORT_PATH
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_PACKET12E_SANITIZED_EVIDENCE_CHAIN_READINESS_V1_REPORT.md"
)

PACKET12E_READY_TO_ADVANCE = "PACKET12E_READY_TO_ADVANCE"
PACKET12E_OWNER_RUN_CHAIN_INCOMPLETE = "PACKET12E_OWNER_RUN_CHAIN_INCOMPLETE"
PACKET12E_BLOCKED_UNSAFE_EVIDENCE = "PACKET12E_BLOCKED_UNSAFE_EVIDENCE"
PACKET12E_BLOCKED_ACCEPTANCE_NOT_CONFIRMED = (
    "PACKET12E_BLOCKED_ACCEPTANCE_NOT_CONFIRMED"
)

NEXT_ACTION_INCOMPLETE = "OWNER_RUN_PACKET_12D_THEN_PACKET_12B_THEN_PACKET_11"
NEXT_ACTION_READY = "ADVANCE_TO_NEXT_GOVERNED_DEMO_EVIDENCE_PACKET"
NEXT_ACTION_UNSAFE = "STOP_REMOVE_UNSAFE_EVIDENCE_AND_RERUN_PACKET_12E"
NEXT_ACTION_ACCEPTANCE = "RUN_PACKET_11_ACCEPTANCE_WITH_SANITIZED_PACKET09_EVIDENCE"

INTERNAL_LEDGER_ONLY = "INTERNAL_LEDGER_ONLY"

ACCEPTED_PACKET11_MARKERS = (
    "acceptance_status: SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED",
    "sanitized_evidence_accepted: yes",
)

UNSAFE_KEY_MARKERS = (
    "accountid",
    "accountnumber",
    "accountidentifier",
    "authorization",
    "bearer",
    "token",
    "apikey",
    "password",
    "secret",
    "credential",
    "rawpayload",
    "rawbrokerpayload",
    "rawresponse",
)

SAFE_FALSE_AUDIT_KEYS = {
    "rawbrokerpayloadpersisted",
    "secretswritten",
    "brokernetworkcallperformed",
    "liveendpointused",
    "orderplacementperformed",
    "ordermutationperformed",
    "ordercloseperformed",
    "positionmutationperformed",
    "trademutationperformed",
    "withdrawalallowednow",
    "transferallowednow",
    "moneymovementallowednow",
    "dashboardfakenumbersallowed",
    "dashboardmocknumbersallowed",
}
SAFE_TRUE_AUDIT_KEYS = {
    "noneworderplaced",
    "nolivetradeplaced",
    "nobrokerstatemodified",
    "nosecretswritten",
}

BEARER_TOKEN_RE = re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{10,}", re.IGNORECASE)
API_KEY_PREFIX_RE = re.compile(
    r"\b(?:sk|sk-proj|api|key|token)[-_][A-Za-z0-9._~+/=-]{16,}\b",
    re.IGNORECASE,
)
LONG_OPAQUE_RE = re.compile(
    r"\b(?=[A-Za-z0-9._~+/=-]{32,}\b)"
    r"(?=[A-Za-z0-9._~+/=-]*[a-z])"
    r"(?=[A-Za-z0-9._~+/=-]*[A-Z])"
    r"(?=[A-Za-z0-9._~+/=-]*\d)"
    r"[A-Za-z0-9._~+/=-]{32,}\b"
)
OANDA_ACCOUNT_ID_RE = re.compile(r"\b\d{3}-\d{3}-\d{6,}-\d{3}\b")
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"\b(?:authorization|api[_-]?key|password|secret|token)\s*[:=]\s*\S+",
    re.IGNORECASE,
)


def run_packet12e_sanitized_evidence_chain_readiness(
    owner_read_output_path: str | Path = DEFAULT_OWNER_READ_OUTPUT_PATH,
    packet09_evidence_path: str | Path = DEFAULT_PACKET09_EVIDENCE_PATH,
    packet11_acceptance_report_path: str | Path = DEFAULT_PACKET11_ACCEPTANCE_REPORT_PATH,
    owner_run_broker_read_output_path: str | Path | None = None,
    acceptance_report_path: str | Path | None = None,
) -> dict[str, Any]:
    if owner_run_broker_read_output_path is not None:
        owner_read_output_path = owner_run_broker_read_output_path
    if acceptance_report_path is not None:
        packet11_acceptance_report_path = acceptance_report_path

    required_paths = {
        "owner_run_sanitized_broker_read_output": Path(owner_read_output_path),
        "packet09_sanitized_owner_run_telemetry_evidence": Path(packet09_evidence_path),
        "packet11_sanitized_evidence_normalizer_acceptance_report": Path(
            packet11_acceptance_report_path
        ),
    }
    missing_required_files = [
        _path_text(path) for path in required_paths.values() if not path.exists()
    ]
    unsafe_findings = _scan_present_files(required_paths)
    acceptance_confirmed = _acceptance_confirmed(
        required_paths["packet11_sanitized_evidence_normalizer_acceptance_report"]
    )

    if unsafe_findings:
        status = PACKET12E_BLOCKED_UNSAFE_EVIDENCE
        next_action = NEXT_ACTION_UNSAFE
    elif missing_required_files:
        status = PACKET12E_OWNER_RUN_CHAIN_INCOMPLETE
        next_action = NEXT_ACTION_INCOMPLETE
    elif not acceptance_confirmed:
        status = PACKET12E_BLOCKED_ACCEPTANCE_NOT_CONFIRMED
        next_action = NEXT_ACTION_ACCEPTANCE
    else:
        status = PACKET12E_READY_TO_ADVANCE
        next_action = NEXT_ACTION_READY

    return {
        "packet_name": PACKET_NAME,
        "packet_id": PACKET_ID,
        "packet12e_status": status,
        "status": status,
        "ready_to_advance": status == PACKET12E_READY_TO_ADVANCE,
        "required_files": {
            name: _path_text(path) for name, path in required_paths.items()
        },
        "owner_run_broker_read_output_path": _path_text(
            required_paths["owner_run_sanitized_broker_read_output"]
        ),
        "packet09_evidence_path": _path_text(
            required_paths["packet09_sanitized_owner_run_telemetry_evidence"]
        ),
        "acceptance_report_path": _path_text(
            required_paths["packet11_sanitized_evidence_normalizer_acceptance_report"]
        ),
        "missing_files": missing_required_files,
        "missing_required_files": missing_required_files,
        "unsafe_evidence_found": bool(unsafe_findings),
        "rejected_unsafe_evidence": unsafe_findings,
        "unsafe_findings": unsafe_findings,
        "acceptance_confirmed": acceptance_confirmed,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "raw_broker_payload_persisted": False,
        "broker_network_call_performed": False,
        "broker_helper_call_required": False,
        "broker_helper_call_performed": False,
        "validator_broker_network_call_performed": False,
        "validator_broker_helper_call_performed": False,
        "network_call_performed": False,
        "money_movement_allowed_now": False,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "next_action": next_action,
    }


def render_packet12e_sanitized_evidence_chain_readiness_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    missing = _sequence_text(result.get("missing_required_files"))
    unsafe = _sequence_text(result.get("unsafe_findings"))
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO PACKET12E SANITIZED EVIDENCE CHAIN READINESS V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- packet_id: {PACKET_ID}",
            f"- repo_branch: {branch}",
            f"- packet12e_status: {_display(result.get('packet12e_status'))}",
            f"- acceptance_confirmed: {_true_false(result.get('acceptance_confirmed'))}",
            f"- next_action: {_display(result.get('next_action'))}",
            "",
            "## Required Files",
            "",
            *[
                f"- {name}: {_display(path)}"
                for name, path in _mapping_items(result.get("required_files"))
            ],
            "",
            "## Missing Required Files",
            "",
            *([f"- {item}" for item in missing] or ["- none"]),
            "",
            "## Unsafe Findings",
            "",
            *([f"- {item}" for item in unsafe] or ["- none"]),
            "",
            "## Safety",
            "",
            f"- no_new_order_placed: {_true_false(result.get('no_new_order_placed'))}",
            f"- no_live_trade_placed: {_true_false(result.get('no_live_trade_placed'))}",
            (
                "- no_broker_state_modified: "
                f"{_true_false(result.get('no_broker_state_modified'))}"
            ),
            f"- no_secrets_written: {_true_false(result.get('no_secrets_written'))}",
            (
                "- raw_broker_payload_persisted: "
                f"{_true_false(result.get('raw_broker_payload_persisted'))}"
            ),
            (
                "- broker_network_call_performed: "
                f"{_true_false(result.get('broker_network_call_performed'))}"
            ),
            (
                "- broker_helper_call_required: "
                f"{_true_false(result.get('broker_helper_call_required'))}"
            ),
            (
                "- broker_helper_call_performed: "
                f"{_true_false(result.get('broker_helper_call_performed'))}"
            ),
            (
                "- money_movement_allowed_now: "
                f"{_true_false(result.get('money_movement_allowed_now'))}"
            ),
            (
                "- withdrawal_allowed_now: "
                f"{_true_false(result.get('withdrawal_allowed_now'))}"
            ),
            (
                "- transfer_allowed_now: "
                f"{_true_false(result.get('transfer_allowed_now'))}"
            ),
            (
                "- profit_reserve_bucket_mode: "
                f"{_display(result.get('profit_reserve_bucket_mode'))}"
            ),
            "",
            "## Machine Result",
            "",
            "```json",
            json.dumps(dict(result), indent=2, sort_keys=True),
            "```",
            "",
        ]
    )


def write_packet12e_sanitized_evidence_chain_readiness_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_packet12e_sanitized_evidence_chain_readiness_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _scan_present_files(paths: Mapping[str, Path]) -> list[str]:
    findings: list[str] = []
    for label, path in paths.items():
        if not path.exists():
            continue
        findings.extend(_scan_file(label, path))
    return findings


def _scan_file(label: str, path: Path) -> list[str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{label}: unreadable non-utf8 evidence file"]
    if path.suffix.lower() == ".json":
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return [f"{label}: invalid json evidence file"]
        return _scan_json_value(label, parsed)
    return _scan_text(label, raw)


def _scan_json_value(label: str, value: Any, trail: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_trail = f"{trail}.{key_text}"
            key_finding = _unsafe_key_finding(label, child_trail, key_text, child)
            if key_finding:
                findings.append(key_finding)
            findings.extend(_scan_json_value(label, child, child_trail))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_scan_json_value(label, child, f"{trail}[{index}]"))
    elif isinstance(value, str):
        value_finding = _unsafe_value_finding(label, trail, value)
        if value_finding:
            findings.append(value_finding)
    return findings


def _scan_text(label: str, raw: str) -> list[str]:
    findings: list[str] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or _is_safe_text_line(stripped):
            continue
        key, value = _split_report_line(stripped)
        if key is not None:
            key_finding = _unsafe_key_finding(
                label,
                f"line {line_number}",
                key,
                value,
            )
            if key_finding:
                findings.append(key_finding)
        value_finding = _unsafe_value_finding(label, f"line {line_number}", stripped)
        if value_finding:
            findings.append(value_finding)
    return findings


def _unsafe_key_finding(
    label: str,
    trail: str,
    key: str,
    value: Any,
) -> str | None:
    normalized = _normalize_marker(key)
    if _safe_audit_key_value(normalized, value):
        return None
    for marker in UNSAFE_KEY_MARKERS:
        if marker in normalized:
            return f"{label} {trail}: unsafe key marker '{key}'"
    return None


def _unsafe_value_finding(label: str, trail: str, value: str) -> str | None:
    stripped = value.strip()
    if _is_safe_text_line(stripped):
        return None
    normalized = _normalize_marker(stripped)
    if BEARER_TOKEN_RE.search(stripped):
        return f"{label} {trail}: bearer-token-like value"
    if API_KEY_PREFIX_RE.search(stripped):
        return f"{label} {trail}: api-key-like value"
    if LONG_OPAQUE_RE.search(stripped):
        return f"{label} {trail}: long opaque credential-like value"
    if OANDA_ACCOUNT_ID_RE.search(stripped):
        return f"{label} {trail}: account-identifier-like value"
    if CREDENTIAL_ASSIGNMENT_RE.search(stripped):
        return f"{label} {trail}: credential-assignment-like value"
    for marker in UNSAFE_KEY_MARKERS:
        if marker in normalized:
            return f"{label} {trail}: unsafe value marker"
    if _looks_like_raw_json_dump(stripped):
        return f"{label} {trail}: raw-json-dump-like string value"
    return None


def _acceptance_confirmed(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return all(marker in text for marker in ACCEPTED_PACKET11_MARKERS)


def _safe_audit_key_value(normalized_key: str, value: Any) -> bool:
    if normalized_key in SAFE_FALSE_AUDIT_KEYS and _is_false(value):
        return True
    if normalized_key in SAFE_TRUE_AUDIT_KEYS and _is_true(value):
        return True
    return False


def _is_safe_text_line(text: str) -> bool:
    normalized = _normalize_marker(text)
    if "rawbrokerpayloadpersistedfalse" in normalized:
        return True
    if "rawownerevidencepayloadpersistedfalse" in normalized:
        return True
    if "nosecretswritten" in normalized:
        return True
    if "fakemockdashboardaccountvaluesareforbidden" in normalized:
        return True
    if "dashboardfakenumbersallowedfalse" in normalized:
        return True
    if "dashboardmocknumbersallowedfalse" in normalized:
        return True
    return False


def _split_report_line(text: str) -> tuple[str | None, str | None]:
    stripped = text.lstrip("- ").strip()
    if ":" not in stripped:
        return None, None
    key, value = stripped.split(":", 1)
    return key.strip(), value.strip()


def _looks_like_raw_json_dump(value: str) -> bool:
    stripped = value.strip()
    if not (
        (stripped.startswith("{") and stripped.endswith("}"))
        or (stripped.startswith("[") and stripped.endswith("]"))
    ):
        return False
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return False
    return isinstance(parsed, (dict, list))


def _normalize_marker(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _is_true(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes"}
    return False


def _is_false(value: Any) -> bool:
    if value is False:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"false", "no"}
    return False


def _sequence_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence):
        return [str(item) for item in value]
    return []


def _mapping_items(value: Any) -> list[tuple[str, Any]]:
    if not isinstance(value, Mapping):
        return []
    return [(str(key), item) for key, item in value.items()]


def _path_text(path: Path) -> str:
    return path.as_posix()


def _display(value: Any) -> str:
    if value in (None, ""):
        return "UNKNOWN"
    return str(value)


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
