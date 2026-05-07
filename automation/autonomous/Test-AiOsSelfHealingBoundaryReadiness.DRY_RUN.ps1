$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
    "docs\AI_OS\autonomous\AIOS_SELF_HEALING_BOUNDARIES_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_REPAIR_PROPOSAL_GENERATION_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_NO_AUTOMATIC_DESTRUCTIVE_REPAIR_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_ROLLBACK_RECOMMENDATION_RULES_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_HUMAN_APPROVAL_BEFORE_REPAIR_APPLY_DRAFT.md"
)

$Results = foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    [PSCustomObject]@{
        Path = $RelativePath
        Exists = Test-Path -LiteralPath $FullPath -PathType Leaf
    }
}

$Missing = $Results | Where-Object { -not $_.Exists }

Write-Host "AI_OS Self-Healing Boundary Readiness DRY_RUN"
$Results | Format-Table -AutoSize

if ($Missing) {
    Write-Host "Result: FAIL"
    exit 1
}

Write-Host "Result: PASS"
exit 0
