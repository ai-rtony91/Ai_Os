$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
    "docs\concepts\aios-autonomous-safety-concepts.md"
)

$Results = foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    [PSCustomObject]@{
        Path = $RelativePath
        Exists = Test-Path -LiteralPath $FullPath -PathType Leaf
    }
}

$Missing = $Results | Where-Object { -not $_.Exists }

Write-Host "AI_OS Autonomous Operating Loop Readiness DRY_RUN"
$Results | Format-Table -AutoSize

if ($Missing) {
    Write-Host "Result: FAIL"
    exit 1
}

Write-Host "Result: PASS"
exit 0
