Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$bootstrapPath = Join-Path $orchestrationRoot "morning_bootstrap.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-CheckList {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [object[]]$Checks
    )

    Write-Host $Title

    if ($Checks.Count -eq 0) {
        Write-Host "  None"
        Write-Host ""
        return
    }

    foreach ($check in ($Checks | Sort-Object order)) {
        Write-Host "  $($check.order). $($check.check_name)"
        Write-Host "    ID: $($check.check_id)"
        Write-Host "    Status: $($check.status)"
        Write-Host "    Expected result: $($check.expected_result)"
        Write-Host "    Command display: $($check.command_display)"

        if ($check.PSObject.Properties.Name -contains "stop_condition") {
            Write-Host "    Stop condition: $($check.stop_condition)"
        }

        if ($check.PSObject.Properties.Name -contains "notes") {
            Write-Host "    Notes: $($check.notes)"
        }

        Write-Host ""
    }
}

$bootstrap = Read-JsonFile -Path $bootstrapPath
$startupChecklist = @($bootstrap.morning_startup_checklist)
$repoHealthChecks = @($bootstrap.repo_health_checks)
$nextSafeAction = $bootstrap.next_safe_action

Write-Host "AI_OS Morning Bootstrap Display"
Write-Host "Mode: $($bootstrap.mode)"
Write-Host "Bootstrap: $($bootstrap.bootstrap_name)"
Write-Host "Purpose: $($bootstrap.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No startup tasks or scheduled tasks are created. Nothing is launched."
Write-Host ""

Write-CheckList -Title "Morning startup checklist:" -Checks $startupChecklist
Write-CheckList -Title "Repo health checks:" -Checks $repoHealthChecks

Write-Host "Next safe action:"
Write-Host "  Action: $($nextSafeAction.action)"
Write-Host "  Command: $($nextSafeAction.command)"
Write-Host "  Stop condition: $($nextSafeAction.stop_condition)"
Write-Host ""

Write-Host "Safety notes:"
foreach ($note in @($bootstrap.safety_notes)) {
    Write-Host "  - $note"
}
Write-Host ""

Write-Host "Next safe action: run only the listed read-only display command, then review git status before any separate APPLY, commit, or push approval."
