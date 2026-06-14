from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


SCHEMA = "AIOS_AUTONOMY_EXECUTE.v1"
SUPPORTED_GOALS = {"forex-paper-bot"}

FOREX_BOT_PATH = Path("apps/trading_lab/trading_lab/forex_paper_bot.py")
FOREX_BOT_TEST_PATH = Path("tests/trading_lab/test_forex_paper_bot.py")
FOREX_BOT_DOC_PATH = Path("docs/orchestration/AIOS_FOREX_PAPER_BOT.md")
FOREX_SCAFFOLD_PATHS = (
    FOREX_BOT_PATH,
    FOREX_BOT_TEST_PATH,
    FOREX_BOT_DOC_PATH,
)

ValidatorRunner = Callable[[Path], dict[str, Any]]


def safety_flags() -> dict[str, bool]:
    return {
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "delete_reset": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_launch": False,
        "runtime_launch": False,
        "scheduler": False,
        "daemon": False,
        "secrets": False,
        "broker_live_trading": False,
        "real_orders": False,
    }


def approval_required() -> dict[str, bool]:
    return {
        "local_paper_scaffold_apply": False,
        "git_add": True,
        "git_commit": True,
        "git_push": True,
        "merge": True,
        "secrets": True,
        "broker_live_trading": True,
        "scheduler_activation": True,
        "destructive_action": True,
        "queue_mutation": True,
        "approval_mutation": True,
        "worker_dispatch": True,
    }


def build_forex_bot_source() -> str:
    return '''from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_DIRECTIONS = {"buy", "sell"}
MAX_RISK_PERCENT = 2.0

PAPER_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}


def blocked_decision(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "decision_type": "blocked",
        "blocked_reason": reason,
        **PAPER_SAFETY,
    }


def _unsafe_scope_reason(
    execution_mode: str,
    live_execution: bool,
    broker_order: bool,
    credentials: Any,
    real_order: bool,
    webhook_url: str | None,
) -> str | None:
    if execution_mode != "paper":
        return "execution_mode_must_be_paper"
    if live_execution:
        return "live_execution_blocked"
    if broker_order:
        return "broker_order_blocked"
    if credentials:
        return "credentials_blocked"
    if real_order:
        return "real_order_blocked"
    if webhook_url:
        return "real_webhook_blocked"
    return None


def validate_signal(
    pair: str,
    direction: str,
    entry_price: float,
    stop_loss: float | None,
    account_equity: float,
    max_risk_percent: float,
    *,
    execution_mode: str = "paper",
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    unsafe_reason = _unsafe_scope_reason(
        execution_mode=execution_mode,
        live_execution=live_execution,
        broker_order=broker_order,
        credentials=credentials,
        real_order=real_order,
        webhook_url=webhook_url,
    )
    if unsafe_reason:
        return blocked_decision(unsafe_reason)

    normalized_pair = str(pair).upper()
    normalized_direction = str(direction).lower()

    if normalized_pair not in SUPPORTED_PAIRS:
        return blocked_decision("unsupported_pair")
    if normalized_direction not in SUPPORTED_DIRECTIONS:
        return blocked_decision("unsupported_direction")
    if stop_loss is None:
        return blocked_decision("stop_loss_required")
    if account_equity <= 0:
        return blocked_decision("account_equity_must_be_positive")
    if entry_price <= 0 or stop_loss <= 0:
        return blocked_decision("prices_must_be_positive")
    if entry_price == stop_loss:
        return blocked_decision("stop_loss_must_differ_from_entry")
    if max_risk_percent <= 0 or max_risk_percent > MAX_RISK_PERCENT:
        return blocked_decision("max_risk_percent_exceeds_paper_limit")

    return {
        "allowed": True,
        "pair": normalized_pair,
        "direction": normalized_direction,
        "entry_price": float(entry_price),
        "stop_loss": float(stop_loss),
        "account_equity": float(account_equity),
        "max_risk_percent": float(max_risk_percent),
        **PAPER_SAFETY,
    }


def calculate_mock_position_size(
    account_equity: float,
    max_risk_percent: float,
    entry_price: float,
    stop_loss: float,
) -> dict[str, float]:
    risk_amount = float(account_equity) * (float(max_risk_percent) / 100.0)
    stop_distance = abs(float(entry_price) - float(stop_loss))
    if stop_distance == 0:
        return {"risk_amount": round(risk_amount, 2), "mock_units": 0.0}
    return {
        "risk_amount": round(risk_amount, 2),
        "mock_units": round(risk_amount / stop_distance, 2),
    }


def paper_decision(
    pair: str,
    direction: str,
    entry_price: float,
    stop_loss: float | None,
    account_equity: float,
    max_risk_percent: float,
    *,
    execution_mode: str = "paper",
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    validation = validate_signal(
        pair=pair,
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        account_equity=account_equity,
        max_risk_percent=max_risk_percent,
        execution_mode=execution_mode,
        live_execution=live_execution,
        broker_order=broker_order,
        credentials=credentials,
        real_order=real_order,
        webhook_url=webhook_url,
    )
    if not validation["allowed"]:
        return validation

    position = calculate_mock_position_size(
        account_equity=validation["account_equity"],
        max_risk_percent=validation["max_risk_percent"],
        entry_price=validation["entry_price"],
        stop_loss=validation["stop_loss"],
    )
    return {
        "allowed": True,
        "decision_type": "paper_decision_only",
        "pair": validation["pair"],
        "direction": validation["direction"],
        "mock_position_size": position,
        "next_safe_action": "Review the paper decision locally. Do not route it to a broker.",
        **PAPER_SAFETY,
    }
'''


def build_forex_bot_test_source() -> str:
    return '''from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_paper_bot.py"


def load_bot_module():
    spec = importlib.util.spec_from_file_location("forex_paper_bot", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_valid_eurusd_paper_signal_allowed():
    bot = load_bot_module()
    decision = bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0)
    assert decision["allowed"] is True
    assert decision["decision_type"] == "paper_decision_only"
    assert decision["execution_allowed"] is False
    assert decision["broker_execution"] is False
    assert decision["real_orders"] is False


def test_valid_sell_signal_allowed():
    bot = load_bot_module()
    decision = bot.paper_decision("GBPUSD", "sell", 1.25, 1.26, 10000, 1.0)
    assert decision["allowed"] is True
    assert decision["direction"] == "sell"


def test_unsafe_scope_is_blocked():
    bot = load_bot_module()
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, live_execution=True)["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, broker_order=True)["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, credentials={"token": "x"})["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, real_order=True)["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, webhook_url="https://example.invalid")["allowed"] is False


def test_invalid_inputs_are_blocked():
    bot = load_bot_module()
    assert bot.paper_decision("AUDUSD", "buy", 1.10, 1.09, 10000, 1.0)["blocked_reason"] == "unsupported_pair"
    assert bot.paper_decision("EURUSD", "hold", 1.10, 1.09, 10000, 1.0)["blocked_reason"] == "unsupported_direction"
    assert bot.paper_decision("EURUSD", "buy", 1.10, None, 10000, 1.0)["blocked_reason"] == "stop_loss_required"
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 5.0)["blocked_reason"] == "max_risk_percent_exceeds_paper_limit"
'''


def build_forex_bot_doc() -> str:
    return """# AIOS Forex Paper Bot

This generated scaffold is paper-only. It models a local Forex paper decision for
review and does not connect to a broker, credential store, real webhook, live
market feed, scheduler, worker dispatcher, or order route.

Supported pairs are EURUSD, GBPUSD, and USDJPY. Supported directions are buy and
sell. The bot blocks missing stop loss values, unsupported pairs, unsupported
directions, risk above the local paper limit, credentials, broker orders, live
execution, real orders, and real webhook routing.

The scaffold exists to prove that AIOS can apply one safe local build action,
run the focused validator, attempt one bounded repair when requested, and report
the result without staging, committing, pushing, dispatching workers, mutating
queues, or enabling live trading.
"""


def forex_scaffold_files() -> dict[Path, str]:
    return {
        FOREX_BOT_PATH: build_forex_bot_source(),
        FOREX_BOT_TEST_PATH: build_forex_bot_test_source(),
        FOREX_BOT_DOC_PATH: build_forex_bot_doc(),
    }


def write_text_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def write_forex_scaffold(repo_root: Path) -> list[str]:
    files_written: list[str] = []
    for relative_path, content in forex_scaffold_files().items():
        target = repo_root / relative_path
        if write_text_if_changed(target, content):
            files_written.append(relative_path.as_posix())
    return files_written


def run_forex_bot_validator(repo_root: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        FOREX_BOT_TEST_PATH.as_posix(),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": "forex_paper_bot_tests",
        "command": " ".join(command),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def blocked_report(goal: str, mode: str, reason: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": goal,
        "mode": mode,
        "files_written": [],
        "validators_run": [],
        "repair_attempts": 0,
        "result": "blocked",
        "blocked_reason": reason,
        "next_safe_action": "Choose a supported local paper-only goal.",
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }


def execute_goal(
    repo_root: Path,
    goal: str,
    *,
    apply: bool = False,
    max_repairs: int = 0,
    validator_runner: ValidatorRunner | None = None,
) -> dict[str, Any]:
    mode = "APPLY" if apply else "DRY_RUN"
    if goal not in SUPPORTED_GOALS:
        return blocked_report(goal, mode, "unsupported_goal")

    if max_repairs < 0:
        return blocked_report(goal, mode, "max_repairs_must_be_non_negative")

    report = {
        "schema": SCHEMA,
        "goal": goal,
        "mode": mode,
        "files_written": [],
        "validators_run": [],
        "repair_attempts": 0,
        "result": "preview_only",
        "next_safe_action": "Run with --apply only inside an approved local write boundary.",
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }

    if not apply:
        return report

    runner = validator_runner or run_forex_bot_validator
    report["files_written"] = write_forex_scaffold(repo_root)

    validation = runner(repo_root)
    report["validators_run"].append(validation)

    while not validation.get("passed", False) and report["repair_attempts"] < max_repairs:
        report["repair_attempts"] += 1
        repaired_files = write_forex_scaffold(repo_root)
        for relative_path in repaired_files:
            if relative_path not in report["files_written"]:
                report["files_written"].append(relative_path)
        validation = runner(repo_root)
        report["validators_run"].append(validation)

    if validation.get("passed", False):
        report["result"] = "passed"
        report["next_safe_action"] = "Review the paper-only scaffold diff. Commit and push still require Anthony approval."
    else:
        report["result"] = "failed"
        report["next_safe_action"] = "Inspect the validator output before attempting another bounded repair."

    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one bounded AIOS autonomy execute goal.")
    parser.add_argument("--goal", required=True, help="Goal to execute. Supported: forex-paper-bot.")
    parser.add_argument("--apply", action="store_true", help="Write the supported local scaffold and run validators.")
    parser.add_argument("--max-repairs", type=int, default=0, help="Maximum bounded repair attempts.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root for tests or sandbox runs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    report = execute_goal(
        repo_root=repo_root,
        goal=args.goal,
        apply=args.apply,
        max_repairs=args.max_repairs,
    )
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0 if report["result"] in {"passed", "preview_only", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
