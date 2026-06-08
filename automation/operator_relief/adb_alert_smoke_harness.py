"""Smoke harness for the gated Operator Relief ADB alert path."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .adb_escalation import MODE_APPLY_ADB_ALERT, MODE_DRY_RUN, CommandRunner, plan_adb_escalation


@dataclass(frozen=True)
class AdbAlertSmokeReport:
    status: str
    mode: str
    escalation_report: dict[str, Any]
    network_listener_started: bool
    port_opened: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_adb_alert_smoke_harness(
    mode: str = MODE_DRY_RUN,
    command_runner: CommandRunner | None = None,
) -> AdbAlertSmokeReport:
    if mode not in {MODE_DRY_RUN, MODE_APPLY_ADB_ALERT}:
        raise ValueError("Mode must be DRY_RUN or APPLY_ADB_ALERT.")

    escalation = plan_adb_escalation("blocked", mode=mode, command_runner=command_runner).to_dict()
    return AdbAlertSmokeReport(
        status="ADB_SMOKE_APPLY_COMPLETE" if escalation["executable"] else "ADB_SMOKE_DRY_RUN",
        mode=mode,
        escalation_report=escalation,
        network_listener_started=False,
        port_opened=False,
        executable=escalation["executable"] is True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Operator Relief ADB alert smoke harness.")
    parser.add_argument("--mode", default=MODE_DRY_RUN, choices=[MODE_DRY_RUN, MODE_APPLY_ADB_ALERT])
    args = parser.parse_args(argv)
    report = run_adb_alert_smoke_harness(mode=args.mode)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.status == "ADB_SMOKE_DRY_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
