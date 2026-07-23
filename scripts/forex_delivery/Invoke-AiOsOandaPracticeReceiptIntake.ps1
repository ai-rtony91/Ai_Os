param(
    [Parameter(Mandatory = $true)]
    [string]$ReceiptJson,

    [switch]$Apply,

    [switch]$OwnerConfirmed
)

$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    if ($env:AIOS_REPO_ROOT -and (Test-Path -LiteralPath $env:AIOS_REPO_ROOT)) {
        return (Resolve-Path -LiteralPath $env:AIOS_REPO_ROOT).Path
    }

    if ($PSScriptRoot) {
        $candidate = Join-Path $PSScriptRoot "../.."
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $gitRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -eq 0 -and $gitRoot) {
        return (Resolve-Path -LiteralPath $gitRoot.Trim()).Path
    }

    throw "AIOS_REPO_ROOT_UNRESOLVED"
}

if (-not $OwnerConfirmed) {
    throw "OWNER_CONFIRMATION_REQUIRED: rerun with -OwnerConfirmed only after reviewing the sanitized closed-trade receipt."
}

$repoRoot = Resolve-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$receiptPath = (Resolve-Path -LiteralPath $ReceiptJson -ErrorAction Stop).Path
$branch = (& git branch --show-current).Trim()

if ($Apply) {
    if ($branch -ne "main") {
        throw "RECEIPT_APPLY_REQUIRES_MAIN_BRANCH:$branch"
    }

    $dirty = @(& git status --porcelain --untracked-files=all)
    if ($dirty.Count -gt 0) {
        $dirty | ForEach-Object { Write-Output $_ }
        throw "RECEIPT_APPLY_REQUIRES_CLEAN_WORKTREE"
    }

    python -m pytest tests/forex_engine/test_oanda_practice_closed_trade_receipt_intake_v1.py -q
    if ($LASTEXITCODE -ne 0) {
        throw "RECEIPT_INTAKE_TESTS_FAILED"
    }
}

$arguments = @(
    "scripts/forex_delivery/run_oanda_practice_closed_trade_receipt_intake_v1.py",
    "--repo-root", $repoRoot,
    "--receipt-json", $receiptPath,
    "--pretty",
    "--i-confirm-receipt-reviewed",
    "--i-confirm-demo-practice-only",
    "--i-confirm-closed-trade-only",
    "--i-confirm-no-credentials-or-account-id",
    "--i-confirm-no-raw-broker-payload",
    "--i-confirm-no-order-created-by-intake",
    "--i-confirm-append-only"
)

if ($Apply) {
    $arguments += "--apply"
}

$output = @(& python @arguments 2>&1)
$exitCode = $LASTEXITCODE
$output | ForEach-Object { Write-Output $_ }

if ($exitCode -ne 0) {
    throw "OANDA_PRACTICE_RECEIPT_INTAKE_BLOCKED:$exitCode"
}

if ($Apply) {
    Write-Output "RECEIPT_APPEND_STATUS=PASS"
    Write-Output "NEXT_GATE=EXTENDED_EVIDENCE_VERDICT"
    & pwsh -NoProfile -File "scripts/forex_delivery/Get-AiOsExtendedEvidenceVerdict.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "EXTENDED_EVIDENCE_VERDICT_FAILED_AFTER_APPEND"
    }
}
else {
    Write-Output "RECEIPT_DRY_RUN_STATUS=PASS"
    Write-Output "NEXT_SAFE_ACTION=Review output, then rerun with -Apply while main is clean."
}
