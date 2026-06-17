from __future__ import annotations

import argparse
from typing import Any

from automation.forex_engine import broker_paper_adapter_plan_approval_gate


def _bool(value: Any) -> str:
    return "true" if value is True else "false"


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Run broker-paper adapter plan approval gate demo.")


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    approval = broker_paper_adapter_plan_approval_gate.build_example_plan_only_approval()
    result = broker_paper_adapter_plan_approval_gate.evaluate_broker_paper_adapter_plan_approval_gate(
        approval=approval
    )
    summary = broker_paper_adapter_plan_approval_gate.summarize_broker_paper_adapter_plan_approval_gate(
        result
    )

    print("AIOS Broker-Paper Adapter Plan Approval Gate Demo")
    print(f"Mode: {summary['mode']}")
    print(f"Classification: {summary['classification']}")
    print(f"Source evidence ready: {_bool(summary['source_evidence_ready'])}")
    print(f"Approval complete: {_bool(summary['approval_complete'])}")
    print(f"Paper/demo adapter planning allowed: {_bool(summary['paper_demo_adapter_planning_allowed'])}")
    print(f"Adapter implementation allowed: {_bool(summary['adapter_implementation_allowed'])}")
    print(f"Broker SDK allowed: {_bool(summary['broker_sdk_allowed'])}")
    print(f"Network/API allowed: {_bool(summary['network_api_allowed'])}")
    print(f"Credentials allowed: {_bool(summary['credentials_allowed'])}")
    print(f"Broker-paper orders allowed: {_bool(summary['broker_paper_orders_allowed'])}")
    print(f"Live orders allowed: {_bool(summary['live_orders_allowed'])}")
    print(f"Next safe action: {summary['next_safe_action']}")
    print("Safety: approval gate only; no broker/API/network/orders/secrets/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
