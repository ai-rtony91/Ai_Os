"""Run consolidated forex live-readiness blocker burndown dry run.

The script runs local dry-run/read-only evaluators only. It never reads secrets,
calls brokers, places orders, or closes trades.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.auto_exit_live_readiness import (  # noqa: E402
    build_auto_exit_live_readiness_model,
    cli_summary as auto_exit_summary,
    write_auto_exit_live_readiness_report,
)
from src.forex_delivery.live_micro_trade_arming_gate import (  # noqa: E402
    build_live_micro_trade_arming_gate_result,
    cli_summary as arming_summary,
)
from src.forex_delivery.one_shot_live_micro_trade_execution_review import (  # noqa: E402
    build_one_shot_live_micro_trade_execution_review_result,
    cli_summary as execution_review_summary,
)
from src.forex_delivery.read_only_evidence_approval import (  # noqa: E402
    build_read_only_evidence_approval_model,
    cli_summary as read_only_summary,
    write_read_only_evidence_approval_report,
)
from src.forex_delivery.trading_history_writeback_verification import (  # noqa: E402
    build_trading_history_writeback_verification_model,
    cli_summary as history_summary,
    write_trading_history_writeback_verification_report,
)


REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/"
    "AIOS_FOREX_LIVE_READINESS_CONSOLIDATED_BLOCKER_BURNDOWN_DRY_RUN_V1.md"
)


def build_consolidated_burndown_model() -> dict[str, Any]:
    read_only = build_read_only_evidence_approval_model(repo_root=REPO_ROOT)
    history = build_trading_history_writeback_verification_model(repo_root=REPO_ROOT)
    auto_exit = build_auto_exit_live_readiness_model(repo_root=REPO_ROOT)
    arming = build_live_micro_trade_arming_gate_result(repo_root=REPO_ROOT)
    execution_review = build_one_shot_live_micro_trade_execution_review_result(
        repo_root=REPO_ROOT
    )

    blockers_before = unique(
        list(arming.get("blocked_reasons") or [])
        + list(execution_review.get("blocked_reasons") or [])
    )
    blockers_removed = unique(
        list(read_only.get("blockers_removed_when_satisfied") or [])
    )
    blockers_remaining = unique(
        list(read_only.get("blocked_reasons") or [])
        + list(history.get("blocked_reasons") or [])
        + list(auto_exit.get("blocked_reasons") or [])
        + list(arming.get("blocked_reasons") or [])
        + list(execution_review.get("blocked_reasons") or [])
    )

    result = {
        "schema": "AIOS_FOREX_LIVE_READINESS_CONSOLIDATED_BLOCKER_BURNDOWN.v1",
        "live_execution_allowed": False,
        "live_trade_placed": False,
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
        "read_only_evidence_approval": read_only_summary(read_only),
        "trading_history_writeback_verification": history_summary(history),
        "auto_exit_live_readiness": auto_exit_summary(auto_exit),
        "live_micro_trade_arming_gate": arming_summary(arming),
        "one_shot_execution_review": execution_review_summary(execution_review),
        "blockers_before": blockers_before,
        "blockers_removed": blockers_removed,
        "blockers_remaining": blockers_remaining,
        "next_safe_action": (
            "Resolve remaining evidence, history, auto-exit, and human approval "
            "blockers. Do not execute live trades from this dry run."
        ),
        "next_single_target": "AIOS-FOREX-AUTO-EXIT-LIVE-READINESS-V1",
    }
    assert_consolidated_sanitized(result)
    write_read_only_evidence_approval_report(read_only, repo_root=REPO_ROOT)
    write_trading_history_writeback_verification_report(history, repo_root=REPO_ROOT)
    write_auto_exit_live_readiness_report(auto_exit, repo_root=REPO_ROOT)
    return result


def build_report(result: Mapping[str, Any]) -> str:
    assert_consolidated_sanitized(result)
    return (
        "# AIOS Forex Live Readiness Consolidated Blocker Burndown Dry Run V1\n\n"
        "## Summary\n"
        f"- live_execution_allowed: {result.get('live_execution_allowed')}\n"
        f"- live_trade_placed: {result.get('live_trade_placed')}\n"
        f"- broker_write_calls_allowed: {result.get('broker_write_calls_allowed')}\n"
        f"- order_placement_allowed: {result.get('order_placement_allowed')}\n"
        f"- close_trade_allowed: {result.get('close_trade_allowed')}\n\n"
        "## Blockers Before\n"
        f"{json.dumps(result.get('blockers_before', []), indent=2, sort_keys=True)}\n\n"
        "## Blockers Removed\n"
        f"{json.dumps(result.get('blockers_removed', []), indent=2, sort_keys=True)}\n\n"
        "## Blockers Remaining\n"
        f"{json.dumps(result.get('blockers_remaining', []), indent=2, sort_keys=True)}\n\n"
        "## Evaluations\n"
        "```json\n"
        f"{json.dumps(cli_summary(result), indent=2, sort_keys=True)}\n"
        "```\n\n"
        "## Explicit Safety Confirmations\n"
        "- No live trade was placed.\n"
        "- No broker write calls were made.\n"
        "- No BUY, SELL, or close action was wired.\n"
        "- No secrets, account identifier values, broker order identifier values, "
        "or transaction identifier values were recorded.\n"
    )


def write_consolidated_report(result: Mapping[str, Any]) -> Path:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(result), encoding="utf-8")
    return REPORT_PATH


def cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": result.get("schema"),
        "live_execution_allowed": False,
        "live_trade_placed": False,
        "read_only_evidence_approval": result.get("read_only_evidence_approval"),
        "trading_history_writeback_verification": result.get(
            "trading_history_writeback_verification"
        ),
        "auto_exit_live_readiness": result.get("auto_exit_live_readiness"),
        "live_micro_trade_arming_gate": result.get("live_micro_trade_arming_gate"),
        "one_shot_execution_review": result.get("one_shot_execution_review"),
        "blockers_removed": result.get("blockers_removed", []),
        "blockers_remaining": result.get("blockers_remaining", []),
        "next_safe_action": result.get("next_safe_action"),
        "next_single_target": result.get("next_single_target"),
    }


def assert_consolidated_sanitized(payload: Mapping[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    for marker in (
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
        "Authorization",
        "Bearer ",
        "accountID",
        "orderID",
        "transactionID",
        "rawBroker",
    ):
        if marker in serialized:
            raise ValueError(f"unsafe_consolidated_marker:{marker}")
    for field in (
        "live_execution_allowed",
        "live_trade_placed",
        "broker_write_calls_allowed",
        "order_placement_allowed",
        "close_trade_allowed",
    ):
        if payload.get(field) is not False:
            raise ValueError(f"{field} must remain false")


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def main(argv: list[str] | None = None) -> int:
    del argv
    result = build_consolidated_burndown_model()
    write_consolidated_report(result)
    print(json.dumps(cli_summary(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
