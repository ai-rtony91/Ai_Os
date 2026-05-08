Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$cssRelativePath = "apps\dashboard\css\aios-static-preview.css"
$cssPath = Join-Path $repoRoot $cssRelativePath

$requiredClasses = @(
    "body.theme-terminal-green",
    "body.theme-cyan-command",
    "body.theme-amber-warning",
    "body.theme-high-contrast"
)

$requiredTokens = @(
    "--surface-page",
    "--text-primary",
    "--accent-primary",
    "--state-pass",
    "--state-warn",
    "--state-danger",
    "--shadow-panel-hover",
    "--grid-line-soft"
)

$suspiciousTerms = @(
    "api_key",
    "token",
    "password",
    "secret",
    "bearer",
    "private_key",
    "oanda",
    "broker",
    "deploy",
    "winget"
)

$errors = @()
$cssExists = Test-Path -LiteralPath $cssPath
$cssContent = ""

if (-not $cssExists) {
    $errors += "Missing CSS file: $cssRelativePath"
} else {
    $cssContent = Get-Content -LiteralPath $cssPath -Raw
}

if ($cssExists) {
    if ($cssContent -notmatch "(?m)^\s*:root\s*\{") {
        $errors += "Missing :root theme token block."
    }

    foreach ($className in $requiredClasses) {
        if ($cssContent -notmatch [regex]::Escape($className)) {
            $errors += "Missing theme class: $className"
        }
    }

    foreach ($token in $requiredTokens) {
        if ($cssContent -notmatch [regex]::Escape($token)) {
            $errors += "Missing semantic token: $token"
        }
    }

    foreach ($term in $suspiciousTerms) {
        if ($cssContent -match [regex]::Escape($term)) {
            $errors += "Suspicious execution term detected in CSS: $term"
        }
    }
}

$result = [pscustomobject]@{
    mode = "DRY_RUN"
    status = $(if ($errors.Count -eq 0) { "PASS" } else { "FAIL" })
    css_file = $cssRelativePath
    css_exists = $cssExists
    required_classes = $requiredClasses
    required_tokens = $requiredTokens
    errors = $errors
    safety = @{
        modifies_files = "NO"
        apis = "BLOCKED"
        secrets = "BLOCKED"
        installs = "BLOCKED"
        deployment = "BLOCKED"
        brokers = "BLOCKED"
        trading_execution = "BLOCKED"
        live_ai_execution = "BLOCKED"
    }
}

$result | ConvertTo-Json -Depth 5

if ($errors.Count -gt 0) {
    exit 1
}
