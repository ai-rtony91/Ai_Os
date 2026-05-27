Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$runtimeBundlePath = Join-Path $orchestrationRoot "runtime\Get-AiOsRuntimeStateBundle.DRY_RUN.ps1"

function Stop-Blocked {
    param([Parameter(Mandatory = $true)][string]$Reason)

    Write-Host "AI_OS Orchestration Spine Live Display"
    Write-Host "Mode: DRY_RUN"
    Write-Host "Result: BLOCKED"
    Write-Host "Reason: $Reason"
    Write-Host ""
    Write-Host "Static fallback used: NO"
    Write-Host "Files changed by helper: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    exit 1
}

function Write-List {
    param([AllowNull()][object[]]$Items)

    $values = @($Items | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    if ($values.Count -eq 0) {
        Write-Host "    - None"
        return
    }

    foreach ($item in $values) {
        Write-Host "    - $item"
    }
}

function Get-PropValue {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = "UNKNOWN"
    )

    if ($null -eq $Object) {
        return $Default
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
        return $Default
    }

    return [string]$property.Value
}

function Write-SectionSummary {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [AllowNull()]$Section
    )

    Write-Host "$Label"
    if ($null -eq $Section) {
        Write-Host "  Status: MISSING"
        Write-Host "  Summary: Runtime bundle did not include this section."
        Write-Host ""
        return
    }

    $items = @($Section.items)
    Write-Host "  Status: $(Get-PropValue -Object $Section -Name 'status')"
    Write-Host "  Summary: $(Get-PropValue -Object $Section -Name 'summary')"
    Write-Host "  Sources:"
    Write-List -Items @($Section.source_paths)
    Write-Host "  Item count: $($items.Count)"
    Write-Host "  Blocked actions:"
    Write-List -Items @($Section.blocked_actions)
    Write-Host ""
}

if (-not (Test-Path -LiteralPath $runtimeBundlePath -PathType Leaf)) {
    Stop-Blocked -Reason "Runtime bundle helper not found: $runtimeBundlePath"
}

$rawOutput = @()
try {
    $rawOutput = @(& powershell -NoProfile -ExecutionPolicy Bypass -File $runtimeBundlePath -QuietJson 2>&1 | ForEach-Object { [string]$_ })
}
catch {
    Stop-Blocked -Reason "Runtime bundle helper failed: $($_.Exception.Message)"
}

if ($LASTEXITCODE -ne 0) {
    Stop-Blocked -Reason "Runtime bundle helper exited with code $LASTEXITCODE. Output: $($rawOutput -join ' ')"
}

$bundle = $null
try {
    $jsonText = ($rawOutput -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($jsonText)) {
        Stop-Blocked -Reason "Runtime bundle helper returned empty output."
    }

    $bundle = $jsonText | ConvertFrom-Json
}
catch {
    Stop-Blocked -Reason "Runtime bundle JSON parsing failed: $($_.Exception.Message)"
}

Write-Host "AI_OS Orchestration Spine Live Display"
Write-Host "Mode: $($bundle.mode)"
Write-Host "Schema: $($bundle.schema)"
Write-Host "Generated: $($bundle.generated_at)"
Write-Host "Static fallback used: NO"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No workers, validators, packets, startup tasks, scheduled tasks, git staging, commits, or pushes are launched."
Write-Host ""

Write-Host "Live spine summary:"
Write-Host "  Confidence: $($bundle.confidence_state.overall_confidence) $($bundle.confidence_state.confidence_score)"
Write-Host "  Bundle integrity: $($bundle.bundle_integrity.status)"
Write-Host "  Auto-git eligible: $($bundle.auto_git_eligibility.safe_auto_allowed)"
Write-Host "  Blocking signals: $(@($bundle.blocking_signals).Count)"
Write-Host "  Human-required signals: $(@($bundle.human_required_signals).Count)"
Write-Host ""

Write-SectionSummary -Label "packet_state" -Section $bundle.packet_state
Write-SectionSummary -Label "worker_state" -Section $bundle.worker_state
Write-SectionSummary -Label "lock_state" -Section $bundle.lock_state
Write-SectionSummary -Label "validator_state" -Section $bundle.validator_state
Write-SectionSummary -Label "approval_state" -Section $bundle.approval_state
Write-SectionSummary -Label "git_state" -Section $bundle.git_state
Write-SectionSummary -Label "supervisor_state" -Section $bundle.supervisor_state

Write-Host "confidence_state"
Write-Host "  Overall: $($bundle.confidence_state.overall_confidence)"
Write-Host "  Score: $($bundle.confidence_state.confidence_score)"
Write-Host "  Reasons:"
Write-List -Items @($bundle.confidence_state.confidence_reasons)
Write-Host ""

Write-Host "auto_git_eligibility"
Write-Host "  Safe auto allowed: $($bundle.auto_git_eligibility.safe_auto_allowed)"
Write-Host "  Minimum confidence score: $($bundle.auto_git_eligibility.minimum_confidence_score)"
Write-Host "  Eligible actions:"
Write-List -Items @($bundle.auto_git_eligibility.eligible_actions)
Write-Host "  Blocked actions:"
Write-List -Items @($bundle.auto_git_eligibility.blocked_actions)
Write-Host "  Stop conditions:"
Write-List -Items @($bundle.auto_git_eligibility.stop_conditions)
Write-Host ""

Write-Host "blocking_signals"
Write-List -Items @($bundle.blocking_signals)
Write-Host ""

Write-Host "human_required_signals"
Write-List -Items @($bundle.human_required_signals)
Write-Host ""

Write-Host "bundle_integrity"
Write-Host "  Status: $($bundle.bundle_integrity.status)"
Write-Host "  Parse errors:"
Write-List -Items @($bundle.bundle_integrity.parse_errors)
Write-Host "  Missing sources:"
Write-List -Items @($bundle.bundle_integrity.missing_sources)
Write-Host ""

Write-Host "Next safe actions:"
foreach ($action in @($bundle.next_safe_actions | Sort-Object rank)) {
    Write-Host ("  {0}. {1}" -f $action.rank, $action.action)
}
Write-Host ""
Write-Host "Runtime mutation skipped: Orchestration spine display is read-only."
Write-Host "Files changed by helper: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
