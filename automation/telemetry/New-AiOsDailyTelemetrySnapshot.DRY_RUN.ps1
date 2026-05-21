Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$evidenceInboxRelativePath = "Reports/telemetry/session_archives/inbox_evidence"
$telemetryScriptsRelativePath = "automation/telemetry"
$evidenceInboxPath = Join-Path $repoRoot $evidenceInboxRelativePath
$telemetryScriptsPath = Join-Path $repoRoot $telemetryScriptsRelativePath

function Get-GitStatusSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RepositoryRoot
    )

    $summary = [ordered]@{
        statusShortBranch = "UNKNOWN"
        modifiedEntryCount = 0
        untrackedEntryCount = 0
        commitStatus = "NOT_COMMITTED"
        pushStatus = "NOT_PUSHED"
    }

    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCommand) {
        $summary.statusShortBranch = "GIT_UNAVAILABLE"
        return $summary
    }

    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $gitCommand.Source
    $processInfo.Arguments = "status --short --branch"
    $processInfo.WorkingDirectory = $RepositoryRoot
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo

    try {
        [void] $process.Start()
        $standardOutput = $process.StandardOutput.ReadToEnd()
        [void] $process.StandardError.ReadToEnd()
        $process.WaitForExit()

        $statusLines = @(
            $standardOutput -split "`r?`n" |
                Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        )

        if (($process.ExitCode -ne 0) -and ($statusLines.Count -eq 0)) {
            $summary.statusShortBranch = "GIT_STATUS_UNAVAILABLE"
            return $summary
        }

        if ($statusLines.Count -gt 0) {
            $summary.statusShortBranch = $statusLines -join "`n"
        }

        $porcelainLines = @($statusLines | Where-Object { $_ -notlike "##*" })
        $summary.untrackedEntryCount = @($porcelainLines | Where-Object { $_ -like "??*" }).Count
        $summary.modifiedEntryCount = @($porcelainLines | Where-Object { $_ -notlike "??*" }).Count
    }
    finally {}

    return $summary
}

function Get-EvidenceInboxSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string] $InboxPath
    )

    $summary = [ordered]@{
        path = "Reports/telemetry/session_archives/inbox_evidence/"
        scanMode = "METADATA_ONLY_NON_RECURSIVE"
        fileCount = 0
        countByExtension = [ordered]@{}
    }

    if (-not (Test-Path -LiteralPath $InboxPath -PathType Container)) {
        return $summary
    }

    $files = @(Get-ChildItem -LiteralPath $InboxPath -File)
    $summary.fileCount = $files.Count

    foreach ($group in ($files | Group-Object Extension | Sort-Object Name)) {
        $extension = if ([string]::IsNullOrWhiteSpace($group.Name)) { "[no_extension]" } else { $group.Name }
        $summary.countByExtension[$extension] = $group.Count
    }

    return $summary
}

function Get-TelemetryScriptInventory {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ScriptsPath
    )

    $inventory = [ordered]@{
        path = "automation/telemetry/"
        inventoryMode = "FILE_NAME_ONLY"
        fileNames = @()
    }

    if (-not (Test-Path -LiteralPath $ScriptsPath -PathType Container)) {
        return $inventory
    }

    $inventory.fileNames = @(
        Get-ChildItem -LiteralPath $ScriptsPath -File |
            Sort-Object Name |
            Select-Object -ExpandProperty Name
    )

    return $inventory
}

$git = Get-GitStatusSummary -RepositoryRoot $repoRoot
$evidenceInbox = Get-EvidenceInboxSummary -InboxPath $evidenceInboxPath
$telemetryScripts = Get-TelemetryScriptInventory -ScriptsPath $telemetryScriptsPath

$snapshot = [ordered]@{
    schema = "aios.daily_telemetry_snapshot.v1"
    snapshotDate = (Get-Date).ToString("yyyy-MM-dd")
    generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    mode = "DRY_RUN"
    repo = "ai-rtony91/Ai_Os"
    workingFolder = $repoRoot
    branch = "v2/aios"
    git = $git
    evidenceInbox = $evidenceInbox
    telemetryScripts = $telemetryScripts
    workflowStatus = [ordered]@{
        dryRunStatus = "PASS"
        applyStatus = "NOT_RUN"
        safetyStatus = "PASS"
    }
    nextSafeAction = "Review this console-only DRY_RUN snapshot before approving any APPLY output file."
}

$snapshot | ConvertTo-Json -Depth 8
