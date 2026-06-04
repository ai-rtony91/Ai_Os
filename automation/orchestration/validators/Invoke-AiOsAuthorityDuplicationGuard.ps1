<#
.SYNOPSIS
    AI_OS Authority Duplication Guard (report-only, DRY_RUN).

.DESCRIPTION
    Enforces the existing AGENTS.md rule against duplicate "boss files":
      - L397/L1192: "Do not create duplicate authority / duplicate docs if a canonical file already exists."
      - L982-986:   "Never let a new session create a new 'brain.' Resume from the existing source of truth."
      - L1041:      "If an existing canonical file already owns the topic: EDIT THAT FILE. DO NOT create another file."

    Rule enforced here (operator rule #9):
      No file may use canonical / source-of-truth / authority language in its NAME unless it is
      (a) listed in the configured evidence paths below,
      (b) clearly marked REFERENCE_ONLY / HISTORICAL / SUPERSEDED / DEPRECATED in its content,
      (c) a point-in-time artifact by naming convention (_DRAFT, phase-N, -pass-N, STAGE, dated, checkpoint, report), or
      (d) under archive/.

    This validator is not authority and does not define canonical ownership. Current authority lives in
    docs/governance/source-of-truth-map.md, and active-system context lives in docs/audits/active-system-map.md.
    The expected reference roots below are evidence paths used for report-only validation.

    Mode: READ_ONLY. No file is created, moved, deleted, or mutated. No commit/push.
    Exit 0 = PASS (no unsanctioned authority files). Exit 1 = STOP (worklist of files to register, mark, or archive).
#>
param(
    [string[]]$ScanRoots = @("docs", "automation", "schemas"),
    [switch]$QuietJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    param([Parameter(Mandatory = $true)][string]$StartPath)
    $candidate = (Resolve-Path -LiteralPath $StartPath).Path
    while (-not [string]::IsNullOrWhiteSpace($candidate)) {
        if ((Test-Path -LiteralPath (Join-Path $candidate "AGENTS.md") -PathType Leaf) -and
            (Test-Path -LiteralPath (Join-Path $candidate "README.md") -PathType Leaf)) {
            return $candidate
        }
        $parent = Split-Path -Parent $candidate
        if ($parent -eq $candidate) { break }
        $candidate = $parent
    }
    throw "Unable to resolve AI_OS repo root from $StartPath."
}

# --- Expected reference roots for report-only validation evidence. ---
# This list is not authority. Update canonical ownership in docs/governance/source-of-truth-map.md.
$expectedReferenceRoots = @(
    # Protected root references
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "RISK_POLICY.md",
    # Wired governance references
    "docs/governance/source-of-truth-map.md",
    "docs/governance/operational-doctrine.md",
    "docs/governance/aios-identity-and-lane-governance.md",
    "docs/governance/canonical-ownership-boundaries.md",
    "docs/governance/WORKER_REGISTRY_CANONICAL_MAP.md",
    "docs/governance/QUEUE_CANONICALIZATION_RECORD.md",
    "docs/audits/active-system-map.md",
    "automation/orchestration/recommendations/Resolve-AiOsSourceOfTruth.ps1",
    "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json",
    "schemas/aios/orchestration/WORKER_REGISTRY_SCHEMA.json",
    # Scoped historical/reference paths that carry canonical/source-of-truth naming
    "docs/AI_OS/signal_intelligence/AIOS_SIGNAL_INTELLIGENCE_SOURCE_OF_TRUTH.md",
    "docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md",
    "docs/security/SECURE_ACCESS_DOCS_CANONICAL_LINEAGE.md",
    "docs/AI_OS/orchestration_consolidation/ORCHESTRATION_CANONICAL_AUTHORITY_DECISION_001.md",
    "docs/AI_OS/orchestration_consolidation/ORCHESTRATION_CANONICAL_AUTHORITY_MAP.md"
)

# Filename signal that a file CLAIMS canonical / authority / source-of-truth status.
$nameSignal = '(?i)(canonical|source[_-]?of[_-]?truth|authority[_-]?map|authority[_-]?decision|primary[_-]?authority|official[_-]?authority|active[_-]?authority|ownership[_-]?boundar|truth[_-]?map)'

# Point-in-time naming conventions -> historical, exempt by nature.
$historicalName = '(?i)(_DRAFT|-pass-\d|phase-\d|stage-?\d|_DRY_RUN|\d{4}-\d{2}-\d{2}|checkpoint|_REPORT|_CREATED_)'

# In-content exemption markers -> the file is honest about not being live authority.
$markerExempt = '(?i)(REFERENCE[_ ]?ONLY|HISTORICAL|SUPERSEDED|ARCHIVED|DEPRECATED|not active|CLEAN-era|no longer (active|canonical)|do not use as authority)'

$repoRoot = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$expectedReferenceSet = @{}
foreach ($s in $expectedReferenceRoots) { $expectedReferenceSet[$s.ToLowerInvariant()] = $true }

$findings = @()
$claimFileCount = 0
$scannedFileCount = 0

foreach ($scanRoot in $ScanRoots) {
    $resolvedRoot = Join-Path $repoRoot $scanRoot
    if (-not (Test-Path -LiteralPath $resolvedRoot -PathType Container)) { continue }

    $files = Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Include "*.md", "*.json" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "[\\/](archive|node_modules|\.git|mock-data)[\\/]" }

    foreach ($file in $files) {
        $scannedFileCount++
        $relPath = $file.FullName.Substring($repoRoot.Length).TrimStart("\", "/").Replace("\", "/")

        if ($file.Name -notmatch $nameSignal) { continue }
        $claimFileCount++

        # Exemptions
        if ($expectedReferenceSet.ContainsKey($relPath.ToLowerInvariant())) { continue }
        if ($file.Name -match $historicalName) { continue }

        $content = ""
        try { $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction Stop } catch { $content = "" }
        if ($content -match $markerExempt) { continue }

        $findings += [pscustomobject]@{
            Path           = $relPath
            CheckId        = "unsanctioned_authority_file"
            Message        = "File name claims canonical/authority/source-of-truth status but is not listed as expected evidence, marked REFERENCE_ONLY/HISTORICAL/SUPERSEDED, historical by naming, or archived."
            NextSafeAction = "If active ownership is intended, update docs/governance/source-of-truth-map.md through an approved APPLY packet; otherwise add a REFERENCE_ONLY/HISTORICAL header or archive after dependency confirmation."
        }
    }
}

$status = if ($findings.Count -gt 0) { "STOP" } else { "PASS" }

if ($QuietJson) {
    [pscustomobject]@{
        status            = $status
        scanned_files     = $scannedFileCount
        authority_claim_files = $claimFileCount
        expected_reference_paths = $expectedReferenceRoots.Count
        findings          = $findings
    } | ConvertTo-Json -Depth 6
    if ($status -eq "PASS") { exit 0 } else { exit 1 }
}

Write-Host "AI_OS AUTHORITY DUPLICATION GUARD: $status"
Write-Host "Mode: report-only validation (no create/move/delete/commit/push)"
Write-Host "Repo root: $repoRoot"
Write-Host "Scan roots: $($ScanRoots -join ', ')"
Write-Host "Files scanned: $scannedFileCount"
Write-Host "Authority-claim files (by name): $claimFileCount"
Write-Host "Expected reference paths: $($expectedReferenceRoots.Count)"
Write-Host "Unsanctioned findings: $($findings.Count)"

if ($findings.Count -gt 0) {
    Write-Host ""
    Write-Host "Files claiming authority without being registered, marked, or archived:"
    foreach ($f in $findings) {
        Write-Host ("  [STOP] {0}" -f $f.Path)
    }
    Write-Host ""
    Write-Host "Fix each by ONE of: update the canonical source-of-truth map through an approved APPLY packet, add REFERENCE_ONLY/HISTORICAL header, or archive after dependency confirmation."
}

Write-Host ""
if ($status -eq "PASS") {
    Write-Host "Next safe action: keep this guard read-only; wire into the validator chain once the worklist is at zero."
    exit 0
}
Write-Host "Next safe action: clear the worklist above through a separate approved APPLY task; do not auto-edit governance docs from this guard."
exit 1
