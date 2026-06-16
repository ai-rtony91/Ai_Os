from __future__ import annotations

from automation.forex_engine import broker_paper_adapter_stub_contract as stub_contract


def main(_argv: list[str] | None = None) -> int:
    contract = stub_contract.build_broker_paper_adapter_stub_contract()
    intent = {
        "symbol": "EURUSD_FAKE",
        "side": "buy",
        "quantity_units": 1000,
        "order_type": "market_stub",
        "stop_loss_pips": 8.0,
        "take_profit_pips": 12.0,
        "max_loss_usd": 10.0,
        "dry_run": True,
        "approved_by_operator": True,
    }
    result = stub_contract.simulate_broker_paper_stub_adapter(intent, contract)
    summary = stub_contract.summarize_broker_paper_stub_contract(result)

    print("AIOS Broker-Paper Adapter Stub Contract Demo")
    print(f"Mode: {summary['mode']}")
    print(f"Classification: {summary['classification']}")
    print(f"Broker SDK allowed: {str(summary['broker_sdk_allowed']).lower()}")
    print(f"Network/API allowed: {str(summary['network_api_allowed']).lower()}")
    print(f"Credentials allowed: {str(summary['credentials_allowed']).lower()}")
    print(f"Env secret read allowed: {str(summary['env_secret_read_allowed']).lower()}")
    print(f"Webhook allowed: {str(summary['webhook_allowed']).lower()}")
    print(f"Scheduler allowed: {str(summary['scheduler_allowed']).lower()}")
    print(f"Daemon allowed: {str(summary['daemon_allowed']).lower()}")
    print(f"Broker-paper orders allowed: {str(summary['broker_paper_orders_allowed']).lower()}")
    print(f"Live orders allowed: {str(summary['live_orders_allowed']).lower()}")
    print(f"Would place order: {str(summary['would_place_order']).lower()}")
    print(f"Order placed: {str(summary['order_placed']).lower()}")
    print(f"Next safe action: {summary['next_safe_action']}")
    print("Safety: stub-only; no broker/API/network/orders/secrets/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
