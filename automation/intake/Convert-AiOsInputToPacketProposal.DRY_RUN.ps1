[CmdletBinding()]
param(
    [string]$InputRoot = "inputs",
    [switch]$IncludeFixtures,
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

function ConvertTo-AiOsSlug {
    param([Parameter(Mandatory = $true)][string]$Value)

    $slug = $Value.ToLowerInvariant() -replace "[^a-z0-9]+", "-"
    $slug = $slug.Trim("-")
    if ([string]::IsNullOrWhiteSpace($slug)) { return "operator-input" }
    if ($slug.Length -gt 48) { return $slug.Substring(0, 48).Trim("-") }
    return $slug
}

function Get-AiOsHash {
    param([Parameter(Mandatory = $true)][string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha.ComputeHash($bytes)
    return ([BitConverter]::ToString($hash) -replace "-", "").ToLowerInvariant().Substring(0, 10)
}

function Test-AiOsPlaceholderText {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) { return $true }
    $trimmed = $Text.Trim()
    return ($trimmed -match "^(todo|tbd|placeholder|sample|example|lorem ipsum|\{.+\})$")
}

function Get-AiOsInputKind {
    param([Parameter(Mandatory = $true)][string]$Name)

    switch -Regex ($Name.ToLowerInvariant()) {
        "^morning_brief(\.txt)?$" { return "morning_brief" }
        "^operator_notes(\.txt)?$" { return "operator_notes" }
        "^next_action(\.txt)?$" { return "next_action" }
        "morning_brief_fixture.*\.txt$" { if ($IncludeFixtures) { return "morning_brief_fixture" } }
    }

    return ""
}

function Test-AiOsDuplicatePacket {
    param(
        [Parameter(Mandatory = $true)][string]$ContentHash,
        [Parameter(Mandatory = $true)][string]$PacketSlug
    )

    $roots = @(
        "automation/orchestration/work_packets/proposed",
        "automation/orchestration/work_packets/approved",
        "automation/orchestration/work_packets/active",
        "automation/orchestration/work_packets/complete",
        "automation/orchestration/work_packets/rejected"
    )

    foreach ($root in $roots) {
        $fullRoot = Resolve-AiOsPath -Path $root
        if (-not (Test-Path -LiteralPath $fullRoot -PathType Container)) { continue }

        foreach ($file in @(Get-ChildItem -LiteralPath $fullRoot -Filter "*.json" -File -ErrorAction SilentlyContinue)) {
            $raw = Get-Content -LiteralPath $file.FullName -Raw
            if ($raw -match [regex]::Escape($ContentHash) -or $raw -match [regex]::Escape($PacketSlug)) {
                return [pscustomobject]@{
                    duplicate = $true
                    path = $file.FullName
                }
            }
        }
    }

    return [pscustomobject]@{
        duplicate = $false
        path = ""
    }
}

$inputRootFull = Resolve-AiOsPath -Path $InputRoot
$pendingRoot = Join-Path $inputRootFull "pending"
$allowedNames = @("morning_brief.txt", "operator_notes.txt", "next_action.txt")
$files = @()

if (Test-Path -LiteralPath $pendingRoot -PathType Container) {
    $files += @(Get-ChildItem -LiteralPath $pendingRoot -Filter "*.txt" -File -ErrorAction SilentlyContinue)
}

if ($IncludeFixtures -and (Test-Path -LiteralPath $inputRootFull -PathType Container)) {
    $files += @(Get-ChildItem -LiteralPath $inputRootFull -Filter "*fixture*.txt" -File -ErrorAction SilentlyContinue)
}

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
$proposals = @()
$rejected = @()

foreach ($file in @($files | Sort-Object FullName -Unique)) {
    $kind = Get-AiOsInputKind -Name $file.Name
    if ([string]::IsNullOrWhiteSpace($kind)) {
        if ($allowedNames -notcontains $file.Name.ToLowerInvariant()) {
            $rejected += [pscustomobject]@{
                source_file = $file.FullName
                reason = "Unsupported input filename."
            }
        }
        continue
    }

    $text = Get-Content -LiteralPath $file.FullName -Raw
    if (Test-AiOsPlaceholderText -Text $text) {
        $rejected += [pscustomobject]@{
            source_file = $file.FullName
            reason = "Input is empty or placeholder content."
        }
        continue
    }

    $firstLine = @($text -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
    $titleSeed = if ($firstLine.Count -gt 0) { [string]$firstLine[0] } else { $kind }
    $slug = ConvertTo-AiOsSlug -Value $titleSeed
    $hash = Get-AiOsHash -Text $text
    $packetId = "$timestamp-$slug-$hash"
    $duplicate = Test-AiOsDuplicatePacket -ContentHash $hash -PacketSlug $slug

    if ($duplicate.duplicate) {
        $rejected += [pscustomobject]@{
            source_file = $file.FullName
            reason = "Duplicate packet intent detected."
            duplicate_path = $duplicate.path
        }
        continue
    }

    $proposals += [pscustomobject]@{
        schema = "AIOS_ORCHESTRATION_PACKET.v1"
        schema_version = "1.0.0"
        packet_id = $packetId
        title = "Packet proposal from $kind"
        objective = $titleSeed
        intent = $titleSeed
        source = [pscustomobject]@{
            input_kind = $kind
            input_file = $file.FullName
            content_hash = $hash
        }
        mode = "DRY_RUN"
        status = "PROPOSED"
        approved_by_human = $false
        commit_allowed = $false
        push_allowed = $false
        live_trading_allowed = $false
        broker_access_allowed = $false
        allowed_paths = @("automation/orchestration/", "automation/intake/", "inputs/")
        allowed_write_boundary = @("automation/orchestration/", "automation/intake/", "inputs/")
        blocked_paths = @("README.md", "AGENTS.md", "WHITEPAPER.md", "docs/", "apps/", "broker/", "OANDA/", "live trading paths", "API key paths", "secrets paths", ".codex_backups/")
        safety_rules = @("No autonomous execution.", "No APPLY without separate human approval.", "No worker execution.", "No commit.", "No push.")
        safety = [pscustomobject]@{
            approved_by_human = $false
            commit_allowed = $false
            push_allowed = $false
            live_trading_allowed = $false
            broker_access_allowed = $false
            autonomous_apply_allowed = $false
        }
        validation_commands = @(
            "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/work_packets/Test-AiOsPacketSchema.DRY_RUN.ps1 -PacketPath automation/orchestration/work_packets/proposed/$packetId.json -OutputJson"
        )
        validators = @(
            [pscustomobject]@{
                name = "packet_structural_validation"
                command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/work_packets/Test-AiOsPacketSchema.DRY_RUN.ps1 -PacketPath automation/orchestration/work_packets/proposed/$packetId.json -OutputJson"
                required = $true
            }
        )
        expected_output = "Structured packet proposal only; no execution."
        next_action = "Review packet proposal and create approval request preview."
        created_timestamp = $generatedAt
        created_utc = $generatedAt
    }
}

$result = [pscustomobject]@{
    schema = "AIOS_INPUT_TO_PACKET_PROPOSAL_PREVIEW.v1"
    mode = "DRY_RUN"
    input_root = $inputRootFull
    pending_root = $pendingRoot
    include_fixtures = [bool]$IncludeFixtures
    files_inspected = @($files).Count
    proposal_count = @($proposals).Count
    rejected_count = @($rejected).Count
    proposals = $proposals
    rejected = $rejected
    writes_performed = 0
    moves_performed = 0
    commit_performed = "NO"
    push_performed = "NO"
    next_safe_action = if (@($proposals).Count -gt 0) { "Review proposal JSON and run packet structural validation." } else { "Place a supported .txt file in inputs/pending/ or review rejected input reasons." }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Input To Packet Proposal Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Files inspected: $($result.files_inspected)"
Write-Host "Proposals: $($result.proposal_count)"
Write-Host "Rejected: $($result.rejected_count)"
Write-Host "Writes performed: 0"
Write-Host "Moves performed: 0"
Write-Host "Next safe action: $($result.next_safe_action)"
