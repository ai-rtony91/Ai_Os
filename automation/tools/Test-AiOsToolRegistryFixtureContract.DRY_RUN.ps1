Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fixtureRelativePath = "apps\dashboard\mock-data\tool-registry-status-fixture.example.json"
$fixturePath = Join-Path $repoRoot $fixtureRelativePath

$expectedTools = @(
    "ChatGPT",
    "Codex",
    "Claude",
    "GitHub",
    "PowerShell",
    "Web/Research",
    "Files/OneDrive",
    "Reports",
    "Telemetry"
)

$allowedStatuses = @(
    "READY",
    "INSTALLED",
    "MISSING",
    "NEEDS_LOGIN",
    "NEEDS_CONFIG",
    "BLOCKED",
    "INTERNAL_MODULE",
    "NOT_APPLICABLE",
    "UNKNOWN"
)

$blockedTerms = @(
    "api_key",
    "token",
    "password",
    "secret",
    "bearer",
    "private_key"
)

function Add-TextEvidence {
    param(
        [object]$Value,
        [System.Collections.Generic.List[string]]$Output
    )

    if ($null -eq $Value) {
        return
    }

    if ($Value -is [System.Collections.IDictionary]) {
        foreach ($key in $Value.Keys) {
            $Output.Add([string]$key)
            Add-TextEvidence -Value $Value[$key] -Output $Output
        }
        return
    }

    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        foreach ($item in $Value) {
            Add-TextEvidence -Value $item -Output $Output
        }
        return
    }

    $properties = @($Value.PSObject.Properties)
    if ($properties.Count -gt 0 -and -not ($Value -is [string])) {
        foreach ($property in $properties) {
            $Output.Add([string]$property.Name)
            Add-TextEvidence -Value $property.Value -Output $Output
        }
        return
    }

    $Output.Add([string]$Value)
}

$errors = @()
$json = $null
$fixtureExists = Test-Path $fixturePath

if (-not $fixtureExists) {
    $errors += "Missing fixture: $fixtureRelativePath"
} else {
    try {
        $json = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
    } catch {
        $errors += "Invalid JSON: $($_.Exception.Message)"
    }
}

if ($null -ne $json) {
    $tools = @($json.tools)
    $toolLabels = @($tools | ForEach-Object { $_.label })
    foreach ($expectedTool in $expectedTools) {
        if ($toolLabels -notcontains $expectedTool) {
            $errors += "Missing expected tool: $expectedTool"
        }
    }

    foreach ($tool in $tools) {
        $status = [string]$tool.detected_status
        if ($allowedStatuses -notcontains $status) {
            $label = if ($tool.label) { $tool.label } else { "UNKNOWN_TOOL" }
            $errors += "Invalid status for $label`: $status"
        }
    }

    $textEvidence = [System.Collections.Generic.List[string]]::new()
    Add-TextEvidence -Value $json -Output $textEvidence
    foreach ($term in $blockedTerms) {
        $matches = @($textEvidence | Where-Object { $_ -match [regex]::Escape($term) })
        if ($matches.Count -gt 0) {
            $errors += "Secret-looking term detected: $term"
        }
    }
}

$result = [pscustomobject]@{
    mode = "DRY_RUN"
    status = $(if ($errors.Count -eq 0) { "PASS" } else { "FAIL" })
    fixture = $fixtureRelativePath
    fixture_exists = $fixtureExists
    expected_tools = $expectedTools
    allowed_statuses = $allowedStatuses
    errors = $errors
    safety = @{
        modifies_files = "NO"
        installs = "BLOCKED"
        secrets = "BLOCKED"
        account_connections = "BLOCKED"
        external_apis = "BLOCKED"
        brokers = "BLOCKED"
        trading_execution = "BLOCKED"
    }
}

$result | ConvertTo-Json -Depth 6

if ($errors.Count -gt 0) {
    exit 1
}
