$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python or add it to PATH, then rerun this runtime check."
}

$check = @'
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from trading_lab.ingest.paper_signal_api import process_paper_signal

repo = Path.cwd()
ledger_path = repo / "apps" / "trading_lab" / "trading_lab" / "results" / "bot" / "PAPER_TRADING_BOT_LEDGER_001.json"
fixture_path = repo / "apps" / "trading_lab" / "trading_lab" / "fixtures" / "paper_signal_api" / "PAPER_SIGNAL_API_VALID_001.json"
url = "http://127.0.0.1:8765/paper-signal"

failures = []

payload = json.loads(fixture_path.read_text(encoding="utf-8"))
payload["alert_time"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
payload["source"] = "LOCAL_RUNTIME_HEALTH_CHECK"
body = json.dumps(payload).encode("utf-8")
request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")

try:
    with urlopen(request, timeout=10) as response:
        server_result = json.loads(response.read().decode("utf-8"))
except URLError as exc:
    failures.append(f"server reachable: FAIL ({exc})")
    server_result = {}
else:
    failures.append("server reachable: PASS")

paper_bot = server_result.get("paper_bot", {}) if isinstance(server_result, dict) else {}
if paper_bot.get("live_execution_status") == "BLOCKED":
    failures.append("server live execution blocked: PASS")
else:
    failures.append("server live execution blocked: FAIL")

try:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
except OSError as exc:
    failures.append(f"ledger readable: FAIL ({exc})")
    ledger = {}
else:
    failures.append("ledger readable: PASS")

if ledger.get("live_execution") == "BLOCKED" and ledger.get("real_orders") == "BLOCKED":
    failures.append("ledger live/order fields blocked: PASS")
else:
    failures.append("ledger live/order fields blocked: FAIL")

base = {
    "symbol": "EUR_USD",
    "timeframe": "M15",
    "direction": "LONG_REVIEW",
    "strategy_id": "PAPER_EMA_VWAP_PULLBACK_001",
    "confidence": 0.82,
    "source": "LOCAL_RUNTIME_HEALTH_CHECK",
}
now = datetime.now(UTC).replace(microsecond=0)
stale_payload = dict(base, alert_time=(now - timedelta(seconds=901)).isoformat().replace("+00:00", "Z"))
skew_payload = dict(base, alert_time=(now + timedelta(seconds=121)).isoformat().replace("+00:00", "Z"))
stale_result = process_paper_signal(stale_payload, validation_time=now, write_outputs=False)["validation_result"]
skew_result = process_paper_signal(skew_payload, validation_time=now, write_outputs=False)["validation_result"]

if stale_result.get("stale_signal_status") == "STALE_SIGNAL_REJECTED":
    failures.append("stale rejection: PASS")
else:
    failures.append("stale rejection: FAIL")

if skew_result.get("clock_skew_status") == "CLOCK_SKEW_DETECTED":
    failures.append("clock skew rejection: PASS")
else:
    failures.append("clock skew rejection: FAIL")

print("AI_OS Paper Runtime Health Check")
for line in failures:
    print(line)

if any(line.endswith("FAIL") or ": FAIL (" in line for line in failures):
    raise SystemExit(1)

print("Summary: PASS - local paper runtime is reachable, readable, and blocked.")
'@

$check | python -
if ($LASTEXITCODE -ne 0) {
    throw "AI_OS paper runtime health check failed."
}
