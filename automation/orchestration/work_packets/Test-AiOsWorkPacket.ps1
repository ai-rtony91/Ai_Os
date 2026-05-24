param(
    [Parameter(Mandatory = $true)][string]$PacketPath,
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$scriptName = Split-Path -Leaf $PSCommandPath
$errors = @()
$result = "UNKNOWN"

if (-not (Test-Path -LiteralPath $PacketPath)) {
    Write-Host "ERROR: Packet file not found: $PacketPath" -ForegroundColor Red
    exit 1
}

$raw = $null
try {
    $raw = Get-Content -LiteralPath $PacketPath -Raw -ErrorAction Stop
} catch {
    Write-Host "ERROR: Cannot read packet file: $_" -ForegroundColor Red
    exit 1
}

$packet = $null
try {
    $packet = $raw | ConvertFrom-Json
} catch {
    Write-Host "ERROR: Packet file is not valid JSON: $_" -ForegroundColor Red
    exit 1
}

# Required field checks
$requiredStringFields = @("packet_id", "mode", "mission", "stop_condition")
foreach ($field in $requiredStringFields) {
    $val = $packet.$field
    if ($null -eq $val -or ($val -is [string] -and [string]::IsNullOrWhiteSpace($val))) {
        $errors += "MISSING_REQUIRED_FIELD: $field"
    }
}

# allowed_write_boundary must be a non-empty array or non-empty string
$awb = $packet.allowed_write_boundary
if ($null -eq $awb) {
    $errors += "MISSING_REQUIRED_FIELD: allowed_write_boundary"
} elseif ($awb -is [array] -and $awb.Count -eq 0) {
    $errors += "EMPTY_REQUIRED_FIELD: allowed_write_boundary must not be empty"
} elseif ($awb -is [string] -and [string]::IsNullOrWhiteSpace($awb)) {
    $errors += "EMPTY_REQUIRED_FIELD: allowed_write_boundary must not be empty"
}

# mode must be DRY_RUN or APPLY
if ($packet.mode -and $packet.mode -notin @("DRY_RUN", "APPLY")) {
    $errors += "INVALID_MODE: mode must be DRY_RUN or APPLY. Got: $($packet.mode)"
}

# Safety defaults: commit_allowed and push_allowed should be false
if ($packet.commit_allowed -eq $true) {
    $errors += "SAFETY_WARNING: commit_allowed is true. Verify this is intentional and human-approved."
}
if ($packet.push_allowed -eq $true) {
    $errors += "SAFETY_WARNING: push_allowed is true. Verify this is intentional and human-approved."
}

if ($errors.Count -eq 0) {
    $result = "VALID"
} else {
    $result = "INVALID"
}

$output = [pscustomobject]@{
    mode                   = "READ_ONLY"
    result                 = $result
    packet_id              = if ($packet.packet_id) { $packet.packet_id } else { "MISSING" }
    packet_mode            = if ($packet.mode) { $packet.mode } else { "MISSING" }
    commit_allowed         = if ($null -ne $packet.commit_allowed) { $packet.commit_allowed } else { "NOT_SET" }
    push_allowed           = if ($null -ne $packet.push_allowed) { $packet.push_allowed } else { "NOT_SET" }
    errors                 = $errors
    error_count            = $errors.Count
    packet_executed        = $false
    commit_performed       = $false
    push_performed         = $false
}

if ($QuietJson) {
    $output | ConvertTo-Json -Depth 4
    exit $(if ($errors.Count -gt 0) { 1 } else { 0 })
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Work Packet Validator" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY - validates packet definition, does not execute it"
Write-Host "Packet: $PacketPath"
Write-Host ""

if ($result -eq "VALID") {
    Write-Host "RESULT: VALID" -ForegroundColor Green
} else {
    Write-Host "RESULT: INVALID" -ForegroundColor Red
}

Write-Host "packet_id: $($output.packet_id)"
Write-Host "packet_mode: $($output.packet_mode)"
Write-Host "commit_allowed: $($output.commit_allowed)"
Write-Host "push_allowed: $($output.push_allowed)"

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Errors ($($errors.Count)):" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  $err" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Packet executed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")

exit $(if ($errors.Count -gt 0) { 1 } else { 0 })
