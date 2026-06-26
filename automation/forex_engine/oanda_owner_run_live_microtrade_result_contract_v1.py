"""Read-only result capture contract for one owner-run live microtrade."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


VERSION = "oanda_owner_run_live_microtrade_result_contract_v1"
PACKET_ID = "AIOS-FOREX-OANDA-OWNER-RUN-LIVE-MICROTRADE-RESULT-CAPTURE-V1"

EXACT_OWNER_WARNING = "Do not execute unless Anthony explicitly approves."
EXACT_RESULT_WARNING = (
    "Owner-run live microtrade result capture only. Codex is not authorized to "
    "execute, call a broker, access credentials, place orders, approve repeat "
    "trading, compound profits, or move money."
)
EXACT_ONE_SENTENCE_ANSWER = (
    "AIOS can now prepare a read-only capture package for one owner-run live "
    "microtrade result, but repeat trading, vacation mode, compounding, and "
    "bank movement remain blocked until the result is reviewed and approved by Anthony."
)
EXACT_NEXT_OWNER_ACTION = (
    "Review the captured owner-run live microtrade result and decide whether it "
    "is profit, loss, breakeven, incomplete, or unsafe; do not treat this as "
    "approval for repeat trading."
)
EXACT_NEXT_CODEX_PACKET = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-RESULT-TO-NEXT-PROOF-ROUTER-V1"
)

OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_READY = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_READY"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE"
)

PROTECTED_FLAG_NAMES = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "live_execution_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "live_micro_trade_exception_allowed",
    "owner_live_execution_approval_present",
    "codex_live_execution_authorized",
    "unattended_vacation_mode_allowed",
    "vacation_profit_trial_allowed",
    "repeat_live_trade_allowed",
)

PROTECTED_FLAGS_FALSE = {name: False for name in PROTECTED_FLAG_NAMES}

REQUIRED_SANITIZED_RESULT_FIELDS = (
    "result_reference",
    "owner_action_confirmed_outside_codex",
    "provider_label",
    "instrument",
    "direction",
    "planned_units",
    "actual_units",
    "open_time_utc",
    "close_time_utc",
    "planned_entry_source",
    "sanitized_entry_price",
    "sanitized_exit_price",
    "realized_pl",
    "realized_pl_currency",
    "planned_max_loss",
    "planned_risk_r",
    "realized_r",
    "spread_observed",
    "slippage_observed",
    "trade_closed",
    "one_shot_only_confirmed",
    "no_repeat_execution_confirmed",
    "no_compounding_confirmed",
    "no_bank_movement_confirmed",
    "no_autonomous_loop_confirmed",
    "no_credentials_in_payload",
    "no_account_id_in_payload",
    "no_broker_order_id_in_payload",
    "no_raw_broker_payload",
    "evidence_references_sanitized",
)

OPTIONAL_SANITIZED_RESULT_FIELDS = (
    "max_units",
    "planned_instrument",
    "planned_direction",
    "planned_one_shot_only",
    "post_trade_capture_evidence_present",
    "post_trade_capture_complete",
    "proof_label",
)

ALLOWED_SANITIZED_RESULT_FIELDS = (
    REQUIRED_SANITIZED_RESULT_FIELDS + OPTIONAL_SANITIZED_RESULT_FIELDS
)

SAFE_TRUE_CONFIRMATION_FIELDS = (
    "owner_action_confirmed_outside_codex",
    "trade_closed",
    "one_shot_only_confirmed",
    "no_repeat_execution_confirmed",
    "no_compounding_confirmed",
    "no_bank_movement_confirmed",
    "no_autonomous_loop_confirmed",
    "no_credentials_in_payload",
    "no_account_id_in_payload",
    "no_broker_order_id_in_payload",
    "no_raw_broker_payload",
)

UNSAFE_MUST_BE_TRUE_FIELDS = (
    "no_credentials_in_payload",
    "no_account_id_in_payload",
    "no_broker_order_id_in_payload",
    "no_raw_broker_payload",
    "no_repeat_execution_confirmed",
    "no_compounding_confirmed",
    "no_bank_movement_confirmed",
    "no_autonomous_loop_confirmed",
)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultContractInput:
    owner_result: Mapping[str, Any] | None
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultContractResult:
    version: str
    packet_id: str
    classification: str
    required_sanitized_fields: tuple[str, ...]
    sanitized_result_fields: Mapping[str, Any]
    missing_fields: tuple[str, ...]
    blocked_items: tuple[str, ...]
    result_capture_only: bool
    owner_warning: str
    result_warning: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    live_micro_trade_exception_allowed: bool
    owner_live_execution_approval_present: bool
    codex_live_execution_authorized: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool
    repeat_live_trade_allowed: bool


def build_sample_profit_result_input() -> OandaOwnerRunLiveMicrotradeResultContractInput:
    return OandaOwnerRunLiveMicrotradeResultContractInput(
        owner_result=_sample_owner_result(realized_pl="0.20", realized_r="0.20")
    )


def build_sample_loss_result_input() -> OandaOwnerRunLiveMicrotradeResultContractInput:
    return OandaOwnerRunLiveMicrotradeResultContractInput(
        owner_result=_sample_owner_result(
            result_reference="SANITIZED-OWNER-RUN-RESULT-LOSS-001",
            sanitized_exit_price="1.09975",
            realized_pl="-0.25",
            realized_r="-0.25",
        )
    )


def build_sample_breakeven_result_input() -> OandaOwnerRunLiveMicrotradeResultContractInput:
    return OandaOwnerRunLiveMicrotradeResultContractInput(
        owner_result=_sample_owner_result(
            result_reference="SANITIZED-OWNER-RUN-RESULT-BREAKEVEN-001",
            sanitized_exit_price="1.10000",
            realized_pl="0.00",
            realized_r="0.00",
        )
    )


def build_sample_missing_owner_result_input() -> OandaOwnerRunLiveMicrotradeResultContractInput:
    return OandaOwnerRunLiveMicrotradeResultContractInput(owner_result=None)


def build_sample_unsafe_result_input() -> OandaOwnerRunLiveMicrotradeResultContractInput:
    owner_result = dict(
        _sample_owner_result(
            result_reference="SANITIZED-OWNER-RUN-RESULT-UNSAFE-001",
            realized_pl="0.20",
            realized_r="0.20",
        )
    )
    owner_result["no_credentials_in_payload"] = False
    owner_result["repeat_live_trade_allowed"] = True
    return OandaOwnerRunLiveMicrotradeResultContractInput(
        owner_result=owner_result,
        unsafe_flags={"owner_result_contains_private_runtime_material": True},
    )


def evaluate_oanda_owner_run_live_microtrade_result_contract(
    contract_input: OandaOwnerRunLiveMicrotradeResultContractInput | Mapping[str, Any] | None = None,
) -> OandaOwnerRunLiveMicrotradeResultContractResult:
    active_input = _coerce_contract_input(contract_input or build_sample_profit_result_input())
    payload = _mapping_or_none(active_input.owner_result)
    sanitized = _sanitize_payload(payload or {})
    missing_fields = _missing_fields(payload)
    blocked_items = _blocked_items(payload, active_input.unsafe_flags)
    classification = (
        OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_BLOCKED_UNSAFE
        if missing_fields or blocked_items
        else OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_READY
    )
    protected_flags = protected_flags_false()
    return OandaOwnerRunLiveMicrotradeResultContractResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        required_sanitized_fields=REQUIRED_SANITIZED_RESULT_FIELDS,
        sanitized_result_fields=jsonable(sanitized),
        missing_fields=missing_fields,
        blocked_items=blocked_items,
        result_capture_only=True,
        owner_warning=EXACT_OWNER_WARNING,
        result_warning=EXACT_RESULT_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def protected_flags_false() -> dict[str, bool]:
    return dict(PROTECTED_FLAGS_FALSE)


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaOwnerRunLiveMicrotradeResultContractResult) -> str:
    return "\n".join(
        (
            f"Result contract status: {result.classification}.",
            "Owner-run result capture only.",
            result.owner_warning,
            result.result_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaOwnerRunLiveMicrotradeResultContractResult) -> str:
    rows = [
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Contract V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- Result capture only: `{str(result.result_capture_only).lower()}`",
        "",
        "## Required Sanitized Fields",
    ]
    rows.extend(f"- `{item}`" for item in result.required_sanitized_fields)
    rows.extend(("", "## Missing Fields"))
    rows.extend(f"- `{item}`" for item in result.missing_fields)
    rows.extend(("", "## Blocked Items"))
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def markdown_safety_lines() -> list[str]:
    return [
        "",
        "## Safety",
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- No credential access occurred.",
        "- No account ID was persisted.",
        "- No broker order ID was persisted.",
        "- No raw broker payload was persisted.",
        "- No live approval was granted.",
        "- No repeat trading approval was granted.",
        "- No real money approval was granted.",
        "- No compounding approval was granted.",
        "- No bank movement approval was granted.",
        "- No autonomous execution was granted.",
        "- Unattended vacation mode remains blocked.",
        "- Vacation profit trial remains blocked unless Anthony separately approves.",
        "- Profit is not guaranteed.",
        "- All protected flags remain false.",
        "- Owner-run result capture only.",
        "- Read-only only.",
    ]


def jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if hasattr(value, "__dataclass_fields__"):
        return {key: jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    return value


def decimal_value(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def text_value(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def truthy_unsafe(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "1",
            "allowed",
            "approved",
            "authorized",
            "enabled",
            "performed",
            "started",
            "called",
            "placed",
            "read",
            "used",
            "persisted",
            "mutated",
        }
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 1
    return False


def unsafe_payload_blockers(payload: Mapping[str, Any] | None, label: str) -> tuple[str, ...]:
    if payload is None:
        return ()
    blockers: list[str] = []

    def visit(node: Any, prefix: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, value in node.items():
                key = _normalized_key(raw_key)
                path = f"{prefix}.{key}" if prefix else key
                if key in PROTECTED_FLAG_NAMES and truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{path}_true")
                if key in UNSAFE_MUST_BE_TRUE_FIELDS and value is not True:
                    blockers.append(f"unsafe_{label}_{path}_not_confirmed_true")
                if _sensitive_key_present(key, value):
                    blockers.append(f"unsafe_{label}_{path}_present")
                visit(value, path)
        elif isinstance(node, (list, tuple)):
            for index, item in enumerate(node):
                visit(item, f"{prefix}[{index}]")

    visit(payload, "")
    return tuple(dict.fromkeys(blockers))


def _coerce_contract_input(
    value: OandaOwnerRunLiveMicrotradeResultContractInput | Mapping[str, Any],
) -> OandaOwnerRunLiveMicrotradeResultContractInput:
    if isinstance(value, OandaOwnerRunLiveMicrotradeResultContractInput):
        return value
    raw = dict(value)
    return OandaOwnerRunLiveMicrotradeResultContractInput(
        owner_result=_mapping_or_none(raw.get("owner_result")),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _mapping_or_none(value: Any) -> Mapping[str, Any] | None:
    if value is None:
        return None
    return value if isinstance(value, Mapping) else {}


def _sample_owner_result(
    *,
    result_reference: str = "SANITIZED-OWNER-RUN-RESULT-PROFIT-001",
    sanitized_exit_price: str = "1.10020",
    realized_pl: str,
    realized_r: str,
) -> dict[str, Any]:
    return {
        "result_reference": result_reference,
        "owner_action_confirmed_outside_codex": True,
        "provider_label": "sanitized_owner_selected_provider",
        "instrument": "EUR_USD",
        "direction": "long",
        "planned_units": Decimal("1"),
        "actual_units": Decimal("1"),
        "max_units": Decimal("1"),
        "open_time_utc": "2026-06-25T14:00:00Z",
        "close_time_utc": "2026-06-25T14:05:00Z",
        "planned_entry_source": "sanitized_ticket_preview",
        "sanitized_entry_price": Decimal("1.10000"),
        "sanitized_exit_price": Decimal(sanitized_exit_price),
        "realized_pl": Decimal(realized_pl),
        "realized_pl_currency": "USD",
        "planned_max_loss": Decimal("1.00"),
        "planned_risk_r": Decimal("1.00"),
        "realized_r": Decimal(realized_r),
        "spread_observed": Decimal("0.00010"),
        "slippage_observed": Decimal("0.00002"),
        "trade_closed": True,
        "one_shot_only_confirmed": True,
        "no_repeat_execution_confirmed": True,
        "no_compounding_confirmed": True,
        "no_bank_movement_confirmed": True,
        "no_autonomous_loop_confirmed": True,
        "no_credentials_in_payload": True,
        "no_account_id_in_payload": True,
        "no_broker_order_id_in_payload": True,
        "no_raw_broker_payload": True,
        "evidence_references_sanitized": (
            "sanitized_owner_journal_reference",
            "sanitized_result_screenshot_reference",
        ),
        "planned_instrument": "EUR_USD",
        "planned_direction": "long",
        "planned_one_shot_only": True,
        "post_trade_capture_evidence_present": True,
        "post_trade_capture_complete": True,
        "proof_label": "deterministic_owner_run_live_microtrade_result_sample",
    }


def _missing_fields(payload: Mapping[str, Any] | None) -> tuple[str, ...]:
    if payload is None:
        return REQUIRED_SANITIZED_RESULT_FIELDS
    missing: list[str] = []
    for field_name in REQUIRED_SANITIZED_RESULT_FIELDS:
        if field_name not in payload:
            missing.append(field_name)
            continue
        value = payload[field_name]
        if value is None:
            missing.append(field_name)
        elif isinstance(value, str) and not value.strip():
            missing.append(field_name)
        elif isinstance(value, (tuple, list)) and not value:
            missing.append(field_name)
    return tuple(missing)


def _blocked_items(
    payload: Mapping[str, Any] | None,
    unsafe_flags: Mapping[str, bool],
) -> tuple[str, ...]:
    blocked = [name for name, value in unsafe_flags.items() if bool(value)]
    blocked.extend(unsafe_payload_blockers(payload, "owner_result"))
    return tuple(dict.fromkeys(blocked))


def _sanitize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field_name: payload[field_name]
        for field_name in ALLOWED_SANITIZED_RESULT_FIELDS
        if field_name in payload
    }


def _normalized_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def _sensitive_key_present(key: str, value: Any) -> bool:
    if key.startswith("no_"):
        return False
    if key in PROTECTED_FLAG_NAMES:
        return False
    if not _present(value):
        return False
    if key in {
        "access_token",
        "authorization",
        "runtime_account",
        "account_identifier",
        "account_id",
        "accountid",
        "broker_order_id",
        "order_id",
        "raw_payload",
        "raw_broker_payload",
        "endpoint_url",
        "headers",
    }:
        return True
    if "api_key" in key or "apikey" in key:
        return True
    if "password" in key:
        return True
    if "secret" in key:
        return True
    if "credential" in key:
        return True
    if "account" in key and "boundary" not in key:
        return True
    if "order" in key and key.endswith("_id"):
        return True
    if "raw" in key and "payload" in key:
        return True
    return False


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (tuple, list, dict)):
        return bool(value)
    return True
