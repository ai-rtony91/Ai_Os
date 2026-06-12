param()

$ErrorActionPreference = "Stop"

# LEGACY APPLY SAFETY GUARD:
# This scaffold targets legacy docs/AI_OS/trading_laboratory paths and must not be run as current execution.
# It does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.
$ExpectedRootName = "Ai.Os"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$RepoName = Split-Path -Leaf $RepoRoot

if ($RepoName -ne $ExpectedRootName) {
    throw "Repo root verification failed. Expected folder '$ExpectedRootName' but found '$RepoName' at '$RepoRoot'."
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$ReportDir = Join-Path $RepoRoot "Reports\health"
$ReportPath = Join-Path $ReportDir "TRADING_LAB_CORE_APPLY_$Timestamp.md"

if (-not (Test-Path -LiteralPath $ReportDir -PathType Container)) {
    throw "Reports\health does not exist. APPLY will not proceed."
}

$Folders = @(
    @{ Path = "docs/AI_OS/trading_laboratory"; Purpose = "Root folder for AI_OS Trading Laboratory documentation, templates, schemas, and reports." },
    @{ Path = "docs/AI_OS/trading_laboratory/telemetry"; Purpose = "Planning area for non-live trading laboratory telemetry concepts and fixtures." },
    @{ Path = "docs/AI_OS/trading_laboratory/paper_trades"; Purpose = "Paper trade ledger templates and review-only paper execution records." },
    @{ Path = "docs/AI_OS/trading_laboratory/signal_logs"; Purpose = "Signal log templates for non-live signal review and audit trails." },
    @{ Path = "docs/AI_OS/trading_laboratory/regime_analysis"; Purpose = "Draft regime tagging and market-condition review rules." },
    @{ Path = "docs/AI_OS/trading_laboratory/expectancy"; Purpose = "Expectancy metric planning and paper-trade analysis templates." },
    @{ Path = "docs/AI_OS/trading_laboratory/postmortems"; Purpose = "Trade postmortem templates for learning and review." },
    @{ Path = "docs/AI_OS/trading_laboratory/replay"; Purpose = "Replay record templates for non-live scenario review." },
    @{ Path = "docs/AI_OS/trading_laboratory/metrics"; Purpose = "Metrics templates for paper-trade and lab performance review." },
    @{ Path = "docs/AI_OS/trading_laboratory/schemas"; Purpose = "JSON schemas for trading laboratory fixtures and records." },
    @{ Path = "docs/AI_OS/trading_laboratory/reports"; Purpose = "Trading Laboratory report templates and daily review drafts." },
    @{ Path = "automation/trading_lab"; Purpose = "DRY_RUN/APPLY governed scaffold scripts for AI_OS Trading Laboratory." }
)

$Files = @(
    @{ Path = "docs/AI_OS/trading_laboratory/README.md"; Content = "# AI_OS Trading Laboratory`n`nStatic scaffold for paper-trade analysis, signal review, regime tagging, expectancy metrics, replay records, and postmortems.`n`nSafety boundary: no broker automation, no live trading, no credentials, no API calls, and no live order path." },
    @{ Path = "docs/AI_OS/trading_laboratory/TRADING_LAB_CORE_SPEC.md"; Content = "# Trading Lab Core Spec`n`nPurpose: define a documentation-first laboratory for paper trades, signal logs, regime analysis, expectancy metrics, replay, and postmortems.`n`nThis spec does not approve backend calls, API calls, credentials, persistence, broker automation, live trading, or live order path behavior." },
    @{ Path = "docs/AI_OS/trading_laboratory/schemas/signal.schema.json"; Content = "{`n  `"$schema`": `"https://json-schema.org/draft/2020-12/schema`",`n  `"title`": `"AI_OS Trading Lab Signal`",`n  `"type`": `"object`",`n  `"additionalProperties`": false,`n  `"properties`": {`n    `"signal_id`": { `"type`": `"string`" },`n    `"timestamp`": { `"type`": `"string`" },`n    `"symbol`": { `"type`": `"string`" },`n    `"direction`": { `"enum`": [`"long`", `"short`", `"flat`", `"review`"] },`n    `"confidence_label`": { `"type`": `"string`" },`n    `"notes`": { `"type`": `"string`" }`n  },`n  `"required`": [`"signal_id`", `"timestamp`", `"symbol`", `"direction`"]`n}" },
    @{ Path = "docs/AI_OS/trading_laboratory/schemas/execution.schema.json"; Content = "{`n  `"$schema`": `"https://json-schema.org/draft/2020-12/schema`",`n  `"title`": `"AI_OS Trading Lab Paper Execution`",`n  `"type`": `"object`",`n  `"additionalProperties`": false,`n  `"properties`": {`n    `"execution_id`": { `"type`": `"string`" },`n    `"signal_id`": { `"type`": `"string`" },`n    `"mode`": { `"const`": `"paper`" },`n    `"entry_price`": { `"type`": `"number`" },`n    `"exit_price`": { `"type`": [`"number`", `"null`"] },`n    `"status`": { `"enum`": [`"OPEN`", `"CLOSED`", `"REVIEW`"] }`n  },`n  `"required`": [`"execution_id`", `"signal_id`", `"mode`", `"status`"]`n}" },
    @{ Path = "docs/AI_OS/trading_laboratory/schemas/regime.schema.json"; Content = "{`n  `"$schema`": `"https://json-schema.org/draft/2020-12/schema`",`n  `"title`": `"AI_OS Trading Lab Regime Tag`",`n  `"type`": `"object`",`n  `"properties`": {`n    `"regime_id`": { `"type`": `"string`" },`n    `"timestamp`": { `"type`": `"string`" },`n    `"symbol`": { `"type`": `"string`" },`n    `"regime_label`": { `"type`": `"string`" },`n    `"evidence`": { `"type`": `"string`" }`n  },`n  `"required`": [`"regime_id`", `"timestamp`", `"symbol`", `"regime_label`"]`n}" },
    @{ Path = "docs/AI_OS/trading_laboratory/schemas/trade_outcome.schema.json"; Content = "{`n  `"$schema`": `"https://json-schema.org/draft/2020-12/schema`",`n  `"title`": `"AI_OS Trading Lab Trade Outcome`",`n  `"type`": `"object`",`n  `"properties`": {`n    `"trade_id`": { `"type`": `"string`" },`n    `"result_r`": { `"type`": `"number`" },`n    `"mistake_tag`": { `"type`": `"string`" },`n    `"postmortem_required`": { `"type`": `"boolean`" }`n  },`n  `"required`": [`"trade_id`", `"result_r`", `"postmortem_required`"]`n}" },
    @{ Path = "docs/AI_OS/trading_laboratory/schemas/expectancy_metrics.schema.json"; Content = "{`n  `"$schema`": `"https://json-schema.org/draft/2020-12/schema`",`n  `"title`": `"AI_OS Trading Lab Expectancy Metrics`",`n  `"type`": `"object`",`n  `"properties`": {`n    `"sample_size`": { `"type`": `"integer`" },`n    `"win_rate`": { `"type`": `"number`" },`n    `"avg_win_r`": { `"type`": `"number`" },`n    `"avg_loss_r`": { `"type`": `"number`" },`n    `"expectancy_r`": { `"type`": `"number`" }`n  },`n  `"required`": [`"sample_size`", `"win_rate`", `"expectancy_r`"]`n}" },
    @{ Path = "docs/AI_OS/trading_laboratory/paper_trades/PAPER_TRADE_LEDGER_TEMPLATE.csv"; Content = "trade_id,signal_id,timestamp,symbol,direction,entry_price,exit_price,result_r,status,notes" },
    @{ Path = "docs/AI_OS/trading_laboratory/signal_logs/SIGNAL_LOG_TEMPLATE.csv"; Content = "signal_id,timestamp,symbol,direction,confidence_label,regime_label,evidence,notes" },
    @{ Path = "docs/AI_OS/trading_laboratory/regime_analysis/REGIME_TAGGING_RULES_DRAFT.md"; Content = "# Regime Tagging Rules Draft`n`nDefine paper-review market regime labels, required evidence, and mismatch handling. No live market execution or broker automation is approved." },
    @{ Path = "docs/AI_OS/trading_laboratory/expectancy/EXPECTANCY_METRICS_DRAFT.md"; Content = "# Expectancy Metrics Draft`n`nTrack paper-trade sample size, win rate, average win/loss in R, expectancy in R, drawdown notes, and INVALID DATA labels where evidence is missing." },
    @{ Path = "docs/AI_OS/trading_laboratory/postmortems/TRADE_POSTMORTEM_TEMPLATE.md"; Content = "# Trade Postmortem Template`n`n- Trade ID:`n- Setup:`n- Regime:`n- Signal evidence:`n- Outcome:`n- Mistake tag:`n- Lesson:`n- Next rule adjustment:`n`nBoundary: postmortems are review-only and do not approve live trading." },
    @{ Path = "docs/AI_OS/trading_laboratory/replay/REPLAY_RECORD_TEMPLATE.json"; Content = "{`n  `"replay_id`": `"TEMPLATE`",`n  `"mode`": `"paper_review_only`",`n  `"source`": `"STATIC_TEMPLATE`",`n  `"events`": [],`n  `"notes`": `"No live execution or broker automation is approved.`"`n}" },
    @{ Path = "docs/AI_OS/trading_laboratory/metrics/TRADING_LAB_METRICS_TEMPLATE.csv"; Content = "date,sample_size,win_rate,avg_win_r,avg_loss_r,expectancy_r,blocked_items,notes" },
    @{ Path = "docs/AI_OS/trading_laboratory/reports/TRADING_LAB_DAILY_REPORT_TEMPLATE.md"; Content = "# Trading Lab Daily Report Template`n`n- Date:`n- Paper trades reviewed:`n- Signals reviewed:`n- Regimes tagged:`n- Expectancy summary:`n- Postmortems required:`n- BLOCKED items:`n- INVALID DATA:`n- Next safe action:" }
)

$Created = New-Object System.Collections.Generic.List[string]
$Skipped = New-Object System.Collections.Generic.List[string]

foreach ($Folder in $Folders) {
    $FullPath = Join-Path $RepoRoot ($Folder.Path -replace "/", "\")
    if (Test-Path -LiteralPath $FullPath -PathType Container) {
        $Skipped.Add("SKIPPED_EXISTS folder $($Folder.Path)")
    } else {
        New-Item -ItemType Directory -Path $FullPath | Out-Null
        $Created.Add("CREATED folder $($Folder.Path)")
    }

    $PurposePath = Join-Path $FullPath "README_FOLDER_PURPOSE.txt"
    if (Test-Path -LiteralPath $PurposePath -PathType Leaf) {
        $Skipped.Add("SKIPPED_EXISTS file $($Folder.Path)/README_FOLDER_PURPOSE.txt")
    } else {
        $PurposeText = "Purpose: $($Folder.Purpose)`n`nBoundary: Review-only scaffold. No credentials, broker automation, live trading, API calls, or live order path behavior."
        Set-Content -LiteralPath $PurposePath -Value $PurposeText -Encoding UTF8
        $Created.Add("CREATED file $($Folder.Path)/README_FOLDER_PURPOSE.txt")
    }
}

foreach ($File in $Files) {
    $FullPath = Join-Path $RepoRoot ($File.Path -replace "/", "\")
    if (Test-Path -LiteralPath $FullPath -PathType Leaf) {
        $Skipped.Add("SKIPPED_EXISTS file $($File.Path)")
    } else {
        $Parent = Split-Path -Parent $FullPath
        if (-not (Test-Path -LiteralPath $Parent -PathType Container)) {
            throw "Parent folder missing for $($File.Path). APPLY aborted."
        }
        Set-Content -LiteralPath $FullPath -Value $File.Content -Encoding UTF8
        $Created.Add("CREATED file $($File.Path)")
    }
}

$Report = @()
$Report += "# AI_OS Trading Laboratory Core APPLY Report"
$Report += ""
$Report += "- Mode: APPLY"
$Report += "- Repo root: $RepoRoot"
$Report += "- Timestamp: $Timestamp"
$Report += "- Report path: $ReportPath"
$Report += "- Created count: $($Created.Count)"
$Report += "- Skipped-existing count: $($Skipped.Count)"
$Report += "- Safety: no backend, no API calls, no credentials, no persistence, no broker/trading automation, no live order path"
$Report += ""
$Report += "## Created"
$Report += ""
foreach ($Item in $Created) { $Report += "- $Item" }
$Report += ""
$Report += "## Skipped Existing"
$Report += ""
foreach ($Item in $Skipped) { $Report += "- $Item" }
$Report += ""
$Report += "APPLY COMPLETE - REVIEW GIT STATUS"

Set-Content -LiteralPath $ReportPath -Value ($Report -join [Environment]::NewLine) -Encoding UTF8

Write-Host "Repo root: $RepoRoot"
Write-Host "Report path: $ReportPath"
Write-Host "Created count: $($Created.Count)"
Write-Host "Skipped-existing count: $($Skipped.Count)"
Write-Host "APPLY COMPLETE - REVIEW GIT STATUS"
