[CmdletBinding()]
param(
    [string[]]$ChangedPaths = @()
)

$ErrorActionPreference = "Stop"

$validators = [System.Collections.Generic.List[string]]::new()
$validators.Add("automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1") | Out-Null
$validators.Add("automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1") | Out-Null

if ($ChangedPaths | Where-Object { $_ -like "automation/orchestration/locks/*" }) {
    $validators.Add("automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1") | Out-Null
}

if ($ChangedPaths | Where-Object { $_ -like "automation/orchestration/approval_inbox/*" }) {
    $validators.Add("automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1") | Out-Null
    $validators.Add("automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1") | Out-Null
}

if ($ChangedPaths | Where-Object { $_ -like "automation/orchestration/commit_packages/*" }) {
    $validators.Add("automation/orchestration/validators/Test-CommitPackageManifest.DRY_RUN.ps1") | Out-Null
}

$blockedPatterns = @("broker/", "OANDA/", "api_keys/", "live_trading/", "live_order/", "real_orders", "webhooks/")
$blockedMatches = @(
    foreach ($path in $ChangedPaths) {
        foreach ($pattern in $blockedPatterns) {
            if ($path -like "*$pattern*") { $path }
        }
    }
) | Select-Object -Unique

[pscustomobject]@{
    schema = "AIOS_CREW_VALIDATOR_RECOMMENDATION.v1"
    mode = "DRY_RUN_READ_ONLY"
    changed_paths = $ChangedPaths
    recommended_validators = @($validators | Select-Object -Unique)
    blocked_path_matches = $blockedMatches
    status = if ($blockedMatches.Count -gt 0) { "BLOCKED" } else { "REVIEW_REQUIRED" }
    modifies_files = $false
    commits = $false
    pushes = $false
    next_safe_action = if ($blockedMatches.Count -gt 0) { "Remove blocked paths before APPLY." } else { "Run recommended validators before approval or commit packaging." }
} | ConvertTo-Json -Depth 8
