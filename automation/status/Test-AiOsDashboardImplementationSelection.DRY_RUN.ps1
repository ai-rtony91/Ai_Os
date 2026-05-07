param(
    [string]$RepoRoot = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
)

$ErrorActionPreference = "Stop"

Write-Host "Task name: AI_OS Stage 41A-41F Dashboard Implementation Selection Dry Run"
Write-Host "Mode: DRY_RUN"
Write-Host "Repo root: $RepoRoot"
Write-Host "Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, dashboard-written, or traded."
Write-Host ""

$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-RequiredFile {
    param(
        [string]$Label,
        [string]$RelativePath
    )

    $fullPath = Join-Path $RepoRoot $RelativePath
    if (Test-Path -LiteralPath $fullPath) {
        Write-Host "[PASS] ${Label}: $RelativePath"
        return $true
    }

    Write-Host "[FAIL] ${Label}: missing $RelativePath"
    $script:failures.Add("Missing required file: $RelativePath")
    return $false
}

function Test-RequiredPhrase {
    param(
        [string]$Phrase,
        [string[]]$RelativePaths
    )

    foreach ($relativePath in $RelativePaths) {
        $fullPath = Join-Path $RepoRoot $relativePath
        if ((Test-Path -LiteralPath $fullPath) -and ((Get-Content -LiteralPath $fullPath -Raw) -match [regex]::Escape($Phrase))) {
            Write-Host "[PASS] $Phrase"
            return $true
        }
    }

    Write-Host "[FAIL] $Phrase"
    $script:failures.Add("Missing required phrase: $Phrase")
    return $false
}

Push-Location $RepoRoot
try {
    $stage41Files = @(
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_IMPLEMENTATION_SELECTION_RUBRIC_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_PROTOTYPE_BOUNDARY_RULES_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_UI_STACK_SCORING_MATRIX_DRAFT.json",
        "automation\status\Test-AiOsDashboardImplementationSelection.DRY_RUN.ps1",
        "Reports\health\STAGE41A_41F_DASHBOARD_IMPLEMENTATION_SELECTION_README.txt"
    )

    Write-Host "File checks:"
    Test-RequiredFile "dashboard implementation selection rubric" $stage41Files[0] | Out-Null
    Test-RequiredFile "prototype boundary rules" $stage41Files[1] | Out-Null
    Test-RequiredFile "UI stack scoring matrix" $stage41Files[2] | Out-Null
    Test-RequiredFile "dashboard implementation selection validator" $stage41Files[3] | Out-Null
    Test-RequiredFile "Stage 41 health README" $stage41Files[4] | Out-Null
    Test-RequiredFile "Stage 36 dashboard prep contract" "docs\AI_OS\dashboard\AIOS_DASHBOARD_PREP_CONTRACT_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 36 dashboard input map" "docs\AI_OS\dashboard\AIOS_DASHBOARD_DATA_INPUT_MAP_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 37 dashboard fixture data" "docs\AI_OS\dashboard\AIOS_DASHBOARD_FIXTURE_DATA_DRAFT.json" | Out-Null
    Test-RequiredFile "Stage 37 dashboard panel layout" "docs\AI_OS\dashboard\AIOS_DASHBOARD_PANEL_LAYOUT_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 38 static dashboard mock contract" "docs\AI_OS\dashboard\AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 38 operator view layout" "docs\AI_OS\dashboard\AIOS_DASHBOARD_OPERATOR_VIEW_LAYOUT_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 39 visual render plan" "docs\AI_OS\dashboard\AIOS_VISUAL_DASHBOARD_RENDER_PLAN_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 39 dashboard theme system" "docs\AI_OS\dashboard\AIOS_DASHBOARD_THEME_SYSTEM_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 39 dashboard widget library" "docs\AI_OS\dashboard\AIOS_DASHBOARD_WIDGET_LIBRARY_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 40 rendering stack evaluation" "docs\AI_OS\dashboard\AIOS_RENDERING_STACK_EVALUATION_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 40 frontend runtime architecture" "docs\AI_OS\dashboard\AIOS_FRONTEND_RUNTIME_ARCHITECTURE_DRAFT.md" | Out-Null
    Test-RequiredFile "Stage 40 UI performance requirements" "docs\AI_OS\dashboard\AIOS_UI_PERFORMANCE_REQUIREMENTS_DRAFT.md" | Out-Null

    if (Test-Path -LiteralPath (Join-Path $RepoRoot $stage41Files[2])) {
        try {
            Get-Content -LiteralPath (Join-Path $RepoRoot $stage41Files[2]) -Raw | ConvertFrom-Json | Out-Null
            Write-Host "[PASS] UI stack scoring matrix JSON parses."
        } catch {
            Write-Host "[FAIL] UI stack scoring matrix JSON does not parse."
            $failures.Add("UI stack scoring matrix JSON parse failed.")
        }
    }

    Write-Host ""
    Write-Host "Phrase checks:"
    $phrases = @(
        "React",
        "Electron",
        "Tauri",
        "low latency",
        "GPU",
        "offline",
        "multi-monitor",
        "read-only dashboard",
        "mock data only",
        "dashboard production outputs require separate approval"
    )

    foreach ($phrase in $phrases) {
        Test-RequiredPhrase $phrase $stage41Files | Out-Null
    }

    $protectedPaths = @(
        "README.md",
        "AGENTS.md",
        "RISK_POLICY.md",
        "SOURCE_LOG.md",
        "ERROR_LOG.md",
        "HALLUCINATION_LOG.md",
        "AAR.md",
        "DAILY_REPORT.md",
        "WHITEPAPER.md",
        "Reports\DAILY_METRICS.csv",
        "Reports\CHECKPOINT_INDEX.md"
    )

    Write-Host ""
    Write-Host "Unstaged protected-file check:"
    $unstaged = @(git diff --name-only -- $protectedPaths)
    if ($unstaged.Count -eq 0) {
        Write-Host "[PASS] unstaged protected-file check is clean."
    } else {
        Write-Host "[FAIL] unstaged protected-file changes detected:"
        $unstaged | ForEach-Object { Write-Host " - $_" }
        $failures.Add("Unstaged protected-file changes detected.")
    }

    Write-Host ""
    Write-Host "Staged protected-file check:"
    $staged = @(git diff --cached --name-only -- $protectedPaths)
    if ($staged.Count -eq 0) {
        Write-Host "[PASS] staged protected-file check is clean."
    } else {
        Write-Host "[FAIL] staged protected-file changes detected:"
        $staged | ForEach-Object { Write-Host " - $_" }
        $failures.Add("Staged protected-file changes detected.")
    }

    Write-Host ""
    Write-Host "Git status check:"
    $gitStatus = @(git status --short --branch)
    $gitStatus | ForEach-Object { Write-Host $_ }
    if ($gitStatus.Count -gt 1) {
        Write-Host "[WARN] git status is not clean."
        $warnings.Add("git status is not clean.")
    } else {
        Write-Host "[PASS] git status has no file changes."
    }

    Write-Host ""
    if ($failures.Count -gt 0) {
        Write-Host "PASS/WARN/FAIL summary: FAIL"
        $failures | ForEach-Object { Write-Host "- $_" }
    } elseif ($warnings.Count -gt 0) {
        Write-Host "PASS/WARN/FAIL summary: WARN"
        $warnings | ForEach-Object { Write-Host "- $_" }
    } else {
        Write-Host "PASS/WARN/FAIL summary: PASS"
    }
}
finally {
    Pop-Location
}

Write-Host "DRY_RUN COMPLETE - NO DASHBOARD IMPLEMENTATION SELECTION ACTIONS APPLIED."
