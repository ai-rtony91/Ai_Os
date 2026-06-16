from __future__ import annotations

from automation.forex_engine import broker_paper_dryrun_risk_governor


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    result = broker_paper_dryrun_risk_governor.evaluate_dryrun_ledger_risk()
    summary = broker_paper_dryrun_risk_governor.summarize_dryrun_risk_governor(result)
    print("AIOS Broker-Paper Dry-Run Risk Governor Demo")
    print(f"Mode: {summary['mode']}")
    print(f"Classification: {summary['classification']}")
    print(f"Records: {summary['records_count']}")
    print(f"Risk accepted: {summary['risk_accepted']}")
    print(f"Risk rejected: {summary['risk_rejected']}")
    print(f"Aggregate max loss USD: {summary['aggregate_max_loss_usd']}")
    print(f"Max daily loss USD: {summary['max_daily_loss_usd']}")
    print(f"Kill switch armed: {_bool_text(summary['kill_switch_armed'])}")
    print(f"Broker SDK allowed: {_bool_text(summary['broker_sdk_allowed'])}")
    print(f"Network/API allowed: {_bool_text(summary['network_api_allowed'])}")
    print(f"Credentials allowed: {_bool_text(summary['credentials_allowed'])}")
    print(f"Env secret read allowed: {_bool_text(summary['env_secret_read_allowed'])}")
    print(f"Webhook allowed: {_bool_text(summary['webhook_allowed'])}")
    print(f"Scheduler allowed: {_bool_text(summary['scheduler_allowed'])}")
    print(f"Daemon allowed: {_bool_text(summary['daemon_allowed'])}")
    print(f"Broker-paper orders allowed: {_bool_text(summary['broker_paper_orders_allowed'])}")
    print(f"Live orders allowed: {_bool_text(summary['live_orders_allowed'])}")
    print(f"Would place order: {_bool_text(summary['would_place_order'])}")
    print(f"Order placed: {_bool_text(summary['order_placed'])}")
    print(f"Next safe action: {summary['next_safe_action']}")
    print("Safety: dry-run risk governor only; no broker/API/network/orders/secrets/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
