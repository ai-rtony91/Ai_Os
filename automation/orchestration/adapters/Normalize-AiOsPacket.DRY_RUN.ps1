param(
    [string]$PacketPath = "automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Read-AiOsJsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolvedPath = Resolve-AiOsPath -Path $Path
    if (-not (Test-Path -LiteralPath $resolvedPath -PathType Leaf)) {
        throw "Packet file not found: $resolvedPath"
    }

    return Get-Content -Raw -LiteralPath $resolvedPath | ConvertFrom-Json
}

function Test-Property {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    return $null -ne ($Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1)
}

function Get-ValueOrDefault {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        $Default
    )

    if (Test-Property -Object $Object -Name $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return $value
        }
    }

    return $Default
}

function ConvertTo-Array {
    param($Value)

    if ($null -eq $Value) {
        return @()
    }

    if ($Value -is [array]) {
        return @($Value | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    }

    if ([string]::IsNullOrWhiteSpace([string]$Value)) {
        return @()
    }

    return @([string]$Value)
}

function Add-FieldMapping {
    param(
        [ref]$Mappings,
        [string]$SourceField,
        [string]$TargetField,
        [bool]$SourceValuePresent,
        [bool]$Lossy,
        [string]$Note
    )

    $Mappings.Value += [pscustomobject]@{
        source_field = $SourceField
        target_field = $TargetField
        source_value_present = $SourceValuePresent
        lossy = $Lossy
        note = $Note
    }
}

function Get-AiOsPacketDialect {
    param([Parameter(Mandatory = $true)]$Packet)

    $canonicalFields = @("id", "version", "title", "lane", "mode", "status", "objective")
    $legacyFields = @("packet_id", "intent", "owner_lane", "assigned_worker", "related_files", "validator")
    $queueFields = @("source_file", "approval_state", "validator_state", "blocked_reason")

    $canonicalMatches = @($canonicalFields | Where-Object { Test-Property -Object $Packet -Name $_ })
    $legacyMatches = @($legacyFields | Where-Object { Test-Property -Object $Packet -Name $_ })
    $queueMatches = @($queueFields | Where-Object { Test-Property -Object $Packet -Name $_ })

    if ($canonicalMatches.Count -eq $canonicalFields.Count) {
        return "canonical_work_packet_v1"
    }

    if ($legacyMatches.Count -gt 0) {
        return "legacy_orchestration_packet_template"
    }

    if ($queueMatches.Count -gt 0) {
        return "queue_packet_entry"
    }

    return "unknown_packet"
}

function Convert-Status {
    param(
        [string]$Dialect,
        [string]$Status,
        [ref]$Warnings
    )

    if ($Dialect -eq "canonical_work_packet_v1") {
        if (@("READY_FOR_DRY_RUN", "READY_FOR_APPLY", "BLOCKED", "REVIEW") -contains $Status) {
            return $Status
        }
        $Warnings.Value += "Canonical packet has an unexpected status; simulated status set to REVIEW."
        return "REVIEW"
    }

    switch ($Status) {
        "blocked" { return "BLOCKED" }
        "complete" { return "REVIEW" }
        "active" { return "READY_FOR_DRY_RUN" }
        "pending" { return "READY_FOR_DRY_RUN" }
        "approved" { return "READY_FOR_DRY_RUN" }
        "dispatched" { return "REVIEW" }
        "validating" { return "REVIEW" }
        default {
            $Warnings.Value += "Legacy status was missing or unknown; simulated status set to REVIEW."
            return "REVIEW"
        }
    }
}

$resolvedPacketPath = Resolve-AiOsPath -Path $PacketPath
$packet = Read-AiOsJsonFile -Path $PacketPath
$dialect = Get-AiOsPacketDialect -Packet $packet
$warnings = @()
$lossyWarnings = @()
$mappings = @()
$missingFields = @()

if ($resolvedPacketPath.Replace("\", "/") -match "/schemas/aios/orchestration/") {
    throw "Blocked path: this DRY_RUN adapter must not touch schemas/aios/orchestration/."
}

$packetId = Get-ValueOrDefault -Object $packet -Name "id" -Default (Get-ValueOrDefault -Object $packet -Name "packet_id" -Default "UNKNOWN_PACKET_ID")
$title = Get-ValueOrDefault -Object $packet -Name "title" -Default "Legacy packet normalization preview"
$lane = Get-ValueOrDefault -Object $packet -Name "lane" -Default (Get-ValueOrDefault -Object $packet -Name "owner_lane" -Default "operator_review")
$mode = Get-ValueOrDefault -Object $packet -Name "mode" -Default "DRY_RUN"
if ($mode -ne "DRY_RUN") {
    $warnings += "Source packet mode was '$mode'; adapter preview forces DRY_RUN for safety."
    $mode = "DRY_RUN"
}

$sourceStatus = [string](Get-ValueOrDefault -Object $packet -Name "status" -Default "")
$canonicalStatus = Convert-Status -Dialect $dialect -Status $sourceStatus -Warnings ([ref]$warnings)
$objective = Get-ValueOrDefault -Object $packet -Name "objective" -Default (Get-ValueOrDefault -Object $packet -Name "intent" -Default "Review legacy packet fields before canonical conversion.")

$allowedActions = @(ConvertTo-Array -Value (Get-ValueOrDefault -Object $packet -Name "allowed_actions" -Default @()))
if ($allowedActions.Count -eq 0) {
    $allowedActions = @("inspect packet", "simulate normalization", "report warnings")
    $missingFields += "allowed_actions"
}

$blockedActions = @(ConvertTo-Array -Value (Get-ValueOrDefault -Object $packet -Name "blocked_actions" -Default @()))
$blockedActions += @("dispatcher edit", "runtime integration", "commit", "push", "broker connection", "live trading", "API key access", "webhook execution")
$blockedActions = @($blockedActions | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique)

$filesInScope = @(ConvertTo-Array -Value (Get-ValueOrDefault -Object $packet -Name "files_in_scope" -Default (Get-ValueOrDefault -Object $packet -Name "related_files" -Default @())))
if ($filesInScope.Count -eq 0) {
    $filesInScope = @("UNKNOWN")
    $missingFields += "files_in_scope"
    $warnings += "No file scope was found; files_in_scope set to UNKNOWN."
}

$validators = @(ConvertTo-Array -Value (Get-ValueOrDefault -Object $packet -Name "validators" -Default (Get-ValueOrDefault -Object $packet -Name "validator" -Default @())))
if ($validators.Count -eq 0) {
    $validators = @("git diff --check")
    $missingFields += "validators"
    $warnings += "No validators were found; defaulted to git diff --check for DRY_RUN review only."
}

$risks = @(ConvertTo-Array -Value (Get-ValueOrDefault -Object $packet -Name "risks" -Default (Get-ValueOrDefault -Object $packet -Name "blocked_by" -Default @())))
if ($risks.Count -eq 0) {
    $risks = @("legacy packet may omit canonical required fields")
    $missingFields += "risks"
}

$stopCondition = Get-ValueOrDefault -Object $packet -Name "stop_condition" -Default "Stop after DRY_RUN adapter report."
if ($stopCondition -eq "Stop after DRY_RUN adapter report.") {
    $missingFields += "stop_condition"
}

$approvalRequired = $true
if (Test-Property -Object $packet -Name "approval_required") {
    $approvalRequired = [bool]$packet.approval_required
} else {
    $missingFields += "approval_required"
}

$createdBy = Get-ValueOrDefault -Object $packet -Name "created_by" -Default "Codex"
if ($createdBy -eq "Codex" -and -not (Test-Property -Object $packet -Name "created_by")) {
    $missingFields += "created_by"
}

$notes = @(ConvertTo-Array -Value (Get-ValueOrDefault -Object $packet -Name "notes" -Default @()))
$notes += "Detected dialect: $dialect"
$notes += "Source packet path: $PacketPath"

Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "id/packet_id" -TargetField "id" -SourceValuePresent ($packetId -ne "UNKNOWN_PACKET_ID") -Lossy $false -Note "Canonical id is preferred; legacy packet_id is accepted."
Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "title" -TargetField "title" -SourceValuePresent (Test-Property -Object $packet -Name "title") -Lossy $false -Note "Missing title becomes a generic normalization preview title."
Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "owner_lane/lane" -TargetField "lane" -SourceValuePresent (-not [string]::IsNullOrWhiteSpace([string]$lane)) -Lossy $false -Note "Legacy owner_lane may not exactly match canonical lane meaning."
Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "intent/objective" -TargetField "objective" -SourceValuePresent (-not [string]::IsNullOrWhiteSpace([string]$objective)) -Lossy $false -Note "Legacy intent maps to canonical objective."
Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "related_files/files_in_scope" -TargetField "files_in_scope" -SourceValuePresent ($filesInScope[0] -ne "UNKNOWN") -Lossy $false -Note "Legacy related_files maps to canonical files_in_scope."
Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "validator/validators" -TargetField "validators" -SourceValuePresent ($validators[0] -ne "git diff --check" -or (Test-Property -Object $packet -Name "validator") -or (Test-Property -Object $packet -Name "validators")) -Lossy $false -Note "Single validator strings become validator arrays."
$hasBlockedByOrRisks = ((Test-Property -Object $packet -Name "blocked_by") -or (Test-Property -Object $packet -Name "risks"))
Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "blocked_by/risks" -TargetField "risks" -SourceValuePresent $hasBlockedByOrRisks -Lossy $true -Note "blocked_by is current state, not a complete risk inventory."

if (Test-Property -Object $packet -Name "assigned_worker") {
    $lossyWarnings += "assigned_worker is preserved in notes only; canonical packet schema does not carry worker assignment."
    $notes += "Legacy assigned_worker: $($packet.assigned_worker)"
    Add-FieldMapping -Mappings ([ref]$mappings) -SourceField "assigned_worker" -TargetField "notes" -SourceValuePresent $true -Lossy $true -Note "Assignment ownership is not part of canonical work packet schema."
}

foreach ($field in @("repo", "branch", "priority", "created_utc", "updated_utc", "next_action", "source_file", "approval_state", "validator_state", "blocked_reason")) {
    if (Test-Property -Object $packet -Name $field) {
        $value = $packet.$field
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            $lossyWarnings += "$field is preserved in notes only."
            $notes += "Legacy $field`: $value"
            Add-FieldMapping -Mappings ([ref]$mappings) -SourceField $field -TargetField "notes" -SourceValuePresent $true -Lossy $true -Note "No direct canonical field exists."
        }
    }
}

if ($dialect -eq "legacy_orchestration_packet_template") {
    $warnings += "Legacy packet template detected; review lane, status, assignment, repo, and branch fields before any APPLY conversion."
}
if ($dialect -eq "queue_packet_entry") {
    $warnings += "Queue packet entry detected; queue runtime fields are not the same as canonical packet contract fields."
}
if ($dialect -eq "unknown_packet") {
    $warnings += "Unknown packet dialect detected; adapter produced REVIEW-only preview."
}

$canonicalPacket = [pscustomobject]@{
    id = [string]$packetId
    version = [string](Get-ValueOrDefault -Object $packet -Name "version" -Default "1.0")
    title = [string]$title
    lane = [string]$lane
    mode = "DRY_RUN"
    status = $canonicalStatus
    objective = [string]$objective
    allowed_actions = $allowedActions
    blocked_actions = $blockedActions
    files_in_scope = $filesInScope
    validators = $validators
    risks = $risks
    stop_condition = [string]$stopCondition
    approval_required = $approvalRequired
    created_by = [string]$createdBy
    notes = @($notes | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
}

$lossyCount = @($mappings | Where-Object { $_.lossy }).Count
$result = [pscustomobject]@{
    task = "Simulate AI_OS packet normalization"
    mode = "DRY_RUN"
    adapter = "Normalize-AiOsPacket.DRY_RUN.ps1"
    source_packet_path = $PacketPath
    resolved_source_packet_path = $resolvedPacketPath
    detected_dialect = $dialect
    canonical_status = $canonicalStatus
    normalization_summary = [pscustomobject]@{
        mapped_field_count = $mappings.Count
        missing_field_count = $missingFields.Count
        warning_count = $warnings.Count
        lossy_conversion_count = $lossyCount
    }
    field_mappings = $mappings
    missing_fields = @($missingFields | Sort-Object -Unique)
    normalization_warnings = @($warnings | Sort-Object -Unique)
    lossy_conversion_warnings = @($lossyWarnings | Sort-Object -Unique)
    canonical_packet_preview = $canonicalPacket
    safety = [pscustomobject]@{
        writes_performed = 0
        dispatcher_edits = "NO"
        runtime_integration = "NO"
        commits_performed = 0
        pushes_performed = 0
        broker_or_live_api_work = "NO"
    }
    validator_friendly = $true
    next_safe_action = "Review warnings and keep normalization simulation-only until an explicit APPLY packet is approved."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Packet Adapter"
Write-Host "Mode: DRY_RUN"
Write-Host "Packet: $PacketPath"
Write-Host "Detected dialect: $dialect"
Write-Host "Canonical status preview: $canonicalStatus"
Write-Host ""
Write-Host "Summary:"
Write-Host "  Mapped fields: $($result.normalization_summary.mapped_field_count)"
Write-Host "  Missing fields: $($result.normalization_summary.missing_field_count)"
Write-Host "  Warnings: $($result.normalization_summary.warning_count)"
Write-Host "  Lossy conversions: $($result.normalization_summary.lossy_conversion_count)"
Write-Host ""
Write-Host "Field mapping examples:"
foreach ($mapping in $mappings) {
    $lossyLabel = if ($mapping.lossy) { "LOSSY" } else { "OK" }
    Write-Host "  - $($mapping.source_field) -> $($mapping.target_field) [$lossyLabel]"
}
Write-Host ""
Write-Host "Normalization warnings:"
if ($warnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in ($warnings | Sort-Object -Unique)) {
        Write-Host "  - $warning"
    }
}
Write-Host ""
Write-Host "Lossy-conversion warnings:"
if ($lossyWarnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in ($lossyWarnings | Sort-Object -Unique)) {
        Write-Host "  - $warning"
    }
}
Write-Host ""
Write-Host "Validator note: no files were changed; this adapter is simulation-only."
Write-Host "Next safe action: $($result.next_safe_action)"
