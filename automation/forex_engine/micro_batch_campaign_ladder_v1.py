"""Micro-batch campaign ladder V1.

This module groups one to ninety-nine sanitized micro executions into campaign
evidence. It is local-only and deterministic: it does not read credentials,
does not call brokers, does not execute orders, and does not claim guaranteed
profit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping


CAMPAIGN_TARGET_NOT_MET = "CAMPAIGN_TARGET_NOT_MET"
CAMPAIGN_25_PERCENT_REACHED = "CAMPAIGN_25_PERCENT_REACHED"
CAMPAIGN_50_PERCENT_REACHED = "CAMPAIGN_50_PERCENT_REACHED"
CAMPAIGN_100_PERCENT_REACHED = "CAMPAIGN_100_PERCENT_REACHED"

REPEATABILITY_NOT_PROVEN = "REPEATABILITY_NOT_PROVEN"
REPEATABILITY_WEAK = "REPEATABILITY_WEAK"
REPEATABILITY_CANDIDATE = "REPEATABILITY_CANDIDATE"
REPEATABILITY_PROVEN = "REPEATABILITY_PROVEN"

PROFIT_TARGET_PLANNING_ONLY = "PROFIT_TARGET_PLANNING_ONLY"
PROFIT_TARGET_PAPER_ONLY = "PROFIT_TARGET_PAPER_ONLY"
PROFIT_TARGET_DEMO_CANDIDATE = "PROFIT_TARGET_DEMO_CANDIDATE"
PROFIT_TARGET_LIVE_EVIDENCE_REQUIRED = "PROFIT_TARGET_LIVE_EVIDENCE_REQUIRED"

EVIDENCE_MISSING = "EVIDENCE_MISSING"
PASSING = "PASSING"
BLOCKED = "BLOCKED"

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "Reports" / "forex_delivery"

REPORT_PATHS = {
    "campaign_ladder": REPORTS_DIR / "AIOS_FOREX_MICRO_BATCH_CAMPAIGN_LADDER_V1.md",
    "target_50": REPORTS_DIR / "AIOS_FOREX_50_PERCENT_CAMPAIGN_TARGET_V1.md",
    "target_100": REPORTS_DIR / "AIOS_FOREX_100_PERCENT_REPEATABILITY_TARGET_V1.md",
}

CAMPAIGN_FIELDS = (
    "campaign_id",
    "micro_execution_ids",
    "strategy_id",
    "candidate_id",
    "instrument",
    "side",
    "start_time",
    "end_time",
    "execution_count",
    "gross_pl",
    "net_pl",
    "return_percent",
    "max_drawdown",
    "win_count",
    "loss_count",
    "breakeven_count",
    "average_r",
    "profit_factor",
    "fees",
    "spread",
    "slippage",
    "stop_loss_compliance",
    "take_profit_compliance",
    "risk_governor_state",
    "broker_proof_state",
    "reconciliation_state",
    "evidence_path",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "password",
    "passwd",
    "secret",
    "token",
    "credential",
    "credentials",
    "account_id",
    "accountid",
    "account_identifier",
    "account_number",
    "broker_order_id",
    "order_id",
    "transaction_id",
    "raw_payload",
    "raw_request",
    "raw_response",
    "authorization",
)

SANITIZED_ALLOWED_KEYS = frozenset(
    {
        "account_id_redacted_confirmation",
        "credential_not_pasted_confirmation",
        "credential_not_persisted_confirmation",
    }
)


def run_micro_batch_campaign_ladder(
    input_state: dict[str, Any] | None = None,
    write_reports: bool = False,
) -> dict[str, Any]:
    """Build sanitized campaign evidence from local input only."""

    sanitized_input, redacted_fields = _sanitize_input(input_state or {})
    campaigns = _normalize_campaigns(sanitized_input)
    campaign_count = len(campaigns)
    micro_execution_count = sum(int(item["execution_count"]) for item in campaigns)
    campaign_target_status = _campaign_target_status(campaigns)
    repeatability_status = _repeatability_status(campaigns)
    profit_proof_status = _profit_proof_status(campaigns, sanitized_input)

    result = {
        "schema": "AIOS_FOREX_MICRO_BATCH_CAMPAIGN_LADDER_V1",
        "write_reports_requested": bool(write_reports),
        "campaign_count": campaign_count,
        "micro_execution_count": micro_execution_count,
        "campaigns": tuple(campaigns),
        "classifications": {
            "CAMPAIGN_TARGET_STATUS": campaign_target_status,
            "REPEATABILITY_STATUS": repeatability_status,
            "PROFIT_PROOF_STATUS": profit_proof_status,
        },
        "target_evidence": {
            "best_return_percent": _best_return_percent(campaigns),
            "campaigns_at_or_above_25_percent": _count_at_or_above(campaigns, 25.0),
            "campaigns_at_or_above_50_percent": _count_at_or_above(campaigns, 50.0),
            "campaigns_at_or_above_100_percent": _count_at_or_above(campaigns, 100.0),
            "evidence_ready_50_percent_campaigns": _count_evidence_ready_50(campaigns),
        },
        "blocked_reasons": tuple(_blocked_reasons(campaigns, redacted_fields)),
        "sanitization": {
            "redacted_fields": tuple(redacted_fields),
            "sensitive_input_rejected_or_redacted": bool(redacted_fields),
            "account_ids_persisted": False,
            "credentials_persisted": False,
            "broker_order_ids_persisted": False,
        },
        "safety_summary": _safety_summary(),
        "profit_doctrine": {
            "profit_guaranteed": False,
            "paper_profit_is_live_profit": False,
            "campaign_count_visible": True,
            "micro_execution_count_visible": True,
            "one_campaign_can_contain_many_micro_executions": True,
        },
        "reports": {
            "written": tuple(),
            "allowed_output_paths": tuple(_display_path(path) for path in REPORT_PATHS.values()),
        },
    }

    if write_reports:
        written = _write_reports(result)
        result["reports"] = {
            **result["reports"],
            "written": tuple(_display_path(path) for path in written),
        }

    return result


def _sanitize_input(payload: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    redacted: list[str] = []

    def scrub(value: Any, path: tuple[str, ...] = ()) -> Any:
        if isinstance(value, Mapping):
            output: dict[str, Any] = {}
            for key, item in value.items():
                key_text = str(key)
                normalized = key_text.lower().strip()
                if normalized not in SANITIZED_ALLOWED_KEYS and any(
                    part in normalized for part in SENSITIVE_KEY_PARTS
                ):
                    redacted.append(".".join(path + (key_text,)))
                    continue
                output[key_text] = scrub(item, path + (key_text,))
            return output
        if isinstance(value, list):
            return [scrub(item, path + (str(index),)) for index, item in enumerate(value)]
        if isinstance(value, tuple):
            return tuple(scrub(item, path + (str(index),)) for index, item in enumerate(value))
        return value

    return scrub(payload), _unique(redacted)


def _normalize_campaigns(input_state: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_campaigns = input_state.get("campaigns")
    if raw_campaigns is None and input_state.get("campaign") is not None:
        raw_campaigns = [input_state["campaign"]]
    if raw_campaigns is None and input_state.get("micro_execution_ids") is not None:
        raw_campaigns = [input_state]
    if not isinstance(raw_campaigns, list | tuple):
        return []

    campaigns: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_campaigns, start=1):
        if not isinstance(raw, Mapping):
            continue
        normalized = _normalize_campaign(raw, index)
        campaigns.append(normalized)
    return campaigns


def _normalize_campaign(raw: Mapping[str, Any], index: int) -> dict[str, Any]:
    micro_execution_ids = _micro_execution_ids(raw)
    execution_count = _execution_count(raw, micro_execution_ids)
    valid_execution_count = 1 <= execution_count <= 99
    return {
        "campaign_id": _text(raw.get("campaign_id"), f"CAMPAIGN-{index:03d}"),
        "micro_execution_ids": tuple(micro_execution_ids),
        "strategy_id": _text(raw.get("strategy_id"), EVIDENCE_MISSING),
        "candidate_id": _text(raw.get("candidate_id"), EVIDENCE_MISSING),
        "instrument": _text(raw.get("instrument"), EVIDENCE_MISSING),
        "side": _normalize_side(raw.get("side")),
        "start_time": _text(raw.get("start_time"), EVIDENCE_MISSING),
        "end_time": _text(raw.get("end_time"), EVIDENCE_MISSING),
        "execution_count": execution_count,
        "execution_count_supported": valid_execution_count,
        "gross_pl": _number(raw.get("gross_pl", raw.get("gross_p_l"))),
        "net_pl": _number(raw.get("net_pl", raw.get("net_p_l"))),
        "return_percent": _number(raw.get("return_percent", raw.get("return_pct"))),
        "max_drawdown": _number(raw.get("max_drawdown")),
        "win_count": int(_number(raw.get("win_count"))),
        "loss_count": int(_number(raw.get("loss_count"))),
        "breakeven_count": int(_number(raw.get("breakeven_count"))),
        "average_r": _number(raw.get("average_r")),
        "profit_factor": _number(raw.get("profit_factor")),
        "fees": _number(raw.get("fees")),
        "spread": _number(raw.get("spread")),
        "slippage": _number(raw.get("slippage")),
        "stop_loss_compliance": _gate(raw.get("stop_loss_compliance")),
        "take_profit_compliance": _gate(raw.get("take_profit_compliance")),
        "risk_governor_state": _text(raw.get("risk_governor_state"), EVIDENCE_MISSING),
        "broker_proof_state": _text(raw.get("broker_proof_state"), EVIDENCE_MISSING),
        "reconciliation_state": _text(raw.get("reconciliation_state"), EVIDENCE_MISSING),
        "evidence_path": _text(raw.get("evidence_path"), EVIDENCE_MISSING),
        "proof_mode": _proof_mode(raw),
    }


def _micro_execution_ids(raw: Mapping[str, Any]) -> list[str]:
    values = raw.get("micro_execution_ids")
    if isinstance(values, list | tuple):
        return [str(item) for item in values if str(item).strip()]
    count = int(_number(raw.get("execution_count", 0)))
    if count <= 0:
        return []
    campaign_id = _text(raw.get("campaign_id"), "CAMPAIGN")
    return [f"{campaign_id}-MICRO-{index:03d}" for index in range(1, count + 1)]


def _execution_count(raw: Mapping[str, Any], micro_execution_ids: list[str]) -> int:
    explicit = _number(raw.get("execution_count"))
    if explicit > 0:
        return int(explicit)
    return len(micro_execution_ids)


def _campaign_target_status(campaigns: Iterable[Mapping[str, Any]]) -> str:
    best = _best_return_percent(campaigns)
    if best >= 100.0:
        return CAMPAIGN_100_PERCENT_REACHED
    if best >= 50.0:
        return CAMPAIGN_50_PERCENT_REACHED
    if best >= 25.0:
        return CAMPAIGN_25_PERCENT_REACHED
    return CAMPAIGN_TARGET_NOT_MET


def _repeatability_status(campaigns: list[Mapping[str, Any]]) -> str:
    evidence_ready_50 = _count_evidence_ready_50(campaigns)
    if evidence_ready_50 >= 2:
        return REPEATABILITY_PROVEN
    if evidence_ready_50 == 1:
        return REPEATABILITY_CANDIDATE
    if _count_at_or_above(campaigns, 25.0) > 0:
        return REPEATABILITY_WEAK
    return REPEATABILITY_NOT_PROVEN


def _profit_proof_status(campaigns: list[Mapping[str, Any]], input_state: Mapping[str, Any]) -> str:
    if not campaigns:
        return PROFIT_TARGET_PLANNING_ONLY
    modes = {_proof_mode(campaign) for campaign in campaigns}
    requested = str(input_state.get("requested_profit_proof", "")).upper().strip()
    if requested == "LIVE":
        return PROFIT_TARGET_LIVE_EVIDENCE_REQUIRED
    if "DEMO" in modes and any(_campaign_evidence_ready(campaign) for campaign in campaigns):
        return PROFIT_TARGET_DEMO_CANDIDATE
    if "PAPER" in modes or "UNKNOWN" in modes:
        return PROFIT_TARGET_PAPER_ONLY
    return PROFIT_TARGET_PLANNING_ONLY


def _campaign_evidence_ready(campaign: Mapping[str, Any]) -> bool:
    return (
        bool(campaign.get("execution_count_supported"))
        and _truthy_gate(campaign.get("stop_loss_compliance"))
        and _truthy_gate(campaign.get("take_profit_compliance"))
        and _state_in(campaign.get("risk_governor_state"), {"PASS", "PASSING", "CLEAR", "RISK_GATES_PASS"})
        and _state_in(campaign.get("broker_proof_state"), {"CURRENT", "BROKER_PROOF_CURRENT", "DEMO_PROOF"})
        and _state_in(campaign.get("reconciliation_state"), {"RECONCILED", "PASS", "CLEAR"})
        and not _missing(campaign.get("evidence_path"))
    )


def _count_evidence_ready_50(campaigns: Iterable[Mapping[str, Any]]) -> int:
    return sum(1 for campaign in campaigns if _number(campaign.get("return_percent")) >= 50.0 and _campaign_evidence_ready(campaign))


def _count_at_or_above(campaigns: Iterable[Mapping[str, Any]], threshold: float) -> int:
    return sum(1 for campaign in campaigns if _number(campaign.get("return_percent")) >= threshold)


def _best_return_percent(campaigns: Iterable[Mapping[str, Any]]) -> float:
    values = [_number(campaign.get("return_percent")) for campaign in campaigns]
    return max(values) if values else 0.0


def _blocked_reasons(campaigns: list[Mapping[str, Any]], redacted_fields: list[str]) -> list[str]:
    reasons: list[str] = []
    if not campaigns:
        reasons.append("campaign_evidence_missing")
    if redacted_fields:
        reasons.append("sensitive_input_redacted")
    for campaign in campaigns:
        if not campaign.get("execution_count_supported"):
            reasons.append(f"{campaign.get('campaign_id')}:execution_count_outside_1_to_99")
        if _number(campaign.get("return_percent")) >= 50.0 and not _campaign_evidence_ready(campaign):
            reasons.append(f"{campaign.get('campaign_id')}:50_percent_target_requires_complete_evidence")
    return _unique(reasons)


def _write_reports(result: Mapping[str, Any]) -> list[Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    renders = {
        "campaign_ladder": _render_campaign_ladder_report(result),
        "target_50": _render_target_50_report(result),
        "target_100": _render_target_100_report(result),
    }
    written: list[Path] = []
    for key, text in renders.items():
        path = REPORT_PATHS[key]
        path.write_text(text, encoding="utf-8", newline="\n")
        written.append(path)
    return written


def _render_campaign_ladder_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Micro-Batch Campaign Ladder V1",
            "",
            "## Campaign Count",
            f"`{result['campaign_count']}`",
            "",
            "## Micro Execution Count",
            f"`{result['micro_execution_count']}`",
            "",
            "## Campaign Doctrine",
            "- Use campaign, not misleading one trade, when grouping 12 to 99 micro executions.",
            "- One campaign may contain many micro executions.",
            "- Campaign reports must show both campaign count and micro execution count.",
            "- Profits are targets and evidence goals, not guarantees.",
            "",
            "## Classifications",
            _table(result["classifications"]),
            "",
            "## Target Evidence",
            _table(result["target_evidence"]),
            "",
            "## Campaign Ledger",
            _campaign_table(result["campaigns"]),
            "",
            "## Blocked Reasons",
            _bullets(result["blocked_reasons"]),
            "",
            "## Safety",
            _table(result["safety_summary"]),
            "",
        ]
    )


def _render_target_50_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex 50 Percent Campaign Target V1",
            "",
            "## Status",
            f"`{result['classifications']['CAMPAIGN_TARGET_STATUS']}`",
            "",
            "## Evidence Gate",
            "The 50 percent campaign target is evidence-gated. A target claim requires campaign count, micro execution count, P/L, fees, spread, slippage, risk governor state, broker proof state, reconciliation state, stop-loss compliance, take-profit compliance, and sanitized evidence path.",
            "",
            "## Visible Counts",
            _table(
                {
                    "campaign_count": result["campaign_count"],
                    "micro_execution_count": result["micro_execution_count"],
                    "campaigns_at_or_above_50_percent": result["target_evidence"]["campaigns_at_or_above_50_percent"],
                    "evidence_ready_50_percent_campaigns": result["target_evidence"]["evidence_ready_50_percent_campaigns"],
                }
            ),
            "",
            "## Profit Proof Status",
            f"`{result['classifications']['PROFIT_PROOF_STATUS']}`",
            "",
            "## Guarantee Boundary",
            "No guaranteed profit is claimed. Paper profit is not live profit.",
            "",
        ]
    )


def _render_target_100_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex 100 Percent Repeatability Target V1",
            "",
            "## Repeatability Status",
            f"`{result['classifications']['REPEATABILITY_STATUS']}`",
            "",
            "## Repeatability Doctrine",
            "The 100 percent target requires repeatability evidence, such as two proven 50 percent campaign profiles or equivalent validated evidence.",
            "",
            "## Visible Counts",
            _table(
                {
                    "campaign_count": result["campaign_count"],
                    "micro_execution_count": result["micro_execution_count"],
                    "campaigns_at_or_above_100_percent": result["target_evidence"]["campaigns_at_or_above_100_percent"],
                    "evidence_ready_50_percent_campaigns": result["target_evidence"]["evidence_ready_50_percent_campaigns"],
                }
            ),
            "",
            "## Blocked Reasons",
            _bullets(result["blocked_reasons"]),
            "",
        ]
    )


def _campaign_table(campaigns: Iterable[Mapping[str, Any]]) -> str:
    columns = (
        "campaign_id",
        "execution_count",
        "return_percent",
        "net_pl",
        "profit_factor",
        "risk_governor_state",
        "broker_proof_state",
        "reconciliation_state",
        "evidence_path",
    )
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    count = 0
    for campaign in campaigns:
        count += 1
        lines.append("| " + " | ".join(f"`{campaign.get(column, EVIDENCE_MISSING)}`" for column in columns) + " |")
    return "\n".join(lines) if count else "- `NO_CAMPAIGNS_RECORDED`"


def _safety_summary() -> dict[str, bool]:
    return {
        "broker_api_called": False,
        "bank_payment_call_performed": False,
        "network_call_performed": False,
        "credentials_read": False,
        "account_identifiers_read": False,
        "env_read": False,
        "secret_files_read": False,
        "live_order_executed": False,
        "demo_order_executed": False,
        "money_movement_performed": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "profit_guaranteed": False,
    }


def _proof_mode(raw: Mapping[str, Any]) -> str:
    value = str(raw.get("proof_mode", raw.get("environment", "UNKNOWN"))).upper().strip()
    if value in {"PAPER", "PAPER_ONLY", "PAPER_REPLAY"}:
        return "PAPER"
    if value in {"DEMO", "DEMO_CANDIDATE", "DEMO_PROOF"}:
        return "DEMO"
    if value in {"LIVE", "LIVE_PROOF_ONLY"}:
        return "LIVE_PROOF_ONLY"
    return "UNKNOWN"


def _state_in(value: Any, allowed: set[str]) -> bool:
    return str(value).upper().strip() in allowed


def _truthy_gate(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).upper().strip() in {PASSING, "PASS", "TRUE", "CLEAR", "COMPLIANT", "ENFORCED"}


def _gate(value: Any) -> str:
    if _truthy_gate(value):
        return PASSING
    if value in (None, ""):
        return EVIDENCE_MISSING
    text = str(value).upper().strip()
    if text in {"FAIL", "FAILED", "FALSE", "BLOCKED", "BREACHED"}:
        return BLOCKED
    return text


def _normalize_side(value: Any) -> str:
    text = str(value or "").upper().strip()
    if text in {"LONG", "BUY"}:
        return "BUY"
    if text in {"SHORT", "SELL"}:
        return "SELL"
    return text or EVIDENCE_MISSING


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == "" or value.strip().upper() in {"UNKNOWN", EVIDENCE_MISSING}
    return False


def _text(value: Any, fallback: str) -> str:
    if _missing(value):
        return fallback
    return str(value)


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _bullets(values: Iterable[Any]) -> str:
    items = [str(value) for value in values]
    return "\n".join(f"- `{item}`" for item in items) if items else "- `NONE`"


def _table(values: Mapping[str, Any]) -> str:
    lines = ["| Field | Value |", "|---|---|"]
    for key, value in values.items():
        lines.append(f"| {key} | `{value}` |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(json.dumps(run_micro_batch_campaign_ladder(write_reports=True), indent=2, sort_keys=True))
