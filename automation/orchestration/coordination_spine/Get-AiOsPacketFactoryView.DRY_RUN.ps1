[CmdletBinding()]
param(
    [string]$PacketRootPath = "automation/orchestration/work_packets",
    [string]$TemplateRootPath = "automation/orchestration/work_packets/templates",
    [string]$ProposedRootPath = "automation/orchestration/work_packets/proposed",
    [string]$ActiveRootPath = "automation/orchestration/work_packets/active",
    [string]$QueueIndexPath = "telemetry/coordination_spine/UNIFIED_QUEUE_INDEX.json",
    [string]$LockStatusPath = "telemetry/coordination_spine/UNIFIED_LOCK_STATUS.json",
    [string]$RecoveryViewPath = "telemetry/coordination_spine/RECOVERY_BOOTSTRAP_VIEW.json",
    [string]$LeadDispatchViewPath = "telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json",
    [string]$OutputPath = "telemetry/coordination_spine/PACKET_FACTORY_VIEW.json",
    [string[]]$DuplicateSearchRoots = @(),
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"
$AiOsPacketFactoryViewErrorTag = "packet_factory_view_uncaught_error"

trap {
    $errorMessage = if ($_ -and $_.Exception) { $_.Exception.Message } else { "unknown_error" }
    $fallback = [ordered]@{
        schema = "AIOS_PACKET_FACTORY_VIEW.v1"
        system = "AI_OS"
        mode = "DRY_RUN"
        generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        source_readers = @()
        packet_sources_scanned = @()
        duplicate_intent_findings = @()
        missing_required_fields = @()
        approval_required_items = @()
        packet_records = @()
        blockers = @($AiOsPacketFactoryViewErrorTag)
        warnings = @($errorMessage)
        queue_context_summary = [pscustomobject]@{ present = $false; packet_count = 0; normalized_state_counts = @{}; source_state_counts = @{} }
        lock_context_summary = [pscustomobject]@{ present = $false; held_locks_count = 0; stale_locks_count = 0; collision_count = 0; safety_status = "UNKNOWN"; write_behavior = "telemetry_only" }
        recovery_context_summary = [pscustomobject]@{ present = $false; recovery_readiness = "BLOCKED"; blockers = @(); warnings = @(); heartbeat_status = "UNKNOWN"; write_behavior = "telemetry_only" }
        lead_dispatch_context_summary = [pscustomobject]@{ present = $false; dispatcher_safety_verdict = "UNKNOWN"; blocked_reason = ""; depends_on_t2b = $false; next_safe_action = "" }
        packet_factory_safety_verdict = "ERROR"
        write_path_enabled = $false
        write_behavior = "telemetry_only"
        recommended_next_packet_action = "Inspect script error and rerun this packet factory view command."
        write_path = (Get-AiOsAbsolutePath -Path $OutputPath)
        error = $errorMessage
    }
    if ($Apply) {
        try {
            Write-AiOsAtomicJson -InputObject $fallback -DestinationPath $OutputPath | Out-Null
        }
        catch {
        }
    }

    ConvertTo-AiOsJsonSafely -InputObject $fallback -Depth 14
    exit 0
}
$AiOsReadBytesLimit = 262144
$AiOsDuplicateScanByteLimit = 65536
$AiOsDuplicateRootEntryLimit = 6
$AiOsDuplicateCandidateLimit = 200
$AiOsDuplicateMatchLimit = 80
$AiOsDuplicateScanBudgetMs = 6000
$AiOsPacketParsingBudgetMs = 4000
$AiOsJsonConvertBudgetMs = 4000

function Get-AiOsSafeTextFromFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][int]$MaxBytes
    )

    $fullPath = Get-AiOsAbsolutePath -Path $Path
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        return ""
    }

    $fileInfo = Get-Item -LiteralPath $fullPath
    if ($null -eq $fileInfo -or $fileInfo.Length -le 0) {
        return ""
    }

    $readLength = [Math]::Min([int]$fileInfo.Length, $MaxBytes)
    $bytes = New-Object byte[] $readLength
    $stream = [System.IO.File]::OpenRead($fullPath)
    try {
        $read = $stream.Read($bytes, 0, $readLength)
        if ($read -lt $bytes.Length) {
            $bytes = $bytes[0..([Math]::Max(0, $read - 1))]
        }
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    }
    finally {
        $stream.Close()
        $stream.Dispose()
    }
}

function ConvertTo-AiOsJsonSafely {
    param(
        [Parameter(Mandatory = $true)]$InputObject,
        [Parameter(Mandatory = $true)][int]$Depth
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $json = $InputObject | ConvertTo-Json -Depth $Depth
        if ($stopwatch.ElapsedMilliseconds -gt $AiOsJsonConvertBudgetMs) {
            return '{"schema":"AIOS_PACKET_FACTORY_VIEW.v1","write_behavior":"telemetry_only","system":"AI_OS","mode":"DRY_RUN","error":"json_output_timeout_guard_triggered"}'
        }
        return $json
    }
    finally {
        $stopwatch.Stop()
    }
}

function Get-AiOsAbsolutePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
}

function Test-AiOsTextFieldPresent {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$FieldName
    )

    $pattern = "(?im)^\s*$([regex]::Escape($FieldName))\s*:"
    return ($Text -match $pattern)
}

function Get-AiOsRequiredMarkdownFields {
    return @(
        "CODEX-ONLY PROMPT",
        "AI_OS EXECUTION TOKEN",
        "AI_OS BOOTSTRAP REQUIRED",
        "IDENTITY MARKER",
        "SUPERVISOR IDENTITY",
        "PACKET ID",
        "MODE",
        "ZONE",
        "WORKER IDENTITY",
        "LANE",
        "WORKTREE",
        "BRANCH",
        "APPROVAL AUTHORITY",
        "MISSION",
        "ALLOWED PATHS",
        "FORBIDDEN PATHS",
        "VALIDATOR CHAIN",
        "STOP POINT",
        "FINAL REPORT FORMAT"
    )
}

function Get-AiOsPacketTextValue {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$FieldName
    )

    $pattern = "(?im)^\s*$([regex]::Escape($FieldName))\s*:\s*(.+?)\s*$"
    if ($Text -match $pattern) {
        return $Matches[1].Trim()
    }

    return ""
}

function Test-AiOsNonEmptyValue {
    param([object]$Value)

    if ($null -eq $Value) {
        return $false
    }

    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $false
    }

    if ($text -match 'PLACEHOLDER') {
        return $false
    }

    return $true
}

function Get-AiOsJsonFieldValue {
    param(
        [Parameter(Mandatory = $true)][object]$Object,
        [Parameter(Mandatory = $true)][string]$FieldName
    )

    if ($Object.PSObject.Properties.Name -contains $FieldName) {
        return $Object.$FieldName
    }

    return $null
}

function Read-AiOsJsonContext {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][scriptblock]$Summarize
    )

    $fullPath = Get-AiOsAbsolutePath -Path $Path
    $exists = Test-Path -LiteralPath $fullPath -PathType Leaf
    $data = $null
    $recordsSeen = 0
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    if ($exists) {
        try {
            if ($stopwatch.ElapsedMilliseconds -lt $AiOsPacketParsingBudgetMs) {
                $raw = Get-AiOsSafeTextFromFile -Path $fullPath -MaxBytes $AiOsReadBytesLimit
                $data = $raw | ConvertFrom-Json
                if ($stopwatch.ElapsedMilliseconds -lt $AiOsJsonConvertBudgetMs) {
                    $recordsSeen = & $Summarize $data
                }
            }
        }
        catch {
            $data = [pscustomobject]@{
                error = $_.Exception.Message
            }
            $recordsSeen = 0
        }
    }

    return [pscustomobject]@{
        source = $Label
        path = $fullPath
        exists = $exists
        records_seen = $recordsSeen
        data = $data
    }
}

function Get-AiOsPacketSourceFiles {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath,
        [Parameter(Mandatory = $true)][string]$Filter,
        [Parameter(Mandatory = $true)][string]$SourceKind
    )

    $fullRoot = Get-AiOsAbsolutePath -Path $RootPath
    if (-not (Test-Path -LiteralPath $fullRoot -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $fullRoot -File -Filter $Filter -ErrorAction SilentlyContinue | ForEach-Object {
        [pscustomobject]@{
            file = $_.FullName
            source_kind = $SourceKind
        }
    })
}

function Get-AiOsMarkdownPacketRecord {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        $text = Get-AiOsSafeTextFromFile -Path $Path -MaxBytes $AiOsReadBytesLimit
        $text = if ($text -eq $null) { "" } else { $text.TrimEnd("`r", "`n") }
        $packetId = Get-AiOsPacketTextValue -Text $text -FieldName "PACKET ID"
        if (-not (Test-AiOsNonEmptyValue -Value $packetId)) {
            $packetId = [System.IO.Path]::GetFileNameWithoutExtension($Path)
        }

        $mode = Get-AiOsPacketTextValue -Text $text -FieldName "MODE"
        $title = Get-AiOsPacketTextValue -Text $text -FieldName "IDENTITY MARKER"
        if (-not (Test-AiOsNonEmptyValue -Value $title)) {
            $title = [System.IO.Path]::GetFileNameWithoutExtension($Path)
        }

        $requiredFields = Get-AiOsRequiredMarkdownFields
        $missingRequiredFields = @()
        foreach ($field in $requiredFields) {
            if (-not (Test-AiOsTextFieldPresent -Text $text -FieldName $field)) {
                $missingRequiredFields += $field
            }
        }

        $approvalRequired = $false
        if ($text -match '(?im)Human Owner approval' -or
            $text -match '(?im)separate explicit APPLY approval' -or
            $text -match '(?im)APPLY approval' -or
            $text -match '(?im)Validator PASS is evidence only' -or
            $text -match '(?im)draft') {
            $approvalRequired = $true
        }

        $duplicateNotes = @()
        if ($text -match '(?im)Get-AiOsPacketFactoryView' -or $text -match '(?im)PACKET_FACTORY_VIEW') {
            $duplicateNotes += "exact_packet_factory_owner_text"
        }
        if ($text -match '(?im)Packet Factory Unifier' -or $text -match '(?im)coordination_spine packet factory') {
            $duplicateNotes += "packet_factory_unifier_phrase"
        }

        $status = "READY"
        if ($duplicateNotes -contains "exact_packet_factory_owner_text") {
            $status = "BLOCKED"
        }
        elseif ($missingRequiredFields.Count -gt 0 -or $approvalRequired -or $duplicateNotes.Count -gt 0) {
            $status = "REVIEW_REQUIRED"
        }

        return [pscustomobject]@{
            file = $Path
            source_kind = "proposed"
            packet_id = $packetId
            title = $title
            mode = $mode
            status = $status
            missing_required_fields = @($missingRequiredFields)
            approval_required = $approvalRequired
            duplicate_notes = @($duplicateNotes | Sort-Object -Unique)
            source_text = $text
        }
    }
    catch {
        return [pscustomobject]@{
            file = $Path
            source_kind = "proposed"
            packet_id = [System.IO.Path]::GetFileNameWithoutExtension($Path)
            title = [System.IO.Path]::GetFileNameWithoutExtension($Path)
            mode = ""
            status = "REVIEW_REQUIRED"
            missing_required_fields = @("parse_error")
            approval_required = $true
            duplicate_notes = @()
            source_text = ""
        }
    }
}

function Get-AiOsJsonPacketRecord {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        $text = Get-AiOsSafeTextFromFile -Path $Path -MaxBytes $AiOsReadBytesLimit
        $packet = $text | ConvertFrom-Json
        $packetId = if (Test-AiOsNonEmptyValue -Value (Get-AiOsJsonFieldValue -Object $packet -FieldName "packet_id")) {
            [string](Get-AiOsJsonFieldValue -Object $packet -FieldName "packet_id")
        }
        else {
            [System.IO.Path]::GetFileNameWithoutExtension($Path)
        }

        $requiredFields = @(
            "packet_id",
            "task_id",
            "title",
            "intent",
            "mission",
            "mode",
            "owner_lane",
            "assigned_worker",
            "repo",
            "branch",
            "worktree",
            "status",
            "allowed_write_boundary",
            "blocked_paths",
            "forbidden_paths",
            "approval_authority",
            "validator_chain",
            "stop_condition",
            "commit_allowed",
            "push_allowed"
        )

        $missingRequiredFields = @()
        foreach ($field in $requiredFields) {
            $value = Get-AiOsJsonFieldValue -Object $packet -FieldName $field
            if (-not (Test-AiOsNonEmptyValue -Value $value)) {
                $missingRequiredFields += $field
            }
        }

        $approvalRequired = $false
        if ([string](Get-AiOsJsonFieldValue -Object $packet -FieldName "status") -in @("proposed", "draft")) {
            $approvalRequired = $true
        }

        $duplicateNotes = @()
        if ($text -match '(?im)Get-AiOsPacketFactoryView' -or $text -match '(?im)PACKET_FACTORY_VIEW') {
            $duplicateNotes += "exact_packet_factory_owner_text"
        }
        if ($text -match '(?im)Packet Factory Unifier' -or $text -match '(?im)coordination_spine packet factory') {
            $duplicateNotes += "packet_factory_unifier_phrase"
        }

        $status = "READY"
        if ($duplicateNotes -contains "exact_packet_factory_owner_text") {
            $status = "BLOCKED"
        }
        elseif ($missingRequiredFields.Count -gt 0 -or $approvalRequired -or $duplicateNotes.Count -gt 0) {
            $status = "REVIEW_REQUIRED"
        }

        return [pscustomobject]@{
            file = $Path
            source_kind = "active"
            packet_id = $packetId
            title = [string](Get-AiOsJsonFieldValue -Object $packet -FieldName "title")
            mode = [string](Get-AiOsJsonFieldValue -Object $packet -FieldName "mode")
            status = $status
            missing_required_fields = @($missingRequiredFields)
            approval_required = $approvalRequired
            duplicate_notes = @($duplicateNotes | Sort-Object -Unique)
            source_text = $text
        }
    }
    catch {
        return [pscustomobject]@{
            file = $Path
            source_kind = "active"
            packet_id = [System.IO.Path]::GetFileNameWithoutExtension($Path)
            title = ""
            mode = ""
            status = "REVIEW_REQUIRED"
            missing_required_fields = @("parse_error")
            approval_required = $true
            duplicate_notes = @()
            source_text = ""
        }
    }
}

function Get-AiOsDuplicateIntentFindings {
    param(
        [Parameter(Mandatory = $true)][array]$SearchRoots
    )

    $queries = @(
        @{ query = "Get-AiOsPacketFactoryView"; severity = "BLOCKED" },
        @{ query = "PACKET_FACTORY_VIEW"; severity = "BLOCKED" },
        @{ query = "module5_packet_factory"; severity = "BLOCKED" },
        @{ query = "Packet Factory Unifier"; severity = "REVIEW_REQUIRED" },
        @{ query = "coordination_spine packet factory"; severity = "REVIEW_REQUIRED" }
    )

    $findings = @()
    $overallStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    foreach ($entry in $queries) {
        $matches = @()
        $expandedRoots = @()
        foreach ($candidateRoot in @($SearchRoots)) {
            if ([string]::IsNullOrWhiteSpace($candidateRoot)) {
                continue
            }
            $expandedRoots += ($candidateRoot -split ",")
        }

        $expandedRoots = @($expandedRoots | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        foreach ($root in $expandedRoots) {
            if ($overallStopwatch.ElapsedMilliseconds -gt $AiOsDuplicateScanBudgetMs) {
                break
            }
            if ($AiOsDuplicateCandidateLimit -le 0) {
                continue
            }

            $rootPath = Get-AiOsAbsolutePath -Path $root.Trim()
            if (-not (Test-Path -LiteralPath $rootPath -PathType Container)) {
                continue
            }

            if ($root.Trim().Length -gt 0) {
                $queryStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
                $candidateFiles = @(Get-ChildItem -LiteralPath $rootPath -Recurse -File -ErrorAction SilentlyContinue |
                    Where-Object { $_.Extension -in @(".md", ".json", ".ps1", ".py") } |
                    Select-Object -First $AiOsDuplicateCandidateLimit)
            }
            else {
                $candidateFiles = @()
            }

            foreach ($candidateFile in $candidateFiles | Select-Object -First $AiOsDuplicateCandidateLimit) {
                if ($queryStopwatch.ElapsedMilliseconds -gt 2000) {
                    break
                }
                if ($candidateFile.Length -gt $AiOsDuplicateScanByteLimit) {
                    continue
                }
                try {
                    $candidateText = Get-AiOsSafeTextFromFile -Path $candidateFile.FullName -MaxBytes $AiOsDuplicateScanByteLimit
                    if ($candidateText.Contains($entry.query)) {
                        $matches += $candidateFile.FullName
                    }
                } catch {
                    continue
                }
            }
        }

        $matches = @($matches | Sort-Object -Unique)
        $status = "CLEAR"
        if ($matches.Count -gt 0) {
            $status = if ($entry.severity -eq "BLOCKED") { "BLOCKED" } else { "REVIEW_REQUIRED" }
        }

        $findings += [pscustomobject]@{
            query = $entry.query
            severity = $entry.severity
            match_count = $matches.Count
            matched_paths = @($matches)
            status = $status
        }
    }

    return @($findings)
}

function Write-AiOsAtomicJson {
    param(
        [Parameter(Mandatory = $true)]$InputObject,
        [Parameter(Mandatory = $true)][string]$DestinationPath
    )

    $destinationFull = Get-AiOsAbsolutePath -Path $DestinationPath
    $destinationDir = Split-Path -Parent $destinationFull
    if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }

    $tempPath = Join-Path $destinationDir ((Split-Path -Leaf $destinationFull) + ".tmp")
    $json = ConvertTo-AiOsJsonSafely -InputObject $InputObject -Depth 14
    [System.IO.File]::WriteAllText($tempPath, $json, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tempPath -Destination $destinationFull -Force
    return $destinationFull
}

$repoRoot = (Get-Location).Path
$queueContext = Read-AiOsJsonContext -Label "UNIFIED_QUEUE_INDEX.json" -Path $QueueIndexPath -Summarize {
    param($data)
    if ($data.PSObject.Properties.Name -contains "packet_count") { return [int]$data.packet_count }
    return 0
}
$lockContext = Read-AiOsJsonContext -Label "UNIFIED_LOCK_STATUS.json" -Path $LockStatusPath -Summarize {
    param($data)
    if ($data.PSObject.Properties.Name -contains "held_locks_count") { return [int]$data.held_locks_count }
    return 0
}
$recoveryContext = Read-AiOsJsonContext -Label "RECOVERY_BOOTSTRAP_VIEW.json" -Path $RecoveryViewPath -Summarize {
    param($data)
    if ($data.PSObject.Properties.Name -contains "recovery_readiness") { return 1 }
    return 0
}
$leadDispatchContext = Read-AiOsJsonContext -Label "LEAD_DISPATCH_VIEW.json" -Path $LeadDispatchViewPath -Summarize {
    param($data)
    if ($data.PSObject.Properties.Name -contains "dispatcher_safety_verdict") { return 1 }
    return 0
}

$templateFiles = @(Get-AiOsPacketSourceFiles -RootPath $TemplateRootPath -Filter "*.json" -SourceKind "template")
$proposedFiles = @(Get-AiOsPacketSourceFiles -RootPath $ProposedRootPath -Filter "*.md" -SourceKind "proposed")
$activeFiles = @(Get-AiOsPacketSourceFiles -RootPath $ActiveRootPath -Filter "*.json" -SourceKind "active")

$packetRecords = @()
foreach ($file in $proposedFiles) {
    $packetRecords += Get-AiOsMarkdownPacketRecord -Path $file.file
}
foreach ($file in $activeFiles) {
    $packetRecords += Get-AiOsJsonPacketRecord -Path $file.file
}

if ($DuplicateSearchRoots.Count -gt $AiOsDuplicateRootEntryLimit) {
    $DuplicateSearchRoots = @($DuplicateSearchRoots | Select-Object -First $AiOsDuplicateRootEntryLimit)
}

$duplicateSearchRoots = if (($DuplicateSearchRoots.Count + $ExtraDuplicateSearchRoots.Count) -gt 0) {
    @($DuplicateSearchRoots + $ExtraDuplicateSearchRoots | Select-Object -First $AiOsDuplicateRootEntryLimit)
} else {
    @(
        "automation/orchestration/work_packets/proposed",
        "automation/orchestration/work_packets/active",
        "automation/orchestration/work_packets/templates",
        "automation/orchestration/coordination_spine",
        "docs/governance",
        "docs/audits",
        "tests/orchestration"
    )
}

$duplicateIntentFindings = @(Get-AiOsDuplicateIntentFindings -SearchRoots $duplicateSearchRoots)

$missingRequiredFields = @()
foreach ($record in $packetRecords) {
    if ($record.missing_required_fields.Count -gt 0) {
        $missingRequiredFields += [pscustomobject]@{
            file = $record.file
            packet_id = $record.packet_id
            source_kind = $record.source_kind
            missing_fields = @($record.missing_required_fields)
        }
    }
}

$approvalRequiredItems = @()
foreach ($record in $packetRecords) {
    if ($record.approval_required -eq $true) {
        $approvalRequiredItems += [pscustomobject]@{
            file = $record.file
            packet_id = $record.packet_id
            source_kind = $record.source_kind
            reason = if ($record.source_kind -eq "proposed") { "proposed_packet_requires_human_apply_approval" } else { "draft_or_proposed_state_requires_review" }
        }
    }
}

$packetSourceCount = $templateFiles.Count + $proposedFiles.Count + $activeFiles.Count
$hasExactDuplicate = @($duplicateIntentFindings | Where-Object { $_.status -eq "BLOCKED" }).Count -gt 0
$hasReviewDuplicate = @($duplicateIntentFindings | Where-Object { $_.status -eq "REVIEW_REQUIRED" }).Count -gt 0
$hasMissingFields = $missingRequiredFields.Count -gt 0
$hasApprovalRequired = $approvalRequiredItems.Count -gt 0

$queueBlocked = $false
$lockBlocked = $false
$recoveryBlocked = $false
$leadDispatchBlocked = $false
$warnings = @()
$blockers = @()

if ($queueContext.exists -and $queueContext.data) {
    $queueData = $queueContext.data
    $queueBlocked = ([int]$queueData.normalized_state_counts.BLOCKED -gt 0)
    if ($queueBlocked) { $blockers += "queue_blocked" }
    if ([int]$queueData.normalized_state_counts.WAITING_APPROVAL -gt 0) { $warnings += "queue_waiting_approval" }
}
else {
    $warnings += "queue_context_unavailable"
}

if ($lockContext.exists -and $lockContext.data) {
    $lockData = $lockContext.data
    $lockBlocked = ([int]$lockData.collision_count -gt 0 -or [string]$lockData.safety_status -eq "REVIEW_REQUIRED")
    if ($lockBlocked) { $blockers += "lock_review_required_or_collision" }
}
else {
    $warnings += "lock_context_unavailable"
}

if ($recoveryContext.exists -and $recoveryContext.data) {
    $recoveryData = $recoveryContext.data
    $recoveryBlocked = ([string]$recoveryData.recovery_readiness -eq "BLOCKED")
    if ($recoveryBlocked) { $blockers += "recovery_blocked" }
}
else {
    $warnings += "recovery_context_unavailable"
}

if ($leadDispatchContext.exists -and $leadDispatchContext.data) {
    $leadData = $leadDispatchContext.data
    $leadDispatchBlocked = ([string]$leadData.dispatcher_safety_verdict -eq "BLOCKED")
    if ($leadDispatchBlocked) { $blockers += "lead_dispatch_blocked" }
}
else {
    $warnings += "lead_dispatch_context_unavailable"
}

foreach ($record in $packetRecords) {
    foreach ($note in @($record.duplicate_notes)) {
        if ($note -eq "exact_packet_factory_owner_text") {
            $blockers += "exact_packet_factory_duplicate:$($record.packet_id)"
        }
        elseif ($note -eq "packet_factory_unifier_phrase") {
            $warnings += "near_packet_factory_duplicate:$($record.packet_id)"
        }
    }
}

$blockers = @($blockers | Sort-Object -Unique)
$warnings = @($warnings | Sort-Object -Unique)

$packetFactorySafetyVerdict = "READY_TO_DRAFT"
if ($packetSourceCount -eq 0) {
    $packetFactorySafetyVerdict = "SAFE_NO_WORK"
}
elseif ($blockers.Count -gt 0) {
    $packetFactorySafetyVerdict = "BLOCKED"
}
elseif ($hasMissingFields -or $hasApprovalRequired -or $hasReviewDuplicate) {
    $packetFactorySafetyVerdict = "REVIEW_REQUIRED"
}

$recommendedNextPacketAction = switch ($packetFactorySafetyVerdict) {
    "SAFE_NO_WORK" { "No packet sources found; add a packet draft or template before requesting packet-factory recommendations." }
    "BLOCKED" { "Resolve queue, lock, recovery, or duplicate-intent blockers before proposing the next packet." }
    "REVIEW_REQUIRED" { "Review missing fields and human approval requirements before APPLY." }
    default { "Draft the next packet using the current templates and approval chain." }
}

$result = [ordered]@{
    schema = "AIOS_PACKET_FACTORY_VIEW.v1"
    system = "AI_OS"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    repo_root = $repoRoot
    source_readers = @(
        [pscustomobject]@{ source = "templates"; path = (Get-AiOsAbsolutePath -Path $TemplateRootPath); exists = (Test-Path -LiteralPath (Get-AiOsAbsolutePath -Path $TemplateRootPath) -PathType Container); records_seen = $templateFiles.Count }
        [pscustomobject]@{ source = "proposed"; path = (Get-AiOsAbsolutePath -Path $ProposedRootPath); exists = (Test-Path -LiteralPath (Get-AiOsAbsolutePath -Path $ProposedRootPath) -PathType Container); records_seen = $proposedFiles.Count }
        [pscustomobject]@{ source = "active"; path = (Get-AiOsAbsolutePath -Path $ActiveRootPath); exists = (Test-Path -LiteralPath (Get-AiOsAbsolutePath -Path $ActiveRootPath) -PathType Container); records_seen = $activeFiles.Count }
        $queueContext
        $lockContext
        $recoveryContext
        $leadDispatchContext
    )
    packet_sources_scanned = @(
        [pscustomobject]@{ source = "templates"; path = (Get-AiOsAbsolutePath -Path $TemplateRootPath); file_count = $templateFiles.Count; packet_count = 0 }
        [pscustomobject]@{ source = "proposed"; path = (Get-AiOsAbsolutePath -Path $ProposedRootPath); file_count = $proposedFiles.Count; packet_count = $proposedFiles.Count }
        [pscustomobject]@{ source = "active"; path = (Get-AiOsAbsolutePath -Path $ActiveRootPath); file_count = $activeFiles.Count; packet_count = $activeFiles.Count }
    )
    proposed_packet_count = $proposedFiles.Count
    active_packet_count = $activeFiles.Count
    packet_template_count = $templateFiles.Count
    packet_records = @($packetRecords)
    duplicate_intent_findings = @($duplicateIntentFindings)
    missing_required_fields = @($missingRequiredFields)
    approval_required_items = @($approvalRequiredItems)
    queue_context_summary = if ($queueContext.exists -and $queueContext.data) {
        [pscustomobject]@{
            present = $true
            packet_count = [int]$queueContext.data.packet_count
            normalized_state_counts = $queueContext.data.normalized_state_counts
            source_state_counts = $queueContext.data.source_state_counts
        }
    } else {
        [pscustomobject]@{
            present = $false
            packet_count = 0
            normalized_state_counts = @{}
            source_state_counts = @{}
        }
    }
    lock_context_summary = if ($lockContext.exists -and $lockContext.data) {
        [pscustomobject]@{
            present = $true
            held_locks_count = [int]$lockContext.data.held_locks_count
            stale_locks_count = [int]$lockContext.data.stale_locks_count
            collision_count = [int]$lockContext.data.collision_count
            safety_status = [string]$lockContext.data.safety_status
            write_behavior = [string]$lockContext.data.write_behavior
        }
    } else {
        [pscustomobject]@{
            present = $false
            held_locks_count = 0
            stale_locks_count = 0
            collision_count = 0
            safety_status = "UNKNOWN"
            write_behavior = "telemetry_only"
        }
    }
    recovery_context_summary = if ($recoveryContext.exists -and $recoveryContext.data) {
        [pscustomobject]@{
            present = $true
            recovery_readiness = [string]$recoveryContext.data.recovery_readiness
            blockers = @($recoveryContext.data.blockers)
            warnings = @($recoveryContext.data.warnings)
            heartbeat_status = [string]$recoveryContext.data.heartbeat_status
            write_behavior = [string]$recoveryContext.data.write_behavior
        }
    } else {
        [pscustomobject]@{
            present = $false
            recovery_readiness = "UNKNOWN"
            blockers = @()
            warnings = @()
            heartbeat_status = "UNKNOWN"
            write_behavior = "telemetry_only"
        }
    }
    lead_dispatch_context_summary = if ($leadDispatchContext.exists -and $leadDispatchContext.data) {
        [pscustomobject]@{
            present = $true
            dispatcher_safety_verdict = [string]$leadDispatchContext.data.dispatcher_safety_verdict
            blocked_reason = [string]$leadDispatchContext.data.blocked_reason
            depends_on_t2b = [bool]$leadDispatchContext.data.depends_on_t2b
            next_safe_action = [string]$leadDispatchContext.data.next_safe_action
        }
    } else {
        [pscustomobject]@{
            present = $false
            dispatcher_safety_verdict = "UNKNOWN"
            blocked_reason = ""
            depends_on_t2b = $false
            next_safe_action = ""
        }
    }
    packet_factory_safety_verdict = $packetFactorySafetyVerdict
    write_path_enabled = $false
    write_behavior = "telemetry_only"
    recommended_next_packet_action = $recommendedNextPacketAction
    blockers = @($blockers)
    warnings = @($warnings)
}

if ($Apply) {
    Write-AiOsAtomicJson -InputObject $result -DestinationPath $OutputPath | Out-Null
}

ConvertTo-AiOsJsonSafely -InputObject $result -Depth 14
