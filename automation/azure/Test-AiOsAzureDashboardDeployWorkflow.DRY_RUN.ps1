$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WorkflowPath = Join-Path $RepoRoot ".github\workflows\azure-deploy.yml"
$ForbiddenTerms = @(
  "OANDA",
  "broker",
  "live-order",
  "webhook",
  "api-key",
  "Flask",
  "Gunicorn",
  "FastAPI",
  "requirements.txt"
)

Write-Host "AI_OS Azure Dashboard Deploy Workflow DRY_RUN"

if (-not (Test-Path -LiteralPath $WorkflowPath -PathType Leaf)) {
  Write-Host "Result: FAIL"
  Write-Host "Missing workflow: .github\workflows\azure-deploy.yml"
  exit 1
}

$Workflow = Get-Content -Raw -LiteralPath $WorkflowPath
$Failures = New-Object System.Collections.Generic.List[string]

if ($Workflow -notmatch "(?m)^\s*workflow_dispatch\s*:") {
  $Failures.Add("workflow_dispatch trigger is missing.")
}

if ($Workflow -match "(?m)^\s*push\s*:") {
  $Failures.Add("push trigger is present; workflow must remain manual-only.")
}

if ($Workflow -notmatch "package:\s*apps/dashboard/dist") {
  $Failures.Add("Deploy package path must be apps/dashboard/dist.")
}

if ($Workflow -notmatch "app-name:\s*algotradez-aios") {
  $Failures.Add("App Service name must be algotradez-aios.")
}

if ($Workflow -notmatch "secrets\.AZUREAPPSERVICE_PUBLISHPROFILE_ALGOTRADEZ_AIOS") {
  $Failures.Add("Publish profile secret reference name is missing.")
}

foreach ($Term in $ForbiddenTerms) {
  if ($Workflow -match [regex]::Escape($Term)) {
    $Failures.Add("Forbidden term appears in workflow: $Term")
  }
}

if ($Failures.Count -gt 0) {
  Write-Host "Result: FAIL"
  foreach ($Failure in $Failures) {
    Write-Host "- $Failure"
  }
  exit 1
}

Write-Host "Workflow file: PASS"
Write-Host "Manual-only trigger: PASS"
Write-Host "Package path: PASS"
Write-Host "App Service name: PASS"
Write-Host "Secret reference name: PASS"
Write-Host "Forbidden-term scan: PASS"
Write-Host "Result: PASS"
exit 0
