param(
    [string]$PacketText = "",
    [string]$PacketPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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
    return -not ($Text.Contains($Label))
}

function Find-MissingFields {
    param([string]$Text)

    $required = @(
        "AI_OS BOOTSTRAP REQUIRED",
        "IDENTITY MARKER",
        "SUPERVISOR IDENTITY",
        "WORKER IDENTITY",
        "ZONE",
        "LANE",
        "APPROVAL AUTHORITY",
        "BRANCH PLAN",
        "VALIDATOR CHAIN",
        "STOP POINT",
        "COMPLETION REPORT FORMAT"
    )

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
$packetValid = $missing.Count -eq 0

$result = [ordered]@{
    schema = "AIOS_CODEX_PACKET_VALIDATOR.v1"
    packet_valid = [bool]$packetValid
    missing_required_fields = @($missing)
    writes_files = $false
    execution_allowed = $false
    can_continue_without_anthony = $false
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 20)
