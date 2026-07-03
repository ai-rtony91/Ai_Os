param(
    [string]$ReportDirectory = ""
)

$ErrorActionPreference = "Stop"

$script:Steps = New-Object System.Collections.Generic.List[object]
$script:FailureClass = "NONE"
$script:ValidationStatus = "PASS"
$script:EvidenceStatus = "UNKNOWN"
$script:ReportStatus = "PASS"

function Resolve-AiOsRepoRoot {
    if ($env:AIOS_REPO_ROOT -and (Test-Path -LiteralPath $env:AIOS_REPO_ROOT)) {
        return (Resolve-Path -LiteralPath $env:AIOS_REPO_ROOT).Path
    }

    if ($PSScriptRoot) {
        $candidate = Join-Path $PSScriptRoot "../.."
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $gitRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -eq 0 -and $gitRoot) {
        return (Resolve-Path -LiteralPath $gitRoot.Trim()).Path
    }

    throw "AIOS_REPO_ROOT_UNRESOLVED"
}

function Get-GitStatusShort {
    return @(& git status --short --untracked-files=all)
}

function Add-StepRecord {
    param(
        [string]$Stage,
        [string]$Status,
        [string]$CleanupAction,
        [string[]]$GitStatusBefore,
        [string[]]$GitStatusAfter,
        [string]$Detail = ""
    )

    $script:Steps.Add([ordered]@{
        stage = $Stage
        status = $Status
        cleanup_action = $CleanupAction
        git_status_before = $GitStatusBefore
        git_status_after = $GitStatusAfter
        detail = $Detail
    })
}

function Assert-CleanGit {
    param([string]$Stage)

    $before = @(Get-GitStatusShort)
    if ($before.Count -gt 0) {
        $script:FailureClass = "DIRTY_WORKTREE_BLOCKED"
        $script:ValidationStatus = "FAIL"
        $script:ReportStatus = "BLOCKED_OR_FAILED"
        Add-StepRecord -Stage $Stage -Status "BLOCKED" -CleanupAction "NONE_UNSAFE_TO_CLEAN" -GitStatusBefore $before -GitStatusAfter $before -Detail "Dirty worktree blocked stage."
        throw "DIRTY_WORKTREE_BLOCKED:$Stage"
    }

    Add-StepRecord -Stage $Stage -Status "CLEAN" -CleanupAction "NONE" -GitStatusBefore $before -GitStatusAfter $before
}

function Classify-Failure {
    param([string]$Text)

    if ($Text -match "AIOS_REPO_ROOT|C:/Dev/Ai.Os|C:\\Dev\\Ai.Os|workspaces|path|Set-Location") { return "PATH_ENV_FAILURE" }
    if ($Text -match "pytest|test") { return "TEST_HARNESS_FAILURE" }
    if ($Text -match "report|artifact") { return "REPORT_ONLY_FAILURE" }
    if ($Text -match "broker|OANDA|order|live_trading|money") { return "LIVE_AUTHORITY_RISK" }
    if ($Text -match "\.env|credential|secret|token") { return "SECRET_ACCESS_RISK" }
    return "UNKNOWN_FAILURE"
}

function Invoke-Checked {
    param(
        [string]$Stage,
        [string]$Command,
        [string[]]$Arguments
    )

    Assert-CleanGit -Stage "${Stage}:CLEAN_BEFORE"

    $output = @(& $Command @Arguments 2>&1)
    $exitCode = $LASTEXITCODE

    if ($output) {
        $output | ForEach-Object { Write-Output $_ }
    }

    if ($exitCode -ne 0) {
        $text = ($output -join "`n")
        $script:FailureClass = Classify-Failure -Text $text
        $script:ValidationStatus = "FAIL"
        $script:ReportStatus = "BLOCKED_OR_FAILED"
        Add-StepRecord -Stage $Stage -Status "FAIL" -CleanupAction "NONE" -GitStatusBefore @() -GitStatusAfter @(Get-GitStatusShort) -Detail (($output | Select-Object -Last 80) -join "`n")
        throw "$Stage FAILED:$exitCode"
    }

    Assert-CleanGit -Stage "${Stage}:CLEAN_AFTER"
    Add-StepRecord -Stage $Stage -Status "PASS" -CleanupAction "NONE" -GitStatusBefore @() -GitStatusAfter @(Get-GitStatusShort)
}

function Test-EvidenceDay {
    $ledger = Join-Path $script:RepoRoot "telemetry/forex/demo_proof_ledger.jsonl"
    if (-not (Test-Path -LiteralPath $ledger)) {
        $script:EvidenceStatus = "LEDGER_MISSING"
        return
    }

    $today = [DateTime]::UtcNow.ToString("yyyy-MM-dd")
    $matches = 0

    foreach ($line in Get-Content -LiteralPath $ledger) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try {
            $obj = $line | ConvertFrom-Json -ErrorAction Stop
            if ($obj.record_type -eq "REAL_DEMO_DAY" -and [string]$obj.date -eq $today) {
                $matches++
            }
        }
        catch {
            $script:EvidenceStatus = "LEDGER_PARSE_WARNING"
        }
    }

    if ($matches -eq 0) { $script:EvidenceStatus = "MISSING_TODAY_EVIDENCE" }
    elseif ($matches -eq 1) { $script:EvidenceStatus = "TODAY_EVIDENCE_PRESENT" }
    else { $script:EvidenceStatus = "DUPLICATE_EVIDENCE_BLOCKED" }
}

function Write-OrchestratorReports {
    if (-not $ReportDirectory) {
        if ($env:RUNNER_TEMP) {
            $ReportDirectory = Join-Path $env:RUNNER_TEMP "aios_daily_forex_orchestrator"
        }
        else {
            $ReportDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "aios_daily_forex_orchestrator"
        }
    }

    New-Item -ItemType Directory -Force -Path $ReportDirectory | Out-Null

    $branch = (& git branch --show-current).Trim()
    $sha = (& git rev-parse --short HEAD).Trim()

    $artifactJson = python -m automation.forex_engine.daily_forex_orchestrator_artifact_v1 --repo-root $script:RepoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "ROLLING_CONTINUITY_ARTIFACT_HELPER_FAILED"
    }
    $artifactSummary = $artifactJson | ConvertFrom-Json -AsHashtable

    $payload = [ordered]@{
        schema = "aios.daily_forex_orchestrator.v1"
        status = $script:ReportStatus
        validation_status = $script:ValidationStatus
        failure_class = $script:FailureClass
        evidence_status = $script:EvidenceStatus
        branch = $branch
        commit_sha = $sha
        report_utc = [DateTime]::UtcNow.ToString("o")
        rolling_continuity = $artifactSummary
        maintenance = $artifactSummary.maintenance
        safety = [ordered]@{
            broker_calls_allowed = $false
            live_orders_allowed = $false
            credential_access_allowed = $false
            env_file_reads_allowed = $false
            money_movement_allowed = $false
            automatic_evidence_append_allowed = $false
            automatic_merge_allowed = $false
            safety_statement = $artifactSummary.safety_statement
        }
        steps = $script:Steps
    }

    $jsonPath = Join-Path $ReportDirectory "aios_daily_forex_orchestrator.json"
    $mdPath = Join-Path $ReportDirectory "AIOS_DAILY_FOREX_ORCHESTRATOR.md"

    $payload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

    @(
        "# AIOS Daily Forex Orchestrator"
        ""
        "status: $($payload.status)"
        "validation_status: $($payload.validation_status)"
        "failure_class: $($payload.failure_class)"
        "evidence_status: $($payload.evidence_status)"
        "branch: $($payload.branch)"
        "commit_sha: $($payload.commit_sha)"
        "report_utc: $($payload.report_utc)"
"real_demo_day_count: $($payload.rolling_continuity.real_demo_day_count)"
"consecutive_real_demo_day_count: $($payload.rolling_continuity.consecutive_real_demo_day_count)"
"missing_dates: $($payload.rolling_continuity.missing_dates -join ',')"
"next_required_evidence_date: $($payload.rolling_continuity.next_required_evidence_date)"
"five_day_window_status: $($payload.rolling_continuity.five_day_window_status)"
"thirty_day_window_status: $($payload.rolling_continuity.thirty_day_window_status)"
"rolling_continuity_status: $($payload.rolling_continuity.rolling_continuity_status)"
"maintenance_status: $($payload.maintenance.status)"
"maintenance_next_best_packet: $($payload.maintenance.next_best_packet)"
"maintenance_blockers: $($payload.maintenance.blockers -join ',')"
        ""
        "Safety: $($payload.safety.safety_statement)"
    ) | Set-Content -LiteralPath $mdPath -Encoding UTF8

    Write-Output "REPORT_JSON=$jsonPath"
    Write-Output "REPORT_MD=$mdPath"
}

try {
    $script:RepoRoot = Resolve-AiOsRepoRoot
    Set-Location -LiteralPath $script:RepoRoot

    Assert-CleanGit -Stage "START"
    Test-EvidenceDay

    Invoke-Checked -Stage "PYTEST_DEMO_DAY_RUNNER" -Command "python" -Arguments @("-m", "pytest", "tests/forex_engine/test_demo_day_evidence_runner_v11_script.py", "-q")
    Invoke-Checked -Stage "DEMO_VERDICT" -Command "pwsh" -Arguments @("-NoProfile", "-File", "scripts/forex_delivery/Get-AiOsDemoVerdict.ps1")
    Invoke-Checked -Stage "GIT_DIFF_CHECK" -Command "git" -Arguments @("diff", "--check")

    Assert-CleanGit -Stage "FINAL"
    Write-OrchestratorReports
    exit 0
}
catch {
    Write-Output "ORCHESTRATOR_FAILED=$($_.Exception.Message)"
    Write-OrchestratorReports
    exit 1
}
