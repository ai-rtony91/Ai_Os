from __future__ import annotations

import json
import sys
from pathlib import Path


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from trading_lab.tv_tp_bridge.aios_paper_validator import validate_aios_paper_signal
from trading_lab.tv_tp_bridge.aios_signal_intake import normalize_tradingview_payload
from trading_lab.tv_tp_bridge.traderspost_handoff_payload import build_traderspost_handoff_payload
from trading_lab.tv_tp_bridge.tv_alert_payload import build_tradingview_alert_payload


def run_demo() -> dict[str, dict]:
    alert = build_tradingview_alert_payload()
    intake = normalize_tradingview_payload(alert)
    validation = validate_aios_paper_signal(intake)
    handoff = build_traderspost_handoff_payload(intake, validation)
    return {
        "tradingview_alert": alert,
        "aios_intake": intake,
        "aios_paper_validation": validation,
        "traderspost_handoff": handoff,
    }


def main() -> int:
    result = run_demo()
    validation = result["aios_paper_validation"]
    handoff = result["traderspost_handoff"]

    print("AI_OS TradingView to TradersPost Paper Bridge Demo")
    print("TradingView alert created: YES")
    print("AI_OS signal intake completed: YES")
    print(f"Paper validation result: {validation['validation_status']}")
    print("TradersPost handoff format prepared: YES")
    print(f"Webhook not sent: {handoff['webhook_status']}")
    print(f"Broker not connected: {handoff['broker_status']}")
    print(f"Live execution blocked: {handoff['live_execution_status']}")
    print("Structured demo result:")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
