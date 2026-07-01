from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_runtime_calendar_status_and_maintenance_mode_v1 import (  # noqa: E402
    evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1,
)


def _base_payload() -> dict:
    return {
        "runtime_supervision_requested": True,
        "runtime_calendar": {
            "timezone": "America/New_York",
            "forex_week_window_defined": True,
            "market_open": True,
            "close_approaching": False,
            "reopen_approaching": False,
            "weekend_closed": False,
            "holiday_degraded": False,
            "low_liquidity_degraded": False,
            "broker_calendar_source": "DECLARED_OWNER_REVIEWED_CALENDAR",
            "runtime_uses_declared_calendar_only": True,
            "no_live_execution_authorized_by_calendar": True,
        },
        "runtime_policy": {
            "ai_runtime_supervision_continuous_when_host_available": True,
            "market_calendar_controls_trade_windows": True,
            "maintenance_windows_control_non_trade_work": True,
            "night_optimization_allowed": True,
            "weekend_heavy_maintenance_allowed": True,
            "post_close_maintenance_allowed": True,
            "pre_open_preparation_allowed": True,
            "close_protection_required": True,
            "no_scheduler_created": True,
            "no_daemon_created": True,
            "no_runtime_trade_without_owner_gate": True,
            "no_unlimited_autonomous_trading": True,
        },
        "cadence_interpretation": {
            "daily_weekly_monthly_are_review_cadence": True,
            "yearly_means_vacation_mode_maturity": True,
            "yearly_profit_guarantee": False,
            "daily_profit_guarantee": False,
            "weekly_profit_guarantee": False,
            "monthly_profit_guarantee": False,
            "fixed_return_promised": False,
        },
    }


def _sample(name: str, **calendar_updates) -> dict:
    payload = _base_payload()
    payload["sample_name"] = name
    payload["runtime_calendar"].update(calendar_updates)
    return payload


def main() -> None:
    samples = [
        _sample("market open active supervision"),
        _sample("close approaching protection", close_approaching=True),
        _sample("market closed maintenance", market_open=False),
        _sample("reopen approaching prep", market_open=False, reopen_approaching=True),
        _sample("weekend heavy maintenance", market_open=False, weekend_closed=True),
        _sample("holiday degraded maintenance", holiday_degraded=True),
        _sample("low liquidity degraded maintenance", low_liquidity_degraded=True),
        _sample(
            "Vacation Mode owner toggle readiness",
            vacation_mode_year_round_runtime_review_requested=True,
        ),
    ]
    summaries = []
    for sample in samples:
        result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(sample)
        summaries.append(
            {
                "sample_name": sample["sample_name"],
                "status": result["status"],
                "current_runtime_posture": result["current_runtime_posture"],
                "primary_job_lane": result["primary_job_lane"],
                "next_best_packet": result["next_best_packet"],
                "job_ids": [job["job_id"] for job in result["job_queue"]],
            }
        )
    print(json.dumps(summaries, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
