param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "SilentlyContinue"

$scriptName = Split-Path -Leaf $PSCommandPath
$resolverScript = Join-Path (Split-Path $PSCommandPath -Parent) "..\recommendations\Resolve-AiOsSourceOfTruth.ps1"
$resolverScript = [System.IO.Path]::GetFullPath($resolverScript)

$testCases = @(
    [ordered]@{ topic = "worker packet builder";          expect_owner_contains = "work_packets";               expect_not_blocked = $true;  expect_risk_not = "CRITICAL" },
    [ordered]@{ topic = "dashboard runtime visibility";   expect_owner_contains = "dashboard";                  expect_not_blocked = $true;  expect_risk_not = "CRITICAL" },
    [ordered]@{ topic = "Trading Lab paper execution";    expect_owner_contains = "trading_lab";                expect_not_blocked = $true;  expect_risk_not = "CRITICAL" },
    [ordered]@{ topic = "broker credentials";             expect_owner_contains = "BLOCKED";                    expect_not_blocked = $false; expect_risk_not = "" },
    [ordered]@{ topic = "README update";                  expect_owner_contains = "README";                     expect_not_blocked = $true;  expect_risk_not = "CRITICAL" },
    [ordered]@{ topic = "worker registry";                expect_owner_contains = "AIOS_WORKER_REGISTRY";       expect_not_blocked = $true;  expect_risk_not = "CRITICAL" },
    [ordered]@{ topic = "source of truth cleanup";        expect_owner_contains = "source-of-truth-map";        expect_not_blocked = $true;  expect_risk_not = "CRITICAL" }
)

$results = @()
$passCount = 0
$failCount = 0

if (-not (Test-Path -LiteralPath $resolverScript)) {
    Write-Host "ERROR: Resolver script not found at: $resolverScript" -ForegroundColor Red
    exit 1
}

foreach ($case in $testCases) {
    $rawOutput = powershell -ExecutionPolicy Bypass -File $resolverScript -Topic $case.topic -QuietJson 2>&1
    $parsed = $null
    try { $parsed = $rawOutput | ConvertFrom-Json } catch {}

    $pass = $true
    $failReasons = @()

    if ($null -eq $parsed) {
        $pass = $false
        $failReasons += "resolver returned no valid JSON"
    } else {
        $ownerStr = "$($parsed.authority_owner)"
        $riskStr  = "$($parsed.risk_class)"

        if (-not $ownerStr.Contains($case.expect_owner_contains)) {
            $pass = $false
            $failReasons += "authority_owner '$ownerStr' does not contain '$($case.expect_owner_contains)'"
        }

        if ($case.expect_not_blocked -eq $false -and $ownerStr -ne "BLOCKED") {
            $pass = $false
            $failReasons += "expected BLOCKED but got '$ownerStr'"
        }

        if ($case.expect_not_blocked -eq $true -and $ownerStr -eq "BLOCKED") {
            $pass = $false
            $failReasons += "topic should not be blocked but authority_owner is BLOCKED"
        }

        # Broker credentials must always be CRITICAL
        if ($case.topic -eq "broker credentials" -and $riskStr -ne "CRITICAL") {
            $pass = $false
            $failReasons += "broker credentials must be CRITICAL risk. Got '$riskStr'"
        }

        # Trading Lab must not be BLOCKED (paper-only boundary, but not hard-blocked for the topic itself)
        if ($case.topic -eq "Trading Lab paper execution" -and $ownerStr -eq "BLOCKED") {
            $pass = $false
            $failReasons += "Trading Lab paper execution should route to trading_lab paths, not BLOCKED"
        }

        # README must flag high risk (protected root file)
        if ($case.topic -eq "README update" -and $riskStr -eq "CRITICAL") {
            $pass = $false
            $failReasons += "README update is high-risk but should not be CRITICAL. Got '$riskStr'"
        }
    }

    if ($pass) { $passCount++ } else { $failCount++ }

    $results += [ordered]@{
        topic        = $case.topic
        result       = if ($pass) { "PASS" } else { "FAIL" }
        authority    = if ($parsed) { $parsed.authority_owner } else { "ERROR" }
        risk_class   = if ($parsed) { $parsed.risk_class } else { "ERROR" }
        fail_reasons = $failReasons
    }
}

$overall = if ($failCount -eq 0) { "ALL_PASS" } else { "FAIL" }

if ($QuietJson) {
    [pscustomobject]@{
        mode       = "READ_ONLY"
        overall    = $overall
        pass_count = $passCount
        fail_count = $failCount
        results    = $results
    } | ConvertTo-Json -Depth 6
    exit $(if ($failCount -gt 0) { 1 } else { 0 })
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Source-of-Truth Resolver Test Harness" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY - runs resolver against test topics"
Write-Host ""

foreach ($r in $results) {
    $color = if ($r.result -eq "PASS") { "Green" } else { "Red" }
    Write-Host "$($r.result): [$($r.topic)]" -ForegroundColor $color
    Write-Host "  authority: $($r.authority)"
    Write-Host "  risk:      $($r.risk_class)"
    if ($r.fail_reasons.Count -gt 0) {
        foreach ($reason in $r.fail_reasons) {
            Write-Host "  FAIL: $reason" -ForegroundColor Red
        }
    }
}

Write-Host ""
if ($overall -eq "ALL_PASS") {
    Write-Host "OVERALL: ALL_PASS ($passCount/$($testCases.Count))" -ForegroundColor Green
} else {
    Write-Host "OVERALL: FAIL ($failCount failed, $passCount passed)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")

exit $(if ($failCount -gt 0) { 1 } else { 0 })
