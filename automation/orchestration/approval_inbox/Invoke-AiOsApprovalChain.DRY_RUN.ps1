[CmdletBinding()]
param(
    [string]$PacketId = "",
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }

    return $root.Trim()
}

function Invoke-AiOsChainStep {
    param(
        [string]$Label,
        [string]$ScriptPath,
        [string[]]$Arguments = @()
    )

    Write-Host ""
    Write-Host "== $Label ==" -ForegroundColor Yellow

    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        Write-Host "STEP_FAILED: script missing: $ScriptPath" -ForegroundColor Red
        return [pscustomobject]@{
            label = $Label
            script_path = $ScriptPath
            exit_code = 127
            status = "STEP_FAILED"
            output = "script missing"
        }
    }

    $output = @(& powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @Arguments 2>&1)
    $exitCode = $LASTEXITCODE

    foreach ($line in $output) {
        Write-Host $line
    }

    $status = if ($exitCode -eq 0) { "OK" } else { "STEP_FAILED" }
    if ($status -eq "STEP_FAILED") {
        Write-Host "STEP_FAILED: $Label exited with code $exitCode" -ForegroundColor Red
    }

    return [pscustomobject]@{
        label = $Label
        script_path = $ScriptPath
        exit_code = $exitCode
        status = $status
        output = ($output -join "`n")
    }
}

$repoRoot = Get-AiOsRepoRoot
Push-Location -LiteralPath $repoRoot
try {
    Write-Host "AI_OS APPROVAL CHAIN" -ForegroundColor Cyan
    Write-Host "Mode: DRY_RUN (default) - reads approval state, emits verdict" -ForegroundColor Cyan
    Write-Host "PacketId filter: $(if ($PacketId) { $PacketId } else { 'ALL' })"
    Write-Host "Apply flag: $(if ($Apply) { 'SET - highlights APPLY-ready status only' } else { 'not set' })"

    $detectionScript = Join-Path $repoRoot "automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1"
    $processorScript = Join-Path $repoRoot "automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1"
    $decisionScript = Join-Path $repoRoot "automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1"
    $previewScript = Join-Path $repoRoot "automation/orchestration/approval_runner/Invoke-AiOsApprovalExecutorPreview.DRY_RUN.ps1"

    $stepResults = @()
    $stepResults += Invoke-AiOsChainStep -Label "Step 1: Approval Match Detection" -ScriptPath $detectionScript -Arguments @("-QuietJson")
    $stepResults += Invoke-AiOsChainStep -Label "Step 2: Approval Processor" -ScriptPath $processorScript
    $stepResults += Invoke-AiOsChainStep -Label "Step 3: Approval Decision" -ScriptPath $decisionScript -Arguments @("-Json")
    $stepResults += Invoke-AiOsChainStep -Label "Step 4: Executor Preview" -ScriptPath $previewScript -Arguments @("-OutputJson")

    Write-Host ""
    Write-Host "== Step 5: Gate File Status ==" -ForegroundColor Yellow
    $gateFile = Join-Path $repoRoot "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"
    $gate = Get-Content -LiteralPath $gateFile -Raw | ConvertFrom-Json

    Write-Host "packet_id        : $($gate.packet_id)"
    Write-Host "approval_status  : $($gate.approval_status)"
    Write-Host "approved_by_human: $($gate.approved_by_human)"
    if ($gate.PSObject.Properties.Name -contains "bound_by") {
        Write-Host "bound_by         : $($gate.bound_by)"
    }
    if ($gate.PSObject.Properties.Name -contains "bound_at") {
        Write-Host "bound_at         : $($gate.bound_at)"
    }

    if ($gate.packet_id -eq "PENDING_ASSIGNMENT") {
        $verdict = "GATE_UNBOUND"
        $reason = "APPLY_APPROVAL_GATE_001.json has packet_id=PENDING_ASSIGNMENT. Bind it to a packet."
    }
    elseif ($PacketId -and $gate.packet_id -ne $PacketId) {
        $verdict = "PACKET_NOT_GATED"
        $reason = "Requested packet $PacketId is not bound to the active gate."
    }
    elseif ($gate.approved_by_human -eq $true -and $gate.approval_status -eq "approved_for_apply") {
        $verdict = "APPROVED_FOR_APPLY"
        $reason = "Human approval granted. Gate is open for APPLY."
    }
    elseif ($gate.approval_status -eq "pending_review") {
        $verdict = "PENDING_HUMAN_REVIEW"
        $reason = "Approval is pending. Human Owner must set approved_by_human=true and approval_status=approved_for_apply."
    }
    else {
        $verdict = "BLOCKED"
        $reason = "Gate state is: $($gate.approval_status)"
    }

    Write-Host ""
    Write-Host "== Step 6: Verdict ==" -ForegroundColor Yellow
    $color = switch ($verdict) {
        "APPROVED_FOR_APPLY" { "Green" }
        "PENDING_HUMAN_REVIEW" { "Yellow" }
        default { "Red" }
    }
    Write-Host "VERDICT : $verdict" -ForegroundColor $color
    Write-Host "REASON  : $reason"

    $nextSafeAction = if ($verdict -eq "APPROVED_FOR_APPLY") {
        if ($Apply) { "Run APPLY lane for packet $($gate.packet_id)." } else { "Gate is approved; rerun with -Apply only to highlight APPLY-ready status. No execution occurs." }
    }
    else {
        "Human Owner must review and update APPLY_APPROVAL_GATE_001.json."
    }

    Write-Host "NEXT SAFE ACTION: $nextSafeAction"
    Write-Host ""
    Write-Host "Commit performed: NO | Push performed: NO | No mutation performed." -ForegroundColor Gray

    $failedSteps = @($stepResults | Where-Object { $_.status -eq "STEP_FAILED" })
    if ($failedSteps.Count -gt 0) {
        Write-Host ""
        Write-Host "Step failures were captured without mutating files: $($failedSteps.Count)" -ForegroundColor Red
    }

    exit 0
}
finally {
    Pop-Location
}
