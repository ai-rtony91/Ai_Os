param(
    [Parameter(Mandatory = $true)]
    [string]$ControlPlaneEvidencePath,
    [string]$OutputReportPath
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Get-AiOsRepoRoot {
    $repoRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoRoot)) {
        throw "REVIEW_REQUIRED: Unable to resolve repository root."
    }
    return $repoRoot.Trim()
}

function Resolve-AiOsPath {
    param([string]$PathHint, [string]$RepoRoot)

    if ([string]::IsNullOrWhiteSpace($PathHint)) {
        return [string]::Empty
    }
    if ([System.IO.Path]::IsPathRooted($PathHint)) {
        return [System.IO.Path]::GetFullPath($PathHint)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $PathHint))
}

function Write-TextAtomic {
    param([string]$Path, [string]$Text)
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $tmp = Join-Path $parent ([guid]::NewGuid().ToString("N") + ".tmp")
    [System.IO.File]::WriteAllText($tmp, $Text, [System.Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force
    }
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Parse-JsonQuiet {
    param([string]$Text)
    try {
        return $Text | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Write-RoutePayload {
    param(
        $Payload
    )
    $json = $Payload | ConvertTo-Json -Depth 20
    [Console]::Write($json + "`r`n")
    [Console]::Out.Flush()
}

function Build-SafeCommand {
    param(
        [string]$NextAction,
        [string]$PacketPath
    )

    if ($NextAction -eq "RUN_CODEX_WITH_PACKET") {
        return ('powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/packet_runner/Invoke-AiOsPacketAutoRunner.DRY_RUN.ps1 -PacketPath "' + $PacketPath + '" -OutputPath "Reports/autonomy_control_plane/run_with_packet.md" -ReportPath "Reports/autonomy_control_plane/run_with_packet.json"')
    }
    if ($NextAction -eq "OPEN_PR") {
        return 'gh pr create --draft --title "AIOS autonomy packet handoff" --body "Safe PR from autonomy router"'
    }
    if ($NextAction -eq "FIX_VALIDATION") {
        if ([string]::IsNullOrWhiteSpace($PacketPath)) {
            return "python automation/validators/aios_governance_validator.py"
        }
        return "python automation/validators/aios_governance_validator.py --input `"$PacketPath`""
    }
    if ($NextAction -eq "REQUEST_APPROVAL") {
        return 'gh pr comment --body "Operator approval required for protected action"'
    }
    if ($NextAction -eq "ESCALATE_SOS") {
        return "python -m automation.operator_relief.run_operator_relief_loop --evidence-path $PacketPath --review"
    }

    return "echo Blocked: manual intervention required"
}

function Get-BlockedReason {
    param($Evidence)
    if ($null -eq $Evidence) {
        return @("missing_evidence")
    }
    $reasons = @()
    if (-not (Test-Path -LiteralPath $Evidence.evidence_path) -and $Evidence.evidence_path) {
        $reasons += "evidence_path_missing"
    }
    if ($Evidence.status -eq "VALIDATION_FAILED") {
        $reasons += "validation_failed"
    }
    if ($Evidence.status -eq "PROTECTED_ACTION_REQUIRED") {
        $reasons += "protected_action_required"
    }
    if ($Evidence.status -eq "SOS_REQUIRED" -or $Evidence.status -eq "ESCALATE_SOS") {
        $reasons += "sos_required"
    }
    if ($Evidence.status -eq "BLOCKED") {
        $reasons += "blocked"
    }
    return $reasons
}

function Choose-NextAction {
    param($Evidence)

    $status = ""
    if ($null -ne $Evidence -and $Evidence.status) {
        $status = [string]$Evidence.status
    }

    switch ($status) {
        "READY_FOR_CODEX" {
            return "RUN_CODEX_WITH_PACKET"
        }
        "VALIDATION_FAILED" {
            return "FIX_VALIDATION"
        }
        "PROTECTED_ACTION_REQUIRED" {
            return "REQUEST_APPROVAL"
        }
        "SOS_REQUIRED" {
            return "ESCALATE_SOS"
        }
        "BLOCKED" {
            return "BLOCKED"
        }
        default {
            return "BLOCKED"
        }
    }
}

try {
    $repoRoot = Get-AiOsRepoRoot
    $evidencePath = Resolve-AiOsPath -PathHint $ControlPlaneEvidencePath -RepoRoot $repoRoot
    if (-not (Test-Path -LiteralPath $evidencePath)) {
        throw "BLOCKED: evidence path not found: $evidencePath"
    }

    $raw = Get-Content -Path $evidencePath -Raw
    $evidence = Parse-JsonQuiet -Text $raw
    if ($null -eq $evidence) {
        throw "BLOCKED: evidence JSON is invalid."
    }

    $packetPath = if ($evidence.packet_path) {
        [string]$evidence.packet_path
    } elseif ($evidence.evidence_path) {
        [string]$evidence.evidence_path
    } else {
        ""
    }
    if (-not (Test-Path -LiteralPath $packetPath) -and -not [string]::IsNullOrWhiteSpace($packetPath)) {
        throw "BLOCKED: packet path from evidence not found: $packetPath"
    }

    $nextAction = Choose-NextAction -Evidence $evidence
    $safeCommand = Build-SafeCommand -NextAction $nextAction -PacketPath $packetPath
    $blockedBy = Get-BlockedReason -Evidence $evidence

    if ($safeCommand -match "merge|force-push|delete|APPLY|broker|live_trading|secret|live trading|delete branch") {
        throw "BLOCKED: generated safe_command contains prohibited action."
    }

    $forbidden = @("merge", "delete", "forc", "APPLY", "broker", "live trading", "secret")
    $reason = if ($blockedBy.Count -gt 0) { $blockedBy -join "; " } else { "control plane action computed from evidence" }

    $route = [ordered]@{
        schema_version = "AIOS-AUTONOMY-NEXT-ACTION-V1"
        next_action = $nextAction
        safe_command = $safeCommand
        reason = $reason
        blocked_by = $blockedBy
        packet_path = $packetPath
        evidence_status = $evidence.status
        created_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        evidence_path = $evidencePath
    }

    if (-not [string]::IsNullOrWhiteSpace($OutputReportPath)) {
        $resolvedReportPath = Resolve-AiOsPath -PathHint $OutputReportPath -RepoRoot $repoRoot
        $md = @"
# Autonomy Next Action

- next_action: $($route.next_action)
- safe_command: $($route.safe_command)
- reason: $($route.reason)
- evidence_status: $($route.evidence_status)
- blocked_by: $($route.blocked_by -join ", ")
"@
        Write-TextAtomic -Path $resolvedReportPath -Text $md
        $route.report_path = $resolvedReportPath
    } else {
        $route.report_path = $null
    }

    Write-RoutePayload -Payload $route
    if ($nextAction -in @("RUN_CODEX_WITH_PACKET", "OPEN_PR")) {
        exit 0
    }
    if ($nextAction -eq "REQUEST_APPROVAL" -and $blockedBy.Count -gt 0) {
        exit 1
    }
    exit 1
} catch {
    $status = "BLOCKED"
    $errorMessage = $_.Exception.Message
    $route = [ordered]@{
        schema_version = "AIOS-AUTONOMY-NEXT-ACTION-V1"
        next_action = "BLOCKED"
        safe_command = "echo Blocked: evidence cannot be routed"
        reason = $errorMessage
        blocked_by = @("router_error")
        packet_path = $null
        evidence_status = $status
        created_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        evidence_path = $ControlPlaneEvidencePath
        error = $errorMessage
    }
    Write-Error "REVIEW_REQUIRED: $errorMessage"
    Write-RoutePayload -Payload $route
    exit 1
}
