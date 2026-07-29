param(
    [string]$IdentityMarker = "",
    [string]$SupervisorIdentity = "",
    [string]$MissionId = "",
    [string]$MissionName = "",
    [string]$ProgramId = "",
    [string]$ProgramName = "",
    [string]$EpicId = "",
    [string]$EpicName = "",
    [string]$BucketId = "",
    [string]$BucketName = "",
    [string]$PacketId = "",
    [string]$PacketName = "",
    [ValidateSet("DRY_RUN", "APPLY")]
    [string]$Mode = "DRY_RUN",
    [string]$Zone = "",
    [string]$Lane = "",
    [string]$WorkerIdentity = "",
    [string]$LockIdentity = "",
    [string]$Worktree = "",
    [string]$Branch = "",
    [string]$ApprovalAuthority = "",
    [string[]]$AllowedMutationFiles = @(),
    [string[]]$ForbiddenPaths = @(),
    [string[]]$ReadFirst = @(),
    [string[]]$Validators = @(),
    [string]$StopPoint = "",
    [switch]$OutputJson,
    [switch]$AsPromptBlock,
    [switch]$FromContinuationPlan,
    [string]$ContinuationPlanScript = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "AiOsCodexPacketContract.ps1")
$packetContract = Get-AiOsCodexPacketContract

function ConvertTo-TextValue {
    param([object]$Value)
    if ($null -eq $Value -or $Value -isnot [string]) { return "" }
    return ([string]$Value).Trim()
}

function ConvertTo-TextList {
    param([object]$Values)
    $items = @()
    if ($null -eq $Values) { return @() }
    foreach ($value in @($Values)) {
        if ($null -ne $value -and $value -is [string] -and -not [string]::IsNullOrWhiteSpace($value)) {
            $items += ([string]$value).Trim()
        }
    }
    return @($items)
}

function Format-List {
    param([string[]]$Values)
    return (($Values | ForEach-Object { "- $_" }) -join "`n")
}

function Test-UnresolvedValue {
    param([string]$Value)
    foreach ($pattern in @($packetContract.unresolved_value_patterns)) {
        if ($Value -match $pattern) { return $true }
    }
    return $false
}

function Invoke-ContinuationPlan {
    param([string]$ScriptPath)
    if ([string]::IsNullOrWhiteSpace($ScriptPath) -or -not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        return $null
    }
    $shell = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($null -eq $shell) { $shell = Get-Command powershell -ErrorAction SilentlyContinue }
    if ($null -eq $shell) { return $null }
    $raw = & $shell.Source -NoProfile -File $ScriptPath -OutputJson
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return $raw | ConvertFrom-Json
}

$continuation = $null
if ($FromContinuationPlan) {
    $planScript = if ([string]::IsNullOrWhiteSpace($ContinuationPlanScript)) {
        Join-Path $PSScriptRoot "..\continuation\Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1"
    } else { $ContinuationPlanScript }
    $continuation = Invoke-ContinuationPlan -ScriptPath $planScript
}

if ([string]::IsNullOrWhiteSpace($PacketId) -and $continuation -and $continuation.recommended_next_packet_id) {
    $PacketId = [string]$continuation.recommended_next_packet_id
}
if ([string]::IsNullOrWhiteSpace($PacketName) -and $continuation -and $continuation.recommended_next_packet_title) {
    $PacketName = [string]$continuation.recommended_next_packet_title
}
if ([string]::IsNullOrWhiteSpace($Zone) -and $continuation -and $continuation.domain) {
    $Zone = [string]$continuation.domain
}
if ([string]::IsNullOrWhiteSpace($Lane) -and $continuation -and $continuation.recommended_lane) {
    $Lane = [string]$continuation.recommended_lane
}
if (@($AllowedMutationFiles).Count -eq 0 -and $continuation -and $continuation.recommended_files) {
    $AllowedMutationFiles = @($continuation.recommended_files)
}
if (@($Validators).Count -eq 0 -and $continuation -and $continuation.required_validators) {
    $Validators = @($continuation.required_validators)
}
if ([string]::IsNullOrWhiteSpace($StopPoint) -and $continuation -and $continuation.exact_next_safe_action) {
    $StopPoint = [string]$continuation.exact_next_safe_action
}

$values = [ordered]@{
    "IDENTITY MARKER" = ConvertTo-TextValue $IdentityMarker
    "SUPERVISOR IDENTITY" = ConvertTo-TextValue $SupervisorIdentity
    "MISSION ID" = ConvertTo-TextValue $MissionId
    "MISSION NAME" = ConvertTo-TextValue $MissionName
    "PROGRAM ID" = ConvertTo-TextValue $ProgramId
    "PROGRAM NAME" = ConvertTo-TextValue $ProgramName
    "EPIC ID" = ConvertTo-TextValue $EpicId
    "EPIC NAME" = ConvertTo-TextValue $EpicName
    "BUCKET ID" = ConvertTo-TextValue $BucketId
    "BUCKET NAME" = ConvertTo-TextValue $BucketName
    "PACKET ID" = ConvertTo-TextValue $PacketId
    "PACKET NAME" = ConvertTo-TextValue $PacketName
    "MODE" = ConvertTo-TextValue $Mode
    "ZONE" = ConvertTo-TextValue $Zone
    "LANE" = ConvertTo-TextValue $Lane
    "WORKER IDENTITY" = ConvertTo-TextValue $WorkerIdentity
    "LOCK IDENTITY" = ConvertTo-TextValue $LockIdentity
    "WORKTREE" = ConvertTo-TextValue $Worktree
    "BRANCH" = ConvertTo-TextValue $Branch
    "APPROVAL AUTHORITY" = ConvertTo-TextValue $ApprovalAuthority
    "STOP POINT" = ConvertTo-TextValue $StopPoint
}
$allowed = ConvertTo-TextList $AllowedMutationFiles
$forbidden = ConvertTo-TextList $ForbiddenPaths
$readFirstValues = ConvertTo-TextList $ReadFirst
$validatorValues = ConvertTo-TextList $Validators

$missing = @()
foreach ($entry in $values.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace($entry.Value)) { $missing += $entry.Key }
    elseif (Test-UnresolvedValue $entry.Value) { $missing += $entry.Key }
}
if ($allowed.Count -eq 0) { $missing += "ALLOWED PATHS" }
if ($forbidden.Count -eq 0) { $missing += "FORBIDDEN PATHS" }
if ($validatorValues.Count -eq 0) { $missing += "VALIDATOR CHAIN" }
foreach ($entry in @($allowed + $forbidden + $readFirstValues + $validatorValues)) {
    if (Test-UnresolvedValue $entry) { $missing += "UNRESOLVED VALUE"; break }
}
$missing = @($missing | Select-Object -Unique)
$packetValid = $missing.Count -eq 0
$schemaText = "AIOS_CODEX_PACKET_GENERATOR.v2"

$generatedPacketText = ""
if ($packetValid) {
    $readFirstText = if ($readFirstValues.Count -gt 0) { Format-List $readFirstValues } else { "- AGENTS.md`n- README.md" }
    $generatedPacketText = @"
CODEX-ONLY PROMPT
AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
$($values['IDENTITY MARKER'])

SUPERVISOR IDENTITY:
$($values['SUPERVISOR IDENTITY'])

MISSION ID:
$($values['MISSION ID'])

MISSION NAME:
$($values['MISSION NAME'])

PROGRAM ID:
$($values['PROGRAM ID'])

PROGRAM NAME:
$($values['PROGRAM NAME'])

EPIC ID:
$($values['EPIC ID'])

EPIC NAME:
$($values['EPIC NAME'])

BUCKET ID:
$($values['BUCKET ID'])

BUCKET NAME:
$($values['BUCKET NAME'])

PACKET ID:
$($values['PACKET ID'])

PACKET NAME:
$($values['PACKET NAME'])

MODE:
$($values['MODE'])

ZONE:
$($values['ZONE'])

LANE:
$($values['LANE'])

WORKER IDENTITY:
$($values['WORKER IDENTITY'])

LOCK IDENTITY:
$($values['LOCK IDENTITY'])

WORKTREE:
$($values['WORKTREE'])

BRANCH:
$($values['BRANCH'])

APPROVAL AUTHORITY:
$($values['APPROVAL AUTHORITY'])

READ FIRST:
$readFirstText

ALLOWED PATHS:
$(Format-List $allowed)

FORBIDDEN PATHS:
$(Format-List $forbidden)

PREFLIGHT:
Run these read-only commands and resolve current state before mutation:
$(Format-List @($packetContract.state_discovery_commands))
Confirm the observed worktree and branch match this packet. Classify dirty files before mutation. On a mismatch, stop with AIOS-PROMPT-AUTH-STATE-MISMATCH. Do not switch branches or create a worktree.

IMPLEMENTATION:
Apply only the approved changes inside ALLOWED PATHS. APPLY does not authorize any protected publishing action. Validator PASS is evidence only.

VALIDATOR CHAIN:
$(Format-List $validatorValues)

STAGING AUTHORITY:
NOT AUTHORIZED

COMMIT AUTHORITY:
NOT AUTHORIZED

PUSH AUTHORITY:
NOT AUTHORIZED

PULL REQUEST AUTHORITY:
NOT AUTHORIZED

MERGE AUTHORITY:
NOT AUTHORIZED

STOP POINT:
$($values['STOP POINT'])

FINAL REPORT FORMAT:
Report summary, files created, files updated, exact validator results, remaining dirty files, resolved worktree, resolved branch, resolved HEAD, staging status, commit status, push status, pull request status, merge status, safe next action, and final status. Use the AGENTS.md success or failure headings. Stop without staging, commit, push, pull request, or merge.
"@
}

$result = [ordered]@{
    schema = $schemaText
    contract_schema = $packetContract.schema
    terminology_preference = $packetContract.terminology.preferred
    generated_packet_text = $generatedPacketText
    packet_valid = [bool]$packetValid
    missing_required_fields = @($missing)
    writes_files = $false
    execution_allowed = $false
    can_continue_without_anthony = $false
}

if ($OutputJson) { $result | ConvertTo-Json -Depth 20; exit 0 }
Write-Output $generatedPacketText
exit 0
