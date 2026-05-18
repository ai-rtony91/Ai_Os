param(
    [string[]]$PacketPaths = @(
        "work_packets/examples/worker_registry_consolidation.json",
        "automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json",
        "automation/orchestration/adapters/LEGACY_PACKET_MAPPING.example.json"
    ),
    [string]$NormalizerPath = (Join-Path $PSScriptRoot "Normalize-AiOsPacket.DRY_RUN.ps1"),
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

function Get-WarningCount {
    param($Value)

    if ($null -eq $Value) {
        return 0
    }

    return @($Value).Count
}

function Get-NormalizationConfidenceScore {
    param(
        [Parameter(Mandatory = $true)]$Normalization
    )

    $score = 100
    $missingCount = [int]$Normalization.normalization_summary.missing_field_count
    $warningCount = [int]$Normalization.normalization_summary.warning_count
    $lossyCount = Get-WarningCount -Value $Normalization.lossy_conversion_warnings

    $score -= ($missingCount * 3)
    $score -= ($warningCount * 4)
    $score -= ($lossyCount * 4)

    if ($Normalization.detected_dialect -eq "legacy_orchestration_packet_template") {
        $score -= 5
    }

    if ($Normalization.detected_dialect -eq "queue_packet_entry") {
        $score -= 12
    }

    if ($Normalization.detected_dialect -eq "unknown_packet") {
        $score -= 30
    }

    if ($score -lt 0) {
        return 0
    }

    if ($score -gt 100) {
        return 100
    }

    return $score
}

function Get-ValidationStatus {
    param(
        [Parameter(Mandatory = $true)]$Normalization,
        [int]$ConfidenceScore
    )

    if ($Normalization.detected_dialect -eq "unknown_packet") {
        return "FAIL"
    }

    if ($ConfidenceScore -lt 50) {
        return "FAIL"
    }

    if (
        [int]$Normalization.normalization_summary.missing_field_count -gt 0 -or
        [int]$Normalization.normalization_summary.warning_count -gt 0 -or
        (Get-WarningCount -Value $Normalization.lossy_conversion_warnings) -gt 0
    ) {
        return "WARN"
    }

    return "PASS"
}

function Invoke-NormalizerDryRun {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Normalizer
    )

    $normalizerFullPath = Resolve-AiOsPath -Path $Normalizer
    if (-not (Test-Path -LiteralPath $normalizerFullPath -PathType Leaf)) {
        throw "Normalizer script not found: $normalizerFullPath"
    }

    $jsonText = & powershell -NoProfile -ExecutionPolicy Bypass -File $normalizerFullPath -PacketPath $Path -OutputJson
    if ($LASTEXITCODE -ne 0) {
        throw "Normalizer failed for packet path: $Path"
    }

    return ($jsonText | ConvertFrom-Json)
}

$results = @()

foreach ($packetPath in $PacketPaths) {
    $normalization = Invoke-NormalizerDryRun -Path $packetPath -Normalizer $NormalizerPath
    $confidence = Get-NormalizationConfidenceScore -Normalization $normalization
    $status = Get-ValidationStatus -Normalization $normalization -ConfidenceScore $confidence
    $unsupportedWarnings = @()

    if ($normalization.detected_dialect -eq "unknown_packet") {
        $unsupportedWarnings += "Unsupported packet dialect: unknown_packet"
    }

    $results += [pscustomobject]@{
        packet_path = $packetPath
        resolved_packet_path = $normalization.resolved_source_packet_path
        detected_dialect = $normalization.detected_dialect
        validation_status = $status
        confidence_score = $confidence
        mapped_field_count = [int]$normalization.normalization_summary.mapped_field_count
        missing_field_count = [int]$normalization.normalization_summary.missing_field_count
        warning_count = [int]$normalization.normalization_summary.warning_count
        lossy_conversion_count = Get-WarningCount -Value $normalization.lossy_conversion_warnings
        missing_field_warnings = @($normalization.missing_fields)
        normalization_warnings = @($normalization.normalization_warnings)
        lossy_conversion_warnings = @($normalization.lossy_conversion_warnings)
        unsupported_dialect_warnings = $unsupportedWarnings
        next_safe_action = $normalization.next_safe_action
    }
}

$totalPackets = $results.Count
$passed = @($results | Where-Object { $_.validation_status -eq "PASS" }).Count
$warnings = @($results | Where-Object { $_.validation_status -eq "WARN" }).Count
$failed = @($results | Where-Object { $_.validation_status -eq "FAIL" }).Count
$unsupported = @($results | Where-Object { $_.unsupported_dialect_warnings.Count -gt 0 }).Count
$averageConfidence = 0

if ($totalPackets -gt 0) {
    $averageConfidence = [math]::Round((($results | Measure-Object -Property confidence_score -Average).Average), 0)
}

$report = [pscustomobject]@{
    task = "Validate AI_OS packet normalization simulations"
    mode = "DRY_RUN"
    adapter = "Test-AiOsPacketNormalization.DRY_RUN.ps1"
    normalizer = $NormalizerPath
    summary = [pscustomobject]@{
        total_packets = $totalPackets
        passed = $passed
        warnings = $warnings
        failed = $failed
        unsupported_dialects = $unsupported
        average_confidence_score = $averageConfidence
    }
    results = $results
    safety = [pscustomobject]@{
        writes_performed = 0
        runtime_edits = "NO"
        dispatcher_edits = "NO"
        schema_edits = "NO"
        commits_performed = 0
        pushes_performed = 0
        broker_or_live_api_work = "NO"
    }
    validator_friendly = $true
    next_safe_action = "Review failed or warning packet results before proposing any APPLY conversion."
}

if ($OutputJson) {
    $report | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Packet Normalization Validation"
Write-Host "Mode: DRY_RUN"
Write-Host "Packets tested: $($report.summary.total_packets)"
Write-Host ""
Write-Host "Summary:"
Write-Host "  PASS: $($report.summary.passed)"
Write-Host "  WARN: $($report.summary.warnings)"
Write-Host "  FAIL: $($report.summary.failed)"
Write-Host "  Unsupported dialects: $($report.summary.unsupported_dialects)"
Write-Host "  Average confidence: $($report.summary.average_confidence_score)"
Write-Host ""

foreach ($result in $results) {
    Write-Host "Packet: $($result.packet_path)"
    Write-Host "  Dialect: $($result.detected_dialect)"
    Write-Host "  Status: $($result.validation_status)"
    Write-Host "  Confidence: $($result.confidence_score)"

    Write-Host "  Missing field warnings:"
    if ($result.missing_field_warnings.Count -eq 0) {
        Write-Host "    NONE"
    } else {
        foreach ($warning in $result.missing_field_warnings) {
            Write-Host "    - $warning"
        }
    }

    Write-Host "  Normalization warnings:"
    if ($result.normalization_warnings.Count -eq 0) {
        Write-Host "    NONE"
    } else {
        foreach ($warning in $result.normalization_warnings) {
            Write-Host "    - $warning"
        }
    }

    Write-Host "  Lossy-conversion warnings:"
    if ($result.lossy_conversion_warnings.Count -eq 0) {
        Write-Host "    NONE"
    } else {
        foreach ($warning in $result.lossy_conversion_warnings) {
            Write-Host "    - $warning"
        }
    }

    Write-Host "  Unsupported dialect warnings:"
    if ($result.unsupported_dialect_warnings.Count -eq 0) {
        Write-Host "    NONE"
    } else {
        foreach ($warning in $result.unsupported_dialect_warnings) {
            Write-Host "    - $warning"
        }
    }

    Write-Host ""
}

Write-Host "Validator note: no files were changed by this validation run."
Write-Host "Next safe action: $($report.next_safe_action)"
