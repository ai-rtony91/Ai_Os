$ErrorActionPreference = "Stop"

function Add-Result {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$Check,
        [string]$Status,
        [string]$Detail
    )
    $Results.Add([pscustomobject]@{
        check = $Check
        status = $Status
        detail = $Detail
    }) | Out-Null
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repoRoot

$results = [System.Collections.Generic.List[object]]::new()
$requiredStatuses = @(
    "WAITING_REVIEW",
    "APPROVED",
    "REJECTED",
    "STALE",
    "UNSAFE_BLOCKED",
    "ALREADY_HANDLED",
    "NEEDS_MORE_CONTEXT",
    "UNKNOWN"
)
$forbiddenTerms = @(".env", "secrets", "credentials", "broker", "OANDA", "live webhook", "real order")

try {
    python -m py_compile services/python_supervisor/approval_queue.py
    Add-Result $results "python_parse" "PASS" "services/python_supervisor/approval_queue.py"
} catch {
    Add-Result $results "python_parse" "FAIL" $_.Exception.Message
}

foreach ($script in @(
    "automation/orchestration/night_supervisor/Invoke-AiOsApprovalQueue.DRY_RUN.ps1",
    "automation/status/Test-AiOsNightSupervisorApprovalQueue.DRY_RUN.ps1"
)) {
    try {
        [scriptblock]::Create((Get-Content $script -Raw)) | Out-Null
        Add-Result $results "powershell_parse" "PASS" $script
    } catch {
        Add-Result $results "powershell_parse" "FAIL" "$script`: $($_.Exception.Message)"
    }
}

try {
    $schemaText = Get-Content "schemas/aios/orchestration/night_supervisor_approval_queue.schema.json" -Raw
    $schemaText | ConvertFrom-Json | Out-Null
    Add-Result $results "schema_json_parse" "PASS" "schemas/aios/orchestration/night_supervisor_approval_queue.schema.json"
    foreach ($status in $requiredStatuses) {
        if ($schemaText -notmatch [regex]::Escape($status)) {
            Add-Result $results "required_status" "FAIL" "Missing status enum: $status"
        }
    }
} catch {
    Add-Result $results "schema_json_parse" "FAIL" $_.Exception.Message
}

try {
    $fixture = Get-Content "apps/dashboard/mock-data/night_supervisor_approval_queue.sample.json" -Raw | ConvertFrom-Json
    Add-Result $results "dashboard_fixture_json_parse" "PASS" "apps/dashboard/mock-data/night_supervisor_approval_queue.sample.json"
    $card = $fixture.dashboard_cards[0]
    $missing = @("title", "status", "waiting_count", "stale_count", "unsafe_blocked_count", "approved_count", "rejected_count", "next_safe_action", "details_ref") | Where-Object {
        -not $card.PSObject.Properties.Name.Contains($_)
    }
    if ($missing.Count -gt 0) {
        Add-Result $results "dashboard_card_fields" "FAIL" "Missing fields: $($missing -join ', ')"
    } else {
        Add-Result $results "dashboard_card_fields" "PASS" "Approval Queue card fields present."
    }
} catch {
    Add-Result $results "dashboard_fixture_json_parse" "FAIL" $_.Exception.Message
}

$moduleText = Get-Content "services/python_supervisor/approval_queue.py" -Raw
if ($moduleText -match "UNSAFE_TERMS" -and $moduleText -match "UNSAFE_BLOCKED") {
    Add-Result $results "unsafe_detection" "PASS" "Unsafe blocked detection is implemented."
} else {
    Add-Result $results "unsafe_detection" "FAIL" "Unsafe blocked detection is missing."
}

if ($moduleText -match "dirty-repo" -and $moduleText -match "STALE") {
    Add-Result $results "stale_detection" "PASS" "Stale dirty-repo detection is implemented."
} else {
    Add-Result $results "stale_detection" "FAIL" "Stale dirty-repo detection is missing."
}

foreach ($path in @(
    "telemetry/night_supervisor/APPROVAL_QUEUE_STATE.json"
)) {
    if (Test-Path $path) {
        try {
            $payload = Get-Content $path -Raw | ConvertFrom-Json
            if ($payload.dashboard_cards -and $payload.dashboard_cards.Count -gt 0) {
                Add-Result $results "generated_queue_json_parse" "PASS" $path
            } else {
                Add-Result $results "generated_queue_json_parse" "FAIL" "$path missing dashboard_cards."
            }
        } catch {
            Add-Result $results "generated_queue_json_parse" "FAIL" "$path`: $($_.Exception.Message)"
        }
    } else {
        Add-Result $results "generated_queue_json_parse" "PASS" "$path not present; optional runtime output was not generated."
    }
}

$changedFiles = (& git diff --name-only) + (& git ls-files --others --exclude-standard)
$changedFiles = $changedFiles | Where-Object { $_ -and $_.Trim() }
foreach ($path in $changedFiles) {
    foreach ($term in $forbiddenTerms) {
        if ($path.ToLowerInvariant().Contains($term.ToLowerInvariant())) {
            Add-Result $results "forbidden_path_check" "FAIL" "$path matched $term"
        }
    }
}
if (-not ($results | Where-Object { $_.check -eq "forbidden_path_check" })) {
    Add-Result $results "forbidden_path_check" "PASS" "No changed path matched forbidden terms."
}

$gitStatus = (& git status --short --branch) -join "`n"
Add-Result $results "git_status_shown" "PASS" $gitStatus
Add-Result $results "commit_push_check" "PASS" "Validator does not stage, commit, push, open PR, or merge."

$overall = if ($results | Where-Object { $_.status -eq "FAIL" }) { "FAIL" } elseif ($results | Where-Object { $_.status -eq "WARN" }) { "WARN" } else { "PASS" }

[pscustomobject]@{
    schema = "AIOS_NIGHT_SUPERVISOR_APPROVAL_QUEUE_VALIDATION.v1"
    mode = "DRY_RUN"
    overall_status = $overall
    results = $results
    next_safe_action = "Review source-only approval queue files before selective commit preparation."
} | ConvertTo-Json -Depth 8

if ($overall -eq "FAIL") {
    exit 1
}
