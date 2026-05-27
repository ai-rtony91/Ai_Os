[CmdletBinding()]
param(
    [string]$PacketPath = "",
    [string]$PacketJson = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Add-AiOsFinding {
    param(
        [System.Collections.Generic.List[object]]$Findings,
        [string]$Severity,
        [string]$CheckId,
        [string]$Message,
        [object]$Evidence = $null
    )

    $Findings.Add([pscustomobject]@{
        severity = $Severity
        check_id = $CheckId
        message = $Message
        evidence = $Evidence
    }) | Out-Null
}

function Get-AiOsProp {
    param($Object, [string[]]$Names)

    foreach ($name in $Names) {
        if ($null -ne $Object -and $Object.PSObject.Properties.Name -contains $name) {
            return $Object.$name
        }
    }
    return $null
}

if ([string]::IsNullOrWhiteSpace($PacketJson)) {
    if ([string]::IsNullOrWhiteSpace($PacketPath) -or -not (Test-Path -LiteralPath $PacketPath -PathType Leaf)) {
        throw "PacketPath is required when PacketJson is not supplied."
    }
    $PacketJson = Get-Content -LiteralPath $PacketPath -Raw
}

$findings = [System.Collections.Generic.List[object]]::new()
$packet = $null

try {
    $packet = $PacketJson | ConvertFrom-Json
}
catch {
    Add-AiOsFinding -Findings $findings -Severity "BLOCKED" -CheckId "json_parse" -Message "Packet JSON could not parse." -Evidence $_.Exception.Message
}

if ($null -ne $packet) {
    foreach ($field in @("packet_id", "objective", "mode", "status", "blocked_paths", "validation_commands", "expected_output")) {
        $value = Get-AiOsProp -Object $packet -Names @($field)
        if ($null -eq $value -or [string]::IsNullOrWhiteSpace([string]$value)) {
            Add-AiOsFinding -Findings $findings -Severity "BLOCKED" -CheckId "missing_$field" -Message "Required packet field is missing or empty." -Evidence $field
        }
    }

    $allowedPaths = @(Get-AiOsProp -Object $packet -Names @("allowed_paths", "allowed_write_boundary"))
    if ($allowedPaths.Count -eq 0 -or [string]::IsNullOrWhiteSpace([string]$allowedPaths[0])) {
        Add-AiOsFinding -Findings $findings -Severity "BLOCKED" -CheckId "missing_allowed_paths" -Message "Packet must include allowed_paths or allowed_write_boundary."
    }

    $safety = Get-AiOsProp -Object $packet -Names @("safety", "safety_rules")
    if ($null -eq $safety) {
        Add-AiOsFinding -Findings $findings -Severity "BLOCKED" -CheckId "missing_safety" -Message "Packet must include a safety block or safety rules."
    }

    $mode = [string](Get-AiOsProp -Object $packet -Names @("mode"))
    if ($mode -notin @("DRY_RUN", "APPLY")) {
        Add-AiOsFinding -Findings $findings -Severity "BLOCKED" -CheckId "invalid_mode" -Message "Packet mode must be DRY_RUN or APPLY." -Evidence $mode
    }

    $status = [string](Get-AiOsProp -Object $packet -Names @("status"))
    if ($status -notin @("PROPOSED", "PENDING_OPERATOR_APPROVAL", "APPROVED", "ASSIGNED", "ACTIVE", "COMPLETE", "REJECTED", "EXPIRED", "BLOCKED", "NEEDS_REVIEW", "proposed", "active", "blocked", "complete")) {
        Add-AiOsFinding -Findings $findings -Severity "REVIEW" -CheckId "noncanonical_status" -Message "Packet status is not in the preferred lifecycle set." -Evidence $status
    }

    $textForUnsafeScope = @(
        [string](Get-AiOsProp -Object $packet -Names @("title")),
        [string](Get-AiOsProp -Object $packet -Names @("objective")),
        [string](Get-AiOsProp -Object $packet -Names @("intent")),
        (@(Get-AiOsProp -Object $packet -Names @("allowed_paths", "allowed_write_boundary")) -join " "),
        (@(Get-AiOsProp -Object $packet -Names @("validation_commands")) -join " "),
        [string](Get-AiOsProp -Object $packet -Names @("expected_output"))
    ) -join " "
    $combinedText = $textForUnsafeScope.ToLowerInvariant()
    $unsafePatterns = @(
        "broker",
        "oanda",
        "live trading",
        "live_trading",
        "api key",
        "api_key",
        "secrets",
        "real webhook",
        "real_webhook"
    )

    foreach ($pattern in $unsafePatterns) {
        if ($combinedText -match [regex]::Escape($pattern)) {
            Add-AiOsFinding -Findings $findings -Severity "BLOCKED" -CheckId "unsafe_path_or_scope" -Message "Packet mentions an unsafe path or blocked scope." -Evidence $pattern
        }
    }
}

$blockedCount = @($findings | Where-Object { $_.severity -eq "BLOCKED" }).Count
$reviewCount = @($findings | Where-Object { $_.severity -eq "REVIEW" }).Count
$resultStatus = if ($blockedCount -gt 0) { "BLOCKED" } elseif ($reviewCount -gt 0) { "REVIEW" } else { "PASS" }

$result = [pscustomobject]@{
    schema = "AIOS_PACKET_STRUCTURAL_VALIDATION.v1"
    mode = "DRY_RUN"
    packet_path = $PacketPath
    status = $resultStatus
    blocked_count = $blockedCount
    review_count = $reviewCount
    findings = @($findings)
    writes_performed = 0
    commit_performed = "NO"
    push_performed = "NO"
    next_safe_action = if ($resultStatus -eq "PASS") { "Packet structure is valid for approval preview." } else { "Resolve packet validation findings before approval preview." }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Packet Structural Validation"
Write-Host "Mode: DRY_RUN"
Write-Host "Status: $($result.status)"
Write-Host "Blocked: $blockedCount"
Write-Host "Review: $reviewCount"
Write-Host "Next safe action: $($result.next_safe_action)"
