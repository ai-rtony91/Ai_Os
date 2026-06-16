from __future__ import annotations

from automation.forex_engine import broker_paper_presecurity_gate


def main(argv: list[str] | None = None) -> int:
    _ = argv
    result = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate()
    print("AIOS Broker-Paper Presecurity Gate Demo")
    print("Mode: PAPER_ONLY_CONTRACT")
    print(f"Classification: {result['classification']}")
    print("Credential boundary required: true")
    print("Env secret read allowed: false")
    print("Broker SDK allowed: false")
    print("Network/API allowed: false")
    print("Webhook allowed: false")
    print("Broker-paper orders allowed: false")
    print("Live orders allowed: false")
    print("Kill switch required: true")
    print("Max loss guard required: true")
    print("Daily stop required: true")
    print("Audit log required: true")
    print("Manual approval required: true")
    print(f"Next safe action: {result['next_safe_action']}")
    print("Safety: no broker/API/network/orders/secrets/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
