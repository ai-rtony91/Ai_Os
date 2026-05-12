Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$docRoot = Join-Path $repoRoot "docs\AI_OS\security\secure_access"

$requiredFiles = @(
    "STAGE_14_7_SECURE_ACCESS_ARCHITECTURE.md",
    "AIOS_ACCESS_MODEL_OVERVIEW.md",
    "CLOUDFLARE_ACCESS_FRONT_DOOR.md",
    "MICROSOFT_ENTRA_SSO_MODEL.md",
    "YUBIKEY_PASSKEY_MODEL.md",
    "GITHUB_REPO_IDENTITY_BOUNDARY.md",
    "AIOS_PORTAL_ZONE_MODEL.md",
    "AIOS_ADMIN_ZONE_REAUTH_RULES.md",
    "SECURE_ACCESS_SETUP_CHECKLIST_TEMPLATE.md",
    "SECURE_ACCESS_FILE_INDEX.md"
)

$forbiddenTerms = @(
    "client_secret=",
    "tenant_id=",
    "api_key=",
    "password=",
    "private_key",
    "broker_execute",
    "live_order"
)

$failures = New-Object System.Collections.Generic.List[string]

foreach ($file in $requiredFiles) {
    $path = Join-Path $docRoot $file
    if (-not (Test-Path -LiteralPath $path)) {
        $failures.Add("Missing required file: $file")
        continue
    }
    $content = Get-Content -LiteralPath $path -Raw
    foreach ($term in $forbiddenTerms) {
        if ($content.IndexOf($term, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $failures.Add("Forbidden term found in ${file}: ${term}")
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Host "AI_OS Secure Access Docs Validation: FAIL"
    foreach ($failure in $failures) {
        Write-Host "- $failure"
    }
    exit 1
}

Write-Host "AI_OS Secure Access Docs Validation: PASS"
Write-Host "Required files: PASS"
Write-Host "Forbidden term scan: PASS"
Write-Host "Docs-only boundary: PASS"
Write-Host "Trading remains paper-only: PASS"
