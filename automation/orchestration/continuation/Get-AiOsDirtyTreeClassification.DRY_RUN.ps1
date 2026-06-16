param(
    [switch]$OutputJson,
    [string]$RepoRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    param([string]$CandidateRoot)

    if (-not [string]::IsNullOrWhiteSpace($CandidateRoot)) {
        try {
            return (Resolve-Path -LiteralPath $CandidateRoot -ErrorAction Stop).Path
        }
        catch {
            throw "Invalid RepoRoot provided: $CandidateRoot"
        }
    }

    try {
        $gitRoot = git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($gitRoot)) {
            return $gitRoot.Trim()
        }
    }
    catch {
        # Fall back to script-relative repo root.
    }

    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function New-FailClosedResult {
    param([string]$RepoRootPath, [string]$Reason)

    return [pscustomobject]@{
        schema = "AIOS_DIRTY_TREE_CLASSIFIER_RESULT.v1"
        generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        repo_root = $RepoRootPath
        status_source = "classifier_wrapper"
        git_status_error = $Reason
        dirty_count = 0
        overall_classification = "UNKNOWN_DIRTY"
        safe_for_dry_run = $false
        safe_for_apply = $false
        sos_required = $false
        protected_stop_required = $false
        review_required = $true
        category_counts = [pscustomobject]@{}
        dirty_files = @()
        next_safe_action = "Review dirty-tree classifier execution failure before continuing."
        safety = [pscustomobject]@{
            prints_secret_values = $false
            writes_files = $false
            mutates_repo = $false
            allows_apply = $false
            allows_protected_action = $false
            uses_live_git_status = $false
        }
    }
}

$repoRootPath = Resolve-RepoRoot -CandidateRoot $RepoRoot
$classifierPath = Join-Path $PSScriptRoot "aios_dirty_tree_classifier.py"
if (-not (Test-Path -LiteralPath $classifierPath -PathType Leaf)) {
    $result = New-FailClosedResult -RepoRootPath $repoRootPath -Reason "classifier_script_missing"
}
else {
    try {
        $raw = & python $classifierPath --repo-root $repoRootPath 2>$null
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($raw | Out-String))) {
            $result = New-FailClosedResult -RepoRootPath $repoRootPath -Reason "classifier_script_failed"
        }
        else {
            $result = ($raw | Out-String) | ConvertFrom-Json
        }
    }
    catch {
        $result = New-FailClosedResult -RepoRootPath $repoRootPath -Reason $_.Exception.Message
    }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 20)
