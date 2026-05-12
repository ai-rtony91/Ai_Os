$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

$botModule = "trading_lab.bot.paper_trading_bot"
$fixture = Join-Path $repoRoot "apps/trading_lab/trading_lab/fixtures/paper_signal_api/PAPER_SIGNAL_API_VALID_001.json"

python -m $botModule --fixture $fixture --validation-time "2026-05-12T00:05:00Z" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Paper trading bot runner failed."
}

$createdFiles = @(
    "apps/trading_lab/trading_lab/bot/paper_trading_bot.py",
    "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_STATUS_001.json",
    "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_LEDGER_001.json",
    "apps/dashboard/mock-data/paper-trading-bot-status.example.json",
    "docs/AI_OS/trading_laboratory/phase_24/PHASE_24_PAPER_TRADING_BOT_PROTOTYPE.md"
)

foreach ($file in $createdFiles) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required bot file: $file"
    }
}

$jsonFiles = @(
    "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_STATUS_001.json",
    "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_LEDGER_001.json",
    "apps/dashboard/mock-data/paper-trading-bot-status.example.json"
)

foreach ($file in $jsonFiles) {
    Get-Content -LiteralPath (Join-Path $repoRoot $file) -Raw | ConvertFrom-Json | Out-Null
}

$status = Get-Content -LiteralPath (Join-Path $repoRoot "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_STATUS_001.json") -Raw | ConvertFrom-Json
$ledger = Get-Content -LiteralPath (Join-Path $repoRoot "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_LEDGER_001.json") -Raw | ConvertFrom-Json
$dashboard = Get-Content -LiteralPath (Join-Path $repoRoot "apps/dashboard/mock-data/paper-trading-bot-status.example.json") -Raw | ConvertFrom-Json

if ($status.decision -notin @("ACCEPT", "REJECT", "REVIEW")) {
    throw "Bot decision must be ACCEPT, REJECT, or REVIEW."
}

if ($status.decision -ne "ACCEPT") {
    throw "Valid sample signal should produce ACCEPT in deterministic dry run."
}

if ($ledger.paper_route_preview.paper_route_status -ne "PAPER_PREVIEW_ONLY") {
    throw "Paper route preview must remain PAPER_PREVIEW_ONLY."
}

if ($ledger.paper_result.paper_result_status -ne "PAPER_RESULT_PREVIEW") {
    throw "Paper result must be PAPER_RESULT_PREVIEW for accepted sample."
}

if ($dashboard.bot_status_id -ne $status.bot_status_id) {
    throw "Dashboard bot status fixture does not mirror bot status output."
}

$blockedStatusFields = @(
    "live_execution_status",
    "broker_status",
    "oanda_status",
    "api_key_status",
    "secrets_status",
    "real_webhook_status",
    "real_order_status"
)

foreach ($field in $blockedStatusFields) {
    if ($status.$field -ne "BLOCKED") {
        throw "Status $field must remain BLOCKED."
    }
    if ($ledger.$field -ne "BLOCKED") {
        throw "Ledger $field must remain BLOCKED."
    }
}

foreach ($field in @("live_execution", "broker", "oanda", "webull", "api_keys", "secrets", "real_webhooks", "real_orders")) {
    if ($ledger.$field -ne "BLOCKED") {
        throw "Ledger $field must remain BLOCKED."
    }
}

$scanText = Get-Content -LiteralPath (Join-Path $repoRoot "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_STATUS_001.json") -Raw
$scanText += Get-Content -LiteralPath (Join-Path $repoRoot "apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_LEDGER_001.json") -Raw
$scanText += Get-Content -LiteralPath (Join-Path $repoRoot "apps/dashboard/mock-data/paper-trading-bot-status.example.json") -Raw

if ($scanText -match '"(live_execution|broker|oanda|webull|real_order|real_webhook).*"\s*:\s*"ENABLED"') {
    throw "Safety scan found ENABLED live/broker/order/webhook field."
}

if ($scanText -match '(api[_-]?key|secret)"\s*:\s*"(?!BLOCKED)') {
    throw "Safety scan found possible secret/API value."
}

Write-Host "PASS: AI_OS paper trading bot prototype produced ACCEPT, paper route preview, paper result, dashboard status, and blocked safety fields."
