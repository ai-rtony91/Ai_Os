$ErrorActionPreference = "Stop"

function Invoke-GitLines {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>$null
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    if ($exitCode -ne 0) {
        return @()
    }

    return @($output)
}

function Get-RepoRoot {
    $root = @(Invoke-GitLines -Arguments @("rev-parse", "--show-toplevel"))
    if ($root.Count -eq 0 -or [string]::IsNullOrWhiteSpace([string]$root[0])) {
        return (Resolve-Path ".").Path
    }
    return ([string]$root[0]).Trim()
}

function Add-Failure {
    param([string]$Message)
    $script:Failures.Add($Message) | Out-Null
}

function Test-RequiredPath {
    param(
        [string]$Path,
        [string]$Description
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        Add-Failure "FAIL: Missing $Description at $Path"
    }
}

function Test-PowerShellParse {
    param([string]$Path)

    try {
        [scriptblock]::Create((Get-Content -LiteralPath $Path -Raw)) | Out-Null
    } catch {
        Add-Failure "FAIL: PowerShell parse failed for $Path - $($_.Exception.Message)"
    }
}

function Test-JsonParse {
    param([string]$Path)

    try {
        Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json | Out-Null
    } catch {
        Add-Failure "FAIL: JSON parse failed for $Path - $($_.Exception.Message)"
    }
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot
$Failures = [System.Collections.Generic.List[string]]::new()

$newScripts = @(
    "automation\telemetry\Invoke-AiOsWorkerProductionSnapshot.ps1",
    "automation\telemetry\Update-AiOsProductionReadout.ps1"
)

foreach ($script in $newScripts) {
    $path = Join-Path $repoRoot $script
    Test-RequiredPath -Path $path -Description "worker production script"
    if (Test-Path -LiteralPath $path) {
        Test-PowerShellParse -Path $path
    }
}

Test-RequiredPath -Path (Join-Path $repoRoot "Reports\telemetry") -Description "Reports telemetry folder"
Test-RequiredPath -Path (Join-Path $repoRoot "docs\AI_OS\telemetry") -Description "docs telemetry folder"

$mockDataFiles = @(
    "apps\dashboard\mock-data\worker-production-v1.example.json",
    "apps\dashboard\mock-data\daily-production-readout-v1.example.json"
)

foreach ($mockDataFile in $mockDataFiles) {
    $path = Join-Path $repoRoot $mockDataFile
    Test-RequiredPath -Path $path -Description "dashboard mock data"
    if (Test-Path -LiteralPath $path) {
        Test-JsonParse -Path $path
    }
}

$blockedTerms = @(
    "OA" + "NDA",
    "API_KEY",
    "SECRET",
    "TOKEN",
    "live order",
    "real order",
    "broker execution",
    "Register-ScheduledTask",
    "schtasks",
    "Start-Process codex"
)

foreach ($script in $newScripts) {
    $path = Join-Path $repoRoot $script
    if (-not (Test-Path -LiteralPath $path)) {
        continue
    }

    $content = Get-Content -LiteralPath $path -Raw
    foreach ($term in $blockedTerms) {
        if ($content -match [regex]::Escape($term)) {
            Add-Failure "FAIL: Blocked term detected in $script"
            break
        }
    }
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

Write-Host "PASS: AI_OS Worker Production Intelligence validation passed."
