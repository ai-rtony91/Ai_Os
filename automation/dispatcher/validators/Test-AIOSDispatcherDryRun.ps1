[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message) | Out-Null
}

function Test-RequiredPath {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-Failure "Missing required path: $Path"
    }
}

$repoRoot = (Resolve-Path -LiteralPath ".").Path
if (-not (Test-Path -LiteralPath (Join-Path $repoRoot ".git"))) {
    Add-Failure "Validator must run from repo root."
}

Write-Host "AI_OS Dispatcher DRY_RUN Validator"
Write-Host "Repo root: $repoRoot"
Write-Host ""
Write-Host "Dispatcher folder status:"

$requiredFolders = @(
    "automation/dispatcher",
    "automation/dispatcher/packets",
    "automation/dispatcher/locks",
    "automation/dispatcher/approval_inbox",
    "automation/dispatcher/commit_packages",
    "automation/dispatcher/recovery",
    "automation/dispatcher/validators",
    "docs/AI_OS/dispatcher",
    "Reports/dispatcher"
)

foreach ($folder in $requiredFolders) {
    $exists = Test-Path -LiteralPath $folder
    Write-Host (" - {0}: {1}" -f $folder, $(if ($exists) { "FOUND" } else { "MISSING" }))
    if (-not $exists) {
        Add-Failure "Missing required folder: $folder"
    }
}

$requiredDocs = @(
    "automation/dispatcher/README.md",
    "automation/dispatcher/packets/README.md",
    "automation/dispatcher/locks/README.md",
    "automation/dispatcher/approval_inbox/README.md",
    "automation/dispatcher/commit_packages/README.md",
    "automation/dispatcher/recovery/README.md",
    "automation/dispatcher/validators/README.md",
    "docs/AI_OS/dispatcher/PHASE_15_3_DISPATCHER_CORE.md",
    "docs/AI_OS/dispatcher/DISPATCHER_PACKET_SCHEMA.md",
    "docs/AI_OS/dispatcher/DISPATCHER_LOCK_SCHEMA.md",
    "docs/AI_OS/dispatcher/DISPATCHER_APPROVAL_SCHEMA.md",
    "docs/AI_OS/dispatcher/DISPATCHER_COMMIT_PACKAGE_SCHEMA.md",
    "docs/AI_OS/dispatcher/DISPATCHER_RECOVERY_BOOTSTRAP.md",
    "docs/AI_OS/dispatcher/DISPATCHER_VALIDATOR_CHAIN.md",
    "docs/AI_OS/dispatcher/DISPATCHER_DASHBOARD_DATA_CONTRACT.md"
)

Write-Host ""
Write-Host "Required dispatcher documents:"
foreach ($doc in $requiredDocs) {
    Test-RequiredPath $doc
    Write-Host (" - {0}: {1}" -f $doc, $(if (Test-Path -LiteralPath $doc) { "FOUND" } else { "MISSING" }))
}

$requiredJson = @(
    "Reports/dispatcher/dispatcher_status.example.json",
    "Reports/dispatcher/dispatcher_recovery_state.example.json",
    "Reports/dispatcher/dispatcher_commit_package.example.json"
)

Write-Host ""
Write-Host "Required dispatcher report examples:"
foreach ($json in $requiredJson) {
    Test-RequiredPath $json
    Write-Host (" - {0}: {1}" -f $json, $(if (Test-Path -LiteralPath $json) { "FOUND" } else { "MISSING" }))
}

Write-Host ""
Write-Host "Parsing Reports/dispatcher JSON files:"
if (Test-Path -LiteralPath "Reports/dispatcher") {
    Get-ChildItem -LiteralPath "Reports/dispatcher" -Filter "*.json" -File | ForEach-Object {
        try {
            Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json | Out-Null
            Write-Host " - $($_.Name): PASS"
        }
        catch {
            Write-Host " - $($_.Name): FAIL"
            Add-Failure "JSON parse failed: $($_.FullName)"
        }
    }
}

Write-Host ""
Write-Host "Git status:"
& git status --short --branch
if ($LASTEXITCODE -ne 0) {
    Add-Failure "git status failed."
}

Write-Host ""
Write-Host "Git diff check:"
& git diff --check
if ($LASTEXITCODE -ne 0) {
    Add-Failure "git diff --check failed."
}

Write-Host ""
Write-Host "Blocked safety term scan:"
$blockedTerms = @(
    ("O" + "ANDA"),
    ("live" + " order"),
    ("real" + " order"),
    ("API" + " key"),
    ("broker" + " execution")
)

$scanRoots = @(
    "automation/dispatcher",
    "docs/AI_OS/dispatcher",
    "Reports/dispatcher"
)

foreach ($root in $scanRoots) {
    if (Test-Path -LiteralPath $root) {
        Get-ChildItem -LiteralPath $root -Recurse -File | ForEach-Object {
            $content = Get-Content -LiteralPath $_.FullName -Raw
            foreach ($term in $blockedTerms) {
                if ($content -match [regex]::Escape($term)) {
                    Add-Failure "Blocked term found in $($_.FullName): $term"
                }
            }
        }
    }
}

if ($failures.Count -eq 0) {
    Write-Host "Blocked safety term scan: PASS"
}
else {
    Write-Host "Blocked safety term scan: REVIEW_REQUIRED"
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "RESULT: PASS"
    exit 0
}

Write-Host "RESULT: FAIL"
foreach ($failure in $failures) {
    Write-Host " - $failure"
}
exit 1

