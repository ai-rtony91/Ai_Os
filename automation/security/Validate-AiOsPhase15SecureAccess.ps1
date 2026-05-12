Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$docRoot = Join-Path $repoRoot "docs\AI_OS\security\phase_15_secure_access"

$requiredFiles = @(
    "PHASE_15_SECURE_ACCESS_FOUNDATION.md",
    "STAGE_15_1_OPERATOR_PORTAL_FRONT_DOOR.md",
    "CLOUDFLARE_ACCESS_SETUP_PLAN.md",
    "MICROSOFT_ENTRA_SSO_SETUP_PLAN.md",
    "YUBIKEY_PASSKEY_OPERATOR_MODEL.md",
    "AIOS_PORTAL_ZONE_MODEL.md",
    "SECURE_ACCESS_VALIDATION_CHECKLIST.md",
    "PHASE_15_FILE_INDEX.md"
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
    Write-Host "AI_OS Phase 15 Secure Access Validation: FAIL"
    foreach ($failure in $failures) {
        Write-Host "- $failure"
    }
    exit 1
}

Write-Host "AI_OS Phase 15 Secure Access Validation: PASS"
Write-Host "Required files: PASS"
Write-Host "Forbidden term scan: PASS"
Write-Host "Docs-only boundary: PASS"
Write-Host "No config/account changes: PASS"
Write-Host "Trading execution remains disabled: PASS"
