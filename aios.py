#!/usr/bin/env python3
"""Root command for the AI_OS master runtime."""
import argparse
import json

from automation.orchestration.aios_master_runtime_v1 import ResumeRejected, run


def main() -> int:
    parser = argparse.ArgumentParser(prog="aios.py")
    parser.add_argument("command", choices=("status", "plan", "run", "resume", "validate"))
    args = parser.parse_args()
    try:
        result = run(command=args.command)
    except ResumeRejected as error:
        print(json.dumps({"schema": "AIOS_MASTER_RUNTIME_ERROR.v1", "status": "BLOCKED", "reason_codes": str(error).split(",")}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("validation", {}).get("status", "PASS") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
