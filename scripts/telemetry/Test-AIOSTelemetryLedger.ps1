param(
  [string]$LedgerPath = "telemetry/work_ledger.jsonl",

  [string]$RepoRoot = "."
)

$LegacyFields = @(
  "eventId",
  "eventType",
  "status",
  "ts",
  "system",
  "summary",
  "packetId",
  "approvalId",
  "risk"
)

$RequiredLegacyCoreFields = @(
  "eventId",
  "eventType",
  "ts",
  "source",
  "system",
  "summary"
)

$CanonicalFields = @(
  "event_id",
  "timestamp_utc",
  "event_type",
  "source",
  "actor",
  "lane",
  "repo_path",
  "branch",
  "mode",
  "authority_token",
  "authority_note",
  "input_reference",
  "output_reference",
  "result",
  "risk_level",
  "next_safe_action",
  "validation_status"
)

$RequiredCanonicalCoreFields = @(
  "event_id",
  "timestamp_utc",
  "event_type",
  "source",
  "result",
  "validation_status"
)

function Resolve-AIOSLedgerPath {
  param(
    [string]$Path,
    [string]$Root
  )

  $ResolvedRoot = [System.IO.Path]::GetFullPath($Root)

  if ([System.IO.Path]::IsPathRooted($Path)) {
    return [System.IO.Path]::GetFullPath($Path)
  }

  return [System.IO.Path]::GetFullPath((Join-Path -Path $ResolvedRoot -ChildPath $Path))
}

function Test-AIOSIsoTimestamp {
  param([object]$Value)

  if ($null -eq $Value -or -not ($Value -is [string]) -or [string]::IsNullOrWhiteSpace($Value)) {
    return $false
  }

  $Parsed = [DateTimeOffset]::MinValue
  return [DateTimeOffset]::TryParse($Value, [ref]$Parsed)
}

function Get-AIOSEventShape {
  param([object]$Event)

  if ($null -eq $Event -or -not ($Event -is [pscustomobject])) {
    return "unknown"
  }

  $Names = @($Event.PSObject.Properties.Name)
  $HasLegacyShape = @($LegacyFields | Where-Object { $Names -contains $_ }).Count -gt 0
  $HasCanonicalShape = @($CanonicalFields | Where-Object { $Names -contains $_ }).Count -gt 0

  if ($HasLegacyShape -and $HasCanonicalShape) {
    return "mixed"
  }

  if ($HasCanonicalShape) {
    return "canonical"
  }

  if ($HasLegacyShape) {
    return "legacy"
  }

  return "unknown"
}

function Test-AIOSStringField {
  param(
    [object]$Event,
    [string]$Field
  )

  $Names = @($Event.PSObject.Properties.Name)

  if (-not ($Names -contains $Field)) {
    return $false
  }

  return $Event.$Field -is [string] -and -not [string]::IsNullOrWhiteSpace($Event.$Field)
}

function Test-AIOSTelemetryEvent {
  param([object]$Event)

  $Warnings = [System.Collections.Generic.List[string]]::new()
  $Errors = [System.Collections.Generic.List[string]]::new()
  $MissingCanonicalFields = [System.Collections.Generic.List[string]]::new()

  if ($null -eq $Event -or -not ($Event -is [pscustomobject])) {
    foreach ($Field in $CanonicalFields) {
      $MissingCanonicalFields.Add($Field)
    }

    return [pscustomobject]@{
      isValid = $false
      shape = "unknown"
      warnings = @($Warnings)
      errors = @("Telemetry event must be a JSON object.")
      missingCanonicalFields = @($MissingCanonicalFields)
    }
  }

  $Names = @($Event.PSObject.Properties.Name)
  $Shape = Get-AIOSEventShape -Event $Event

  foreach ($Field in $CanonicalFields) {
    if (-not ($Names -contains $Field)) {
      $MissingCanonicalFields.Add($Field)
    }
  }

  if ($Shape -eq "unknown") {
    $Errors.Add("Telemetry event does not match legacy camelCase or canonical snake_case shape.")
  }

  if ($Shape -eq "legacy" -or $Shape -eq "mixed") {
    $MissingLegacyCoreFields = @($RequiredLegacyCoreFields | Where-Object { -not ($Names -contains $_) })

    if ($MissingLegacyCoreFields.Count -gt 0) {
      $Errors.Add("Legacy telemetry event is missing required field(s): $($MissingLegacyCoreFields -join ', ').")
    }

    foreach ($Field in $RequiredLegacyCoreFields) {
      if (($Names -contains $Field) -and -not (Test-AIOSStringField -Event $Event -Field $Field)) {
        $Errors.Add("$Field must be a non-empty string when present.")
      }
    }

    if (($Names -contains "ts") -and -not (Test-AIOSIsoTimestamp -Value $Event.ts)) {
      $Errors.Add("Legacy telemetry ts must be an ISO 8601 timestamp.")
    }

    if (($Names -contains "system") -and $Event.system -ne "AI_OS") {
      $Errors.Add("Legacy telemetry system must be AI_OS.")
    }

    if ($MissingCanonicalFields.Count -gt 0) {
      $Warnings.Add("Event uses legacy camelCase telemetry fields and is missing canonical snake_case fields.")
    }
  }

  if ($Shape -eq "canonical" -or $Shape -eq "mixed") {
    $MissingCanonicalCoreFields = @($RequiredCanonicalCoreFields | Where-Object { -not ($Names -contains $_) })

    if ($MissingCanonicalCoreFields.Count -gt 0) {
      $Errors.Add("Canonical telemetry event is missing required core field(s): $($MissingCanonicalCoreFields -join ', ').")
    }

    foreach ($Field in $RequiredCanonicalCoreFields) {
      if (($Names -contains $Field) -and -not (Test-AIOSStringField -Event $Event -Field $Field)) {
        $Errors.Add("$Field must be a non-empty string when present.")
      }
    }

    if (($Names -contains "timestamp_utc") -and -not (Test-AIOSIsoTimestamp -Value $Event.timestamp_utc)) {
      $Errors.Add("Canonical telemetry timestamp_utc must be an ISO 8601 timestamp.")
    }

    if ($MissingCanonicalFields.Count -gt 0) {
      $Warnings.Add("Canonical telemetry event is missing target field(s): $($MissingCanonicalFields -join ', ').")
    }
  }

  if ($Shape -eq "mixed") {
    $Warnings.Add("Event contains both legacy camelCase and canonical snake_case telemetry fields.")
  }

  return [pscustomobject]@{
    isValid = $Errors.Count -eq 0
    shape = $Shape
    warnings = @($Warnings)
    errors = @($Errors)
    missingCanonicalFields = @($MissingCanonicalFields)
  }
}

$ResolvedLedgerPath = Resolve-AIOSLedgerPath -Path $LedgerPath -Root $RepoRoot

if (-not (Test-Path -LiteralPath $ResolvedLedgerPath)) {
  [pscustomobject]@{
    ledgerPath = $ResolvedLedgerPath
    totalLines = 0
    validEventLines = 0
    invalidJsonLines = 0
    legacyEvents = 0
    canonicalEvents = 0
    mixedEvents = 0
    unknownEvents = 0
    schemaWarnings = 0
    schemaErrors = 0
    finalStatus = "NO_LEDGER"
    nextSafeAction = "No telemetry ledger found. No mutation performed."
  } | Format-List
  exit 0
}

$Lines = @(Get-Content -LiteralPath $ResolvedLedgerPath)
$NonEmptyLines = @($Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

if ($NonEmptyLines.Count -eq 0) {
  [pscustomobject]@{
    ledgerPath = $ResolvedLedgerPath
    totalLines = 0
    validEventLines = 0
    invalidJsonLines = 0
    legacyEvents = 0
    canonicalEvents = 0
    mixedEvents = 0
    unknownEvents = 0
    schemaWarnings = 0
    schemaErrors = 0
    finalStatus = "EMPTY_LEDGER"
    nextSafeAction = "Telemetry ledger is empty. No mutation performed."
  } | Format-List
  exit 0
}

$ValidEventLines = 0
$InvalidJsonLines = 0
$SchemaWarnings = 0
$SchemaErrors = 0
$LegacyEvents = 0
$CanonicalEvents = 0
$MixedEvents = 0
$UnknownEvents = 0
$IssueRows = [System.Collections.Generic.List[object]]::new()
$LineNumber = 0

foreach ($Line in $Lines) {
  $LineNumber += 1

  if ([string]::IsNullOrWhiteSpace($Line)) {
    continue
  }

  try {
    $Event = $Line | ConvertFrom-Json
  } catch {
    $InvalidJsonLines += 1
    $SchemaErrors += 1
    $IssueRows.Add([pscustomobject]@{
      line = $LineNumber
      severity = "error"
      shape = "unknown"
      message = "Invalid JSON line."
    })
    continue
  }

  $Result = Test-AIOSTelemetryEvent -Event $Event

  switch ($Result.shape) {
    "legacy" { $LegacyEvents += 1 }
    "canonical" { $CanonicalEvents += 1 }
    "mixed" { $MixedEvents += 1 }
    default { $UnknownEvents += 1 }
  }

  if ($Result.isValid) {
    $ValidEventLines += 1
  }

  foreach ($Warning in $Result.warnings) {
    $SchemaWarnings += 1
    $IssueRows.Add([pscustomobject]@{
      line = $LineNumber
      severity = "warning"
      shape = $Result.shape
      message = $Warning
    })
  }

  foreach ($ErrorMessage in $Result.errors) {
    $SchemaErrors += 1
    $IssueRows.Add([pscustomobject]@{
      line = $LineNumber
      severity = "error"
      shape = $Result.shape
      message = $ErrorMessage
    })
  }
}

$FinalStatus = if ($InvalidJsonLines -gt 0 -or $SchemaErrors -gt 0) {
  "FAIL"
} elseif ($SchemaWarnings -gt 0) {
  "WARN"
} else {
  "PASS"
}

$NextSafeAction = if ($FinalStatus -eq "FAIL") {
  "Review invalid JSON or hard schema errors. Do not edit prior ledger history; emit corrective evidence only through an approved writer lane."
} elseif ($FinalStatus -eq "WARN") {
  "Treat legacy or mixed telemetry as evidence-only. Do not wire dashboard, queue, or runtime decisions to telemetry yet."
} else {
  "Use this as read-only audit evidence. Telemetry remains evidence-only until separately approved for wiring."
}

[pscustomobject]@{
  ledgerPath = $ResolvedLedgerPath
  totalLines = $NonEmptyLines.Count
  validEventLines = $ValidEventLines
  invalidJsonLines = $InvalidJsonLines
  legacyEvents = $LegacyEvents
  canonicalEvents = $CanonicalEvents
  mixedEvents = $MixedEvents
  unknownEvents = $UnknownEvents
  schemaWarnings = $SchemaWarnings
  schemaErrors = $SchemaErrors
  finalStatus = $FinalStatus
  nextSafeAction = $NextSafeAction
} | Format-List

if ($IssueRows.Count -gt 0) {
  $IssueRows | Format-Table -AutoSize
}

if ($FinalStatus -eq "FAIL") {
  exit 1
}

exit 0
