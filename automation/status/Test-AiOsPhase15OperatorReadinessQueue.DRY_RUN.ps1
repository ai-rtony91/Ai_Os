$ErrorActionPreference = "Stop"

Write-Host "AI_OS Phase 15 Operator Readiness Queue v1 DRY_RUN"
Write-Host "Mode: read-only validation"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/operator-readiness-queue-v1.example.json"

if (-not (Test-Path -LiteralPath $fixturePath -PathType Leaf)) {
    throw "Missing operator readiness queue fixture: $fixturePath"
}

$record = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

$requiredFields = @(
    "readiness_record_id",
    "workspace_mode",
    "operator_mode",
    "dashboard_state",
    "validator_status",
    "latency_system_status",
    "risk_gate_status",
    "regime_filter_status",
    "signal_queue_status",
    "unresolved_alerts",
    "approval_required",
    "blocked_reason",
    "readiness_score",
    "readiness_status",
    "checked_at"
)

$fieldNames = @($record.PSObject.Properties.Name)
foreach ($field in $requiredFields) {
    if ($fieldNames -notcontains $field) {
        throw "Operator readiness queue fixture missing required field: $field"
    }
}

if ($record.workspace_mode -ne "paper_only") {
    throw "workspace_mode must remain paper_only."
}

if ($record.approval_required -ne $true) {
    throw "approval_required must remain true for Phase 15 readiness review."
}

if ($null -eq $record.blocked_reason -or [string]::IsNullOrWhiteSpace([string]$record.blocked_reason)) {
    throw "blocked_reason must be present."
}

$score = [double]$record.readiness_score
if ($score -lt 0 -or $score -gt 100) {
    throw "readiness_score must be between 0 and 100."
}

$allowedStatuses = @(
    "READY_FOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED_REVIEW",
    "UNKNOWN"
)
if ($allowedStatuses -notcontains $record.readiness_status) {
    throw "readiness_status is not allowed: $($record.readiness_status)"
}

if ($record.readiness_status -ne "READY_FOR_REVIEW" -and [string]::IsNullOrWhiteSpace([string]$record.blocked_reason)) {
    throw "blocked_reason is required when readiness_status is not READY_FOR_REVIEW."
}

foreach ($field in @("live_execution_status", "broker_status", "oanda_status", "api_key_status", "credential_status", "real_order_status")) {
    if ($record.safety_gates.$field -ne "BLOCKED") {
        throw "Safety gate $field must remain BLOCKED."
    }
}

foreach ($field in @("dashboard_ui_edits", "javascript_dashboard_edits", "startup_tasks", "installs")) {
    if ($record.safety_gates.$field -ne "BLOCKED") {
        throw "Safety gate $field must remain BLOCKED."
    }
}

$prohibitedEnablementFields = @(
    "broker_enabled",
    "oanda_enabled",
    "api_key",
    "api_keys",
    "credential",
    "credentials",
    "secret",
    "secrets",
    "real_order_enabled",
    "live_execution_enabled"
)

foreach ($field in $prohibitedEnablementFields) {
    if ($fieldNames -contains $field) {
        throw "Prohibited enablement field found in operator readiness queue fixture: $field"
    }
}

[DateTimeOffset]::Parse($record.checked_at) | Out-Null

Write-Host "PASS: JSON parses."
Write-Host "PASS: Required readiness fields are present."
Write-Host "PASS: readiness_score is within 0-100."
Write-Host "PASS: readiness_status is allowed."
Write-Host "PASS: blocked_reason is present."
Write-Host "PASS: Paper-only safety gates remain blocked for live execution, broker, OANDA, API keys, credentials, and real orders."
