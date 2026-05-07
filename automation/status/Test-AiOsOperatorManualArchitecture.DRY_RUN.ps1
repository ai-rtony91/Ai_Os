param(
    [string]$RepoRoot = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
)

$ErrorActionPreference = "Stop"

Write-Host "Task name: AI_OS Stage 43A-43J Operator Manual Architecture Dry Run"
Write-Host "Mode: DRY_RUN"
Write-Host "Repo root: $RepoRoot"
Write-Host "Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, dashboard-written, background-service-created, autonomous-action-enabled, or traded."
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
    $stage43Files = @(
        "docs\AI_OS\dashboard\AIOS_OPERATOR_MANUAL_ARCHITECTURE_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_VOICE_TOUR_GUIDE_SYSTEM_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_TOOLTIP_AND_PANEL_HELP_SYSTEM_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_OPERATOR_ONBOARDING_FLOW_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_ASSISTANT_PERSONA_AND_BEHAVIOR_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_SCREENSHOT_AND_DEMO_CAPTURE_PLAN_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_CONTEXTUAL_WARNING_AND_EXPLANATION_SYSTEM_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_INTERACTIVE_TRAINING_MODE_DRAFT.md",
        "automation\status\Test-AiOsOperatorManualArchitecture.DRY_RUN.ps1",
        "Reports\health\STAGE43A_43J_OPERATOR_MANUAL_ARCHITECTURE_README.txt"
    )

    Write-Host "File checks:"
    Test-RequiredFile "operator manual architecture" $stage43Files[0] | Out-Null
    Test-RequiredFile "voice tour guide system" $stage43Files[1] | Out-Null
    Test-RequiredFile "tooltip and panel help system" $stage43Files[2] | Out-Null
    Test-RequiredFile "operator onboarding flow" $stage43Files[3] | Out-Null
    Test-RequiredFile "assistant persona and behavior" $stage43Files[4] | Out-Null
    Test-RequiredFile "screenshot and demo capture plan" $stage43Files[5] | Out-Null
    Test-RequiredFile "contextual warning and explanation system" $stage43Files[6] | Out-Null
    Test-RequiredFile "interactive training mode" $stage43Files[7] | Out-Null
    Test-RequiredFile "operator manual architecture validator" $stage43Files[8] | Out-Null
    Test-RequiredFile "Stage 43 health README" $stage43Files[9] | Out-Null

    $priorDashboardFiles = @(
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_PREP_CONTRACT_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_DATA_INPUT_MAP_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_FIXTURE_DATA_DRAFT.json",
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_PANEL_LAYOUT_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_OPERATOR_VIEW_LAYOUT_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_VISUAL_DASHBOARD_RENDER_PLAN_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_THEME_SYSTEM_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_WIDGET_LIBRARY_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_RENDERING_STACK_EVALUATION_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_FRONTEND_RUNTIME_ARCHITECTURE_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_UI_PERFORMANCE_REQUIREMENTS_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_DASHBOARD_IMPLEMENTATION_SELECTION_RUBRIC_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_PROTOTYPE_BOUNDARY_RULES_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_UI_STACK_SCORING_MATRIX_DRAFT.json",
        "docs\AI_OS\dashboard\AIOS_STATIC_DASHBOARD_PROTOTYPE_ARCHITECTURE_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_OPERATOR_COCKPIT_LAYOUT_SYSTEM_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_WIDGET_RENDER_PIPELINE_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_ALERT_HIERARCHY_AND_COLOR_SYSTEM_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_MULTI_MONITOR_WORKFLOW_DRAFT.md",
        "docs\AI_OS\dashboard\AIOS_PANEL_DOCKING_AND_FLOATING_RULES_DRAFT.md"
    )

    foreach ($path in $priorDashboardFiles) {
        Test-RequiredFile "Stage 36-42 dashboard prerequisite" $path | Out-Null
    }

    Write-Host ""
    Write-Host "Phrase checks:"
    $phrases = @(
        "voice guide",
        "tooltip",
        "operator manual",
        "training mode",
        "assistant behavior",
        "non-blocking",
        "read-only dashboard",
        "fixture-only",
        "no hidden actions",
        "dashboard production outputs require separate approval"
    )

    foreach ($phrase in $phrases) {
        Test-RequiredPhrase $phrase $stage43Files | Out-Null
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

Write-Host "DRY_RUN COMPLETE - NO OPERATOR MANUAL ARCHITECTURE ACTIONS APPLIED."
