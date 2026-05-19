param()

$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
  $scriptRoot = Split-Path -Parent $MyInvocation.ScriptName
  $repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..")

  $requiredPaths = @(
    ".git",
    "project.manifest.json",
    "automation\orchestration\queue\DISPATCHER_QUEUE.json"
  )

  foreach ($path in $requiredPaths) {
    $fullPath = Join-Path $repoRoot $path
    if (-not (Test-Path -LiteralPath $fullPath)) {
      throw "AI_OS repo validation failed. Missing: $path"
    }
  }

  return $repoRoot.Path
}

$repoRoot = Get-AiOsRepoRoot
$queuePath = Join-Path $repoRoot "automation\orchestration\queue\DISPATCHER_QUEUE.json"
$queue = Get-Content -LiteralPath $queuePath -Raw | ConvertFrom-Json
$items = @($queue.items)

Write-Host ""
Write-Host "AI_OS AUTOMATION QUEUE" -ForegroundColor Cyan
Write-Host "Repo:   $repoRoot"
Write-Host "Status: $($queue.status)"
Write-Host "Items:  $($items.Count)"
Write-Host ""

Write-Host "Counts" -ForegroundColor Yellow
$items |
  Group-Object status |
  Sort-Object Name |
  ForEach-Object {
    Write-Host ("  {0,-12} {1}" -f $_.Name, $_.Count)
  }

Write-Host ""
Write-Host "Packets" -ForegroundColor Yellow
foreach ($item in $items) {
  Write-Host ("  {0,-28} {1,-10} {2,-8} {3}" -f $item.packet_id, $item.status, $item.priority, $item.assigned_worker)
  Write-Host ("    {0}" -f $item.title)
}

exit 0
