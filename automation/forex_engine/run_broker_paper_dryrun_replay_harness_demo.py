from __future__ import annotations

from automation.forex_engine import broker_paper_dryrun_replay_harness


def _bool_text(value: object) -> str:
    return "true" if value is True else "false"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    result = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    summary = broker_paper_dryrun_replay_harness.summarize_dryrun_replay_harness(result)
    contract = broker_paper_dryrun_replay_harness.build_broker_paper_dryrun_replay_harness_contract()
    print("AIOS Broker-Paper Dry-Run Replay Harness Demo")
    print(f"Mode: {summary['mode']}")
    print(f"Classification: {summary['classification']}")
    print(f"Records replayed: {summary['records_replayed']}")
    print(f"Stub accepted: {summary['stub_accepted']}")
    print(f"Stub rejected: {summary['stub_rejected']}")
    print(f"Risk accepted: {summary['risk_accepted']}")
    print(f"Risk rejected: {summary['risk_rejected']}")
    print(f"Aggregate max loss USD: {summary['aggregate_max_loss_usd']}")
    print(f"Max daily loss USD: {summary['max_daily_loss_usd']}")
    print(f"Kill switch armed: {_bool_text(summary['kill_switch_armed'])}")
    print(f"Broker SDK allowed: {_bool_text(contract['broker_sdk_allowed'])}")
    print(f"Network/API allowed: {_bool_text(contract['network_api_allowed'])}")
    print(f"Credentials allowed: {_bool_text(contract['credentials_allowed'])}")
    print(f"Env secret read allowed: {_bool_text(contract['env_secret_read_allowed'])}")
    print(f"Webhook allowed: {_bool_text(contract['webhook_allowed'])}")
    print(f"Scheduler allowed: {_bool_text(contract['scheduler_allowed'])}")
    print(f"Daemon allowed: {_bool_text(contract['daemon_allowed'])}")
    print(f"Broker-paper orders allowed: {_bool_text(summary['broker_paper_orders_allowed'])}")
    print(f"Live orders allowed: {_bool_text(summary['live_orders_allowed'])}")
    print(f"Would place order: {_bool_text(summary['would_place_order'])}")
    print(f"Order placed: {_bool_text(summary['order_placed'])}")
    print(f"Next safe action: {summary['next_safe_action']}")
    print("Safety: dry-run replay harness only; no broker/API/network/orders/secrets/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
