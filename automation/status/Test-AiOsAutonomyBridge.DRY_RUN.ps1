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
$forbiddenTerms = @(".env", "secrets", "credentials", "broker", "OANDA", "live webhook", "real order")

try {
    python -m py_compile services/python_supervisor/autonomy_bridge.py
    Add-Result $results "python_parse" "PASS" "services/python_supervisor/autonomy_bridge.py"
} catch {
    Add-Result $results "python_parse" "FAIL" $_.Exception.Message
}

foreach ($script in @(
    "automation/orchestration/night_supervisor/Invoke-AiOsAutonomyBridge.DRY_RUN.ps1",
    "automation/status/Test-AiOsAutonomyBridge.DRY_RUN.ps1"
)) {
    try {
        [scriptblock]::Create((Get-Content $script -Raw)) | Out-Null
        Add-Result $results "powershell_parse" "PASS" $script
    } catch {
        Add-Result $results "powershell_parse" "FAIL" "$script`: $($_.Exception.Message)"
    }
}

try {
    Get-Content "schemas/aios/orchestration/autonomy_bridge_state.schema.json" -Raw | ConvertFrom-Json | Out-Null
    Add-Result $results "schema_json_parse" "PASS" "schemas/aios/orchestration/autonomy_bridge_state.schema.json"
} catch {
    Add-Result $results "schema_json_parse" "FAIL" $_.Exception.Message
}

try {
    Get-Content "apps/dashboard/mock-data/autonomy_bridge_state.sample.json" -Raw | ConvertFrom-Json | Out-Null
    Add-Result $results "dashboard_fixture_json_parse" "PASS" "apps/dashboard/mock-data/autonomy_bridge_state.sample.json"
} catch {
    Add-Result $results "dashboard_fixture_json_parse" "FAIL" $_.Exception.Message
}

$generatedJson = @(
    "telemetry/morning_digest/MORNING_DIGEST_STATE.json",
    "telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json"
)
foreach ($path in $generatedJson) {
    if (Test-Path $path) {
        try {
            $payload = Get-Content $path -Raw | ConvertFrom-Json
            if (-not $payload.dashboard_cards -or $payload.dashboard_cards.Count -lt 1) {
                Add-Result $results "generated_dashboard_cards" "FAIL" "$path missing dashboard_cards."
            } else {
                $card = $payload.dashboard_cards[0]
                $missing = @("title", "status", "summary", "metrics", "next_action", "details_ref") | Where-Object { -not $card.PSObject.Properties.Name.Contains($_) }
                if ($missing.Count -gt 0) {
                    Add-Result $results "generated_dashboard_cards" "FAIL" "$path missing card fields: $($missing -join ', ')"
                } else {
                    Add-Result $results "generated_dashboard_cards" "PASS" $path
                }
            }
        } catch {
            Add-Result $results "generated_json_parse" "FAIL" "$path`: $($_.Exception.Message)"
        }
    } else {
        Add-Result $results "generated_json_parse" "WARN" "$path not present; APPLY has not generated runtime output."
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
    schema = "AIOS_AUTONOMY_BRIDGE_VALIDATION.v1"
    mode = "DRY_RUN"
    overall_status = $overall
    results = $results
    next_safe_action = "Review validator output before commit approval."
} | ConvertTo-Json -Depth 8

if ($overall -eq "FAIL") {
    exit 1
}
