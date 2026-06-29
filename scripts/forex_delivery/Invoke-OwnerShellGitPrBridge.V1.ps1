param(
    [switch] $DryRun,
    [switch] $NoMerge,
    [string] $BranchPrefix = "owner/forex-promotion-pipeline-v1"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$scriptStartTime = Get-Date -Format o
$repoRoot = "C:\Dev\Ai.Os"
$ownerBridgeReport = "Reports/forex_delivery/AIOS_OWNER_SHELL_GIT_PR_BRIDGE_V1_REPORT.md"

$allowedBridgeArtifacts = @(
    "automation/forex_engine/forex_promotion_pipeline_v1.py",
    "tests/forex_engine/test_forex_promotion_pipeline_v1.py",
    "scripts/forex_delivery/Invoke-ForexPromotionPipeline.V1.ps1",
    "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_CHECKPOINT.md",
    "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_OWNER_APPROVAL_CARD.md",
    "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_NEXT_CODEX_PACKET_V1.md",
    "Reports/forex_delivery/AIOS_ENVIRONMENT_DOCTOR_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_ENVIRONMENT_DOCTOR_V2_WINPS51_ONLY_REPORT.md",
    $ownerBridgeReport,
    "scripts/forex_delivery/Invoke-OwnerShellGitPrBridge.V1.ps1"
)

$status = [ordered]@{
    OWNER_BRIDGE_STARTED = $scriptStartTime
    REPO_OK = "PENDING"
    DIRTY_SCOPE_OK = "PENDING"
    GIT_ADD_OK = "PENDING"
    BRANCH_CREATED = "PENDING"
    FILES_STAGED = "PENDING"
    COMMIT_CREATED = "PENDING"
    PUSH_OK = "PENDING"
    PR_URL = "PENDING"
    CHECKS_OK = "PENDING"
    MERGE_OK = "PENDING"
    MAIN_SYNC_OK = "PENDING"
    OWNER_BRIDGE_STOP_REASON = "PENDING"
}

function Get-GitDirtyPaths {
    $statusLines = git status --short
    $paths = @()

    foreach ($line in $statusLines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        if ($line.Length -lt 4) {
            continue
        }

        $path = $line.Substring(3).Trim()
        if ($path -like "*->*") {
            $segments = $path -split "\s*->\s*", 2
            $path = $segments[-1].Trim()
        }

        if ([string]::IsNullOrWhiteSpace($path)) {
            continue
        }

        if ($path -like "*/") {
            continue
        }

        $paths += $path
    }

    return $paths
}

function Format-Status([string]$label, [string]$value) {
    Write-Output ("{0}:{1}" -f $label, $value)
}

function Print-Status([hashtable]$statusTable) {
    foreach ($label in $statusTable.Keys) {
        Format-Status $label $statusTable[$label]
    }
}

function Ensure-PathExists([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "MISSING_ARTIFACT:$path"
    }
}

function Ensure-AllowedScope([string[]]$dirtyPaths) {
    $invalid = @()

    foreach ($path in $dirtyPaths) {
        if ($allowedBridgeArtifacts -contains $path) {
            continue
        }

        $invalid += $path
    }

    if ($invalid.Count -gt 0) {
        throw "UNKNOWN_DIRTY_FILES:$($invalid -join ', ')"
    }
}

try {
    Format-Status "OWNER_BRIDGE_STARTED" $scriptStartTime

    Set-Location -LiteralPath $repoRoot
    if ((Resolve-Path .).Path -ne (Resolve-Path $repoRoot).Path) {
        throw "REPO_PATH_MISMATCH"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot ".git"))) {
        throw "NOT_A_GIT_REPO"
    }

    foreach ($artifact in $allowedBridgeArtifacts) {
        Ensure-PathExists $artifact
    }
    Ensure-PathExists $ownerBridgeReport
    $status.REPO_OK = "OK"

    $dirtyPaths = Get-GitDirtyPaths
    Ensure-AllowedScope $dirtyPaths
    $status.DIRTY_SCOPE_OK = "OK"

    if ($DryRun) {
        $status.GIT_ADD_OK = "DRY_RUN"
        $status.BRANCH_CREATED = "DRY_RUN"
        $status.FILES_STAGED = "DRY_RUN"
        $status.COMMIT_CREATED = "DRY_RUN"
        $status.PUSH_OK = "DRY_RUN"
        $status.PR_URL = "DRY_RUN"
        $status.CHECKS_OK = "DRY_RUN"
        $status.MERGE_OK = if ($NoMerge) { "NO_MERGE_DRY_RUN" } else { "DRY_RUN" }
        $status.MAIN_SYNC_OK = if ($NoMerge) { "NO_MERGE_DRY_RUN" } else { "DRY_RUN" }
        $status.OWNER_BRIDGE_STOP_REASON = "DRY_RUN_COMPLETE"
        Print-Status $status
        return
    }

    $ghStatus = gh auth status --hostname github.com 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "GH_AUTH_FAILED"
    }

    $repoStatus = gh repo view --json nameWithOwner 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "GITHUB_UNREACHABLE"
    }

    git add -- $allowedBridgeArtifacts
    if ($LASTEXITCODE -ne 0) {
        throw "GIT_ADD_FAILED"
    }

    $stagedPaths = git diff --cached --name-only
    if (-not $stagedPaths -or $stagedPaths.Count -eq 0) {
        throw "NO_FILES_STAGED"
    }

    foreach ($path in $stagedPaths) {
        if ($allowedBridgeArtifacts -notcontains $path) {
            throw "STAGED_SCOPE_VIOLATION:$path"
        }
    }

    $status.GIT_ADD_OK = "OK"
    $status.FILES_STAGED = ($stagedPaths -join ";")

    $branchSuffix = Get-Date -Format "yyyyMMdd-HHmmss"
    $branchName = "$BranchPrefix-$branchSuffix"
    git checkout -B $branchName
    if ($LASTEXITCODE -ne 0) {
        throw "BRANCH_CREATE_FAILED"
    }

    $status.BRANCH_CREATED = $branchName

    $commitMessage = "chore(forex): promote pipeline artifacts for owner publish bridge"
    git commit -m $commitMessage
    if ($LASTEXITCODE -ne 0) {
        throw "COMMIT_FAILED"
    }

    $status.COMMIT_CREATED = (git rev-parse --short HEAD).Trim()

    git push -u origin $branchName
    if ($LASTEXITCODE -ne 0) {
        throw "PUSH_FAILED"
    }

    $status.PUSH_OK = "OK"

    $prTitle = "chore(forex): promote pipeline artifacts from owner shell bridge"
    $prBody = "Publish pipeline artifacts for owner-controlled PR workflow from a restricted shell bridge."
    $prCreateOutput = gh pr create --title $prTitle --body $prBody --base "main" --head $branchName 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "PR_CREATE_FAILED"
    }

    $prUrl = ($prCreateOutput | Select-String -Pattern "https://github.com/.*/pull/\d+" -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { $_.Value } | Select-Object -First 1)
    if (-not $prUrl) {
        throw "PR_URL_MISSING"
    }

    $status.PR_URL = $prUrl

    gh pr checks --watch $prUrl
    if ($LASTEXITCODE -ne 0) {
        throw "PR_CHECKS_FAILED"
    }

    $prStateJson = gh pr view $prUrl --json checksState,mergeStateStatus
    if ($LASTEXITCODE -ne 0) {
        throw "PR_VIEW_FAILED"
    }

    $prState = $prStateJson | ConvertFrom-Json
    if ($prState.checksState -ne "SUCCESS") {
        throw "PR_CHECKS_NOT_SUCCESS"
    }

    if ($prState.mergeStateStatus -ne "CLEAN") {
        throw "MERGE_STATE_NOT_CLEAN:$($prState.mergeStateStatus)"
    }

    $status.CHECKS_OK = "OK"

    if ($NoMerge) {
        $status.MERGE_OK = "NO_MERGE"
        $status.MAIN_SYNC_OK = "NO_MERGE"
        $status.OWNER_BRIDGE_STOP_REASON = "READY_FOR_OWNER_MERGE"
        Print-Status $status
        return
    }

    gh pr merge --squash $prUrl
    if ($LASTEXITCODE -ne 0) {
        throw "PR_MERGE_FAILED"
    }

    $status.MERGE_OK = "OK"

    git checkout main
    if ($LASTEXITCODE -ne 0) {
        throw "CHECKOUT_MAIN_FAILED"
    }

    git fetch origin
    if ($LASTEXITCODE -ne 0) {
        throw "GIT_FETCH_FAILED"
    }

    git pull --ff-only origin main
    if ($LASTEXITCODE -ne 0) {
        throw "MAIN_PULL_FAILED"
    }

    if ((git status --short)) {
        throw "DIRTY_SCOPE_AFTER_SYNC"
    }

    $status.MAIN_SYNC_OK = "OK"
    $status.OWNER_BRIDGE_STOP_REASON = "COMPLETED"
    Print-Status $status
}
catch {
    $status.OWNER_BRIDGE_STOP_REASON = $_.Exception.Message

    if ($status.REPO_OK -eq "PENDING") {
        $status.REPO_OK = "FAILED"
    }
    if ($status.DIRTY_SCOPE_OK -eq "PENDING") {
        $status.DIRTY_SCOPE_OK = "FAILED"
    }
    if ($status.GIT_ADD_OK -eq "PENDING") {
        $status.GIT_ADD_OK = "FAILED"
    }
    if ($status.BRANCH_CREATED -eq "PENDING") {
        $status.BRANCH_CREATED = "FAILED"
    }
    if ($status.FILES_STAGED -eq "PENDING") {
        $status.FILES_STAGED = "FAILED"
    }
    if ($status.COMMIT_CREATED -eq "PENDING") {
        $status.COMMIT_CREATED = "FAILED"
    }
    if ($status.PUSH_OK -eq "PENDING") {
        $status.PUSH_OK = "FAILED"
    }
    if ($status.PR_URL -eq "PENDING") {
        $status.PR_URL = "FAILED"
    }
    if ($status.CHECKS_OK -eq "PENDING") {
        $status.CHECKS_OK = "FAILED"
    }
    if ($status.MERGE_OK -eq "PENDING") {
        $status.MERGE_OK = "FAILED"
    }
    if ($status.MAIN_SYNC_OK -eq "PENDING") {
        $status.MAIN_SYNC_OK = "FAILED"
    }

    Print-Status $status
    throw
}
