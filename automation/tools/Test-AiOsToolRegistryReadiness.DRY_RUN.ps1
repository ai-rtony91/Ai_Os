Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$requiredPaths = @(
    "docs\AI_OS\tools\AIOS_TOOL_REGISTRY_STATUS_MODEL_DRAFT.md",
    "docs\AI_OS\tools\AIOS_TOOL_INSTALL_READINESS_CHECKLIST_DRAFT.md",
    "docs\AI_OS\tools\AIOS_TOOL_REGISTRY_DASHBOARD_STATUS_CONTRACT_DRAFT.md",
    "docs\AI_OS\tools\AIOS_TOOL_AUTH_BOUNDARY_RULES_DRAFT.md",
    "automation\tools\Get-AiOsToolRegistrySnapshot.DRY_RUN.ps1",
    "apps\dashboard\mock-data\tool-registry-status-fixture.example.json",
    "Reports\health\AIOS_TOOL_REGISTRY_HEALTH_TEMPLATE.md"
)

$missing = @()
foreach ($relativePath in $requiredPaths) {
    $fullPath = Join-Path $repoRoot $relativePath
    if (-not (Test-Path $fullPath)) {
        $missing += $relativePath
    }
}

$snapshotScript = Join-Path $repoRoot "automation\tools\Get-AiOsToolRegistrySnapshot.DRY_RUN.ps1"
$snapshot = & $snapshotScript

$result = [pscustomobject]@{
    mode = "DRY_RUN"
    status = $(if ($missing.Count -eq 0) { "PASS" } else { "FAIL" })
    missing_files = $missing
    tools_checked = $snapshot.tools.Count
    safety = @{
        installs = "BLOCKED"
        secrets = "BLOCKED"
        account_connections = "BLOCKED"
        external_apis = "BLOCKED"
        brokers = "BLOCKED"
        dashboard_code_edits = "BLOCKED"
    }
}

$result | ConvertTo-Json -Depth 5

if ($missing.Count -gt 0) {
    exit 1
}
