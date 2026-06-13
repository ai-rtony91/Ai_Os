param(
    [Parameter(Mandatory = $true)][string]$PacketId,
    [Parameter(Mandatory = $true)][string]$Branch,
    [string]$CodexReportText = "",
    [string]$CodexReportPath = "",
    [ValidateSet("DRY_RUN", "APPLY")][string]$Mode = "DRY_RUN",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-CodexReportText {
    param([string]$Text, [string]$Path)

    if (-not [string]::IsNullOrWhiteSpace($Text)) {
        return $Text
    }

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "CodexReportPath not found: $Path"
    }

    return (Get-Content -LiteralPath $Path -Raw)
}

function Extract-ListField {
    param([psobject]$Obj, [string]$Field)
    if (-not $Obj) {
        return @()
    }
    if (-not (Get-Member -InputObject $Obj -Name $Field -MemberType NoteProperty)) {
        return @()
    }
    $value = $Obj.$Field
    if ($null -eq $value) {
        return @()
    }
    if ($value -is [string]) {
        return @($value)
    }
    if ($value -is [System.Collections.IEnumerable]) {
        return @($value)
    }
    return @([string]$value)
}

function Parse-ReportPayload {
    param([string]$Raw)
    if ([string]::IsNullOrWhiteSpace($Raw)) {
        return [pscustomobject]@{
            packet_id = ""
            branch = ""
            commit_hash = ""
            files_changed = @()
            tests_run = ""
            tests_blocked = @()
            validation_claims = @()
            safety_claims = @()
            requested_next_action = ""
            raw = ""
        }
    }

    try {
        $parsed = $Raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return [pscustomobject]@{
            packet_id = ""
            branch = ""
            commit_hash = ""
            files_changed = @()
            tests_run = ""
            tests_blocked = @()
            validation_claims = @()
            safety_claims = @()
            requested_next_action = ""
            raw = $Raw
            parse_error = $_.Exception.Message
        }
    }

    return [pscustomobject]@{
        packet_id = if (Get-Member -InputObject $parsed -Name "packet_id" -MemberType NoteProperty) { [string]$parsed.packet_id } else { "" }
        branch = if (Get-Member -InputObject $parsed -Name "branch" -MemberType NoteProperty) { [string]$parsed.branch } else { "" }
        commit_hash = if (Get-Member -InputObject $parsed -Name "commit_hash" -MemberType NoteProperty) { [string]$parsed.commit_hash } else { "" }
        files_changed = if (Get-Member -InputObject $parsed -Name "files_changed" -MemberType NoteProperty) { Extract-ListField -Obj $parsed -Field "files_changed" } else { @() }
        tests_run = if (Get-Member -InputObject $parsed -Name "tests_run" -MemberType NoteProperty) { [string]$parsed.tests_run } else { "" }
        tests_blocked = if (Get-Member -InputObject $parsed -Name "tests_blocked" -MemberType NoteProperty) { Extract-ListField -Obj $parsed -Field "tests_blocked" } else { @() }
        validation_claims = if (Get-Member -InputObject $parsed -Name "validation_results" -MemberType NoteProperty) { Extract-ListField -Obj $parsed -Field "validation_results" } else { @("Repository write state check pending.") }
        safety_claims = if (Get-Member -InputObject $parsed -Name "safety_flags" -MemberType NoteProperty) { Extract-ListField -Obj $parsed -Field "safety_flags" } else { @("No broker/OANDA/webhook/order/secrets actions.") }
        requested_next_action = if (Get-Member -InputObject $parsed -Name "requested_next_action" -MemberType NoteProperty) { [string]$parsed.requested_next_action } else { "Await manual review and approved reviewed PowerShell command." }
        raw = $Raw
    }
}

$repoRoot = (Get-Location).Path
$relayDir = Join-Path $repoRoot "control/review_bridge/codex_reports"
if (-not (Test-Path -LiteralPath $repoRoot)) {
    throw "Repo root not found."
}

$safeMode = if ($Mode -eq "APPLY") { "APPLY" } else { "DRY_RUN" }
$isApply = ($safeMode -eq "APPLY")
$timestamp = (Get-Date).ToString("yyyy-MM-ddTHH-mm-ssZ")

$reportText = Read-CodexReportText -Text $CodexReportText -Path $CodexReportPath
$payload = Parse-ReportPayload -Raw $reportText
$reportPacketId = if ([string]::IsNullOrWhiteSpace($payload.packet_id)) { $PacketId } else { $payload.packet_id }

$relayItem = [ordered]@{
    packet_id = $PacketId
    branch = $Branch
    timestamp = (Get-Date).ToString("o")
    codex_packet_id = $reportPacketId
    commit_hash = $payload.commit_hash
    raw_report = $payload.raw
    files_changed = @($payload.files_changed)
    tests_run = $payload.tests_run
    tests_blocked = @($payload.tests_blocked)
    validation_claims = @($payload.validation_claims)
    safety_claims = @($payload.safety_claims)
    requested_next_action = $payload.requested_next_action
    writes_files = $isApply
    mode = $safeMode
}

$filePath = Join-Path $relayDir ("report_{0}.json" -f $timestamp.Replace(":", "-"))
$output = [ordered]@{
    schema = "AIOS_CODEX_RELAY_REPORT_ITEM.v1"
    mode = if ($isApply) { "APPLY" } else { "DRY_RUN_READ_ONLY" }
    packet_id = $PacketId
    branch = $Branch
    relay_file = $filePath
    writes_files = $isApply
    report_item = $relayItem
}

if ($isApply) {
    if (-not (Test-Path -LiteralPath $relayDir -PathType Container)) {
        New-Item -ItemType Directory -Path $relayDir -Force | Out-Null
    }
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    $jsonPayload = $relayItem | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($filePath, $jsonPayload, $utf8NoBOM)
}
else {
    $output.write_preview = $relayItem
}

if ($OutputJson) {
    $output | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($output | ConvertTo-Json -Depth 20)
