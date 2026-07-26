param(
    [string]$PacketText = "",
    [string]$PacketPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "AiOsCodexPacketContract.ps1")
$packetContract = Get-AiOsCodexPacketContract

function Read-Text {
    param([string]$Text, [string]$Path)
    if (-not [string]::IsNullOrWhiteSpace($Text)) {
        return $Text
    }
    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "PacketPath not found: $Path"
    }
    return (Get-Content -LiteralPath $Path -Raw)
}

function Missing-Field {
    param([string]$Text, [string]$Label)

    $normalized = $Text -replace "`r`n", "`n"
    $normalized = $normalized -replace "`r", "`n"
    $lines = @($normalized -split "`n")

    foreach ($line in $lines) {
        $trimmed = $line.Trim()

        if ($trimmed -eq $Label) {
            return $false
        }

        if ($trimmed.StartsWith($Label + ":")) {
            return $false
        }
    }

    return $true
}

function Find-MissingFields {
    param([string]$Text)

    $required = @($packetContract.required_fields)

    $missing = @()
    foreach ($field in $required) {
        if (Missing-Field -Text $Text -Label $field) {
            $missing += $field
        }
    }

    return @($missing)
}

$rawPacketText = Read-Text -Text $PacketText -Path $PacketPath
$missing = Find-MissingFields -Text $rawPacketText
$missing = @($missing)
$packetValid = $missing.Count -eq 0
$terminologyWarnings = @()
foreach ($term in @($packetContract.terminology.drift_terms)) {
    if ($rawPacketText.IndexOf($term, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
        $terminologyWarnings += "Terminology drift: prefer software-engineering terminology over '$term' in new explanatory prose."
    }
}

$result = [ordered]@{
    schema = "AIOS_CODEX_PACKET_VALIDATOR.v1"
    packet_valid = [bool]$packetValid
    missing_required_fields = @($missing)
    terminology_warnings = @($terminologyWarnings)
    writes_files = $false
    execution_allowed = $false
    can_continue_without_anthony = $false
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 20)
