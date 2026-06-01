param(
  [string]$RepoRoot = ".",
  [int]$MaxFindingDetails = 250
)

$ErrorActionPreference = "Stop"
$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$validatorPath = "automation/orchestration/validators/Test-AiOsDuplicateBrainReferences.DRY_RUN.ps1"

function ConvertTo-RelativePath {
  param([System.IO.FileSystemInfo]$Item)
  return ($Item.FullName.Substring($resolvedRepoRoot.Length + 1) -replace "\\", "/")
}

function Get-ReferenceClassification {
  param(
    [string]$SourcePath,
    [string]$Line,
    [string]$Conflict
  )

  $normalized = ($SourcePath -replace "\\", "/")
  $lower = $normalized.ToLowerInvariant()
  $lineLower = $Line.ToLowerInvariant()

  if ($normalized -eq $validatorPath) { return "FIXTURE_REFERENCE" }
  if ($lower.StartsWith("archive/")) { return "ARCHIVE_REFERENCE" }

  $retentionOnlyLine = $lineLower -match "reference/source|source/reference|reference-only|reference only|referencefiles|reference files|source material|historical|evidence|compatibility|retention|decision|required before archive|not active|not the active|not primary|not the primary|not canonical|pending file-by-file|fixture ownership review|safe delete candidates|safe delete candidate count|legacydocsaios|expectedfiles|expected files|canonical source missing|fallback is disabled|fallback disabled"
  $activeAuthorityLine = $lineLower -match "active authority|active queue authority|active approval authority|primary worker authority|primary source|canonical authority|source[- ]of[- ]truth|active source|canonical source"

  if ($lower -match "^docs/(audits|governance|workflows)/" -or $lower.EndsWith(".md")) {
    return "DOC_REFERENCE"
  }

  if (-not $retentionOnlyLine) {
    if ($Conflict -eq "legacy_operator_registry_primary_source" -and $lineLower -match "primary worker authority|primary source|source.?of.?truth|canonical authority|active worker|worker authority") {
      return "ACTIVE_DEPENDENCY"
    }
    if ($Conflict -eq "root_work_packets_active_queue_authority" -and $lineLower -match "active queue authority|source[- ]of[- ]truth|canonical queue|primary queue|active queue") {
      return "ACTIVE_DEPENDENCY"
    }
    if ($Conflict -eq "root_approvals_active_approval_authority" -and $lineLower -match "active approval authority|source[- ]of[- ]truth|canonical approval|primary approval|active approval") {
      return "ACTIVE_DEPENDENCY"
    }
    if ($Conflict -eq "old_orchestration_example_fallback_active_source" -and ($activeAuthorityLine -or $lineLower -match "fallback|default|read-json|null|test-jsonfile")) {
      return "ACTIVE_DEPENDENCY"
    }
    if ($Conflict -eq "docs_ai_os_active_authority" -and $activeAuthorityLine) {
      return "ACTIVE_DEPENDENCY"
    }
  }

  if ($lower -match "(^|/)(mock-data|fixtures|fixture|examples|window_snapshots)(/|$)" -or $lower -match "\.example\." -or $lineLower -match "\.example\.json|fixture|example") {
    return "FIXTURE_REFERENCE"
  }

  if ($Conflict -eq "legacy_operator_registry_primary_source") {
    if ($lower -match "automation/operator/(get-aiosoperatorregistryadapter|test-aiosworkerautorouting|test-aiosparallelworkerreports|invoke-aiosworkfloworchestrator|start-aiosparalleldryruncrew|start-aioscontrolledapplylane)[^/]*\.ps1") {
      return "REVIEW_REQUIRED"
    }
    if ($lower -match "automation/work_intelligence/aios_work_intelligence_config\.json") {
      return "REVIEW_REQUIRED"
    }
    if ($lineLower -match "compatibility|fallback|legacyregistrypath|legacy_worker_registry|legacy_operator|not the primary|evidence only") {
      return "REVIEW_REQUIRED"
    }
  }

  if ($Conflict -eq "root_work_packets_active_queue_authority") {
    if ($lower -match "automation/orchestration/supervisor/") {
      return "REVIEW_REQUIRED"
    }
    if ($lineLower -match "automation/orchestration/work_packets|work_packets\\get-aios|work packet summary|preview_only|target_folder|filesinscope") {
      return "REVIEW_REQUIRED"
    }
    if ($lineLower -match "\.example\.json|schema\.json|examples/|fixture") {
      return "FIXTURE_REFERENCE"
    }
  }

  if ($Conflict -eq "root_approvals_active_approval_authority") {
    if ($lower -match "automation/orchestration/(relay|approval_runner)/" -or $lower -match "^(relay|telemetry)/") {
      return "REVIEW_REQUIRED"
    }
    if ($lineLower -match "relay/approvals|relay\\approvals|approvals\\|\$relaypaths\.approvals|approveddir|approvalpath|approval resume|sample-only|roundtrip|outbox|telemetry/") {
      return "REVIEW_REQUIRED"
    }
    if ($lineLower -match "\.example\.json|schema\.json|examples/|fixture") {
      return "FIXTURE_REFERENCE"
    }
  }

  if ($Conflict -eq "old_orchestration_example_fallback_active_source") {
    if (-not $retentionOnlyLine -and $lineLower -match "fallback|default|source|read-json|null|test-jsonfile") {
      return "ACTIVE_DEPENDENCY"
    }
    return "FIXTURE_REFERENCE"
  }

  if ($Conflict -eq "docs_ai_os_active_authority") {
    if ($lower -match "automation/(progress|signal_intelligence|status)/") {
      return "REVIEW_REQUIRED"
    }
    if ($lower -match "automation/operator/worker_queue/" -or $lower -match "automation/orchestration/recommendations/") {
      return "REVIEW_REQUIRED"
    }
    if (-not $retentionOnlyLine -and $lineLower -match "allowed_paths|allowed path|authority|canonical|source.?of.?truth|active") {
      return "ACTIVE_DEPENDENCY"
    }
    return "DOC_REFERENCE"
  }

  return "ACTIVE_DEPENDENCY"
}

function Get-DeleteReadiness {
  param(
    [string]$Conflict,
    [string]$Classification
  )

  if ($Classification -eq "ACTIVE_DEPENDENCY") {
    return "NOT_SAFE_TO_DELETE"
  }
  if ($Classification -eq "REVIEW_REQUIRED") {
    return "REVIEW_BEFORE_ARCHIVE"
  }
  if ($Conflict -in @("docs_ai_os_active_authority", "root_work_packets_active_queue_authority", "root_approvals_active_approval_authority")) {
    return "PROTECTED_NOT_DELETE_IN_THIS_PACKET"
  }
  return "ARCHIVE_CANDIDATE_AFTER_REFERENCE_REVIEW"
}

$patterns = @(
  [pscustomobject]@{
    conflict = "legacy_operator_registry_primary_source"
    regex = "automation[/\\]operator[/\\]AIOS_PARALLEL_WORKER_REGISTRY\.json"
    old_brain_path = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json"
  },
  [pscustomobject]@{
    conflict = "root_work_packets_active_queue_authority"
    regex = "(^|['""`\s(])work_packets[/\\]"
    old_brain_path = "work_packets/**"
  },
  [pscustomobject]@{
    conflict = "root_approvals_active_approval_authority"
    regex = "(^|['""`\s(])approvals[/\\]"
    old_brain_path = "approvals/**"
  },
  [pscustomobject]@{
    conflict = "old_orchestration_example_fallback_active_source"
    regex = "automation[/\\]orchestration[/\\][^'""`\s]+\.example\.json"
    old_brain_path = "automation/orchestration/*.example.json"
  },
  [pscustomobject]@{
    conflict = "docs_ai_os_active_authority"
    regex = "docs[/\\]AI_OS[/\\]"
    old_brain_path = "docs/AI_OS/**"
  }
)

$scanExtensions = @(".ps1", ".psm1", ".psd1", ".json", ".md", ".txt", ".yml", ".yaml", ".js", ".jsx", ".ts", ".tsx", ".csv")
$files = Get-ChildItem -LiteralPath $resolvedRepoRoot -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch "\\.git\\" -and
    $_.FullName -notmatch "\\node_modules\\" -and
    $_.FullName -notmatch "\\.venv\\" -and
    $_.FullName -notmatch "\\docs\\AI_OS\\" -and
    $scanExtensions -contains $_.Extension.ToLowerInvariant()
  }

$findings = New-Object System.Collections.Generic.List[object]
foreach ($file in $files) {
  $relative = ConvertTo-RelativePath -Item $file
  $lineNumber = 0
  foreach ($line in Get-Content -LiteralPath $file.FullName -ErrorAction SilentlyContinue) {
    $lineNumber += 1
    foreach ($pattern in $patterns) {
      if ($line -match $pattern.regex) {
        $classification = Get-ReferenceClassification -SourcePath $relative -Line $line -Conflict $pattern.conflict
        $findings.Add([pscustomobject]@{
          classification = $classification
          conflict = $pattern.conflict
          old_brain_path = $pattern.old_brain_path
          source_path = $relative
          line = $lineNumber
          delete_readiness = Get-DeleteReadiness -Conflict $pattern.conflict -Classification $classification
        }) | Out-Null
      }
    }
  }
}

$activeCount = @($findings | Where-Object { $_.classification -eq "ACTIVE_DEPENDENCY" }).Count
$reviewCount = @($findings | Where-Object { $_.classification -eq "REVIEW_REQUIRED" }).Count
$fixtureCount = @($findings | Where-Object { $_.classification -eq "FIXTURE_REFERENCE" }).Count
$docCount = @($findings | Where-Object { $_.classification -eq "DOC_REFERENCE" }).Count
$archiveCount = @($findings | Where-Object { $_.classification -eq "ARCHIVE_REFERENCE" }).Count
$safeToDeleteNow = @()
$unsafeToDelete = @("work_packets/**", "approvals/**", "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json", "docs/AI_OS/**")

$result = [pscustomobject]@{
  schema = "AIOS_DUPLICATE_BRAIN_REFERENCE_VALIDATOR.v1"
  mode = "DRY_RUN"
  repo_root = $resolvedRepoRoot
  status = if ($activeCount -gt 0) { "FAIL" } elseif ($reviewCount -gt 0) { "REVIEW_REQUIRED" } else { "PASS" }
  summary = [pscustomobject]@{
    active_dependency_count = $activeCount
    review_required_count = $reviewCount
    fixture_reference_count = $fixtureCount
    doc_reference_count = $docCount
    archive_reference_count = $archiveCount
    total_findings = $findings.Count
    safe_delete_candidate_count = $safeToDeleteNow.Count
    protected_unsafe_to_delete_count = $unsafeToDelete.Count
  }
  archive_delete_readiness = [pscustomobject]@{
    safe_to_delete_now = $safeToDeleteNow
    safe_delete_candidate_count = $safeToDeleteNow.Count
    unsafe_to_delete = $unsafeToDelete
    protected_unsafe_to_delete_count = $unsafeToDelete.Count
    archive_candidates_after_review = @($findings | Where-Object { $_.delete_readiness -eq "ARCHIVE_CANDIDATE_AFTER_REFERENCE_REVIEW" } | Select-Object -ExpandProperty old_brain_path -Unique)
    review_before_archive = @($findings | Where-Object { $_.delete_readiness -eq "REVIEW_BEFORE_ARCHIVE" } | Select-Object -ExpandProperty old_brain_path -Unique)
  }
  finding_details_capped = $true
  max_finding_details = $MaxFindingDetails
  findings = @($findings | Sort-Object classification, conflict, source_path, line | Select-Object -First $MaxFindingDetails)
}

$result | ConvertTo-Json -Depth 8

if ($activeCount -gt 0) {
  exit 1
}

exit 0
