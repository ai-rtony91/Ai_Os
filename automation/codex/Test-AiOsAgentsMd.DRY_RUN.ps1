$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $root = & git rev-parse --show-toplevel 2>$null
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    if ($exitCode -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        return (Resolve-Path ".").Path
    }

    return ([string]$root).Trim()
}

function Add-Failure {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $script:Failures.Add($Message) | Out-Null
}

function Require-Text {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,
        [Parameter(Mandatory = $true)]
        [string]$Needle
    )

    if ($Content -notlike "*$Needle*") {
        Add-Failure "FAIL: AGENTS.md missing required text: $Needle"
    }
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$Failures = [System.Collections.Generic.List[string]]::new()
$agentsPath = Join-Path $repoRoot "AGENTS.md"
$docPath = Join-Path $repoRoot "docs\AI_OS\codex\PHASE_15_2_CODEX_PERSISTENT_INSTRUCTION_LAYER.md"

if (-not (Test-Path -LiteralPath $agentsPath)) {
    Add-Failure "FAIL: AGENTS.md does not exist."
} else {
    $agentsContent = Get-Content -LiteralPath $agentsPath -Raw

    Require-Text -Content $agentsContent -Needle "AI_OS"
    Require-Text -Content $agentsContent -Needle "Big Pack Mode"
    Require-Text -Content $agentsContent -Needle "DRY_RUN"
    Require-Text -Content $agentsContent -Needle "APPLY"
    Require-Text -Content $agentsContent -Needle "Never use git add ."
    Require-Text -Content $agentsContent -Needle "No live trading"
    Require-Text -Content $agentsContent -Needle "No API keys"
    Require-Text -Content $agentsContent -Needle "No real orders"
    Require-Text -Content $agentsContent -Needle "Simple user mode"
    Require-Text -Content $agentsContent -Needle "Telemetry"

    $blockedEnablementPatterns = @(
        '^\s*enable\s+live\s+trading',
        '^\s*allow\s+live\s+trading',
        'live\s+broker\s+execution\s+enabled',
        'connect\s+to\s+live\s+broker',
        'place\s+real\s+orders',
        'send\s+real\s+orders',
        'execute\s+real\s+webhook'
    )

    foreach ($pattern in $blockedEnablementPatterns) {
        if ($agentsContent -match $pattern) {
            Add-Failure "FAIL: AGENTS.md contains blocked live broker enablement language: $pattern"
        }
    }
}

if (-not (Test-Path -LiteralPath $docPath)) {
    Add-Failure "FAIL: Phase 15.2 Codex instruction documentation is missing."
}

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$diffCheckOutput = & git diff --check 2>&1
$diffCheckExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

if ($diffCheckOutput) {
    $diffCheckOutput | ForEach-Object { Write-Host $_ }
}

if ($diffCheckExitCode -ne 0) {
    Add-Failure "FAIL: git diff --check reported whitespace or conflict-marker problems."
}

if ($Failures.Count -gt 0) {
    foreach ($failure in $Failures) {
        Write-Host $failure
    }
    exit 1
}

Write-Host "PASS: AI_OS AGENTS.md validation passed."
