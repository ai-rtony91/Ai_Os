param()

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
Set-Location -LiteralPath $RepoRoot

$LedgerRelativePath = "telemetry/forex/demo_proof_ledger.jsonl"
$LedgerPath = Join-Path $RepoRoot $LedgerRelativePath
$StartDemoRunScript = Join-Path $RepoRoot "scripts/forex_delivery/Start-AiOsDemoRun.ps1"
$VerdictScript = Join-Path $RepoRoot "scripts/forex_delivery/Get-AiOsDemoVerdict.ps1"
$RunnerValidationScript = Join-Path $RepoRoot "tests/forex_engine/test_demo_day_evidence_runner_v11_script.py"
$RecorderValidationScript = Join-Path $RepoRoot "tests/forex_engine/test_forex_demo_run_day_recorder_v1.py"

function Invoke-CheckedNative {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command,

        [Parameter(Mandatory = $true)]
        [string]$FailureCode
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw $FailureCode
    }
}

function Assert-NoGitIndexLock {
    $GitIndexLockPath = (Invoke-CheckedNative { git rev-parse --git-path index.lock } "GIT_INDEX_LOCK_PATH_FAILED").Trim()
    if (Test-Path -LiteralPath $GitIndexLockPath) {
        throw "GIT_INDEX_LOCK_PRESENT:$GitIndexLockPath"
    }
}

function Test-RealDemoDayForUtcDate {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$UtcDateText
    )

    $LineNumber = 0
    foreach ($RawLine in Get-Content -LiteralPath $Path -ErrorAction Stop) {
        $LineNumber++
        $Line = $RawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($Line)) {
            continue
        }

        try {
            $Obj = $Line | ConvertFrom-Json -ErrorAction Stop
        }
        catch {
            throw "DEMO_LEDGER_JSON_PARSE_FAILED:$LineNumber"
        }

        $RecordTypeProp = $Obj.PSObject.Properties["record_type"]
        if ($null -eq $RecordTypeProp -or $RecordTypeProp.Value -ne "REAL_DEMO_DAY") {
            continue
        }

        $DateProp = $Obj.PSObject.Properties["date"]
        if ($null -eq $DateProp) {
            continue
        }

        if ([string]$DateProp.Value -eq $UtcDateText) {
            return $true
        }
    }

    return $false
}

Assert-NoGitIndexLock

$CurrentBranch = (Invoke-CheckedNative { git branch --show-current } "GIT_BRANCH_SHOW_CURRENT_FAILED").Trim()
if ($CurrentBranch -ne "main") {
    throw "REQUIRES_MAIN_BRANCH:$CurrentBranch"
}

Invoke-CheckedNative { git fetch origin main } "GIT_FETCH_ORIGIN_MAIN_FAILED"
Invoke-CheckedNative { git merge --ff-only origin/main } "GIT_FAST_FORWARD_ORIGIN_MAIN_FAILED"

Assert-NoGitIndexLock

$BranchStatusLines = @(Invoke-CheckedNative { git status --short --branch } "GIT_STATUS_BRANCH_FAILED")
if ($BranchStatusLines.Count -ne 1) {
    throw "MAIN_BRANCH_MUST_BE_CLEAN_AND_SYNCED:$($BranchStatusLines -join ' | ')"
}

$BranchStatusLine = $BranchStatusLines[0].Trim()
if ($BranchStatusLine -ne "## main...origin/main") {
    throw "MAIN_BRANCH_MUST_BE_CLEAN_AND_SYNCED:$BranchStatusLine"
}

if (-not (Test-Path -LiteralPath $LedgerPath)) {
    throw "DEMO_PROOF_LEDGER_MISSING:$LedgerPath"
}

$TodayUtcText = [DateTime]::UtcNow.ToString("yyyy-MM-dd")
$HasDuplicateToday = Test-RealDemoDayForUtcDate -Path $LedgerPath -UtcDateText $TodayUtcText

if ($HasDuplicateToday) {
    Write-Output "DAY_EVIDENCE_APPEND_BLOCKED=DUPLICATE_REAL_DEMO_DAY"
    Write-Output "ACTION=VERDICT_ONLY"
    Invoke-CheckedNative { pwsh -NoProfile -File $VerdictScript } "GET_AI_OS_DEMO_VERDICT_FAILED"
    exit 0
}

Invoke-CheckedNative { python -m pytest $RunnerValidationScript -q } "DEMO_DAY_EVIDENCE_RUNNER_SCRIPT_TEST_FAILED"
Invoke-CheckedNative { python -m pytest $RecorderValidationScript -q } "FOREX_DEMO_RUN_DAY_RECORDER_TEST_FAILED"
Invoke-CheckedNative { pwsh -NoProfile -File $StartDemoRunScript -DryRun } "START_AI_OS_DEMO_RUN_DRYRUN_FAILED"
Invoke-CheckedNative { pwsh -NoProfile -File $StartDemoRunScript } "START_AI_OS_DEMO_RUN_APPLY_FAILED"
Invoke-CheckedNative { pwsh -NoProfile -File $VerdictScript } "GET_AI_OS_DEMO_VERDICT_FAILED"

$PostApplyStatusLines = @(Invoke-CheckedNative { git status --short --untracked-files=all } "GIT_STATUS_POST_APPLY_FAILED")
if ($PostApplyStatusLines.Count -eq 0) {
    throw "NO_GIT_DIFF_AFTER_DEMO_APPEND"
}
if ($PostApplyStatusLines.Count -ne 1) {
    throw "POST_APPLY_SCOPE_VIOLATION:$($PostApplyStatusLines -join ' | ')"
}

$PostApplyLine = $PostApplyStatusLines[0].Trim()
$PostApplyPath = if ($PostApplyLine.Length -ge 3) { $PostApplyLine.Substring(3).Trim() } else { "" }
if ($PostApplyPath -ne $LedgerRelativePath) {
    throw "POST_APPLY_SCOPE_VIOLATION:$PostApplyPath"
}

$EvidenceBranchName = "feature/forex-demo-day-evidence-$([DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff'))"
Invoke-CheckedNative { git checkout -b $EvidenceBranchName } "GIT_CREATE_EVIDENCE_BRANCH_FAILED"
Invoke-CheckedNative { git add -- $LedgerRelativePath } "GIT_ADD_LEDGER_FAILED"

$CachedPaths = @(Invoke-CheckedNative { git diff --cached --name-only } "GIT_CACHED_DIFF_NAME_ONLY_FAILED")
if ($CachedPaths.Count -ne 1 -or $CachedPaths[0].Trim() -ne $LedgerRelativePath) {
    throw "CACHED_SCOPE_VIOLATION:$($CachedPaths -join ' | ')"
}

Invoke-CheckedNative { git commit -m "chore(forex): record demo day evidence" } "GIT_COMMIT_LEDGER_FAILED"
$CommitHash = (Invoke-CheckedNative { git rev-parse --short HEAD } "GIT_REV_PARSE_HEAD_FAILED").Trim()

Write-Output "EVIDENCE_BRANCH=$EvidenceBranchName"
Write-Output "EVIDENCE_COMMIT=$CommitHash"
Write-Output "PR_CREATION_SKIPPED=STOP_AFTER_COMMIT"
