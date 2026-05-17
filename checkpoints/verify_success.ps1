$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path "$PSScriptRoot\.."
Set-Location $RootDir

$Missing = $false

foreach ($f in "validation_result.json","task_log.json","approval.json","completion_report.json") {
  if (!(Test-Path $f)) {
    Write-Host "MISSING: $f"
    $Missing = $true
  }
}

foreach ($d in "proof","logs","validation","checkpoints") {
  if (!(Test-Path $d)) {
    Write-Host "MISSING DIR: $d"
    $Missing = $true
  }
}

if ($Missing) {
  Write-Host "AIOS VERIFY FAILED"
  exit 1
}

Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ" | Set-Content proof\last_verified.txt
Write-Host "AIOS VERIFY PASSED"
