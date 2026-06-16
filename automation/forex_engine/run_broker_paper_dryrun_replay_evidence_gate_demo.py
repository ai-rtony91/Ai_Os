from __future__ import annotations

import argparse
from typing import Any

from automation.forex_engine import broker_paper_dryrun_replay_evidence_gate


def _bool(value: Any) -> str:
    return "true" if value is True else "false"


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Run broker-paper dry-run replay evidence gate demo.")


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    result = broker_paper_dryrun_replay_evidence_gate.build_default_replay_evidence_gate_result()
    summary = broker_paper_dryrun_replay_evidence_gate.summarize_replay_evidence_gate(result)

    print("AIOS Broker-Paper Dry-Run Replay Evidence Gate Demo")
    print(f"Mode: {summary['mode']}")
    print(f"Classification: {summary['classification']}")
    print(f"Evidence ready: {_bool(summary['evidence_ready'])}")
    print(f"Records replayed: {summary['records_replayed']}")
    print(f"Stub accepted/rejected: {summary['stub_accepted']}/{summary['stub_rejected']}")
    print(f"Risk accepted/rejected: {summary['risk_accepted']}/{summary['risk_rejected']}")
    print(f"Aggregate max loss USD: {summary['aggregate_max_loss_usd']}")
    print(f"Max daily loss USD: {summary['max_daily_loss_usd']}")
    print(f"Kill switch armed: {_bool(summary['kill_switch_armed'])}")
    print(f"All unsafe flags false: {_bool(summary['all_unsafe_flags_false'])}")
    print(f"Broker SDK allowed: {_bool(summary['broker_sdk_allowed'])}")
    print(f"Network/API allowed: {_bool(summary['network_api_allowed'])}")
    print(f"Credentials allowed: {_bool(summary['credentials_allowed'])}")
    print(f"Broker-paper orders allowed: {_bool(summary['broker_paper_orders_allowed'])}")
    print(f"Live orders allowed: {_bool(summary['live_orders_allowed'])}")
    print(f"EOM milestone status: {summary['eom_milestone_status']}")
    print(f"Next safe action: {summary['next_safe_action']}")
    print("Safety: evidence gate only; no broker/API/network/orders/secrets/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
