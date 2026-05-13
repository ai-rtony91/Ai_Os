Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$mockRoot = Join-Path $repoRoot "apps\dashboard\mock-data"

$files = @(
  "aios-command-center-state-v1.example.json",
  "aios-approval-inbox-v1.example.json",
  "aios-merge-readiness-queue-v1.example.json",
  "aios-conflict-center-v1.example.json",
  "aios-operator-guidance-v1.example.json",
  "aios-worker-age-tracking-v1.example.json"
)

$errors = New-Object System.Collections.Generic.List[string]

function Read-AiOsJson {
  param([Parameter(Mandatory = $true)][string] $Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing JSON file: $Path"
  }
  return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

$state = $null
$approval = $null
$merge = $null
$conflict = $null
$guidance = $null
$age = $null

try { $state = Read-AiOsJson -Path (Join-Path $mockRoot $files[0]) } catch { $errors.Add($_.Exception.Message) }
try { $approval = Read-AiOsJson -Path (Join-Path $mockRoot $files[1]) } catch { $errors.Add($_.Exception.Message) }
try { $merge = Read-AiOsJson -Path (Join-Path $mockRoot $files[2]) } catch { $errors.Add($_.Exception.Message) }
try { $conflict = Read-AiOsJson -Path (Join-Path $mockRoot $files[3]) } catch { $errors.Add($_.Exception.Message) }
try { $guidance = Read-AiOsJson -Path (Join-Path $mockRoot $files[4]) } catch { $errors.Add($_.Exception.Message) }
try { $age = Read-AiOsJson -Path (Join-Path $mockRoot $files[5]) } catch { $errors.Add($_.Exception.Message) }

if ($state -and [string]::IsNullOrWhiteSpace($state.next_safe_action)) {
  $errors.Add("Command Center state is missing next_safe_action.")
}

if ($guidance -and [string]::IsNullOrWhiteSpace($guidance.next_recommended_action)) {
  $errors.Add("Operator guidance is missing next_recommended_action.")
}

foreach ($item in @($approval.approval_requests)) {
  if ([string]::IsNullOrWhiteSpace($item.next_safe_action)) {
    $errors.Add("Approval inbox item missing next_safe_action.")
  }
}

foreach ($item in @($merge.merge_readiness_queue)) {
  if ($item.state -eq "READY" -and [string]::IsNullOrWhiteSpace($item.next_safe_action)) {
    $errors.Add("Merge-ready item missing next_safe_action.")
  }
}

if (@($conflict.conflicts).Count -gt 0) {
  foreach ($item in @($merge.merge_readiness_queue)) {
    if ($item.state -eq "READY") {
      $errors.Add("Merge-ready state is invalid while unresolved conflicts exist.")
    }
  }
}

foreach ($item in @($age.worker_age_tracking)) {
  if (($item.age_state -eq "STALE" -or $item.age_state -eq "BLOCKED") -and [string]::IsNullOrWhiteSpace($item.next_safe_action)) {
    $errors.Add("Stale or blocked worker age item missing next_safe_action.")
  }
}

Write-Host "AI_OS Command Center State DRY_RUN Validator"
Write-Host "Repo: $repoRoot"

if ($errors.Count -gt 0) {
  foreach ($errorItem in $errors) {
    Write-Host "ERROR: $errorItem"
  }
  throw "AI_OS COMMAND CENTER STATE VALIDATION: FAIL"
}

Write-Host "AI_OS COMMAND CENTER STATE VALIDATION: PASS"
