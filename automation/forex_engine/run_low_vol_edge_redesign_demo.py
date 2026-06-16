from __future__ import annotations

from automation.forex_engine import low_vol_edge_redesign


def main(argv: list[str] | None = None) -> int:
    _ = argv
    result = low_vol_edge_redesign.apply_low_vol_edge_redesign()
    print("AIOS Forex Low-Vol Edge Redesign Demo")
    print("Mode: PAPER_ONLY")
    print(f"Original max degradation pct: {result['original_max_degradation_pct']}")
    print(f"OOS repair max degradation pct: {result['repaired_max_degradation_pct']}")
    print(f"Redesigned max degradation pct: {result['redesigned_max_degradation_pct']}")
    print(f"Low-vol action: {result['low_vol_policy_action']}")
    print(f"Rejected low-vol intents: {result['rejected_low_vol_intents']}")
    print(f"Allowed low-vol intents: {result['low_vol_trade_allowed_count']}")
    print(f"Classification: {result['classification']}")
    print("Broker-paper contract ready: false")
    print("Live ready: false")
    print("Security gate required before broker-paper: true")
    print(f"Required security packet: {result['required_security_packet']}")
    print(f"Next safe action: {result['next_safe_action']}")
    print("Safety: no broker/API/network/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
