from __future__ import annotations

import json
from typing import Any, Mapping
from urllib import error, request


PACKET_ID = (
    "AIOS-FOREX-OANDA-DEMO-CREDENTIAL-ACCOUNT-PERMISSION-PREFLIGHT-NO-ORDER-V1"
)
PREFLIGHT_VERSION = "v1"

PREFLIGHT_BLOCKED_CONTEXT = "PREFLIGHT_BLOCKED_CONTEXT"
PREFLIGHT_DRY_RUN_READY = "PREFLIGHT_DRY_RUN_READY"
PREFLIGHT_BLOCKED_RUNTIME_CREDENTIALS_MISSING = (
    "PREFLIGHT_BLOCKED_RUNTIME_CREDENTIALS_MISSING"
)
PREFLIGHT_BLOCKED_HTTP_GET_CALLABLE_REQUIRED = (
    "PREFLIGHT_BLOCKED_HTTP_GET_CALLABLE_REQUIRED"
)
PREFLIGHT_READ_ONLY_ATTEMPTED = "PREFLIGHT_READ_ONLY_ATTEMPTED"
PREFLIGHT_REJECTED = "PREFLIGHT_REJECTED"

DEMO_API_BASE_URL_PREFIX = "https://api-fxpractice.oanda.com"
LIVE_API_BASE_URL = "https://api-fxtrade.oanda.com"
REDACTED_ACCOUNT_ID_REFERENCE = "REDACTED_RUNTIME_ACCOUNT_ID"
REDACTED_TOKEN_REFERENCE = "REDACTED_RUNTIME_ACCESS_TOKEN"
HTTP_TIMEOUT_SECONDS = 10

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "order_mutation_allowed",
    "position_mutation_allowed",
)

CONTEXT_REQUIRED_TRUE_FIELDS = (
    "demo_endpoint_only",
    "live_endpoint_absent",
    "runtime_token_external",
    "runtime_account_id_external",
    "no_order_endpoint_allowed",
    "order_mutation_forbidden",
    "read_only_only",
    "owner_present_for_manual_run",
    "prior_403_evidence_captured",
    "no_second_order_attempt_allowed",
)

CONTEXT_REQUIRED_FALSE_FIELDS = (
    "live_api_base_url_allowed",
    "credential_persistence_detected",
    "account_id_persistence_detected",
    "prior_order_placement_performed",
)

FORBIDDEN_URL_TERMS = (
    "/orders",
    "/trades",
    "/positions",
    "/transactions",
    "api-fxtrade.oanda.com",
)

SENSITIVE_KEY_TERMS = (
    "account_id",
    "accountid",
    "access_token",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
    "api_key",
)


def evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1(
    preflight_context: dict | None = None,
    runtime_access_token: str | None = None,
    runtime_account_id: str | None = None,
    http_get_callable: object | None = None,
    execute_preflight: bool = False,
) -> dict:
    context = _mapping(preflight_context)
    context_blockers = _preflight_context_blockers(context)

    endpoint_plan = _read_only_endpoint_plan(
        context=context,
        runtime_account_id=runtime_account_id,
    )
    endpoint_blockers = _endpoint_plan_blockers(endpoint_plan)

    blockers = _unique(context_blockers + endpoint_blockers)
    status = _status(
        blockers=blockers,
        execute_preflight=execute_preflight,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
        http_get_callable=http_get_callable,
    )

    raw_results: list[dict[str, Any]] = []
    network_call_performed = False

    if status == PREFLIGHT_READ_ONLY_ATTEMPTED:
        network_call_performed = True
        for endpoint in endpoint_plan["endpoints"]:
            request_payload = _http_get_request(
                endpoint["url"],
                runtime_access_token=runtime_access_token,
            )
            _raise_if_unsafe_request(request_payload)
            raw_results.append(
                {
                    "endpoint_name": endpoint["name"],
                    "result": http_get_callable(request_payload),  # type: ignore[misc]
                }
            )

    root_cause = _root_cause_summary(
        raw_results,
        runtime_account_id=runtime_account_id,
        attempted=status == PREFLIGHT_READ_ONLY_ATTEMPTED,
    )

    return {
        "packet_id": PACKET_ID,
        "preflight_version": PREFLIGHT_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": _warnings(status),
        "preflight_context_summary": _preflight_context_summary(context),
        "read_only_endpoint_plan": _sanitize_endpoint_plan(
            endpoint_plan,
            runtime_account_id=runtime_account_id,
        ),
        "credential_runtime_summary": _credential_runtime_summary(
            execute_preflight=execute_preflight,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        ),
        "preflight_attempt": {
            "execute_preflight_requested": execute_preflight is True,
            "network_call_performed": network_call_performed,
            "order_placement_performed": False,
            "order_mutation_performed": False,
            "position_mutation_performed": False,
            "endpoints_attempted": len(raw_results),
            "max_endpoint_attempts_each": 1,
            "read_only_only": True,
            "post_orders_called": False,
        },
        "sanitized_preflight_result": _sanitize_value(
            raw_results,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
        )
        if raw_results
        else None,
        "root_cause_summary": root_cause,
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status, root_cause),
    }


def get_oanda_demo_read_only_with_urllib(
    get_request: Mapping[str, Any],
) -> dict[str, Any]:
    _raise_if_unsafe_request(get_request)
    req = request.Request(
        url=_text(get_request.get("url")),
        headers={
            str(key): str(value)
            for key, value in _mapping(get_request.get("headers")).items()
        },
        method="GET",
    )
    timeout = _number(get_request.get("timeout_seconds"), HTTP_TIMEOUT_SECONDS)
    try:
        with request.urlopen(req, timeout=timeout) as response:  # nosec B310
            body = response.read().decode("utf-8")
            return {
                "status_code": response.getcode(),
                "status": "success" if response.getcode() == 200 else "response",
                "body": _parse_json_body(body),
            }
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "status_code": exc.code,
            "status": "http_error",
            "body": _parse_json_body(body),
        }
    except error.URLError as exc:
        return {
            "status_code": 0,
            "status": "url_error",
            "reason": str(exc.reason),
        }


def build_oanda_demo_read_only_endpoint_plan_v1(
    demo_api_base_url: str,
    runtime_account_id: str | None = None,
) -> dict[str, Any]:
    base_url = _trim_trailing_slash(demo_api_base_url)
    account_id = (
        runtime_account_id
        if _present(runtime_account_id)
        else REDACTED_ACCOUNT_ID_REFERENCE
    )
    endpoints = [
        {
            "name": "accounts",
            "method": "GET",
            "url": f"{base_url}/v3/accounts",
        },
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
            "name": "account_instruments",
            "method": "GET",
            "url": f"{base_url}/v3/accounts/{account_id}/instruments",
        },
    ]
    return {
        "demo_api_base_url": base_url,
        "endpoints": endpoints,
        "forbidden_url_terms": list(FORBIDDEN_URL_TERMS),
        "read_only_only": True,
        "mutation_endpoints_allowed": False,
    }


def validate_oanda_demo_read_only_endpoint_url_v1(url: str) -> list[str]:
    blockers: list[str] = []
    if not url.startswith(DEMO_API_BASE_URL_PREFIX):
        blockers.append("url_must_start_with_oanda_practice_base")
    for term in FORBIDDEN_URL_TERMS:
        if term in url:
            blockers.append(f"url_forbidden_term_{term.strip('/').replace('/', '_')}")
    return blockers


def _status(
    *,
    blockers: list[str],
    execute_preflight: bool,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
    http_get_callable: object | None,
) -> str:
    if any(blocker.startswith("endpoint_plan_") for blocker in blockers):
        return PREFLIGHT_REJECTED
    if blockers:
        return PREFLIGHT_BLOCKED_CONTEXT
    if not execute_preflight:
        return PREFLIGHT_DRY_RUN_READY
    if not _present(runtime_access_token) or not _present(runtime_account_id):
        return PREFLIGHT_BLOCKED_RUNTIME_CREDENTIALS_MISSING
    if not callable(http_get_callable):
        return PREFLIGHT_BLOCKED_HTTP_GET_CALLABLE_REQUIRED
    return PREFLIGHT_READ_ONLY_ATTEMPTED


def _preflight_context_blockers(context: Mapping[str, Any]) -> list[str]:
    if not context:
        return ["missing_preflight_context"]

    blockers: list[str] = []
    if context.get("broker") != "OANDA_DEMO":
        blockers.append("preflight_context_broker_must_be_oanda_demo")
    if context.get("environment") != "DEMO":
        blockers.append("preflight_context_environment_must_be_demo")
    if not _text(context.get("demo_api_base_url")).startswith(DEMO_API_BASE_URL_PREFIX):
        blockers.append("preflight_context_demo_api_base_url_must_be_practice")
    if _text(context.get("live_api_base_url")):
        blockers.append("preflight_context_live_api_base_url_must_be_absent")

    for field in CONTEXT_REQUIRED_TRUE_FIELDS:
        if not _bool(context.get(field)):
            blockers.append(f"preflight_context_{field}_required")
    for field in CONTEXT_REQUIRED_FALSE_FIELDS:
        if _bool(context.get(field)):
            blockers.append(f"preflight_context_{field}_must_be_false")
    if _number(context.get("prior_order_attempt_count"), -1) != 1:
        blockers.append("preflight_context_prior_order_attempt_count_must_equal_one")
    blockers.extend(_authority_blockers(context, "preflight_context"))
    return blockers


def _read_only_endpoint_plan(
    *,
    context: Mapping[str, Any],
    runtime_account_id: str | None,
) -> dict[str, Any]:
    base_url = _text(
        context.get("demo_api_base_url"),
        DEMO_API_BASE_URL_PREFIX,
    )
    return build_oanda_demo_read_only_endpoint_plan_v1(
        base_url,
        runtime_account_id=runtime_account_id,
    )


def _endpoint_plan_blockers(endpoint_plan: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for endpoint in endpoint_plan.get("endpoints", []):
        endpoint_mapping = _mapping(endpoint)
        method = _text(endpoint_mapping.get("method"))
        url = _text(endpoint_mapping.get("url"))
        if method != "GET":
            blockers.append("endpoint_plan_method_must_be_get")
        for url_blocker in validate_oanda_demo_read_only_endpoint_url_v1(url):
            blockers.append(f"endpoint_plan_{url_blocker}")
    return _unique(blockers)


def _http_get_request(
    url: str,
    *,
    runtime_access_token: str | None,
) -> dict[str, Any]:
    return {
        "method": "GET",
        "url": url,
        "headers": {
            "Authorization": f"Bearer {runtime_access_token}",
            "Content-Type": "application/json",
        },
        "timeout_seconds": HTTP_TIMEOUT_SECONDS,
    }


def _raise_if_unsafe_request(get_request: Mapping[str, Any]) -> None:
    method = _text(get_request.get("method"))
    url = _text(get_request.get("url"))
    if method != "GET":
        raise ValueError("read_only_preflight_requires_get_method")
    blockers = validate_oanda_demo_read_only_endpoint_url_v1(url)
    if blockers:
        raise ValueError(f"unsafe_read_only_preflight_url:{','.join(blockers)}")


def _preflight_context_summary(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(context.get("broker"), "MISSING"),
        "environment": _text(context.get("environment"), "MISSING"),
        "demo_endpoint_only": _bool(context.get("demo_endpoint_only")),
        "live_endpoint_absent": _bool(context.get("live_endpoint_absent")),
        "demo_api_base_url_is_practice": _text(
            context.get("demo_api_base_url")
        ).startswith(DEMO_API_BASE_URL_PREFIX),
        "live_api_base_url_allowed": _bool(context.get("live_api_base_url_allowed")),
        "runtime_token_external": _bool(context.get("runtime_token_external")),
        "runtime_account_id_external": _bool(
            context.get("runtime_account_id_external")
        ),
        "credential_persistence_detected": _bool(
            context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            context.get("account_id_persistence_detected")
        ),
        "no_order_endpoint_allowed": _bool(context.get("no_order_endpoint_allowed")),
        "order_mutation_forbidden": _bool(context.get("order_mutation_forbidden")),
        "read_only_only": _bool(context.get("read_only_only")),
        "owner_present_for_manual_run": _bool(
            context.get("owner_present_for_manual_run")
        ),
        "prior_403_evidence_captured": _bool(
            context.get("prior_403_evidence_captured")
        ),
        "prior_order_placement_performed": _bool(
            context.get("prior_order_placement_performed")
        ),
        "prior_order_attempt_count": _number(
            context.get("prior_order_attempt_count"),
            0,
        ),
        "no_second_order_attempt_allowed": _bool(
            context.get("no_second_order_attempt_allowed")
        ),
    }


def _sanitize_endpoint_plan(
    endpoint_plan: Mapping[str, Any],
    *,
    runtime_account_id: str | None,
) -> dict[str, Any]:
    return _sanitize_value(
        endpoint_plan,
        runtime_access_token=None,
        runtime_account_id=runtime_account_id,
    )


def _credential_runtime_summary(
    *,
    execute_preflight: bool,
    runtime_access_token: str | None,
    runtime_account_id: str | None,
) -> dict[str, bool]:
    return {
        "execute_preflight_requested": execute_preflight is True,
        "runtime_access_token_supplied": _present(runtime_access_token),
        "runtime_account_id_supplied": _present(runtime_account_id),
        "credential_persistence_allowed": False,
        "account_id_persistence_allowed": False,
        "dotenv_read_allowed": False,
        "credential_value_returned": False,
        "account_id_value_returned": False,
    }


def _root_cause_summary(
    raw_results: list[Mapping[str, Any]],
    *,
    runtime_account_id: str | None,
    attempted: bool,
) -> dict[str, Any]:
    if not attempted:
        return {
            "token_valid": "unknown",
            "account_visible_to_token": "unknown",
            "account_details_accessible": "unknown",
            "account_summary_accessible": "unknown",
            "instruments_accessible": "unknown",
            "eur_usd_available": "unknown",
            "account_practice_confirmed": "unknown",
            "trading_permission_likely": "unknown",
            "likely_403_root_cause": "unknown_requires_owner_broker_review",
        }

    by_name = {
        _text(result.get("endpoint_name")): _mapping(result.get("result"))
        for result in raw_results
    }
    accounts = by_name.get("accounts", {})
    details = by_name.get("account_details", {})
    summary = by_name.get("account_summary", {})
    instruments = by_name.get("account_instruments", {})

    token_valid = _success(accounts)
    account_visible = _account_visible(accounts, runtime_account_id)
    details_accessible = _success(details)
    summary_accessible = _success(summary)
    instruments_accessible = _success(instruments)
    eur_usd_available = _instrument_available(instruments, "EUR_USD")
    practice_confirmed = _practice_confirmed(details, summary)
    trading_permission_likely = _trading_permission_likely(
        account_visible=account_visible,
        details_accessible=details_accessible,
        summary_accessible=summary_accessible,
        instruments_accessible=instruments_accessible,
        eur_usd_available=eur_usd_available,
    )

    return {
        "token_valid": token_valid,
        "account_visible_to_token": account_visible,
        "account_details_accessible": details_accessible,
        "account_summary_accessible": summary_accessible,
        "instruments_accessible": instruments_accessible,
        "eur_usd_available": eur_usd_available,
        "account_practice_confirmed": practice_confirmed,
        "trading_permission_likely": trading_permission_likely,
        "likely_403_root_cause": _likely_root_cause(
            accounts=accounts,
            account_visible=account_visible,
            details_accessible=details_accessible,
            summary_accessible=summary_accessible,
            instruments_accessible=instruments_accessible,
            eur_usd_available=eur_usd_available,
        ),
    }


def _success(result: Mapping[str, Any]) -> bool | str:
    status_code = _number(result.get("status_code"), 0)
    if status_code == 200 or _text(result.get("status")).lower() == "success":
        return True
    if status_code in {401, 403, 404}:
        return False
    return "unknown"


def _account_visible(
    accounts_result: Mapping[str, Any],
    runtime_account_id: str | None,
) -> bool | str:
    if not _present(runtime_account_id):
        return "unknown"
    if _success(accounts_result) is not True:
        return False if _success(accounts_result) is False else "unknown"
    return _contains_value(_body(accounts_result), runtime_account_id)


def _instrument_available(
    instruments_result: Mapping[str, Any],
    instrument: str,
) -> bool | str:
    if _success(instruments_result) is not True:
        return False if _success(instruments_result) is False else "unknown"
    return _contains_value(_body(instruments_result), instrument)


def _practice_confirmed(*results: Mapping[str, Any]) -> bool | str:
    combined = [_body(result) for result in results if result]
    if not combined:
        return "unknown"
    text = json.dumps(combined, sort_keys=True).lower()
    if "practice" in text or '"environment": "demo"' in text:
        return True
    if all(_success(result) is True for result in results if result):
        return "unknown"
    return False


def _trading_permission_likely(
    *,
    account_visible: bool | str,
    details_accessible: bool | str,
    summary_accessible: bool | str,
    instruments_accessible: bool | str,
    eur_usd_available: bool | str,
) -> bool | str:
    values = (
        account_visible,
        details_accessible,
        summary_accessible,
        instruments_accessible,
        eur_usd_available,
    )
    if all(value is True for value in values):
        return True
    if any(value is False for value in values):
        return False
    return "unknown"


def _likely_root_cause(
    *,
    accounts: Mapping[str, Any],
    account_visible: bool | str,
    details_accessible: bool | str,
    summary_accessible: bool | str,
    instruments_accessible: bool | str,
    eur_usd_available: bool | str,
) -> str:
    if _number(accounts.get("status_code"), 0) in {401, 403}:
        return "token_invalid_or_expired"
    if account_visible is False:
        return "token_account_mismatch"
    if details_accessible is False:
        return "account_permission_restricted"
    if summary_accessible is False or instruments_accessible is False:
        return "account_not_visible_to_token"
    if eur_usd_available is False:
        return "account_permission_restricted"
    if all(
        value is True
        for value in (
            account_visible,
            details_accessible,
            summary_accessible,
            instruments_accessible,
            eur_usd_available,
        )
    ):
        return "order_permission_restricted"
    return "unknown_requires_owner_broker_review"


def _body(result: Mapping[str, Any]) -> Any:
    return result.get("body", {})


def _contains_value(value: Any, expected: str | None) -> bool:
    if not _present(expected):
        return False
    if isinstance(value, Mapping):
        return any(_contains_value(child, expected) for child in value.values())
    if isinstance(value, list):
        return any(_contains_value(child, expected) for child in value)
    return value == expected


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
            if _sensitive_key(key_text):
                sanitized[key_text] = "REDACTED_RUNTIME_ONLY_REFERENCE"
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
    return any(term in key_text for term in SENSITIVE_KEY_TERMS)


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            authority = _mapping(node.get("execution_authority"))
            for field in EXECUTION_AUTHORITY_FIELDS:
                if _bool(node.get(field)) or _bool(authority.get(field)):
                    blockers.append(f"unsafe_{label}_{field}_true")
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "read_only_preflight_only",
        "practice_demo_endpoint_only",
        "no_orders_endpoint",
        "no_trade_or_position_mutation",
        "no_second_order_attempt",
        "runtime_credentials_external_only",
        "no_credential_or_account_id_persistence",
        "execution_authority_false",
    ]
    if status == PREFLIGHT_DRY_RUN_READY:
        warnings.append("dry_run_preview_only_no_network_call")
    if status == PREFLIGHT_READ_ONLY_ATTEMPTED:
        warnings.append("read_only_get_endpoints_attempted_once_each")
    return warnings


def _next_safe_action(status: str, root_cause: Mapping[str, Any]) -> str:
    if status == PREFLIGHT_READ_ONLY_ATTEMPTED:
        if root_cause.get("trading_permission_likely") is True:
            return "prepare_secure_credential_persistence_design_after_owner_review"
        return "owner_review_oanda_demo_account_token_permissions_no_order_retry"
    if status == PREFLIGHT_DRY_RUN_READY:
        return "owner_may_run_read_only_preflight_once_with_runtime_credentials"
    if status == PREFLIGHT_BLOCKED_RUNTIME_CREDENTIALS_MISSING:
        return "owner_must_supply_runtime_env_credentials_outside_repo"
    if status == PREFLIGHT_BLOCKED_HTTP_GET_CALLABLE_REQUIRED:
        return "owner_runtime_script_must_supply_read_only_http_get_callable"
    if status == PREFLIGHT_REJECTED:
        return "remove_mutation_or_live_endpoint_from_preflight_plan"
    return "repair_preflight_context_before_owner_read_only_run"


def _parse_json_body(body: str) -> Any:
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def _trim_trailing_slash(value: str) -> str:
    return value.rstrip("/")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _number(value: Any, default: float) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def _present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
