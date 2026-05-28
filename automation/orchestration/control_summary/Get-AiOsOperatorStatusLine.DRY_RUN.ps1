[CmdletBinding()]
param(
    [switch]$Compact,
    [switch]$Explain
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-AiOsGitRead {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        output = @($output | ForEach-Object { [string]$_ })
        exit_code = $exitCode
    }
}

function Remove-AiOsGitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -notmatch "^warning:" })
}

function Get-AiOsFirstCleanLine {
    param([string[]]$Lines)

    $cleanLines = @(Remove-AiOsGitWarnings -Lines $Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($cleanLines.Count -eq 0) {
        return "UNKNOWN"
    }

    return $cleanLines[0].Trim()
}

function Test-AiOsFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    return Test-Path -LiteralPath $Path -PathType Leaf
}

function Get-AiOsBranchName {
    $branchResult = Invoke-AiOsGitRead -Arguments @("branch", "--show-current")
    if ($branchResult.exit_code -ne 0) {
        return "UNKNOWN"
    }

    return Get-AiOsFirstCleanLine -Lines $branchResult.output
}

function Get-AiOsRepoState {
    $statusResult = Invoke-AiOsGitRead -Arguments @("status", "--short", "--branch")
    if ($statusResult.exit_code -ne 0) {
        return "UNKNOWN"
    }

    $statusLines = @(Remove-AiOsGitWarnings -Lines $statusResult.output | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_) -and $_ -notlike "##*"
    })

    if ($statusLines.Count -eq 0) {
        return "CLEAN"
    }

    return "DIRTY"
}

function Get-AiOsPrLabel {
    param([Parameter(Mandatory = $true)][string]$Branch)

    if ($Branch -eq "phase-orchestration-contract-normalization") {
        return "PR #296"
    }

    return "PR unknown"
}

function Get-AiOsBackupStatus {
    $taskNames = @(
        "AI_OS_T9_FOB_Backup_3x_Daily",
        "AI_OS_T9_FOB_Backup_Twice_Daily"
    )

    $scheduledTaskCommand = Get-Command Get-ScheduledTask -ErrorAction SilentlyContinue
    if ($null -eq $scheduledTaskCommand) {
        return "unknown"
    }

    foreach ($taskName in $taskNames) {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($null -eq $task) {
            continue
        }

        $triggerCount = @($task.Triggers).Count
        if ($taskName -eq "AI_OS_T9_FOB_Backup_3x_Daily" -and $triggerCount -eq 3) {
            return "3x/day"
        }

        if ($taskName -eq "AI_OS_T9_FOB_Backup_Twice_Daily" -and $triggerCount -eq 2) {
            return "2x/day"
        }

        return "$triggerCount triggers"
    }

    return "unknown"
}

function Get-AiOsProgressEstimate {
    param(
        [Parameter(Mandatory = $true)][string]$BackupStatus
    )

    $progress = 50
    $basis = [System.Collections.Generic.List[string]]::new()

    $contractExists = Test-AiOsFile -Path "schemas/aios/orchestration/orchestration_result_contract.schema.json"
    $overnightSchemaExists = Test-AiOsFile -Path "schemas/aios/orchestration/overnight_supervisor.schema.json"
    if ($contractExists -and $overnightSchemaExists) {
        $progress = [Math]::Max($progress, 70)
        $basis.Add("orchestration contracts exist") | Out-Null
    }

    $normalizerExists = Test-AiOsFile -Path "services/python_supervisor/contract_normalizer.py"
    $morningBriefExists = Test-AiOsFile -Path "services/python_supervisor/morning_brief_synthesizer.py"
    if ($normalizerExists -and $morningBriefExists) {
        $progress = [Math]::Max($progress, 75)
        $basis.Add("Python glue and Morning Brief exist") | Out-Null
    }

    $validateMarkerExists = Test-AiOsFile -Path "automation/orchestration/pr_gates/Invoke-AiOsPrLaneRunner.DRY_RUN.ps1"
    if ($validateMarkerExists -and $progress -ge 75) {
        $progress = [Math]::Max($progress, 80)
        $basis.Add("PR lane validate reader exists; live validate status not queried") | Out-Null
    }

    if ($BackupStatus -ne "unknown") {
        $progress = [Math]::Max($progress, 85)
        $basis.Add("backup scheduler is visible") | Out-Null
    }

    if ($progress -gt 90) {
        $progress = 90
    }

    if ($basis.Count -eq 0) {
        $basis.Add("baseline governed orchestration evidence only") | Out-Null
    }

    return [pscustomobject]@{
        percent = $progress
        basis = @($basis)
    }
}

$branch = Get-AiOsBranchName
$repoState = Get-AiOsRepoState
$prLabel = Get-AiOsPrLabel -Branch $branch
$backupStatus = Get-AiOsBackupStatus
$estimate = Get-AiOsProgressEstimate -BackupStatus $backupStatus
$nextSafeAction = "review/merge/sync"

$statusLine = "AI_OS $($estimate.percent)% est | L4.5->5 | branch $branch | repo $repoState | $prLabel | backup $backupStatus | codex output unknown | next: $nextSafeAction"

Write-Output $statusLine

if ($Explain) {
    Write-Output ""
    Write-Output "Estimate basis:"
    foreach ($item in $estimate.basis) {
        Write-Output "- $item"
    }
    Write-Output "- exact Codex output remaining percent is not available from repo-local evidence"
    Write-Output "- maximum stays below 90 until protected-main merge, local sync, and unattended DRY_RUN evidence are proven"
}
