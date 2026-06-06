"""Run the AI_OS Forex Engine v1 Sprint 9 broker sandbox model demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.broker_sandbox import BrokerSandbox
from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.models import (
    BrokerSandboxMode,
    SandboxOrderRequest,
    SandboxOrderSide,
    SandboxOrderType,
)


def build_demo_outputs(config=None):
    config = config or ForexEngineConfig()
    validate_config(config)
    sandbox = BrokerSandbox(config)
    valid = sandbox.submit_order(
        SandboxOrderRequest(
            mode=BrokerSandboxMode.SANDBOX_MODEL_ONLY,
            symbol="EURUSD",
            side=SandboxOrderSide.BUY,
            order_type=SandboxOrderType.MARKET,
            units=1000,
            client_order_id="demo-valid-eurusd-buy",
            metadata={"source": "sprint_9_demo"},
        )
    )
    invalid_symbol = sandbox.submit_order(
        SandboxOrderRequest(
            mode=BrokerSandboxMode.SANDBOX_MODEL_ONLY,
            symbol="AUDCAD",
            side=SandboxOrderSide.BUY,
            order_type=SandboxOrderType.MARKET,
            units=1000,
            client_order_id="demo-invalid-symbol",
        )
    )
    invalid_units = sandbox.submit_order(
        SandboxOrderRequest(
            mode=BrokerSandboxMode.SANDBOX_MODEL_ONLY,
            symbol="EURUSD",
            side=SandboxOrderSide.BUY,
            order_type=SandboxOrderType.MARKET,
            units=0,
            client_order_id="demo-invalid-units",
        )
    )
    live_blocked = sandbox.submit_order(
        SandboxOrderRequest(
            mode="LIVE",
            symbol="EURUSD",
            side=SandboxOrderSide.BUY,
            order_type=SandboxOrderType.MARKET,
            units=1000,
            client_order_id="demo-live-blocked",
        )
    )
    readiness = sandbox.build_readiness_check()
    return sandbox, valid, invalid_symbol, invalid_units, live_blocked, readiness


def main() -> int:
    config = ForexEngineConfig()
    sandbox, valid, invalid_symbol, invalid_units, live_blocked, readiness = build_demo_outputs(config)

    print("AI_OS Forex Engine v1 Sprint 9 Broker Sandbox Demo")
    print(f"Mode: {config.mode}")
    print(f"Sandbox mode: {sandbox.account_state.mode}")
    print("Broker connectivity: DISABLED")
    print("Credentials required: False")
    print(f"Order request: {valid.symbol} {valid.side}")
    print(f"Valid order status: {valid.status}")
    print("Fill model: SIMULATED")
    print(f"Order state: {valid.status}")
    print(f"Invalid symbol rejection: {invalid_symbol.reject_reason}")
    print(f"Invalid units rejection: {invalid_units.reject_reason}")
    print(f"Live trading blocked result: {live_blocked.status} / {live_blocked.reject_reason}")
    print(f"Readiness status: {readiness.status}")
    print(f"Next safe action: {readiness.next_safe_action}")
    print("Safety note: Local broker sandbox model only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
