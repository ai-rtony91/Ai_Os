from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
from typing import Any, Mapping, Sequence
from urllib.parse import urlencode, urlparse


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-READ-ONLY-FILLED-TRADE-PL-CAPTURE-V1"
CAPTURE_VERSION = "v1"

READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY = (
    "READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY"
)
READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED = (
    "READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED"
)
BLOCKED_BY_MISSING_VAULT_ADAPTER = "BLOCKED_BY_MISSING_VAULT_ADAPTER"
BLOCKED_BY_MISSING_TOKEN = "BLOCKED_BY_MISSING_TOKEN"
BLOCKED_BY_MISSING_ACCOUNT_ID = "BLOCKED_BY_MISSING_ACCOUNT_ID"
BLOCKED_BY_UNSAFE_CONTEXT = "BLOCKED_BY_UNSAFE_CONTEXT"
BLOCKED_BY_UNSAFE_ENDPOINT = "BLOCKED_BY_UNSAFE_ENDPOINT"
BLOCKED_BY_MISSING_HTTP_GET_ADAPTER = "BLOCKED_BY_MISSING_HTTP_GET_ADAPTER"

FILLED_TRADE_PL_POSITIVE = "FILLED_TRADE_PL_POSITIVE"
FILLED_TRADE_PL_NEGATIVE = "FILLED_TRADE_PL_NEGATIVE"
FILLED_TRADE_PL_ZERO = "FILLED_TRADE_PL_ZERO"
FILLED_TRADE_PL_OPEN_UNREALIZED = "FILLED_TRADE_PL_OPEN_UNREALIZED"
FILLED_TRADE_PL_NOT_FOUND = "FILLED_TRADE_PL_NOT_FOUND"
BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE = (
    "BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE"
)

PRACTICE_API_BASE_URL = "https://api-fxpractice.oanda.com"
LIVE_API_HOST = "api-fxtrade.oanda.com"

ACCESS_TOKEN_CREDENTIAL_NAME = "AIOS_OANDA_DEMO_ACCESS_TOKEN"
ACCOUNT_ID_CREDENTIAL_NAME = "AIOS_OANDA_DEMO_ACCOUNT_ID"
APPROVED_VAULT_CREDENTIAL_NAMES = (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
)

REDACTED_TOKEN_REFERENCE = "REDACTED_RUNTIME_ACCESS_TOKEN"
REDACTED_ACCOUNT_ID_REFERENCE = "REDACTED_RUNTIME_ACCOUNT_ID"
REDACTED_RUNTIME_ONLY_REFERENCE = "REDACTED_RUNTIME_ONLY_REFERENCE"

DEFAULT_INSTRUMENT = "EUR_USD"
DEFAULT_ORDER_CREATE_TRANSACTION_ID = "319"
DEFAULT_ORDER_FILL_TRANSACTION_ID = "320"
DEFAULT_RELATED_TRANSACTION_IDS = ("319", "320", "321", "322")
DEFAULT_CLIENT_ORDER_ID = "AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001"

READ_ONLY_ENDPOINT_NAMES = (
    "accounts",
    "account_details",
    "account_summary",
    "open_trades",
    "open_positions",
    "transactions_window",
)

EXECUTION_AUTHORITY_FIELDS = (
    "order_placement_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "broker_write_allowed",
    "live_endpoint_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

SENSITIVE_KEY_EXACT = {
    "access_token",
    "token",
    "authorization",
    "password",
    "secret",
    "secret_value",
    "credential_value",
    "api_key",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
}

SENSITIVE_KEY_TERMS = (
    "access_token",
    "authorization",
    "password",
    "secret",
    "credential_value",
    "api_key",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
)

REALIZED_PL_KEYS = {"pl", "realizedPL", "profitLoss"}
UNREALIZED_PL_KEYS = {"unrealizedPL"}


def evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1(
    capture_context: Mapping[str, Any] | None = None,
    *,
    vault_load_callable: object | None = None,
    http_get_callable: object | None = None,
    execute_capture: bool = False,
    endpoint_plan_override: Sequence[Mapping[str, Any] | str] | None = None,
    related_transaction_ids: Sequence[str | int] | None = None,
    order_create_transaction_id: str | int = DEFAULT_ORDER_CREATE_TRANSACTION_ID,
    order_fill_transaction_id: str | int = DEFAULT_ORDER_FILL_TRANSACTION_ID,
    instrument: str = DEFAULT_INSTRUMENT,
    client_order_id: str = DEFAULT_CLIENT_ORDER_ID,
) -> dict[str, Any]:
    context = _context_or_default(capture_context)
    transaction_ids = _normalize_transaction_ids(
        related_transaction_ids or DEFAULT_RELATED_TRANSACTION_IDS
    )
    order_create_id = _text(order_create_transaction_id)
    order_fill_id = _text(order_fill_transaction_id)
    trade_instrument = _text(instrument, DEFAULT_INSTRUMENT)
    client_id = _text(client_order_id, DEFAULT_CLIENT_ORDER_ID)

    endpoint_plan = _endpoint_plan_from_context(
        context,
        account_id=REDACTED_ACCOUNT_ID_REFERENCE,
        related_transaction_ids=transaction_ids,
        endpoint_plan_override=endpoint_plan_override,
    )
    context_blockers = _context_blockers(context)
    endpoint_blockers = _endpoint_plan_blockers(endpoint_plan)
    blockers = _unique(context_blockers + endpoint_blockers)

    token: str | None = None
    account_id: str | None = None
    vault_records: list[dict[str, Any]] = []
    read_results: list[dict[str, Any]] = []
    pl_evidence: dict[str, Any] = {}

    if context_blockers:
        status = BLOCKED_BY_UNSAFE_CONTEXT
        pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
    elif endpoint_blockers:
        status = BLOCKED_BY_UNSAFE_ENDPOINT
        pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
    elif execute_capture is not True:
        status = READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY
        pl_classification = None
    elif not callable(vault_load_callable):
        status = BLOCKED_BY_MISSING_VAULT_ADAPTER
        pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
        blockers = _unique(blockers + ["windows_vault_load_adapter_required"])
    else:
        vault_records = [
            _load_vault_record(vault_load_callable, ACCESS_TOKEN_CREDENTIAL_NAME),
            _load_vault_record(vault_load_callable, ACCOUNT_ID_CREDENTIAL_NAME),
        ]
        token = _extract_loaded_secret(vault_records[0])
        account_id = _extract_loaded_secret(vault_records[1])

        if not _present(token):
            status = BLOCKED_BY_MISSING_TOKEN
            pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
            blockers = _unique(blockers + ["vault_demo_access_token_missing"])
        elif not _present(account_id):
            status = BLOCKED_BY_MISSING_ACCOUNT_ID
            pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
            blockers = _unique(blockers + ["vault_demo_account_id_missing"])
        elif not callable(http_get_callable):
            status = BLOCKED_BY_MISSING_HTTP_GET_ADAPTER
            pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
            blockers = _unique(blockers + ["http_get_callable_required"])
        else:
            endpoint_plan = _endpoint_plan_from_context(
                context,
                account_id=account_id,
                related_transaction_ids=transaction_ids,
                endpoint_plan_override=endpoint_plan_override,
            )
            runtime_endpoint_blockers = _endpoint_plan_blockers(endpoint_plan)
            if runtime_endpoint_blockers:
                status = BLOCKED_BY_UNSAFE_ENDPOINT
                pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
                blockers = _unique(blockers + runtime_endpoint_blockers)
            else:
                read_results = [
                    _perform_read_only_get(
                        endpoint,
                        runtime_access_token=token,
                        http_get_callable=http_get_callable,
                    )
                    for endpoint in endpoint_plan["endpoints"]
                ]
                failures = _read_failures(read_results)
                if failures:
                    status = BLOCKED_BY_UNSAFE_ENDPOINT
                    pl_classification = BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE
                    blockers = _unique(blockers + failures)
                else:
                    status = READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED
                    pl_evidence = _build_pl_evidence(
                        read_results,
                        related_transaction_ids=transaction_ids,
                        order_create_transaction_id=order_create_id,
                        order_fill_transaction_id=order_fill_id,
                        instrument=trade_instrument,
                        client_order_id=client_id,
                    )
                    pl_classification = _classify_pl_evidence(pl_evidence)

    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "capture_version": CAPTURE_VERSION,
        "status": status,
        "pl_capture_classification": pl_classification,
        "blockers": blockers,
        "warnings": _warnings(status),
        "owner_filled_trade_evidence": {
            "orderCreateTransaction_id": order_create_id,
            "orderFillTransaction_id": order_fill_id,
            "relatedTransactionIDs": transaction_ids,
            "cancel_reason": None,
            "result_bucket": "FILLED_PNL_UNKNOWN",
            "fill_status": "FILLED",
            "profitability_status": "PNL_NOT_CAPTURED",
            "allocation_decision": "NO_NEXT_ALLOCATION_UNTIL_PNL_CAPTURE",
            "instrument": trade_instrument,
            "client_order_id": client_id,
        },
        "capture_context_summary": _capture_context_summary(context),
        "vault_load_boundary": {
            "adapter_required_for_execute": True,
            "adapter_supplied": callable(vault_load_callable),
            "vault_load_attempted": bool(vault_records),
            "credential_names": list(APPROVED_VAULT_CREDENTIAL_NAMES),
            "credential_values_runtime_only": True,
            "credential_values_printed": False,
            "credential_values_persisted_to_repo": False,
            "approved_credential_names_only": True,
        },
        "sanitized_vault_load_result": _sanitize_value(
            vault_records,
            runtime_access_token=token,
            runtime_account_id=account_id,
        )
        if vault_records
        else None,
        "read_only_endpoint_policy": {
            "allowed_endpoints": _allowed_endpoint_templates(),
            "method_allowed": "GET",
            "practice_base_url_only": True,
            "live_base_url_allowed": False,
            "mutation_endpoints_allowed": False,
            "orders_mutation_allowed": False,
            "trade_close_allowed": False,
        },
        "read_only_endpoint_plan": _sanitize_value(
            endpoint_plan,
            runtime_access_token=token,
            runtime_account_id=account_id,
        ),
        "read_only_capture_results": _sanitize_value(
            read_results,
            runtime_access_token=token,
            runtime_account_id=account_id,
        ),
        "pl_evidence": _sanitize_value(
            pl_evidence,
            runtime_access_token=token,
            runtime_account_id=account_id,
        ),
        "execution_authority": _execution_authority(),
        "safety_proof": _safety_proof(read_results, vault_records),
        "next_safe_action": _next_safe_action(status, pl_classification),
    }
    result.update(_execution_authority())
    result.update(_safety_proof(read_results, vault_records))
    return _sanitize_value(
        result,
        runtime_access_token=token,
        runtime_account_id=account_id,
    )


def default_oanda_demo_read_only_filled_trade_pl_capture_context_v1() -> dict[str, Any]:
    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_only": True,
        "windows_vault_only": True,
        "demo_api_base_url": PRACTICE_API_BASE_URL,
        "live_api_base_url": "",
        "live_credentials_allowed": False,
        "live_mode": False,
        "read_only_pl_capture_only": True,
        "no_env_file": True,
        "no_repo_persistence": True,
        "no_live_credentials": True,
        "no_order_placement": True,
        "no_order_close": True,
        "no_order_mutation": True,
        "no_trade_mutation": True,
        "no_position_mutation": True,
        "no_second_order_attempt": True,
        "profit_claimed": False,
        "execution_authority": _execution_authority(),
    }


def validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1(
    url: str,
    *,
    method: str = "GET",
) -> list[str]:
    blockers: list[str] = []
    parsed = urlparse(url)
    normalized_method = _text(method).upper()

    if normalized_method != "GET":
        blockers.append("method_must_be_get")
    if parsed.scheme != "https" or parsed.netloc != "api-fxpractice.oanda.com":
        blockers.append("url_must_use_oanda_practice_base")
    if LIVE_API_HOST in url:
        blockers.append("live_endpoint_forbidden")

    path_parts = [part for part in parsed.path.split("/") if part]
    allowed_shape = (
        path_parts == ["v3", "accounts"]
        or (
            len(path_parts) == 3
            and path_parts[0:2] == ["v3", "accounts"]
            and _present(path_parts[2])
        )
        or (
            len(path_parts) == 4
            and path_parts[0:2] == ["v3", "accounts"]
            and _present(path_parts[2])
            and path_parts[3] in {
                "summary",
                "openTrades",
                "openPositions",
                "transactions",
            }
        )
    )
    if not allowed_shape:
        blockers.append("url_must_be_allowed_read_only_pl_capture_endpoint")
    if "/orders" in parsed.path:
        blockers.append("orders_endpoint_forbidden")
    if parsed.path.endswith("/trades") or "/trades/" in parsed.path:
        blockers.append("trade_mutation_or_close_endpoint_forbidden")
    if parsed.path.endswith("/positions") or "/positions/" in parsed.path:
        blockers.append("position_mutation_endpoint_forbidden")
    return _unique(blockers)


def _load_vault_record(
    vault_load_callable: object,
    credential_name: str,
) -> dict[str, Any]:
    payload = {"credential_name": credential_name}
    try:
        result = vault_load_callable(payload)  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive adapter boundary
        result = {
            "credential_name": credential_name,
            "load_status": "vault_adapter_exception",
            "error_type": type(exc).__name__,
            "secret_value": "",
        }
    return {
        "operation": "load",
        "credential_name": credential_name,
        "result": result,
    }


def _extract_loaded_secret(vault_record: Mapping[str, Any]) -> str:
    result = vault_record.get("result")
    if isinstance(result, str):
        return result
    if isinstance(result, Mapping):
        for key in (
            "secret_value",
            "value",
            "secret",
            "credential_value",
            "password",
        ):
            value = result.get(key)
            if isinstance(value, str):
                return value
    return ""


def _context_or_default(context: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if context is None:
        return default_oanda_demo_read_only_filled_trade_pl_capture_context_v1()
    return context if isinstance(context, Mapping) else {}


def _context_blockers(context: Mapping[str, Any]) -> list[str]:
    if not context:
        return ["missing_read_only_pl_capture_context"]

    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("context_environment_must_be_demo")
    if context.get("demo_only") is not True:
        blockers.append("context_demo_only_required")
    if context.get("windows_vault_only") is not True:
        blockers.append("context_windows_vault_only_required")
    if context.get("live_mode") is True:
        blockers.append("context_live_mode_must_be_false")
    if context.get("live_credentials_allowed") is True:
        blockers.append("context_live_credentials_allowed_must_be_false")
    if _text(context.get("live_api_base_url")):
        blockers.append("context_live_api_base_url_must_be_absent")
    if not _text(context.get("demo_api_base_url")).startswith(PRACTICE_API_BASE_URL):
        blockers.append("context_demo_api_base_url_must_be_practice")
    if context.get("profit_claimed") is True:
        blockers.append("context_profit_claim_must_be_false")

    required_true = (
        "read_only_pl_capture_only",
        "no_env_file",
        "no_repo_persistence",
        "no_live_credentials",
        "no_order_placement",
        "no_order_close",
        "no_order_mutation",
        "no_trade_mutation",
        "no_position_mutation",
        "no_second_order_attempt",
    )
    for field in required_true:
        if context.get(field) is not True:
            blockers.append(f"context_{field}_required")
    blockers.extend(_authority_blockers(context, "read_only_pl_capture_context"))
    return _unique(blockers)


def _endpoint_plan_from_context(
    context: Mapping[str, Any],
    *,
    account_id: str,
    related_transaction_ids: Sequence[str],
    endpoint_plan_override: Sequence[Mapping[str, Any] | str] | None,
) -> dict[str, Any]:
    if endpoint_plan_override is not None:
        endpoints = [_normalize_endpoint(endpoint) for endpoint in endpoint_plan_override]
    else:
        base_url = _text(context.get("demo_api_base_url"), PRACTICE_API_BASE_URL)
        tx_query = _transaction_query(related_transaction_ids)
        endpoints = [
            {"name": "accounts", "method": "GET", "url": f"{base_url}/v3/accounts"},
            {
                "name": "account_details",
                "method": "GET",
                "url": f"{base_url}/v3/accounts/{account_id}",
            },
            {
                "name": "account_summary",
                "method": "GET",
                "url": f"{base_url}/v3/accounts/{account_id}/summary",
            },
            {
                "name": "open_trades",
                "method": "GET",
                "url": f"{base_url}/v3/accounts/{account_id}/openTrades",
            },
            {
                "name": "open_positions",
                "method": "GET",
                "url": f"{base_url}/v3/accounts/{account_id}/openPositions",
            },
            {
                "name": "transactions_window",
                "method": "GET",
                "url": (
                    f"{base_url}/v3/accounts/{account_id}/transactions"
                    f"?{tx_query}"
                ),
            },
        ]
    return {
        "endpoints": endpoints,
        "allowed_endpoint_templates": _allowed_endpoint_templates(),
        "read_only_only": True,
        "mutation_endpoints_allowed": False,
    }


def _normalize_endpoint(endpoint: Mapping[str, Any] | str) -> dict[str, Any]:
    if isinstance(endpoint, str):
        return {"name": "override_endpoint", "method": "GET", "url": endpoint}
    mapping = endpoint if isinstance(endpoint, Mapping) else {}
    return {
        "name": _text(mapping.get("name"), "override_endpoint"),
        "method": _text(mapping.get("method"), "GET"),
        "url": _text(mapping.get("url")),
    }


def _endpoint_plan_blockers(endpoint_plan: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for endpoint in endpoint_plan.get("endpoints", []):
        endpoint_mapping = endpoint if isinstance(endpoint, Mapping) else {}
        method = _text(endpoint_mapping.get("method"), "GET")
        url = _text(endpoint_mapping.get("url"))
        for blocker in validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1(
            url,
            method=method,
        ):
            blockers.append(f"unsafe_endpoint_{blocker}")
    return _unique(blockers)


def _perform_read_only_get(
    endpoint: Mapping[str, Any],
    *,
    runtime_access_token: str,
    http_get_callable: object,
) -> dict[str, Any]:
    method = _text(endpoint.get("method"), "GET").upper()
    url = _text(endpoint.get("url"))
    endpoint_name = _text(endpoint.get("name"), "read_only_endpoint")
    payload = {
        "endpoint_name": endpoint_name,
        "method": method,
        "url": url,
        "runtime_access_token": runtime_access_token,
        "timeout_seconds": 20,
    }
    if method != "GET":
        return {
            "endpoint_name": endpoint_name,
            "method": method,
            "url": url,
            "network_call_performed": False,
            "status_code": None,
            "error": "non_get_method_blocked_before_transport",
        }
    try:
        response = http_get_callable(payload)  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive adapter boundary
        return {
            "endpoint_name": endpoint_name,
            "method": method,
            "url": url,
            "network_call_performed": True,
            "status_code": None,
            "error_type": type(exc).__name__,
            "error": "read_only_http_get_adapter_exception",
        }
    return {
        "endpoint_name": endpoint_name,
        "method": method,
        "url": url,
        "network_call_performed": True,
        "status_code": _response_status_code(response),
        "response": response,
    }


def _read_failures(read_results: Sequence[Mapping[str, Any]]) -> list[str]:
    failures: list[str] = []
    expected = set(READ_ONLY_ENDPOINT_NAMES)
    observed = {
        _text(result.get("endpoint_name"))
        for result in read_results
        if _text(result.get("endpoint_name"))
    }
    for missing in sorted(expected - observed):
        failures.append(f"missing_endpoint_result_{missing}")
    for result in read_results:
        endpoint_name = _text(result.get("endpoint_name"), "unknown_endpoint")
        if result.get("method") != "GET":
            failures.append(f"{endpoint_name}_method_not_get")
        if result.get("network_call_performed") is not True:
            failures.append(f"{endpoint_name}_network_call_not_performed")
        if result.get("status_code") != 200:
            failures.append(f"{endpoint_name}_status_not_200")
    return _unique(failures)


def _build_pl_evidence(
    read_results: Sequence[Mapping[str, Any]],
    *,
    related_transaction_ids: Sequence[str],
    order_create_transaction_id: str,
    order_fill_transaction_id: str,
    instrument: str,
    client_order_id: str,
) -> dict[str, Any]:
    responses = {
        _text(result.get("endpoint_name")): _response_json_payload(
            result.get("response")
        )
        for result in read_results
    }
    transactions = _transactions_from_payload(
        responses.get("transactions_window"),
        related_transaction_ids=related_transaction_ids,
        order_fill_transaction_id=order_fill_transaction_id,
        client_order_id=client_order_id,
    )
    realized_values = _realized_pl_values(transactions)
    open_trade_evidence = _open_trade_evidence(
        responses.get("open_trades"),
        instrument=instrument,
    )
    open_position_evidence = _open_position_evidence(
        responses.get("open_positions"),
        instrument=instrument,
    )
    account_summary = _account_summary_evidence(responses.get("account_summary"))
    return {
        "transaction_match": {
            "orderCreateTransaction_id": order_create_transaction_id,
            "orderFillTransaction_id": order_fill_transaction_id,
            "relatedTransactionIDs": list(related_transaction_ids),
            "matched_transaction_count": len(transactions),
        },
        "realized_pl_values": [str(value) for value in realized_values],
        "realized_pl_total": str(sum(realized_values, Decimal("0"))),
        "open_trade_evidence": open_trade_evidence,
        "open_position_evidence": open_position_evidence,
        "account_summary_snapshot": account_summary,
        "evidence_found": bool(
            realized_values or open_trade_evidence or open_position_evidence
        ),
    }


def _classify_pl_evidence(pl_evidence: Mapping[str, Any]) -> str:
    realized_values = [
        _decimal_or_none(value)
        for value in pl_evidence.get("realized_pl_values", [])
    ]
    realized_values = [value for value in realized_values if value is not None]
    has_open_evidence = bool(
        pl_evidence.get("open_trade_evidence")
        or pl_evidence.get("open_position_evidence")
    )
    if realized_values:
        total = sum(realized_values, Decimal("0"))
        if total > 0:
            return FILLED_TRADE_PL_POSITIVE
        if total < 0:
            return FILLED_TRADE_PL_NEGATIVE
        if has_open_evidence:
            return FILLED_TRADE_PL_OPEN_UNREALIZED
        return FILLED_TRADE_PL_ZERO
    if has_open_evidence:
        return FILLED_TRADE_PL_OPEN_UNREALIZED
    return FILLED_TRADE_PL_NOT_FOUND


def _transactions_from_payload(
    payload: Any,
    *,
    related_transaction_ids: Sequence[str],
    order_fill_transaction_id: str,
    client_order_id: str,
) -> list[Mapping[str, Any]]:
    if not isinstance(payload, Mapping):
        return []
    raw_transactions = payload.get("transactions", [])
    if not isinstance(raw_transactions, list):
        return []
    related_ids = {str(value) for value in related_transaction_ids}
    matched: list[Mapping[str, Any]] = []
    for transaction in raw_transactions:
        if not isinstance(transaction, Mapping):
            continue
        transaction_id = _text(transaction.get("id"))
        if transaction_id in related_ids or transaction_id == order_fill_transaction_id:
            matched.append(transaction)
        elif _client_order_id_matches(transaction, client_order_id):
            matched.append(transaction)
    return matched


def _client_order_id_matches(transaction: Mapping[str, Any], client_order_id: str) -> bool:
    if not client_order_id:
        return False
    direct_keys = ("clientOrderID", "client_order_id")
    for key in direct_keys:
        if _text(transaction.get(key)) == client_order_id:
            return True
    for key in ("clientExtensions", "orderClientExtensions"):
        nested = transaction.get(key)
        if isinstance(nested, Mapping) and _text(nested.get("id")) == client_order_id:
            return True
    return False


def _realized_pl_values(transactions: Sequence[Mapping[str, Any]]) -> list[Decimal]:
    values: list[Decimal] = []
    for transaction in transactions:
        values.extend(_collect_decimal_values(transaction, REALIZED_PL_KEYS))
    return values


def _open_trade_evidence(payload: Any, *, instrument: str) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping):
        return []
    raw_trades = payload.get("trades", [])
    if not isinstance(raw_trades, list):
        return []
    evidence: list[dict[str, Any]] = []
    for trade in raw_trades:
        if not isinstance(trade, Mapping):
            continue
        if _text(trade.get("instrument")) != instrument:
            continue
        units = _decimal_or_none(trade.get("currentUnits"))
        unrealized = _first_decimal_value(trade, UNREALIZED_PL_KEYS)
        if units is not None and units != 0:
            evidence.append(
                {
                    "trade_id": _text(trade.get("id"), "UNKNOWN"),
                    "instrument": instrument,
                    "currentUnits": str(units),
                    "unrealizedPL": str(unrealized)
                    if unrealized is not None
                    else None,
                }
            )
    return evidence


def _open_position_evidence(payload: Any, *, instrument: str) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping):
        return []
    raw_positions = payload.get("positions", [])
    if not isinstance(raw_positions, list):
        return []
    evidence: list[dict[str, Any]] = []
    for position in raw_positions:
        if not isinstance(position, Mapping):
            continue
        if _text(position.get("instrument")) != instrument:
            continue
        position_unrealized = _first_decimal_value(position, UNREALIZED_PL_KEYS)
        long_units = _position_units(position.get("long"))
        short_units = _position_units(position.get("short"))
        if long_units != 0 or short_units != 0:
            evidence.append(
                {
                    "instrument": instrument,
                    "long_units": str(long_units),
                    "short_units": str(short_units),
                    "unrealizedPL": str(position_unrealized)
                    if position_unrealized is not None
                    else None,
                }
            )
    return evidence


def _account_summary_evidence(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    account = payload.get("account")
    account = account if isinstance(account, Mapping) else payload
    snapshot: dict[str, Any] = {}
    for key in ("balance", "NAV", "unrealizedPL", "pl", "marginUsed"):
        if key in account:
            snapshot[key] = account.get(key)
    return snapshot


def _response_json_payload(response: Any) -> Any:
    if not isinstance(response, Mapping):
        return {}
    for key in ("json", "body_json", "payload", "data"):
        value = response.get(key)
        if isinstance(value, (Mapping, list)):
            return value
    body = response.get("body")
    if isinstance(body, str):
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, (Mapping, list)) else {}
    return {}


def _response_status_code(response: Any) -> int | None:
    if not isinstance(response, Mapping):
        return None
    for key in ("status_code", "status"):
        value = response.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _capture_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_only": context.get("demo_only") is True,
        "windows_vault_only": context.get("windows_vault_only") is True,
        "demo_api_base_url_is_practice": _text(
            context.get("demo_api_base_url")
        ).startswith(PRACTICE_API_BASE_URL),
        "live_api_base_url_present": bool(_text(context.get("live_api_base_url"))),
        "live_credentials_allowed": context.get("live_credentials_allowed") is True,
        "read_only_pl_capture_only": context.get("read_only_pl_capture_only") is True,
        "no_env_file": context.get("no_env_file") is True,
        "no_order_placement": context.get("no_order_placement") is True,
        "no_order_close": context.get("no_order_close") is True,
        "no_second_order_attempt": context.get("no_second_order_attempt") is True,
        "profit_claimed": context.get("profit_claimed") is True,
    }


def _allowed_endpoint_templates() -> list[str]:
    return [
        "GET https://api-fxpractice.oanda.com/v3/accounts",
        "GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>",
        (
            "GET https://api-fxpractice.oanda.com/v3/accounts/"
            "<runtime_account_id>/summary"
        ),
        (
            "GET https://api-fxpractice.oanda.com/v3/accounts/"
            "<runtime_account_id>/openTrades"
        ),
        (
            "GET https://api-fxpractice.oanda.com/v3/accounts/"
            "<runtime_account_id>/openPositions"
        ),
        (
            "GET https://api-fxpractice.oanda.com/v3/accounts/"
            "<runtime_account_id>/transactions"
        ),
    ]


def _transaction_query(related_transaction_ids: Sequence[str]) -> str:
    if not related_transaction_ids:
        return urlencode({"from": "319", "to": "322"})
    return urlencode(
        {
            "from": related_transaction_ids[0],
            "to": related_transaction_ids[-1],
        }
    )


def _safety_proof(
    read_results: Sequence[Mapping[str, Any]],
    vault_records: Sequence[Mapping[str, Any]],
) -> dict[str, bool]:
    return {
        "broker_network_call_performed": bool(read_results),
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "orders_endpoint_called": False,
        "live_endpoint_used": False,
        "credential_read_performed": bool(vault_records),
        "account_id_read_performed": bool(vault_records),
        "credential_value_printed": False,
        "account_id_value_printed": False,
        "dotenv_read": False,
        "env_read": False,
        "vault_value_persisted_to_repo": False,
        "profit_claimed": False,
    }


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "demo_only",
        "read_only_oanda_practice_get_only",
        "windows_vault_adapter_boundary_only",
        "no_order_placement",
        "no_order_close",
        "no_trade_or_position_mutation",
        "no_live_endpoint",
        "no_credential_or_account_id_printing",
        "no_credential_or_account_id_repo_persistence",
        "no_dotenv_or_env_read",
        "no_profit_claim_without_pl_evidence",
        "no_next_allocation_without_pl_capture",
    ]
    if status == READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY:
        warnings.append("default_ready_state_no_vault_or_broker_call")
    if status == READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED:
        warnings.append("owner_confirmed_read_only_pl_capture_attempted")
    return warnings


def _next_safe_action(status: str, pl_classification: str | None) -> str:
    if status == READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY:
        return "owner_may_review_template_before_manual_read_only_pl_capture"
    if pl_classification == FILLED_TRADE_PL_NOT_FOUND:
        return "owner_review_sanitized_read_only_capture_and_prepare_missing_pl_evidence_packet"
    if pl_classification in {
        FILLED_TRADE_PL_POSITIVE,
        FILLED_TRADE_PL_NEGATIVE,
        FILLED_TRADE_PL_ZERO,
        FILLED_TRADE_PL_OPEN_UNREALIZED,
    }:
        return "create_sanitized_pl_evidence_result_bucket_report_no_order"
    return "stop_and_review_read_only_pl_capture_blocker"


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            authority = node.get("execution_authority")
            authority_mapping = authority if isinstance(authority, Mapping) else {}
            for field in EXECUTION_AUTHORITY_FIELDS:
                if node.get(field) is True or authority_mapping.get(field) is True:
                    blockers.append(f"unsafe_{label}_{field}_true")
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _collect_decimal_values(node: Any, keys: set[str]) -> list[Decimal]:
    values: list[Decimal] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            if str(key) in keys:
                decimal_value = _decimal_or_none(value)
                if decimal_value is not None:
                    values.append(decimal_value)
            values.extend(_collect_decimal_values(value, keys))
    elif isinstance(node, list):
        for child in node:
            values.extend(_collect_decimal_values(child, keys))
    return values


def _first_decimal_value(node: Any, keys: set[str]) -> Decimal | None:
    values = _collect_decimal_values(node, keys)
    return values[0] if values else None


def _position_units(side: Any) -> Decimal:
    if not isinstance(side, Mapping):
        return Decimal("0")
    value = _decimal_or_none(side.get("units"))
    return value if value is not None else Decimal("0")


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _normalize_transaction_ids(values: Sequence[str | int]) -> list[str]:
    return [_text(value) for value in values if _text(value)]


def _sanitize_value(
    value: Any,
    *,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if key_text in {"credential_name", "credential_names"}:
                sanitized[key_text] = child
            elif _sensitive_key(key_text) and isinstance(child, str):
                sanitized[key_text] = REDACTED_RUNTIME_ONLY_REFERENCE
            elif key_text == "id" and child == runtime_account_id:
                sanitized[key_text] = REDACTED_ACCOUNT_ID_REFERENCE
            else:
                sanitized[key_text] = _sanitize_value(
                    child,
                    runtime_access_token=runtime_access_token,
                    runtime_account_id=runtime_account_id,
                )
        return sanitized
    if isinstance(value, list):
        return [
            _sanitize_value(
                child,
                runtime_access_token=runtime_access_token,
                runtime_account_id=runtime_account_id,
            )
            for child in value
        ]
    if isinstance(value, str):
        redacted = value
        if runtime_access_token:
            redacted = redacted.replace(runtime_access_token, REDACTED_TOKEN_REFERENCE)
        if runtime_account_id:
            redacted = redacted.replace(runtime_account_id, REDACTED_ACCOUNT_ID_REFERENCE)
        return redacted
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return repr(value)


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    if key_text in {"credential_name", "credential_names"}:
        return False
    return key_text in SENSITIVE_KEY_EXACT or any(
        term in key_text for term in SENSITIVE_KEY_TERMS
    )


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else str(value).strip() if value is not None else default


def _present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
