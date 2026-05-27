[CmdletBinding()]
param(
    [string]$CommandRequestPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsRequestPreview {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return [pscustomobject]@{
            status = "SAMPLE_USED"
            command_id = "CMD-PREVIEW-SAMPLE"
            packet_id = "PKT-PREVIEW-SAMPLE"
            approval_required = $true
            approval_token_status = "REQUIRED_NOT_GRANTED"
            result = "REQUESTED"
            command_preview = "git diff --check"
            error = ""
        }
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            error = "Command request file not found."
        }
    }

    try {
        $request = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
        return [pscustomobject]@{
            status = "FOUND"
            command_id = $request.command_id
            packet_id = $request.packet_id
            approval_required = [bool]$request.approval_required
            approval_token_status = [string]$request.approval_token_status
            result = [string]$request.result
            command_preview = [string]$request.command_preview
            error = ""
        }
    }
    catch {
        return [pscustomobject]@{
            status = "INVALID_JSON"
            error = $_.Exception.Message
        }
    }
}

$request = Get-AiOsRequestPreview -Path $CommandRequestPath
$states = @(
    "REQUESTED",
    "PREVIEWED",
    "APPROVAL_REQUIRED",
    "APPROVED",
    "EXECUTING",
    "COMPLETE",
    "FAILED",
    "BLOCKED",
    "EXPIRED"
)

$previewState = if ($request.status -in @("MISSING", "INVALID_JSON")) {
    "BLOCKED"
}
elseif ($request.approval_required -and $request.approval_token_status -ne "GRANTED") {
    "APPROVAL_REQUIRED"
}
elseif ($request.approval_required -and $request.approval_token_status -eq "GRANTED") {
    "APPROVED"
}
else {
    "PREVIEWED"
}

$preview = [pscustomobject]@{
    schema = "AIOS_APPROVAL_EXECUTOR_PREVIEW.v1"
    mode = "DRY_RUN"
    execution_enabled = $false
    approval_mutation_enabled = $false
    command_execution_enabled = $false
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    command_id = $request.command_id
    packet_id = $request.packet_id
    command_preview = $request.command_preview
    request_status = $request.status
    preview_state = $previewState
    state_model = $states
    transitions_previewed = @(
        "REQUESTED -> PREVIEWED",
        "PREVIEWED -> APPROVAL_REQUIRED when approval is missing",
        "APPROVAL_REQUIRED -> APPROVED only when a separate human approval is granted",
        "APPROVED -> EXECUTING is blocked in this DRY_RUN helper",
        "Any invalid, expired, or unsafe request -> BLOCKED"
    )
    blocked_actions = @(
        "command execution",
        "approval mutation",
        "queue mutation",
        "commit",
        "push",
        "PR creation",
        "merge",
        "secrets",
        "broker/OANDA/trading/webhook/live orders"
    )
    next_safe_action = if ($previewState -eq "APPROVAL_REQUIRED") {
        "Review the command request and obtain separate human approval before any execution helper exists."
    } elseif ($previewState -eq "APPROVED") {
        "Approval is only previewed. Do not execute from this helper."
    } else {
        "Review preview state. Execution remains disabled."
    }
    error = $request.error
}

if ($OutputJson) {
    $preview | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Approval Executor Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($preview.schema)"
Write-Host "Execution enabled: $($preview.execution_enabled)"
Write-Host "Preview state: $($preview.preview_state)"
Write-Host "Approval mutation enabled: $($preview.approval_mutation_enabled)"
Write-Host "Next safe action: $($preview.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
