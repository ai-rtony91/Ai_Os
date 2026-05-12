$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

$requiredFiles = @(
    "docs\AI_OS\trading_laboratory\tradingview_traderspost_bridge\STAGE_14_6_TV_TP_PAPER_BRIDGE.md",
    "docs\AI_OS\trading_laboratory\tradingview_traderspost_bridge\TV_ALERT_TEMPLATE_GUIDE.md",
    "docs\AI_OS\trading_laboratory\tradingview_traderspost_bridge\TRADERSPOST_HANDOFF_TEMPLATE_GUIDE.md",
    "docs\AI_OS\trading_laboratory\tradingview_traderspost_bridge\TV_TP_SAFETY_RULES.md",
    "docs\AI_OS\trading_laboratory\tradingview_traderspost_bridge\TV_TP_FILE_INDEX.md",
    "apps\trading_lab\trading_lab\tv_tp_bridge\__init__.py",
    "apps\trading_lab\trading_lab\tv_tp_bridge\tv_alert_payload.py",
    "apps\trading_lab\trading_lab\tv_tp_bridge\aios_signal_intake.py",
    "apps\trading_lab\trading_lab\tv_tp_bridge\aios_paper_validator.py",
    "apps\trading_lab\trading_lab\tv_tp_bridge\traderspost_handoff_payload.py",
    "apps\trading_lab\trading_lab\tv_tp_bridge\run_tv_tp_bridge_demo.py",
    "apps\trading_lab\mock-data\tv_tp_bridge\tradingview_alert.example.json",
    "apps\trading_lab\mock-data\tv_tp_bridge\aios_intake_result.example.json",
    "apps\trading_lab\mock-data\tv_tp_bridge\aios_paper_validation_result.example.json",
    "apps\trading_lab\mock-data\tv_tp_bridge\traderspost_handoff_blocked.example.json"
)

$jsonFiles = $requiredFiles | Where-Object { $_.EndsWith(".json") }
$scanFiles = $requiredFiles
$failures = New-Object System.Collections.Generic.List[string]

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        $failures.Add("Missing required file: $file")
    }
}

foreach ($file in $jsonFiles) {
    if (Test-Path -LiteralPath $file) {
        try {
            Get-Content -LiteralPath $file -Raw | ConvertFrom-Json | Out-Null
        } catch {
            $failures.Add("Invalid JSON: $file ($($_.Exception.Message))")
        }
    }
}

$blockedTerms = @(
    ("api" + "_" + "key"),
    ("sec" + "ret"),
    ("broker" + "_" + "execute"),
    ("live" + "_" + "order"),
    ("oanda" + " token"),
    ("real" + "_" + "webhook" + "_" + "url"),
    ("traderspost" + "_" + "webhook" + "_" + "url")
)

foreach ($file in $scanFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        continue
    }
    $content = Get-Content -LiteralPath $file -Raw
    foreach ($term in $blockedTerms) {
        if ($content.IndexOf($term, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $failures.Add("Blocked term found in ${file}: ${term}")
        }
    }
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $failures.Add("Python was not found on PATH.")
} else {
    $env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"
    python "apps\trading_lab\trading_lab\tv_tp_bridge\run_tv_tp_bridge_demo.py"
    if ($LASTEXITCODE -ne 0) {
        $failures.Add("Python demo failed with exit code $LASTEXITCODE.")
    }
}

if ($failures.Count -gt 0) {
    Write-Host "AI_OS TV/TP Paper Bridge Validation: FAIL"
    foreach ($failure in $failures) {
        Write-Host "- $failure"
    }
    exit 1
}

Write-Host "AI_OS TV/TP Paper Bridge Validation: PASS"
Write-Host "Required files: PASS"
Write-Host "JSON parse: PASS"
Write-Host "Python demo: PASS"
Write-Host "Unsafe term scan: PASS"
Write-Host "Safety: paper-only; webhook not sent; broker not connected; live execution blocked."
