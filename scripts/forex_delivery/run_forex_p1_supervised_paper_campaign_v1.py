#!/usr/bin/env python3
"""Operator-started entry point for the bounded P1 paper campaign."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_p1_supervised_paper_campaign_v1 import (
    CampaignPaths,
    run_campaign,
)
from automation.forex_engine.forex_p1_practice_paper_campaign_runtime_v1 import (
    completed_paper_records,
)
from automation.forex_engine.oanda_read_only_client import OandaReadOnlyClient

REPORTS = ROOT / "Reports" / "forex_delivery"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run up to 30 sequential PAPER evidence captures.")
    parser.add_argument("--owner-local-runtime", action="store_true")
    parser.add_argument("--cycles", type=int, default=30)
    parser.add_argument("--reviewer", default="Human Owner Anthony")
    parser.add_argument("--maximum-session-loss", type=float)
    parser.add_argument("--kill-switch-file", type=Path, default=ROOT / ".aios/runtime/forex/kill_switch.active")
    parser.add_argument("--risk-halt-file", type=Path, default=ROOT / ".aios/runtime/forex/risk_halt.active")
    parser.add_argument("--cancel-file", type=Path, default=ROOT / ".aios/runtime/forex/cancel_campaign.active")
    args = parser.parse_args()
    if not args.owner_local_runtime:
        print("RUNTIME_CREDENTIAL_OR_PRACTICE_DATA_REQUIRED")
        return 2
    token = os.environ.get("OANDA_API_TOKEN", "")
    account = os.environ.get("OANDA_ACCOUNT_ID", "")
    if not token or not account:
        print("RUNTIME_CREDENTIAL_OR_PRACTICE_DATA_REQUIRED")
        return 2
    client = OandaReadOnlyClient(
        api_token=token, account_id=account, environment="practice"
    )
    paths = CampaignPaths(
        candidate=REPORTS / ".p1_campaign_candidate.tmp",
        ledger=REPORTS / "AIOS_FOREX_P1_30_TRADE_CAMPAIGN_V1_LEDGER.json",
        replay_state=REPORTS / "AIOS_FOREX_P1_30_TRADE_CAMPAIGN_V1_REPLAY_STATE.json",
        replay_report=REPORTS / "AIOS_FOREX_P1_30_TRADE_CAMPAIGN_V1_REPLAY_REPORT.md",
        event_log=REPORTS / "AIOS_FOREX_P1_30_TRADE_CAMPAIGN_V1_EVENTS.jsonl",
        campaign_state=REPORTS / "AIOS_FOREX_P1_30_TRADE_CAMPAIGN_V1_STATE.json",
        campaign_report=REPORTS / "AIOS_FOREX_P1_30_TRADE_CAMPAIGN_V1_REPORT.md",
    )
    candidates = completed_paper_records(
        client,
        cycles=args.cycles,
        reviewer_identity=args.reviewer,
        runtime_path=ROOT / ".aios/runtime/forex_p1_supervised_paper_sessions/active.json",
        sleep=time.sleep,
        owner_cancelled=args.cancel_file.exists,
        kill_switch_active=args.kill_switch_file.exists,
        risk_halt_active=args.risk_halt_file.exists,
    )
    state = run_campaign(
        candidates, paths, repository_root=ROOT, output=sys.stdout,
        kill_switch_active=args.kill_switch_file.exists(),
        risk_halt_active=args.risk_halt_file.exists(),
        maximum_session_loss=args.maximum_session_loss,
    )
    print(f"CAMPAIGN_STOP_REASON: {state['stop_reason']}")
    return 0 if state["stop_reason"] in {
        "TARGET_REACHED", "OWNER_SESSION_CYCLE_LIMIT"
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
