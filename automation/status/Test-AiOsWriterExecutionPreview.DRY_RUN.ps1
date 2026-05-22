param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-RequiredFile {
    param(
        [string]$Label,
        [string]$RelativePath
    )

    $path = Join-Path $script:ResolvedRepoRoot $RelativePath
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Write-Host "[PASS] $Label`: $RelativePath"
        return
    }

    Write-Host "[FAIL] $Label`: $RelativePath"
    $script:failures.Add("Missing required file: $Label ($RelativePath)") | Out-Null
}

function Test-Text {
    param(
        [string]$Label,
        [string]$Text,
        [string]$Expected
    )

    if ($Text -match [regex]::Escape($Expected)) {
        Write-Host "[PASS] $Label"
        return
    }

    Write-Host "[FAIL] $Label"
    $script:failures.Add("Missing required text: $Expected") | Out-Null
}

Write-Host 'Task name: AI_OS Stage 27A-27D Writer Execution Preview Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, auto-filled, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual writer execution preview state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER EXECUTION PREVIEW ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
Test-RequiredFile -Label 'writer execution preview helper' -RelativePath 'automation\writers\Preview-AiOsWriterExecution.DRY_RUN.ps1'
Test-RequiredFile -Label 'writer system concepts' -RelativePath 'docs\concepts\aios-writer-system-concepts.md'
Test-RequiredFile -Label 'file population approval gate draft' -RelativePath 'docs\AI_OS\automation\AIOS_FILE_POPULATION_APPROVAL_GATE_DRAFT.md'
Test-RequiredFile -Label 'writer validator chain checker' -RelativePath 'automation\status\Test-AiOsWriterValidatorChain.DRY_RUN.ps1'
Test-RequiredFile -Label 'safe file-population validator' -RelativePath 'automation\status\Test-AiOsSafeFilePopulationWorkflow.DRY_RUN.ps1'

$filesToScan = @(
    'automation\writers\Preview-AiOsWriterExecution.DRY_RUN.ps1',
    'docs\concepts\aios-writer-system-concepts.md',
    'docs\AI_OS\automation\AIOS_FILE_POPULATION_APPROVAL_GATE_DRAFT.md'
)

$text = ''
foreach ($relativePath in $filesToScan) {
    $path = Join-Path $script:ResolvedRepoRoot $relativePath
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $text += "`n"
        $text += Get-Content -LiteralPath $path -Raw
    }
}

Write-Host ''
Write-Host 'Phrase checks:'
$requiredPhrases = @(
    'NO FILES WERE WRITTEN',
    'protected file without approval',
    'missing validator',
    'blocked fields present',
    'verify ownership contract',
    'run validator chain',
    'verify approval gate',
    'future APPLY consideration'
)

foreach ($phrase in $requiredPhrases) {
    Test-Text -Label $phrase -Text $text -Expected $phrase
}

$protectedPaths = @(
    'README.md',
    'AGENTS.md',
    'RISK_POLICY.md',
    'SOURCE_LOG.md',
    'ERROR_LOG.md',
    'HALLUCINATION_LOG.md',
    'AAR.md',
    'DAILY_REPORT.md',
    'WHITEPAPER.md',
    'Reports\DAILY_METRICS.csv',
    'Reports\CHECKPOINT_INDEX.md'
)

Write-Host ''
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Host '[WARN] git command unavailable.'
    $warnings.Add('git command unavailable.') | Out-Null
}
else {
    Push-Location -LiteralPath $script:ResolvedRepoRoot
    try {
        Write-Host 'Unstaged protected-file check:'
        $protectedDiff = @(& git diff --name-only -- $protectedPaths 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[FAIL] unstaged protected-file check failed.'
            $protectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('unstaged protected-file check failed.') | Out-Null
        }
        elseif ($protectedDiff.Count -gt 0) {
            Write-Host '[FAIL] unstaged protected files changed.'
            $protectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('unstaged protected files changed.') | Out-Null
        }
        else {
            Write-Host '[PASS] unstaged protected-file check is clean.'
        }

        Write-Host ''
        Write-Host 'Staged protected-file check:'
        $cachedProtectedDiff = @(& git diff --cached --name-only -- $protectedPaths 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[FAIL] staged protected-file check failed.'
            $cachedProtectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('staged protected-file check failed.') | Out-Null
        }
        elseif ($cachedProtectedDiff.Count -gt 0) {
            Write-Host '[FAIL] staged protected files changed.'
            $cachedProtectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('staged protected files changed.') | Out-Null
        }
        else {
            Write-Host '[PASS] staged protected-file check is clean.'
        }

        Write-Host ''
        Write-Host 'Git status check:'
        $gitStatus = @(& git status --short --branch 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[WARN] git status failed.'
            $gitStatus | ForEach-Object { Write-Host $_ }
            $warnings.Add('git status failed.') | Out-Null
        }
        else {
            $gitStatus | ForEach-Object { Write-Host $_ }
            if ($gitStatus.Count -gt 1) {
                Write-Host '[WARN] git status is not clean.'
                $warnings.Add('git status is not clean.') | Out-Null
            }
            else {
                Write-Host '[PASS] git status has no listed changes.'
            }
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host ''
if ($failures.Count -gt 0) {
    $writerExecutionPreviewState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $writerExecutionPreviewState = 'WARN_REVIEW_REQUIRED'
}
else {
    $writerExecutionPreviewState = 'WRITER_EXECUTION_PREVIEW_READY_FOR_REVIEW'
}

Write-Host "Conceptual writer execution preview state: $writerExecutionPreviewState"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER EXECUTION PREVIEW ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER EXECUTION PREVIEW ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO WRITER EXECUTION PREVIEW ACTIONS APPLIED.' -f [char]0x2014)
