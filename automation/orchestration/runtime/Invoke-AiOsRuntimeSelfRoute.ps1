param(
    [switch]$Apply,
    [switch]$QuietJson,
    [switch]$OutputJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsObjectProperty {
    param(
        [AllowNull()]$Object,
        [string]$Name,
        [AllowNull()]$Default = ""
    )

    if ($null -eq $Object) {
        return $Default
    }

    if ($Object.PSObject.Properties.Name -contains $Name) {
        return $Object.$Name
    }

    return $Default
}

if (-not ($QuietJson -or $OutputJson)) {
    Write-Host "AIOS Runtime Self Route"
    Write-Host "Mode: $(if ($Apply) { 'APPLY_REPORT_ONLY' } else { 'DRY_RUN_REPORT_ONLY' })"
    Write-Host ""
}

$recommendation = powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$recommendedCommand = [string](Get-AiOsObjectProperty -Object $recommendation -Name "recommended_command" -Default "")
$recommendationReason = [string](Get-AiOsObjectProperty -Object $recommendation -Name "reason" -Default "")
$contract = Get-AiOsObjectProperty -Object $recommendation -Name "orchestration_result_contract" -Default $null
$contractStatus = [string](Get-AiOsObjectProperty -Object $contract -Name "status" -Default "UNKNOWN")
$approvalRequired = [bool](Get-AiOsObjectProperty -Object $contract -Name "approval_required" -Default $false)
$contractNextSafeAction = [string](Get-AiOsObjectProperty -Object $contract -Name "next_safe_action" -Default "")
$normalizedCommand = $recommendedCommand.Trim()
$hasActionableCommand = -not [string]::IsNullOrWhiteSpace($normalizedCommand) -and $normalizedCommand -notmatch "(?i)^No command recommended"
$commandValidatorPath = "automation/orchestration/validators/Test-AiOsRecommendedCommand.ps1"
$validationOutput = @()
$validationExitCode = $null
$validationStatus = "NOT_RUN"
$routeStatus = "report_only"
$exitCode = 0
$rejectionReasons = @()

if ($hasActionableCommand) {
    if (-not (Test-Path -LiteralPath $commandValidatorPath)) {
        $validationStatus = "BLOCKED"
        $routeStatus = "blocked"
        $exitCode = 1
        $rejectionReasons += "recommended_command_validator_missing"
    }
    else {
        $validationOutput = @(powershell -NoProfile -ExecutionPolicy Bypass -File $commandValidatorPath $normalizedCommand)
        $validationExitCode = $LASTEXITCODE
        $validationStatus = if ($validationExitCode -eq 0) { "PASS" } else { "BLOCKED" }

        if ($validationExitCode -ne 0) {
            $routeStatus = "rejected"
            $exitCode = 1
            $rejectionReasons += "recommended_command_failed_validation"
        }
    }
}
else {
    $validationStatus = "NOT_APPLICABLE"
}

if ($routeStatus -eq "report_only") {
    if ($contractStatus -eq "BLOCKED" -or $approvalRequired) {
        $routeStatus = "blocked"
        $exitCode = 1
        if ($approvalRequired) {
            $rejectionReasons += "human_owner_review_required"
        }
        if ($contractStatus -eq "BLOCKED") {
            $rejectionReasons += "recommendation_contract_blocked"
        }
    }
    elseif ($hasActionableCommand -and $validationStatus -eq "PASS") {
        $routeStatus = "route_ready_report_only"
    }
    elseif (-not $hasActionableCommand) {
        $routeStatus = "no_action_report_only"
    }
}

$nextSafeAction = if (-not [string]::IsNullOrWhiteSpace($contractNextSafeAction)) {
    $contractNextSafeAction
}
elseif ($hasActionableCommand) {
    "Use this validated recommendation as evidence for a separate bounded packet. Do not execute it from self-route."
}
else {
    "Stop or idle according to the action recommendation; no command is executable from self-route."
}

$report = [pscustomobject]@{
    schema = "AIOS_RUNTIME_SELF_ROUTE_REPORT.v1"
    mode = if ($Apply) { "APPLY_REPORT_ONLY" } else { "DRY_RUN_REPORT_ONLY" }
    route_status = $routeStatus
    recommended_command = $recommendedCommand
    recommendation_reason = $recommendationReason
    recommendation_contract_status = $contractStatus
    approval_required = $approvalRequired
    command_validation_status = $validationStatus
    command_validation_exit_code = $validationExitCode
    command_validation_output = @($validationOutput)
    command_execution_allowed = $false
    command_executed = $false
    rejection_reasons = @($rejectionReasons | Select-Object -Unique)
    next_safe_action = $nextSafeAction
    stop_condition = "REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION"
    safety = [pscustomobject]@{
        autonomous_execution = $false
        live_worker_dispatch = $false
        scheduler_activation = $false
        daemon_activation = $false
        queue_mutation = $false
        approval_mutation = $false
        broker = $false
        credentials = $false
        live_trading = $false
        real_orders = $false
        real_webhooks = $false
        network = $false
        reports_written = $false
        files_written = $false
        git_add = $false
        git_commit = $false
        git_push = $false
        merge = $false
    }
}

if ($QuietJson -or $OutputJson) {
    $report | ConvertTo-Json -Depth 8
    exit $exitCode
}

Write-Host "Recommended command:"
Write-Host $recommendedCommand
Write-Host ""
Write-Host "Route status: $routeStatus"
Write-Host "Contract status: $contractStatus"
Write-Host "Approval required: $approvalRequired"
Write-Host "Command validation: $validationStatus"
foreach ($line in $validationOutput) {
    Write-Host $line
}
Write-Host ""
Write-Host "Next safe action:"
Write-Host $nextSafeAction
Write-Host ""
Write-Host "Command executed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Stop condition: REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION"

exit $exitCode
