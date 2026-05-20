Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..\..")
$InboxRelativePath = "Reports\telemetry\session_archives\inbox_screenshots"
$InboxPath = Join-Path $RepoRoot $InboxRelativePath
$DetectedDate = Get-Date -Format "yyyy-MM-dd"

Write-Host "AI_OS screenshot intake DRY_RUN"
Write-Host "Metadata preview only. No OCR, content reading, classification, ledger writes, control actions, broker actions, or trading actions."
Write-Host "Inbox: $InboxPath"

if (-not (Test-Path -Path $InboxPath -PathType Container)) {
  Write-Host "Inbox folder does not exist. Nothing would be indexed."
  return
}

$files = Get-ChildItem -Path $InboxPath -File

if ($files.Count -eq 0) {
  Write-Host "Inbox folder is empty. Nothing would be indexed."
  return
}

$files | Sort-Object -Property Name | ForEach-Object {
  [PSCustomObject]@{
    screenshot_id = "DRY_RUN"
    file_name = $_.Name
    source_path = $_.FullName
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
