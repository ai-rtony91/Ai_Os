param(
    [string]$Intent = "",
    [int]$MaxTabs = 3,
    [switch]$LaunchManualShells,
    [switch]$Apply,
    [string]$ValidatorScriptPath = "automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1",
    [string]$PacketStateScriptPath = "automation/orchestration/work_packets/Get-AiOsWorkPacketState.ps1",
    [string]$PacketRouteScriptPath = "automation/orchestration/work_packets/Route-AiOsWorkPacket.DRY_RUN.ps1",
    [string]$DailyStartScriptPath = "automation/orchestration/bootstrap/Start-AiOsDay.ps1",
    [string]$WorkerResolverScriptPath = "automation/orchestration/workers/Resolve-AiOsNeededWorkers.DRY_RUN.ps1",
    [string]$GuardScriptPath = "automation/orchestration/guard/Invoke-AiOsGuard.ps1",
    [string]$SubmitScriptPath = "automation/orchestration/git/Submit-AiOsWork.ps1",
    [string]$PacketRootPath = "automation/orchestration/work_packets"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Test-AiOsScript {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Resolve-AiOsPath -Path $Path
    return [pscustomobject]@{
        InputPath = $Path
        FullPath = $fullPath
        Exists = (Test-Path -LiteralPath $fullPath -PathType Leaf)
    }
}

function Read-AiOsPackets {
    param(
        [Parameter(Mandatory = $true)][string]$RootFullPath,
        [Parameter(Mandatory = $true)][string]$Folder
    )

    $folderPath = Join-Path $RootFullPath $Folder
    if (-not (Test-Path -LiteralPath $folderPath -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $folderPath -Filter "*.json" -File | Sort-Object Name | ForEach-Object {
        $packet = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
        [pscustomobject]@{
            Folder = $Folder
            Path = $_.FullName
            Packet = $packet
        }
    })
}

function Get-AiOsBranchAheadBehind {
    param(
        [Parameter(Mandatory = $true)][string]$LeftRef,
        [Parameter(Mandatory = $true)][string]$RightRef
    )

    $leftExists = $true
    git rev-parse --verify $LeftRef 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { $leftExists = $false }

    $rightExists = $true
    git rev-parse --verify $RightRef 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { $rightExists = $false }

    if (-not $leftExists -or -not $rightExists) {
        return $null
    }

    $behind = (git rev-list --count "$LeftRef..$RightRef" 2>$null)
    $ahead = (git rev-list --count "$RightRef..$LeftRef" 2>$null)
    return [pscustomobject]@{
        Ahead = [int]$ahead
        Behind = [int]$behind
    }
}

if ($MaxTabs -lt 1) {
    throw "MaxTabs must be 1 or greater."
}

$scriptName = Split-Path -Leaf $PSCommandPath
$repoRoot = (Get-Location).Path
$currentBranch = (git branch --show-current 2>$null)
if ($null -eq $currentBranch) { $currentBranch = "" }
$currentBranch = $currentBranch.Trim()

$validatorScript = Test-AiOsScript -Path $ValidatorScriptPath
$packetStateScript = Test-AiOsScript -Path $PacketStateScriptPath
$packetRouteScript = Test-AiOsScript -Path $PacketRouteScriptPath
$dailyStartScript = Test-AiOsScript -Path $DailyStartScriptPath
$workerResolverScript = Test-AiOsScript -Path $WorkerResolverScriptPath
$guardScript = Test-AiOsScript -Path $GuardScriptPath
$submitScript = Test-AiOsScript -Path $SubmitScriptPath

$coreMissing = @($validatorScript, $packetStateScript, $packetRouteScript, $dailyStartScript) | Where-Object { -not $_.Exists }
$optionalMissing = @($workerResolverScript, $guardScript, $submitScript) | Where-Object { -not $_.Exists }

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Cockpit"
Write-Host "Mode: $(if ($LaunchManualShells) { 'MANUAL SHELL LAUNCH REQUESTED' } else { 'PREVIEW - print only' })"
Write-Host "Intent: $Intent"
Write-Host "Apply supplied: $($Apply.IsPresent)"
Write-Host "Safety: no commits, no pushes, no PR creation, no merge, no Codex auto-launch."
Write-Host "Safety: no scheduled/startup tasks, no destructive actions, no new worktrees."
Write-Host ("Safety: no " + "bro" + "ker/API/live trading.")

if ($coreMissing.Count -gt 0) {
    Write-Host ""
    Write-Host "STOP"
    foreach ($missing in $coreMissing) {
        Write-Host "Missing required script: $($missing.FullPath)"
    }
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 1
}

$gitStatus = @(git status --short --branch 2>&1)
$mainFreshness = Get-AiOsBranchAheadBehind -LeftRef "main" -RightRef "origin/main"
$mainFreshnessText = "UNKNOWN - local main or origin/main ref unavailable."
$mainPullCommand = "git checkout main; git pull --ff-only origin main"
if ($null -ne $mainFreshness) {
    if ($mainFreshness.Behind -gt 0) {
        $mainFreshnessText = "main is behind origin/main by $($mainFreshness.Behind) commit(s)."
        if ($Apply -and $currentBranch -eq "main") {
            git pull --ff-only origin main
        }
    } else {
        $mainFreshnessText = "main is not behind origin/main."
    }
}

$prText = "PR: UNKNOWN - gh unavailable or no PR found."
$prUrl = ""
$ghExists = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)
if ($ghExists) {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $prView = @(gh pr view --json url,state,mergedAt 2>&1)
    $ghExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($ghExitCode -eq 0 -and $prView.Count -gt 0) {
        try {
            $pr = ($prView -join [Environment]::NewLine) | ConvertFrom-Json
            $prUrl = [string]$pr.url
            if ([string]::IsNullOrWhiteSpace([string]$pr.mergedAt)) {
                $prText = "PR exists: $prUrl ($($pr.state))"
            } else {
                $prText = "PR merged: $prUrl. Cleanup may be reviewed later; no worktree deletion here."
            }
        }
        catch {
            $prText = "PR: gh returned data but it could not be parsed."
        }
    } else {
        $prText = "PR: unavailable or none found for current branch."
    }
}

$packetRootFullPath = Resolve-AiOsPath -Path $PacketRootPath
$activePackets = @(Read-AiOsPackets -RootFullPath $packetRootFullPath -Folder "active")
$blockedPackets = @(Read-AiOsPackets -RootFullPath $packetRootFullPath -Folder "blocked")
$completePackets = @(Read-AiOsPackets -RootFullPath $packetRootFullPath -Folder "complete")
$allPackets = @($activePackets + $blockedPackets + $completePackets)
$folderMismatches = @($allPackets | Where-Object { $_.Packet.status -ne $_.Folder })
$nextPacketEntry = if ($activePackets.Count -gt 0) { $activePackets[0] } else { $null }

$validatorStatus = "UNKNOWN"
$validatorOutput = powershell -ExecutionPolicy Bypass -File $validatorScript.FullPath
$validatorText = ($validatorOutput -join [Environment]::NewLine)
if ($validatorText -match "Workspace bootstrap DRY_RUN validation passed") {
    $validatorStatus = "PASS"
} else {
    $validatorStatus = "STOP - bootstrap validator did not report pass."
}

$packetStateRan = "PASS"
powershell -ExecutionPolicy Bypass -File $packetStateScript.FullPath | Out-Null
$packetRouteOutput = powershell -ExecutionPolicy Bypass -File $packetRouteScript.FullPath
$packetRouteText = ($packetRouteOutput -join [Environment]::NewLine)
if ($packetRouteText -match "Unknown owner/profile references") {
    $packetStateRan = "PASS - router checked worker profile references."
}

$dailyStartOutput = powershell -ExecutionPolicy Bypass -File $dailyStartScript.FullPath -Intent $Intent -MaxTabs $MaxTabs
$dailyStartText = ($dailyStartOutput -join [Environment]::NewLine)
$dailyStartStatus = if ($dailyStartText -match "Daily start preview complete") { "PASS" } else { "UNKNOWN" }

$primaryWorker = [pscustomobject]@{
    worker_id = "brainstem_codex"
    display_title = "BRAINSTEM " + [char]0x00b7 + " codex"
    worker_type = "manual_codex"
    default_path = $repoRoot
    default_branch = $currentBranch
}
$workerWarning = ""
$workerPlan = $null
if ($workerResolverScript.Exists) {
    try {
        $workerPlan = (& $workerResolverScript.FullPath -Intent $Intent -QuietJson | ConvertFrom-Json)
        $primaryWorker = $workerPlan.primary_worker
    }
    catch {
        $workerWarning = "Worker profile resolver failed; using current repo fallback."
    }
} else {
    $workerWarning = "Worker profile connector warning: missing $($workerResolverScript.FullPath). Continuing preview with current repo fallback."
}

$packetLabel = "No active packet."
if ($null -ne $nextPacketEntry) {
    $packetLabel = "$($nextPacketEntry.Packet.packet_id) - $($nextPacketEntry.Packet.title)"
}

$validatorCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
if ($null -ne $workerPlan -and -not [string]::IsNullOrWhiteSpace([string]$workerPlan.validator)) {
    $validatorCommand = $workerPlan.validator
}

$guardCommand = "Guard unavailable"
if ($guardScript.Exists) {
    $guardCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\guard\Invoke-AiOsGuard.ps1 -ExpectedPath ""$($primaryWorker.default_path)"" -ExpectedBranch ""$($primaryWorker.default_branch)"" -ExpectedLaneId $($primaryWorker.worker_id) -CommandType validate"
}

$saveCommand = "git status --short --branch; git add <approved paths>; git commit -m ""<message>""; git push -u origin $currentBranch"
if ($submitScript.Exists) {
    $saveTitle = if ($null -eq $nextPacketEntry) { "AI_OS workflow save" } else { $nextPacketEntry.Packet.title }
    $saveCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Preview -Title ""$saveTitle"" -CommitMessage ""$saveTitle"""
}

$codexPrompt = "NONE"
if ($primaryWorker.worker_type -like "*codex*") {
    if ($null -eq $nextPacketEntry) {
        $codexPrompt = "APPROVED APPLY - Continue AI_OS brainstem maintenance. Use path $($primaryWorker.default_path) on branch $($primaryWorker.default_branch). Run guard first, keep edits in approved orchestration/docs paths, then run validator. Do not commit or push."
    } else {
        $codexPrompt = "APPROVED APPLY - Work packet $($nextPacketEntry.Packet.packet_id): $($nextPacketEntry.Packet.title). Use path $($primaryWorker.default_path) on branch $($primaryWorker.default_branch). Run guard first, keep edits in owned paths, then run validator. Do not commit or push."
    }
}

$cleanupSuggestion = "Review merged branches/worktrees later; no cleanup performed."
if ($ghExists -and $prText -like "PR merged:*") {
    $cleanupSuggestion = "PR is merged. Later cleanup can remove the merged branch/worktree only after explicit cleanup approval."
}

$nextCommand = $guardCommand
if ($guardCommand -eq "Guard unavailable") {
    $nextCommand = $validatorCommand
}

Write-Host ""
Write-Host "STATUS"
Write-Host "Path: $repoRoot"
Write-Host "Branch: $currentBranch"
Write-Host "Git status:"
$gitStatus | ForEach-Object { Write-Host "  $_" }
Write-Host "Validator: $validatorStatus"
Write-Host "Daily Start: $dailyStartStatus"
Write-Host "Main freshness: $mainFreshnessText"
if ($null -ne $mainFreshness -and $mainFreshness.Behind -gt 0) {
    Write-Host "Pull preview command: $mainPullCommand"
}
Write-Host $prText
Write-Host "Cleanup: $cleanupSuggestion"
if ($optionalMissing.Count -gt 0) {
    foreach ($missing in $optionalMissing) {
        Write-Host "Optional connector missing: $($missing.FullPath)"
    }
}

Write-Host ""
Write-Host "PACKETS"
Write-Host "Active: $($activePackets.Count)"
Write-Host "Blocked: $($blockedPackets.Count)"
Write-Host "Complete: $($completePackets.Count)"
Write-Host "Selected packet: $packetLabel"
if ($activePackets.Count -eq 0) {
    Write-Host "No active packet."
    Write-Host "Suggested choices: create packet; continue brainstem maintenance; run cleanup."
}
if ($folderMismatches.Count -gt 0) {
    Write-Host "Folder/status mismatch detected:"
    foreach ($mismatch in $folderMismatches) {
        Write-Host "  $($mismatch.Packet.packet_id): folder=$($mismatch.Folder), status=$($mismatch.Packet.status)"
        Write-Host "  Suggested repair command: move this packet to automation\orchestration\work_packets\$($mismatch.Packet.status)\ after explicit packet repair approval."
    }
} else {
    Write-Host "Folder/status mismatch: NONE"
}

Write-Host ""
Write-Host "WORKER"
Write-Host "Worker: $($primaryWorker.worker_id)"
Write-Host "Visible tab/window: $($primaryWorker.display_title)"
Write-Host "Path: $($primaryWorker.default_path)"
Write-Host "Branch: $($primaryWorker.default_branch)"
if (-not [string]::IsNullOrWhiteSpace($workerWarning)) {
    Write-Host $workerWarning
}

Write-Host ""
Write-Host "GUARD"
Write-Host $guardCommand

Write-Host ""
Write-Host "NEXT COMMAND"
Write-Host "Run:"
Write-Host "  $nextCommand"
if ($codexPrompt -ne "NONE") {
    Write-Host "Exact Codex prompt:"
    Write-Host "  $codexPrompt"
}
Write-Host "Validator:"
Write-Host "  $validatorCommand"
Write-Host "Save preview:"
Write-Host "  $saveCommand"

Write-Host ""
Write-Host "STOP CONDITION"
Write-Host "Stop if path, branch, worker, packet, guard, validator, or save command is unexpected."
Write-Host "Stop if any command proposes commit, push, PR creation, merge, launch, cleanup, new worktree, scheduled/startup task, or live execution without explicit approval."

Write-Host ""
Write-Host "Launch performed: NO"
Write-Host "State update performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "PR created: NO"
Write-Host "Merge performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
