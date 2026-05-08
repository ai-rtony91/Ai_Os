Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

function New-ToolStatus {
    param(
        [string]$ToolId,
        [string]$Label,
        [string]$Category,
        [string]$DetectedStatus,
        [bool]$Installed = $false,
        [string]$Command = "",
        [string]$Version = "",
        [string]$PathHint = "",
        [bool]$NeedsLogin = $false,
        [bool]$NeedsConfig = $false,
        [string]$BlockedReason = "",
        [string]$Notes = ""
    )

    [pscustomobject]@{
        tool_id = $ToolId
        label = $Label
        category = $Category
        desired_status = "READY"
        detected_status = $DetectedStatus
        installed = $Installed
        command = $Command
        version = $Version
        path_hint = $PathHint
        needs_login = $NeedsLogin
        needs_config = $NeedsConfig
        blocked_reason = $BlockedReason
        last_checked = (Get-Date).ToString("s")
        notes = $Notes
    }
}

function Get-CommandVersion {
    param([string]$Command, [string[]]$Arguments)
    try {
        $output = & $Command @Arguments 2>$null
        if ($LASTEXITCODE -eq 0 -and $output) {
            return ($output | Select-Object -First 1).ToString()
        }
    } catch {
        return ""
    }
    return ""
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$reportsRoot = Join-Path $repoRoot "Reports"
$oneDriveReady = [bool]$env:OneDrive -and (Test-Path $env:OneDrive)
$codexCommand = Get-Command codex -ErrorAction SilentlyContinue
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
$ghCommand = Get-Command gh -ErrorAction SilentlyContinue
$pwshCommand = Get-Command pwsh -ErrorAction SilentlyContinue
$chatGptPath = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\ChatGPT.exe"
$claudeLocal = Join-Path $env:LOCALAPPDATA "Claude"
$claudeRoaming = Join-Path $env:APPDATA "Claude"

$items = @()
$items += New-ToolStatus -ToolId "chatgpt" -Label "ChatGPT" -Category "assistant" -DetectedStatus ($(if (Test-Path $chatGptPath) { "INSTALLED" } else { "UNKNOWN" })) -Installed (Test-Path $chatGptPath) -PathHint $chatGptPath -NeedsLogin $true -Notes "Manual browser/app access only. No credential check."
$items += New-ToolStatus -ToolId "codex" -Label "Codex" -Category "coding_agent" -DetectedStatus ($(if ($codexCommand) { "INSTALLED" } else { "MISSING" })) -Installed ([bool]$codexCommand) -Command "codex" -Version (Get-CommandVersion -Command "codex" -Arguments @("--version")) -PathHint ($(if ($codexCommand) { $codexCommand.Source } else { "" })) -Notes "Read-only command/version detection."
$items += New-ToolStatus -ToolId "claude" -Label "Claude" -Category "assistant" -DetectedStatus ($(if ((Test-Path $claudeLocal) -or (Test-Path $claudeRoaming)) { "INSTALLED" } else { "UNKNOWN" })) -Installed ((Test-Path $claudeLocal) -or (Test-Path $claudeRoaming)) -PathHint "$claudeLocal;$claudeRoaming" -NeedsLogin $true -Notes "Local path hints only. No login automation."
$items += New-ToolStatus -ToolId "github" -Label "GitHub" -Category "source_control" -DetectedStatus ($(if ($gitCommand -and $ghCommand) { "READY" } elseif ($gitCommand) { "NEEDS_CONFIG" } else { "MISSING" })) -Installed ([bool]$gitCommand) -Command "git/gh" -Version (Get-CommandVersion -Command "git" -Arguments @("--version")) -NeedsConfig (-not [bool]$ghCommand) -Notes "Git detected. GitHub CLI is optional; gh auth status requires separate approval."
$items += New-ToolStatus -ToolId "powershell" -Label "PowerShell" -Category "shell" -DetectedStatus "READY" -Installed $true -Command "powershell" -Version $PSVersionTable.PSVersion.ToString() -NeedsConfig (-not [bool]$pwshCommand) -Notes "Windows PowerShell present. pwsh availability is optional."
$items += New-ToolStatus -ToolId "web_research" -Label "Web/Research" -Category "research" -DetectedStatus "UNKNOWN" -Installed $false -BlockedReason "No scraping or external automation in detection." -Notes "Browser presence only; manual use."
$items += New-ToolStatus -ToolId "files_onedrive" -Label "Files/OneDrive" -Category "files" -DetectedStatus ($(if ($oneDriveReady) { "READY" } else { "UNKNOWN" })) -Installed $oneDriveReady -PathHint $env:OneDrive -Notes "Path detection only. No upload/download actions."
$items += New-ToolStatus -ToolId "reports" -Label "Reports" -Category "internal_module" -DetectedStatus ($(if (Test-Path $reportsRoot) { "INTERNAL_MODULE" } else { "MISSING" })) -Installed (Test-Path $reportsRoot) -PathHint $reportsRoot -Notes "Internal report folders only."
$items += New-ToolStatus -ToolId "telemetry" -Label "Telemetry" -Category "internal_module" -DetectedStatus "INTERNAL_MODULE" -Installed $true -PathHint (Join-Path $reportsRoot "health") -Notes "No live telemetry service."

[pscustomobject]@{
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToString("s")
    tools = $items
}
