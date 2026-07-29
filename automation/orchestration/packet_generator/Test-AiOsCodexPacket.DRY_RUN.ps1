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
    if (-not [string]::IsNullOrWhiteSpace($Text)) { return $Text }
    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "PacketPath not found: $Path" }
    return Get-Content -LiteralPath $Path -Raw
}

function Get-SectionValue {
    param([string]$Text, [string]$Label)
    $lines = @(($Text -replace "`r`n", "`n" -replace "`r", "`n") -split "`n")
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index].Trim() -ne ($Label + ":")) { continue }
        $valueLines = @()
        for ($cursor = $index + 1; $cursor -lt $lines.Count; $cursor++) {
            $line = $lines[$cursor]
            if ($line.Trim() -match '^[A-Z][A-Z0-9 _/-]*:$') { break }
            $valueLines += $line
        }
        return ($valueLines -join "`n").Trim()
    }
    return $null
}

$rawPacketText = Read-Text -Text $PacketText -Path $PacketPath
$normalized = $rawPacketText -replace "`r`n", "`n" -replace "`r", "`n"
$defects = @()
$missing = @()

$firstLine = if ($normalized.Length -gt 0) { @($normalized -split "`n")[0] } else { "" }
if ($firstLine -cne $packetContract.first_line) { $defects += "FIRST LINE" }
foreach ($marker in @($packetContract.required_markers)) {
    if (-not (@($normalized -split "`n") -ccontains $marker)) { $missing += $marker }
}
foreach ($field in @($packetContract.required_fields)) {
    $value = Get-SectionValue -Text $normalized -Label $field
    if ($null -eq $value -or [string]::IsNullOrWhiteSpace($value)) { $missing += $field }
}
foreach ($pattern in @($packetContract.unresolved_value_patterns)) {
    if ($normalized -match $pattern) { $defects += "UNRESOLVED VALUE"; break }
}
$mode = Get-SectionValue -Text $normalized -Label "MODE"
if ($null -ne $mode -and $mode -notin @("DRY_RUN", "APPLY")) { $defects += "MODE" }
foreach ($command in @($packetContract.state_discovery_commands)) {
    if ($normalized.IndexOf($command, [System.StringComparison]::Ordinal) -lt 0) {
        $defects += "PREFLIGHT STATE DISCOVERY: $command"
    }
}
foreach ($field in @($packetContract.protected_action_fields)) {
    $value = Get-SectionValue -Text $normalized -Label $field
    if ($null -ne $value -and $value -cne "NOT AUTHORIZED") { $defects += $field }
}

$missing = @($missing | Select-Object -Unique)
$defects = @($defects | Select-Object -Unique)
$packetValid = $missing.Count -eq 0 -and $defects.Count -eq 0
$terminologyWarnings = @()
foreach ($term in @($packetContract.terminology.drift_terms)) {
    if ($normalized.IndexOf($term, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
        $terminologyWarnings += "Terminology drift: prefer software-engineering terminology over '$term' in new explanatory prose."
    }
}

$result = [ordered]@{
    schema = "AIOS_CODEX_PACKET_VALIDATOR.v2"
    contract_schema = $packetContract.schema
    packet_valid = [bool]$packetValid
    missing_required_fields = @($missing)
    validation_defects = @($defects)
    terminology_warnings = @($terminologyWarnings)
    writes_files = $false
    execution_allowed = $false
    protected_actions_authorized = $false
    can_continue_without_anthony = $false
}

$result | ConvertTo-Json -Depth 20
