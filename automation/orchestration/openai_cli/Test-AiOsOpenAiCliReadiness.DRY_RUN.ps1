[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path ".").Path
$outputDir = Join-Path $repoRoot "docs/AI_OS/openai_cli/readiness_outputs"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

$openAiCommand = Get-Command openai -ErrorAction SilentlyContinue
$openAiCliDetected = $null -ne $openAiCommand
$apiKeyDetected = -not [string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable("OPENAI_API_KEY"))

$forbiddenSecretFiles = @()
foreach ($relativePath in @(".env", "project.json", "service-account.json")) {
    if (Test-Path -LiteralPath (Join-Path $repoRoot $relativePath) -PathType Leaf) {
        $forbiddenSecretFiles += $relativePath
    }
}

$result = [ordered]@{
    schema = "aios.openai_cli_readiness.v1"
    mode = "DRY_RUN"
    local_fixture_only = $true
    openai_cli_detected = [bool]$openAiCliDetected
    openai_api_key_env_detected = [bool]$apiKeyDetected
    api_key_value_printed = $false
    forbidden_secret_files_present = @($forbiddenSecretFiles)
    live_openai_api_call = $false
    admin_api_used = $false
    service_account_created = $false
    env_file_created = $false
    network_required = $false
    package_install_required = $false
    repo_mutation_allowed = $false
    human_approval_required = $true
    fail_closed = $true
    profitability_priority = "TRUSTED_PROVEN_PROFITABILITY"
    stop_point = "Stop after local readiness report. Do not call OpenAI."
}

$jsonPath = Join-Path $outputDir "OPENAI_CLI_READINESS_RESULT_001.json"
$reportPath = Join-Path $outputDir "OPENAI_CLI_READINESS_REPORT_001.md"

$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$report = @"
# OpenAI CLI Readiness Report 001

Mode: DRY_RUN
Local fixture only: true
OpenAI CLI detected: $openAiCliDetected
OPENAI_API_KEY env detected: $apiKeyDetected
API key printed: false
Forbidden secret files present: $($forbiddenSecretFiles.Count)
OpenAI call performed: false
Admin API used: false
Service account created: false
.env created: false
Package install required: false
Network required: false
Repo mutation allowed: false
Human approval required: true
Fail closed: true
Profitability priority: TRUSTED_PROVEN_PROFITABILITY

Stop point:
Stop after local readiness report. Do not call OpenAI.
"@

Set-Content -LiteralPath $reportPath -Value $report -Encoding UTF8

Write-Host "AI_OS_OPENAI_CLI_READINESS"
Write-Host "LOCAL_READINESS_ONLY"
Write-Host "NO_OPENAI_CALL"
Write-Host "NO_API_KEY_PRINTED"
Write-Host "NO_ENV_CREATED"
Write-Host "NO_ADMIN_API"
Write-Host "OPENAI_CLI_DETECTED=$openAiCliDetected"
Write-Host "OPENAI_API_KEY_ENV_DETECTED=$apiKeyDetected"

