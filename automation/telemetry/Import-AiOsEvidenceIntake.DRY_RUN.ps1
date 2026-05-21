Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..\..")
$InboxRelativePath = "Reports\telemetry\session_archives\inbox_evidence"
$InboxPath = Join-Path $RepoRoot $InboxRelativePath
$DetectedDate = Get-Date -Format "yyyy-MM-dd"

function Get-AiOsEvidenceType {
  param(
    [string]$Extension
  )

  switch ($Extension.ToLowerInvariant()) {
    ".png" { return "image" }
    ".jpg" { return "image" }
    ".jpeg" { return "image" }
    ".webp" { return "image" }
    ".url" { return "link_or_text" }
    ".html" { return "link_or_text" }
    ".txt" { return "link_or_text" }
    ".pdf" { return "document" }
    ".md" { return "document" }
    ".csv" { return "document" }
    default { return "other" }
  }
}

Write-Host "AI_OS evidence intake DRY_RUN"
Write-Host "Metadata preview only. No OCR, content reading, link opening, URL browsing, classification, ledger writes, control actions, broker actions, or trading actions."
Write-Host "Inbox: $InboxPath"

if (-not (Test-Path -Path $InboxPath -PathType Container)) {
  Write-Host "Evidence inbox folder does not exist. Nothing would be indexed."
  return
}

$files = @(Get-ChildItem -Path $InboxPath -File)

if ($files.Count -eq 0) {
  Write-Host "Evidence inbox folder is empty. Nothing would be indexed."
  return
}

$files | Sort-Object -Property Name | ForEach-Object {
  $extension = $_.Extension.ToLowerInvariant()

  [PSCustomObject]@{
    evidence_id = "DRY_RUN"
    file_name = $_.Name
    source_path = $_.FullName
    evidence_extension = $extension
    evidence_type = Get-AiOsEvidenceType -Extension $extension
    detected_date = $DetectedDate
    created_time = $_.CreationTime.ToString("o")
    modified_time = $_.LastWriteTime.ToString("o")
    file_size_bytes = $_.Length
    session_label = ""
    related_worker = ""
    related_phase = ""
    related_stage = ""
    related_commit = ""
    notes = "DRY_RUN metadata preview only"
    reviewed_status = "unreviewed"
  }
} | Format-Table -AutoSize
