param(
    [string]$MissionId = "", [string]$MissionName = "",
    [string]$ProgramId = "", [string]$ProgramName = "",
    [string]$EpicId = "", [string]$EpicName = "",
    [string]$BucketId = "", [string]$BucketName = "",
    [string]$PacketId = "", [string]$PacketName = "",
    [string]$IdentityMarker = "", [string]$SupervisorIdentity = "",
    [string]$WorkerIdentity = "", [string]$LockIdentity = "",
    [string]$Mode = "", [string]$Zone = "", [string]$Lane = "",
    [string]$Worktree = "", [string]$Branch = "",
    [string]$ApprovalAuthority = "",
    [string[]]$AllowedPaths = @(), [string[]]$ForbiddenPaths = @(),
    [string[]]$Preflight = @(), [string[]]$Validators = @(),
    [string]$StopPoint = "", [string[]]$FinalReportFormat = @(),
    [string]$StagingAuthority = "", [string]$CommitAuthority = "",
    [string]$PushAuthority = "", [string]$PullRequestAuthority = "",
    [string]$MergeAuthority = "",
    [switch]$OutputJson, [switch]$AsPromptBlock,
    # Retained aliases prevent older callers from being mis-bound. They never
    # supply or invent v2 contract values.
    [string[]]$AllowedMutationFiles = @(), [string]$StartBranch = "",
    [string[]]$ReadFirst = @(), [string]$Mission = "",
    [switch]$FromContinuationPlan, [string]$ContinuationPlanScript = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "AiOsCodexPacketContract.ps1")
$contract = Get-AiOsCodexPacketContract

function Format-List([string[]]$Values) {
    return (@($Values | ForEach-Object { if (-not [string]::IsNullOrWhiteSpace($_)) { "- $_" } }) -join "`n")
}

function Test-Placeholder([string]$Value) {
    foreach ($pattern in @($contract.unresolved_placeholder_patterns)) {
        if ($Value -match $pattern) { return $true }
    }
    return $false
}

function Invoke-ContinuationPlan([string]$ScriptPath) {
    if ([string]::IsNullOrWhiteSpace($ScriptPath) -or -not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        return $null
    }
    try {
        # Preserve cross-host compatibility: reuse the current PowerShell
        # process rather than assuming either powershell.exe or pwsh exists.
        $powerShellHost = (Get-Process -Id $PID).Path
        $raw = & $powerShellHost -NoProfile -ExecutionPolicy Bypass -File $ScriptPath -OutputJson
        if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
        return $raw | ConvertFrom-Json
    }
    catch { return $null }
}

$scalars = [ordered]@{
    "MISSION ID"=$MissionId; "MISSION NAME"=$MissionName
    "PROGRAM ID"=$ProgramId; "PROGRAM NAME"=$ProgramName
    "EPIC ID"=$EpicId; "EPIC NAME"=$EpicName
    "BUCKET ID"=$BucketId; "BUCKET NAME"=$BucketName
    "PACKET ID"=$PacketId; "PACKET NAME"=$PacketName
    "IDENTITY MARKER"=$IdentityMarker; "SUPERVISOR IDENTITY"=$SupervisorIdentity
    "WORKER IDENTITY"=$WorkerIdentity; "LOCK IDENTITY"=$LockIdentity
    "MODE"=$Mode; "ZONE"=$Zone; "LANE"=$Lane; "WORKTREE"=$Worktree
    "BRANCH"=$Branch; "APPROVAL AUTHORITY"=$ApprovalAuthority; "STOP POINT"=$StopPoint
}
$lists = [ordered]@{
    "ALLOWED PATHS"=@($AllowedPaths); "FORBIDDEN PATHS"=@($ForbiddenPaths)
    "PREFLIGHT"=@($Preflight); "VALIDATOR CHAIN"=@($Validators)
    "FINAL REPORT FORMAT"=@($FinalReportFormat)
}
$protected = [ordered]@{
    "STAGING AUTHORITY"=$StagingAuthority; "COMMIT AUTHORITY"=$CommitAuthority
    "PUSH AUTHORITY"=$PushAuthority; "PULL REQUEST AUTHORITY"=$PullRequestAuthority
    "MERGE AUTHORITY"=$MergeAuthority
}

$missing = @()
$defects = @()
foreach ($entry in $scalars.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace([string]$entry.Value)) { $missing += $entry.Key }
    elseif (Test-Placeholder ([string]$entry.Value)) { $defects += "unresolved_placeholder:$($entry.Key)" }
}
foreach ($entry in $lists.GetEnumerator()) {
    $items = @($entry.Value | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    if ($items.Count -eq 0) { $missing += $entry.Key }
    elseif (Test-Placeholder ($items -join "`n")) { $defects += "unresolved_placeholder:$($entry.Key)" }
}
foreach ($entry in $protected.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace([string]$entry.Value)) { $missing += $entry.Key }
    elseif (Test-Placeholder ([string]$entry.Value)) { $defects += "unresolved_placeholder:$($entry.Key)" }
    elseif ([string]$entry.Value -notmatch $contract.protected_authority_pattern) { $defects += "malformed_protected_authority:$($entry.Key)" }
}
if ($Mode -notin @("DRY_RUN", "APPLY")) { $defects += "invalid_mode" }
foreach ($command in @($contract.required_repository_state_commands)) {
    if ($Preflight -notcontains $command) { $defects += "missing_preflight_command:$command" }
}

$text = @"
CODEX-ONLY PROMPT
AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

MISSION ID:
$MissionId
MISSION NAME:
$MissionName
PROGRAM ID:
$ProgramId
PROGRAM NAME:
$ProgramName
EPIC ID:
$EpicId
EPIC NAME:
$EpicName
BUCKET ID:
$BucketId
BUCKET NAME:
$BucketName
PACKET ID:
$PacketId
PACKET NAME:
$PacketName

IDENTITY MARKER:
$IdentityMarker
SUPERVISOR IDENTITY:
$SupervisorIdentity
WORKER IDENTITY:
$WorkerIdentity
LOCK IDENTITY:
$LockIdentity
MODE:
$Mode
ZONE:
$Zone
LANE:
$Lane
WORKTREE:
$Worktree
BRANCH:
$Branch
APPROVAL AUTHORITY:
$ApprovalAuthority

ALLOWED PATHS:
$(Format-List $AllowedPaths)
FORBIDDEN PATHS:
$(Format-List $ForbiddenPaths)
PREFLIGHT:
$(Format-List $Preflight)
VALIDATOR CHAIN:
$(Format-List $Validators)
STOP POINT:
$StopPoint
FINAL REPORT FORMAT:
$(Format-List $FinalReportFormat)

STAGING AUTHORITY:
$StagingAuthority
COMMIT AUTHORITY:
$CommitAuthority
PUSH AUTHORITY:
$PushAuthority
PULL REQUEST AUTHORITY:
$PullRequestAuthority
MERGE AUTHORITY:
$MergeAuthority

execution_allowed=false
can_continue_without_anthony=false
writes_files=false
"@

$result = [ordered]@{
    schema="AIOS_CODEX_PACKET_GENERATOR.v2"; contract_schema=$contract.schema
    generated_packet_text=$text; packet_valid=($missing.Count -eq 0 -and $defects.Count -eq 0)
    missing_required_fields=@($missing); validation_defects=@($defects)
    writes_files=$false; execution_allowed=$false; can_continue_without_anthony=$false
}
if ($OutputJson) { $result | ConvertTo-Json -Depth 20 } else { Write-Output $text }
exit 0
