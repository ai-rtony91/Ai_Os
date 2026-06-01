[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$DryNotify,
    [ValidateSet("", "file", "webhook", "telegram")][string]$ChannelOverride = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$dispatcher = Join-Path $PSScriptRoot "Send-AiOsNotification.ps1"
$message = "AI_OS notification self-test $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))"
$args = @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $dispatcher,
    "-Message",
    $message,
    "-Severity",
    "WARN",
    "-Subject",
    "AI_OS"
)
if ($Apply) { $args += "-Apply" }
if ($DryNotify) { $args += "-DryNotify" }
if (-not [string]::IsNullOrWhiteSpace($ChannelOverride)) { $args += @("-ChannelOverride", $ChannelOverride) }

$output = & powershell @args
$exit = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
$output | ForEach-Object { Write-Host $_ }

if ($exit -ne 0) {
    Write-Host "FAIL exit=$exit"
    exit $exit
}

$outboxLine = @($output | Where-Object { $_ -match "^OUTBOX_FILE=" } | Select-Object -First 1)
if ($outboxLine.Count -gt 0) {
    $path = [string]$outboxLine[0].Substring("OUTBOX_FILE=".Length)
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Write-Host "FAIL missing_outbox_file=$path"
        exit 2
    }
}

Write-Host "PASS"
exit 0
