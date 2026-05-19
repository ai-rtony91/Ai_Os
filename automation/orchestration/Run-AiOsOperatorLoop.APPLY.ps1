[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$BranchName,

    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

$ErrorActionPreference = "Stop"

Write-Host "AI_OS Operator Loop"
Write-Host "Mode: APPLY"
Write-Host ""

$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    throw "Must start from main. Current branch: $currentBranch"
}

Write-Host "Step 1: Create branch"
git checkout -b $BranchName

Write-Host ""
Write-Host "Step 2: Run preflight"
$preflightOutput = powershell -ExecutionPolicy Bypass -File "automation\orchestration\Run-AiOsPreflight.DRY_RUN.ps1"
$preflightOutput

if ($preflightOutput -match '"overall_result":\s+"FAIL"') {
    throw "Preflight failed. APPLY stopped."
}

Write-Host ""
Write-Host "Step 3: Stage changed orchestration/docs files only"
$approvedPathPattern = "automation/orchestration/|docs/concepts/aios-dispatcher-orchestration-concepts\.md|docs/architecture/aios-system-architecture\.md|docs/workflows/aios-operator-workflows\.md|docs/audits/"
$files = git status --short | ForEach-Object {
    if ($_ -match "^\?\? ($approvedPathPattern)") {
        $_.Substring(3).Trim()
    }
    elseif ($_ -match "^ M ($approvedPathPattern)") {
        $_.Substring(3).Trim()
    }
}

if (-not $files -or $files.Count -eq 0) {
    throw "No approved files to stage."
}

foreach ($file in $files) {
    git add -- $file
}

Write-Host ""
Write-Host "Step 4: Commit"
git commit -m $CommitMessage

Write-Host ""
Write-Host "Step 5: Push"
git push -u origin $BranchName

Write-Host ""
Write-Host "Step 6: PR URL"
Write-Host "https://github.com/ai-rtony91/Ai_Os/pull/new/$BranchName"

Write-Host ""
Write-Host "APPLY complete."
