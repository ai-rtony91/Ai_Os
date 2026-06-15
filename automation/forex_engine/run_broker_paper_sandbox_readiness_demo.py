from __future__ import annotations

from automation.forex_engine import broker_paper_sandbox_readiness


def main(_argv: list[str] | None = None) -> int:
    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness()
    blockers = list(result.get("blockers") or [])
    blocker_text = "none" if not blockers else "; ".join(blockers[:3])
    lines = [
        "AIOS Broker-Paper Sandbox Readiness Contract",
        f"Mode: {result['mode']}",
        f"Readiness: {result['readiness_status']}",
        f"Broker-paper contract ready: {str(result['broker_paper_sandbox_contract_ready']).lower()}",
        "Live ready: false",
        "Real order ready: false",
        "Broker integration active: false",
        "Credentials required now: false",
        "Protected gate required: true",
        f"Blockers: {blocker_text}",
        f"Next safe action: {result['next_safe_action']}",
        "Safety: no broker/API/network/orders/secrets/live execution.",
    ]
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
