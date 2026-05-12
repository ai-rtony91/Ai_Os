$ErrorActionPreference = "Stop"

function Fail {
    param([string]$Message)
    Write-Host "FAIL: $Message"
    exit 1
}

$repoRoot = (Get-Location).Path

$requiredFiles = @(
    "docs/AI_OS/trading_laboratory/phase_14_8/PHASE_14_8_PAPER_ROUTE_EVIDENCE_CONSOLIDATION.md",
    "docs/AI_OS/trading_laboratory/phase_14_8/PAPER_ROUTE_EVIDENCE_001.json",
    "docs/AI_OS/trading_laboratory/phase_14_8/PAPER_ROUTE_SAMPLE_RUN_001.json",
    "docs/AI_OS/trading_laboratory/phase_14_8/PAPER_ROUTE_EVIDENCE_README.md"
)

foreach ($relativePath in $requiredFiles) {
    $path = Join-Path $repoRoot $relativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Fail "Missing required file: $relativePath"
    }
}

$markdownPath = Join-Path $repoRoot "docs/AI_OS/trading_laboratory/phase_14_8/PHASE_14_8_PAPER_ROUTE_EVIDENCE_CONSOLIDATION.md"
$markdownText = Get-Content -LiteralPath $markdownPath -Raw
$requiredMarkdownTerms = @(
    "paper-only",
    "Live execution is BLOCKED",
    "OANDA",
    "TradersPost-style",
    "TradingView-style"
)

foreach ($term in $requiredMarkdownTerms) {
    if ($markdownText -notlike "*$term*") {
        Fail "Markdown consolidation file missing required text: $term"
    }
}

$jsonFiles = @(
    "docs/AI_OS/trading_laboratory/phase_14_8/PAPER_ROUTE_EVIDENCE_001.json",
    "docs/AI_OS/trading_laboratory/phase_14_8/PAPER_ROUTE_SAMPLE_RUN_001.json"
)

foreach ($relativePath in $jsonFiles) {
    $path = Join-Path $repoRoot $relativePath
    $jsonText = Get-Content -LiteralPath $path -Raw

    try {
        $json = $jsonText | ConvertFrom-Json
    }
    catch {
        Fail "Invalid JSON in $relativePath"
    }

    if ($json.live_execution_status -ne "BLOCKED") {
        Fail "$relativePath live_execution_status must be BLOCKED"
    }
    if ($json.broker_status -ne "BLOCKED") {
        Fail "$relativePath broker_status must be BLOCKED"
    }
    if ($json.oanda_status -ne "BLOCKED") {
        Fail "$relativePath oanda_status must be BLOCKED"
    }
    if ($json.real_order_status -ne "BLOCKED") {
        Fail "$relativePath real_order_status must be BLOCKED"
    }

    $scanText = $jsonText
    $scanText = [regex]::Replace($scanText, '"api_key_status"\s*:\s*"BLOCKED"', "", "IgnoreCase")
    $scanText = [regex]::Replace($scanText, '"API key storage"', "", "IgnoreCase")
    $scanText = [regex]::Replace($scanText, '"secret storage"', "", "IgnoreCase")

    $forbiddenTerms = @(
        "api_key",
        "secret",
        "password",
        "token",
        "account_id"
    )

    foreach ($term in $forbiddenTerms) {
        if ($scanText -match [regex]::Escape($term)) {
            Fail "$relativePath contains forbidden term: $term"
        }
    }
}

Write-Host "PASS: Phase 14.8 paper route evidence consolidation DRY_RUN validation passed."
Write-Host "Paper-only route evidence is present."
Write-Host "Live execution, broker execution, OANDA, real orders, secrets, and internet calls remain BLOCKED."
