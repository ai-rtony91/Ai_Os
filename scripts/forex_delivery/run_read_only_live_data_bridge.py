"""Run the AIOS forex read-only live data bridge.

Default behavior is fixture/readiness fallback. Broker read-only mode requires
AIOS_FOREX_READONLY_LIVE_ENABLE=1, AIOS_FOREX_BROKER=oanda, and runtime
credential presence. Output and report content are sanitized.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.read_only_live_data_sanitizer import (  # noqa: E402
    SANITIZED_EVIDENCE_PATH,
    assert_no_forbidden_output,
)
from forex_delivery.read_only_live_data_bridge import (  # noqa: E402
    build_read_only_live_data_bridge_read_model,
    build_sanitized_report,
)


REPORT_PATH = REPO_ROOT / SANITIZED_EVIDENCE_PATH


def main(argv: list[str] | None = None) -> int:
    _ = argv
    try:
        model = build_read_only_live_data_bridge_read_model()
        assert_no_forbidden_output(model)
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(build_sanitized_report(model), encoding="utf-8")
        print(json.dumps(_cli_summary(model), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = {
            "schema": "AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_ERROR.v1",
            "status": "FAILED_SANITIZED",
            "error_type": type(exc).__name__,
            "secret_values_printed": False,
            "account_id_printed": False,
            "live_execution_allowed": False,
            "broker_write_calls_allowed": False,
            "order_placement_allowed": False,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


def _cli_summary(model: dict[str, object]) -> dict[str, object]:
    broker_state = dict(model.get("broker_state") or {})
    positions = dict(model.get("positions") or {})
    risk_pl = dict(model.get("risk_pl") or {})
    history = dict(model.get("trading_history") or {})
    readiness = dict(model.get("execution_readiness") or {})
    return {
        "schema": "AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_CLI_SUMMARY.v1",
        "source_type": model.get("source_type"),
        "source_label": model.get("source_label"),
        "freshness_utc": model.get("freshness_utc"),
        "stale_status": model.get("stale_status"),
        "read_only": True,
        "broker_reachable": broker_state.get("account_reachable"),
        "positions_reconciled": positions.get("positions_reconciled"),
        "pl_available": risk_pl.get("daily_pl_available"),
        "trading_history_available": history.get("trading_history_available"),
        "live_execution_allowed": False,
        "report_path": SANITIZED_EVIDENCE_PATH,
        "next_safe_action": readiness.get("next_safe_action"),
        "block_reason": model.get("block_reason"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
