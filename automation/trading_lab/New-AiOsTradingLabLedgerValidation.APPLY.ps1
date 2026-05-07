param()

$ErrorActionPreference = "Stop"

$ExpectedRootName = "ai-rtony91_Ai_Os_CLEAN"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$RepoName = Split-Path -Leaf $RepoRoot

if ($RepoName -ne $ExpectedRootName) {
    throw "Repo root verification failed. Expected '$ExpectedRootName' but found '$RepoName' at '$RepoRoot'."
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$ReportDir = Join-Path $RepoRoot "Reports\health"
$ReportPath = Join-Path $ReportDir "TRADING_LAB_LEDGER_VALIDATION_APPLY_$Timestamp.md"

if (-not (Test-Path -LiteralPath $ReportDir -PathType Container)) {
    throw "Reports\health does not exist. APPLY will not proceed."
}

$Folders = @(
    @{ Path = "docs/AI_OS/trading_laboratory/validation"; Purpose = "Validation specifications, rules, result templates, and error-code drafts for the AI_OS Trading Laboratory." }
)

$Files = @(
    @{ Path = "docs/AI_OS/trading_laboratory/validation/README_FOLDER_PURPOSE.txt"; Content = "Purpose: Validation specifications, rules, result templates, and error-code drafts for the AI_OS Trading Laboratory.`n`nBoundary: No credentials, no broker/live trading logic, no backend/API calls, no persistence, and no live order path." },
    @{ Path = "docs/AI_OS/trading_laboratory/validation/TRADING_LAB_SCHEMA_VALIDATION_SPEC.md"; Content = "# Trading Lab Schema Validation Spec`n`nDefines static validation expectations for paper-trade ledgers, signal logs, regime records, trade outcomes, and expectancy metrics.`n`nNo credentials, broker/live trading logic, backend/API calls, persistence, or live order path are approved." },
    @{ Path = "docs/AI_OS/trading_laboratory/validation/VALIDATION_RULES_DRAFT.md"; Content = "# Validation Rules Draft`n`n- Required columns must be present.`n- Required schema fields must be present.`n- Unknown data must be labeled UNKNOWN.`n- Mismatches must be reported, not hidden.`n- Invalid records must be labeled INVALID DATA.`n`nValidation is review-only and does not approve trading automation." },
    @{ Path = "docs/AI_OS/trading_laboratory/validation/VALIDATION_RESULT_TEMPLATE.json"; Content = "{`n  `"validation_name`": `"TRADING_LAB_TEMPLATE`",`n  `"mode`": `"review_only`",`n  `"status`": `"REVIEW`",`n  `"checked_files`": [],`n  `"errors`": [],`n  `"unknowns`": [],`n  `"blocked_actions`": [`"credentials`", `"broker/live trading logic`", `"live order path`"]`n}" },
    @{ Path = "docs/AI_OS/trading_laboratory/validation/VALIDATION_ERROR_CODES_DRAFT.md"; Content = "# Validation Error Codes Draft`n`n- `MISSING_REQUIRED_COLUMN`: Required ledger column missing.`n- `MISSING_REQUIRED_FIELD`: Required schema field missing.`n- `INVALID_DATA`: Evidence conflicts or cannot be verified.`n- `UNKNOWN_VALUE`: Required evidence is unknown.`n- `BLOCKED_ACTION`: Proposed action touches credentials, broker/live trading logic, or live order path." },
    @{ Path = "docs/AI_OS/trading_laboratory/paper_trades/PAPER_TRADE_LEDGER_COLUMNS.md"; Content = "# Paper Trade Ledger Columns`n`nRequired columns: trade_id, signal_id, timestamp, symbol, direction, entry_price, exit_price, result_r, status, notes.`n`nLedger is paper-review only and does not approve live trading." },
    @{ Path = "docs/AI_OS/trading_laboratory/signal_logs/SIGNAL_LOG_COLUMNS.md"; Content = "# Signal Log Columns`n`nRequired columns: signal_id, timestamp, symbol, direction, confidence_label, regime_label, evidence, notes.`n`nSignal logs are review-only and must not trigger broker/live trading logic." },
    @{ Path = "docs/AI_OS/trading_laboratory/metrics/EXPECTANCY_CALCULATION_NOTES.md"; Content = "# Expectancy Calculation Notes`n`nExpectancy in R should be calculated from reviewed paper-trade outcomes only. Missing or conflicting evidence must be labeled UNKNOWN or INVALID DATA.`n`nNo live trading, broker automation, credentials, backend/API calls, persistence, or live order path behavior is approved." }
)

$Created = New-Object System.Collections.Generic.List[string]
$Skipped = New-Object System.Collections.Generic.List[string]
$Blocked = New-Object System.Collections.Generic.List[string]

foreach ($Folder in $Folders) {
    $FullPath = Join-Path $RepoRoot ($Folder.Path -replace "/", "\")
    if (Test-Path -LiteralPath $FullPath -PathType Container) {
        $Skipped.Add("SKIPPED_EXISTS folder $($Folder.Path)")
    } else {
        $Parent = Split-Path -Parent $FullPath
        if (-not (Test-Path -LiteralPath $Parent -PathType Container)) {
            $Blocked.Add("BLOCKED_PARENT_MISSING folder $($Folder.Path)")
        } else {
            New-Item -ItemType Directory -Path $FullPath | Out-Null
            $Created.Add("CREATED folder $($Folder.Path)")
        }
    }
}

foreach ($File in $Files) {
    $FullPath = Join-Path $RepoRoot ($File.Path -replace "/", "\")
    if (Test-Path -LiteralPath $FullPath -PathType Leaf) {
        $Skipped.Add("SKIPPED_EXISTS file $($File.Path)")
    } else {
        $Parent = Split-Path -Parent $FullPath
        if (-not (Test-Path -LiteralPath $Parent -PathType Container)) {
            $Blocked.Add("BLOCKED_PARENT_MISSING file $($File.Path)")
        } else {
            Set-Content -LiteralPath $FullPath -Value $File.Content -Encoding UTF8
            $Created.Add("CREATED file $($File.Path)")
        }
    }
}

$Report = @()
$Report += "# AI_OS Trading Laboratory Ledger + Schema Validation APPLY Report"
$Report += ""
$Report += "- Mode: APPLY"
$Report += "- Repo root: $RepoRoot"
$Report += "- Timestamp: $Timestamp"
$Report += "- Report path: $ReportPath"
$Report += "- Created count: $($Created.Count)"
$Report += "- Skipped-existing count: $($Skipped.Count)"
$Report += "- Blocked-parent-missing count: $($Blocked.Count)"
$Report += "- Safety: no credentials, no broker/live trading logic, no backend/API calls, no persistence, no live order path"
$Report += ""
$Report += "## Created"
$Report += ""
foreach ($Item in $Created) { $Report += "- $Item" }
$Report += ""
$Report += "## Skipped Existing"
$Report += ""
foreach ($Item in $Skipped) { $Report += "- $Item" }
$Report += ""
$Report += "## Blocked"
$Report += ""
foreach ($Item in $Blocked) { $Report += "- $Item" }
$Report += ""
$Report += "APPLY COMPLETE - REVIEW GIT STATUS"

Set-Content -LiteralPath $ReportPath -Value ($Report -join [Environment]::NewLine) -Encoding UTF8

Write-Host "Repo root: $RepoRoot"
Write-Host "Report path: $ReportPath"
Write-Host "Created count: $($Created.Count)"
Write-Host "Skipped-existing count: $($Skipped.Count)"
Write-Host "Blocked-parent-missing count: $($Blocked.Count)"
Write-Host "APPLY COMPLETE - REVIEW GIT STATUS"
