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

function New-AiOsBlockedRoutePreview {
    param(
        [string]$Reason,
        [AllowNull()]$SourceRecommendation,
        [AllowNull()]$ValidatedCommand
    )

    return [pscustomobject]@{
        schema = "AIOS_BOUNDED_WORKER_ROUTING_PREVIEW.v1"
        routing_status = "blocked"
        source_recommendation = $SourceRecommendation
        validated_command = $ValidatedCommand
        proposed_worker_identity = $null
        proposed_lane = $null
        proposed_task_summary = "No worker route available because route preview generation was blocked."
        proposed_write_scope = @()
        required_approvals = [pscustomobject]@{
            human_owner_review_before_execution = $true
            worker_dispatch = $true
            queue_mutation = $true
            approval_mutation = $true
            local_apply = $true
            commit = $true
            push = $true
            merge = $true
            scheduler_or_daemon = $true
            broker_or_trading = $true
        }
        blocked_actions = @(
            "execute_recommended_command",
            "launch_codex",
            "dispatch_worker",
            "mutate_runtime_queue",
            "mutate_worker_inbox",
            "mutate_approval_state",
            "start_scheduler",
            "start_daemon",
            "access_network",
            "write_reports",
            "touch_broker_trading_credentials_orders_or_webhooks",
            "git_add",
            "git_commit",
            "git_push",
            "git_merge",
            $Reason
        )
        commands_executed = @()
        queues_mutated = $false
        approvals_mutated = $false
        workers_dispatched = $false
        files_written = @()
        safety = [pscustomobject]@{
            preview_only = $true
            command_execution = $false
            codex_launch = $false
            worker_dispatch = $false
            queue_mutation = $false
            approval_mutation = $false
            scheduler_activation = $false
            daemon_activation = $false
            network_access = $false
            reports_written = $false
            file_writes = $false
            broker = $false
            credentials = $false
            live_trading = $false
            real_orders = $false
            real_webhooks = $false
            git_add = $false
            git_commit = $false
            git_push = $false
            merge = $false
            runtime_supervisor_consumable_status = $true
        }
        runtime_supervisor_blocker = $Reason
        next_safe_action = "Stop; routing preview evidence could not be generated."
    }
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
$routePreviewPath = "automation/orchestration/aios_bounded_worker_routing_preview.py"
$validationOutput = @()
$validationExitCode = $null
$validationStatus = "NOT_RUN"
$routePreview = $null
$routePreviewOutput = @()
$routePreviewExitCode = $null
$routePreviewStatus = "NOT_RUN"
$routePreviewBlocker = ""
$routePreviewNextSafeAction = ""
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

$validatedCommandEvidence = [ordered]@{
    command = $normalizedCommand
    validator = $commandValidatorPath
    validation_status = $validationStatus
    status = $validationStatus
    exit_code = $validationExitCode
    output = @($validationOutput)
    execution_allowed = $false
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

if (-not (Test-Path -LiteralPath $routePreviewPath)) {
    $routePreview = New-AiOsBlockedRoutePreview `
        -Reason "route_preview_module_missing" `
        -SourceRecommendation $recommendation `
        -ValidatedCommand $validatedCommandEvidence
    $routePreviewStatus = "blocked"
    $routePreviewBlocker = "route_preview_module_missing"
    $routePreviewExitCode = 1
}
else {
    try {
        $recommendationJson = $recommendation | ConvertTo-Json -Depth 20 -Compress
        $validatedCommandJson = $validatedCommandEvidence | ConvertTo-Json -Depth 10 -Compress
        $routePreviewOutput = @(
            python $routePreviewPath `
                --recommendation $recommendationJson `
                --validated-command $validatedCommandJson
        )
        $routePreviewExitCode = $LASTEXITCODE
        $routePreviewJson = ($routePreviewOutput -join "`n")
        if ([string]::IsNullOrWhiteSpace($routePreviewJson)) {
            $routePreview = New-AiOsBlockedRoutePreview `
                -Reason "route_preview_empty_output" `
                -SourceRecommendation $recommendation `
                -ValidatedCommand $validatedCommandEvidence
            $routePreviewStatus = "blocked"
            $routePreviewBlocker = "route_preview_empty_output"
        }
        else {
            $routePreview = $routePreviewJson | ConvertFrom-Json
            $routePreviewStatus = [string](Get-AiOsObjectProperty -Object $routePreview -Name "routing_status" -Default "UNKNOWN")
            $routePreviewBlocker = [string](Get-AiOsObjectProperty -Object $routePreview -Name "runtime_supervisor_blocker" -Default "")
            $routePreviewNextSafeAction = [string](Get-AiOsObjectProperty -Object $routePreview -Name "next_safe_action" -Default "")
        }
    }
    catch {
        $routePreview = New-AiOsBlockedRoutePreview `
            -Reason "route_preview_generation_failed" `
            -SourceRecommendation $recommendation `
            -ValidatedCommand $validatedCommandEvidence
        $routePreviewStatus = "blocked"
        $routePreviewBlocker = "route_preview_generation_failed"
        $routePreviewExitCode = 1
    }
}

if ($routePreviewStatus -in @("blocked", "rejected")) {
    $routeStatus = $routePreviewStatus
    $exitCode = 1
    $rejectionReasons += "route_preview_$routePreviewStatus"
    if (-not [string]::IsNullOrWhiteSpace($routePreviewBlocker)) {
        $rejectionReasons += "route_preview_blocker:$routePreviewBlocker"
    }
}
elseif ($routePreviewStatus -eq "route_ready" -and $validationStatus -notin @("PASS")) {
    $routeStatus = "blocked"
    $exitCode = 1
    $rejectionReasons += "route_preview_ready_without_validated_command"
}

$nextSafeAction = if (-not [string]::IsNullOrWhiteSpace($contractNextSafeAction)) {
    $contractNextSafeAction
}
elseif ($routePreviewStatus -in @("blocked", "rejected") -and -not [string]::IsNullOrWhiteSpace($routePreviewNextSafeAction)) {
    $routePreviewNextSafeAction
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
    route_preview_status = $routePreviewStatus
    route_preview_exit_code = $routePreviewExitCode
    route_preview = $routePreview
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
    $report | ConvertTo-Json -Depth 20
    exit $exitCode
}

Write-Host "Recommended command:"
Write-Host $recommendedCommand
Write-Host ""
Write-Host "Route status: $routeStatus"
Write-Host "Contract status: $contractStatus"
Write-Host "Approval required: $approvalRequired"
Write-Host "Command validation: $validationStatus"
Write-Host "Route preview: $routePreviewStatus"
if (-not [string]::IsNullOrWhiteSpace($routePreviewBlocker)) {
    Write-Host "Route preview blocker: $routePreviewBlocker"
}
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
