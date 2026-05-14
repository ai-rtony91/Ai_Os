param(
  [string[]]$AllowedFiles = @(),
  [string[]]$BlockedFiles = @(".env", "Reports/security/*")
)

$Status = git status --short --branch

$ChangedFiles = @()
foreach ($Line in $Status) {
  if ($Line -like "##*") {
    continue
  }

  if ($Line.Trim().Length -eq 0) {
    continue
  }

  $Path = $Line.Substring(3).Trim().Trim('"')
  $ChangedFiles += $Path
}

$BlockedHit = $null
foreach ($File in $ChangedFiles) {
  foreach ($Pattern in $BlockedFiles) {
    if ($File -like $Pattern) {
      $BlockedHit = $File
      break
    }
  }
  if ($BlockedHit) { break }
}

$OutOfScopeHit = $null
if ($AllowedFiles.Count -gt 0) {
  foreach ($File in $ChangedFiles) {
    $Allowed = $false
    foreach ($Pattern in $AllowedFiles) {
      if ($File -like $Pattern) {
        $Allowed = $true
        break
      }
    }

    if (-not $Allowed) {
      $OutOfScopeHit = $File
      break
    }
  }
}

$Result = [ordered]@{
  clean = ($ChangedFiles.Count -eq 0)
  blocked = [bool]($BlockedHit -or $OutOfScopeHit)
  changedFiles = $ChangedFiles
  blockedFile = $BlockedHit
  outOfScopeFile = $OutOfScopeHit
  checkedAt = (Get-Date).ToString("o")
}

$Result | ConvertTo-Json -Depth 8

if ($Result.blocked) {
  exit 2
}

exit 0
