from __future__ import annotations

import argparse

from automation.forex_engine import broker_paper_dryrun_intent_ledger


def _bool_text(value: object) -> str:
    return "true" if value is True else "false"


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Run the local broker-paper dry-run intent ledger demo.")


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    ledger = broker_paper_dryrun_intent_ledger.replay_dryrun_intent_batch()
    summary = broker_paper_dryrun_intent_ledger.summarize_dryrun_intent_ledger(ledger)
    contract = ledger["contract"]
    print("AIOS Broker-Paper Dry-Run Intent Ledger Demo")
    print(f"Mode: {summary['mode']}")
    print(f"Classification: {summary['classification']}")
    print(f"Ledger storage: {summary['ledger_storage']}")
    print(f"Records: {summary['records_count']}")
    print(f"Accepted: {summary['accepted_count']}")
    print(f"Rejected: {summary['rejected_count']}")
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
    print("Safety: dry-run ledger only; no broker/API/network/orders/secrets/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
