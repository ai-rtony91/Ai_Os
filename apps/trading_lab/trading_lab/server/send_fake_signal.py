from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


DEFAULT_URL = "http://127.0.0.1:8765/paper-signal"
FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "paper_signal_api"
    / "PAPER_SIGNAL_API_VALID_001.json"
)


def load_payload() -> dict[str, object]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["alert_time"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload["source"] = "LOCAL_FAKE_SIGNAL"
    return payload


def post_signal(url: str = DEFAULT_URL) -> dict[str, object]:
    body = json.dumps(load_payload()).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    try:
        result = post_signal()
    except URLError as exc:
        print(f"FAIL: Local paper server is not reachable at {DEFAULT_URL}. Start it first.")
        print(f"Detail: {exc}")
        return 1

    paper_bot = result.get("paper_bot", {})
    decision = paper_bot.get("decision", "UNKNOWN") if isinstance(paper_bot, dict) else "UNKNOWN"
    live_status = paper_bot.get("live_execution_status", "UNKNOWN") if isinstance(paper_bot, dict) else "UNKNOWN"
    visible = paper_bot.get("visible_status_output", "No visible status returned.") if isinstance(paper_bot, dict) else "No visible status returned."

    print("AI_OS Fake Paper Signal Result")
    print(f"Decision: {decision}")
    print(f"Live Trading: {live_status}")
    print(f"Status: {visible}")

    if live_status != "BLOCKED":
        print("FAIL: Live trading did not remain BLOCKED.")
        return 1
    if decision not in {"ACCEPT", "REJECT", "REVIEW"}:
        print("FAIL: Paper bot did not return a valid paper decision.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
