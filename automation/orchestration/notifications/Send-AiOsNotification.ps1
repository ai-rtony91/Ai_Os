[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Message,
    [string]$Severity = "INFO",
    [string]$Subject = "AI_OS",
    [switch]$Apply,
    [switch]$DryNotify,
    [ValidateSet("", "file", "webhook", "telegram")][string]$ChannelOverride = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$configLocal = Join-Path $PSScriptRoot "notification-config.local.json"
$configExample = Join-Path $PSScriptRoot "notification-config.example.json"
$statePath = Join-Path $PSScriptRoot "state\rate_window.json"
$logPath = Join-Path $repoRoot "relay\logs\notifications.log"

function Get-AiOsUtc {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Write-AiOsNotificationLog {
    param(
        [string]$Channel,
        [string]$Status,
        [string]$Detail = ""
    )

    $logDir = Split-Path -Parent $logPath
    if (-not (Test-Path -LiteralPath $logDir -PathType Container)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $subjectFirst40 = if ($Subject.Length -gt 40) { $Subject.Substring(0, 40) } else { $Subject }
    $entry = [ordered]@{
        utc = Get-AiOsUtc
        channel = $Channel
        severity = $Severity.ToUpperInvariant()
        subject_first_40 = $subjectFirst40
        status = $Status
        detail = $Detail
        redacted = $true
    }
    Add-Content -LiteralPath $logPath -Value (($entry | ConvertTo-Json -Compress -Depth 5))
}

function Get-AiOsSeverityValue {
    param([string]$Value)
    switch ($Value.ToUpperInvariant()) {
        "DEBUG" { return 0 }
        "INFO" { return 1 }
        "WARN" { return 2 }
        "WARNING" { return 2 }
        "ERROR" { return 3 }
        "CRITICAL" { return 4 }
        default { return 1 }
    }
}

function Read-AiOsJsonFile {
    param([string]$Path)
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Get-AiOsStoredCredential {
    param([Parameter(Mandatory = $true)][string]$Name)
    $cmd = Get-Command Get-StoredCredential -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        return $null
    }
    return Get-StoredCredential -Target $Name
}

function Get-AiOsCredentialSecret {
    param([object]$Credential)
    if ($null -eq $Credential) {
        return ""
    }
    if ($Credential.Password -is [securestring]) {
        return (New-Object System.Net.NetworkCredential("", $Credential.Password)).Password
    }
    return [string]$Credential.Password
}

function Write-AiOsFileNotification {
    param([object]$Config)
    $outboxRel = $Config.channels.file.outbox
    if ([string]::IsNullOrWhiteSpace($outboxRel)) {
        $outboxRel = "relay/reports/SOS_OUTBOX/"
    }
    $outbox = Join-Path $repoRoot $outboxRel
    if (-not (Test-Path -LiteralPath $outbox -PathType Container)) {
        New-Item -ItemType Directory -Path $outbox -Force | Out-Null
    }
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss_fff")
    $target = Join-Path $outbox ("SOS_{0}.md" -f $stamp)
    $body = @(
        "# $Subject",
        "",
        "- Severity: $($Severity.ToUpperInvariant())",
        "- Sent at UTC: $(Get-AiOsUtc)",
        "- Channel: file",
        "- Secrets used: none",
        "",
        $Message
    ) -join "`n"
    Set-Content -LiteralPath $target -Value ($body + "`n") -Encoding UTF8
    Write-AiOsNotificationLog -Channel "file" -Status "SENT" -Detail "length=$($Message.Length)"
    Write-Host "STATUS=SENT"
    Write-Host "CHANNEL=file"
    Write-Host "OUTBOX_FILE=$target"
}

function Test-AiOsRateLimit {
    param([int]$MaxPerHour)
    $stateDir = Split-Path -Parent $statePath
    if (-not (Test-Path -LiteralPath $stateDir -PathType Container)) {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
    }

    $now = (Get-Date).ToUniversalTime()
    $events = @()
    if (Test-Path -LiteralPath $statePath -PathType Leaf) {
        $existing = Read-AiOsJsonFile -Path $statePath
        if ($null -ne $existing.events) {
            $events = @($existing.events)
        }
    }

    $window = @($events | Where-Object {
        try {
            ([datetime]$_).ToUniversalTime() -gt $now.AddHours(-1)
        } catch {
            $false
        }
    })

    if ($window.Count -ge $MaxPerHour) {
        Set-Content -LiteralPath $statePath -Value (([ordered]@{ events = $window } | ConvertTo-Json -Depth 5) + "`n") -Encoding UTF8
        return $false
    }

    $window += $now.ToString("o")
    Set-Content -LiteralPath $statePath -Value (([ordered]@{ events = $window } | ConvertTo-Json -Depth 5) + "`n") -Encoding UTF8
    return $true
}

if ($Message -match "(?i)\b(trade|order|buy|sell|live|broker)\b") {
    Write-AiOsNotificationLog -Channel "blocked" -Status "PAYLOAD_BLOCKED_TRADING_TERMS" -Detail "length=$($Message.Length)"
    Write-Host "STATUS=PAYLOAD_BLOCKED_TRADING_TERMS"
    exit 2
}

$configPath = if (Test-Path -LiteralPath $configLocal -PathType Leaf) { $configLocal } else { $configExample }
$config = Read-AiOsJsonFile -Path $configPath
$channel = if ([string]::IsNullOrWhiteSpace($ChannelOverride)) { [string]$config.channel } else { $ChannelOverride }
$channel = $channel.ToLowerInvariant()

if (@("file", "webhook", "telegram") -notcontains $channel) {
    Write-AiOsNotificationLog -Channel $channel -Status "UNKNOWN_CHANNEL"
    Write-Host "STATUS=UNKNOWN_CHANNEL"
    exit 2
}

if ((Get-AiOsSeverityValue -Value $Severity) -lt (Get-AiOsSeverityValue -Value ([string]$config.severity_floor))) {
    Write-AiOsNotificationLog -Channel $channel -Status "BELOW_FLOOR"
    Write-Host "STATUS=BELOW_FLOOR"
    exit 0
}

if (-not (Test-AiOsRateLimit -MaxPerHour ([int]$config.max_per_hour))) {
    Write-AiOsNotificationLog -Channel $channel -Status "RATE_LIMITED"
    Write-Host "STATUS=RATE_LIMITED"
    exit 2
}

if ($DryNotify -or -not $Apply) {
    Write-AiOsNotificationLog -Channel $channel -Status "DRY_NOTIFY" -Detail "would_send_length=$($Message.Length)"
    Write-Host "STATUS=DRY_NOTIFY"
    Write-Host "CHANNEL=$channel"
    Write-Host "REDACTED=true"
    exit 0
}

if ($channel -eq "file") {
    Write-AiOsFileNotification -Config $config
    exit 0
}

if ($channel -eq "webhook") {
    $credName = [string]$config.channels.webhook.credential_name
    $credential = Get-AiOsStoredCredential -Name $credName
    $targetUri = Get-AiOsCredentialSecret -Credential $credential
    if ([string]::IsNullOrWhiteSpace($targetUri)) {
        Write-AiOsNotificationLog -Channel "webhook" -Status "MISSING_CREDENTIAL_$credName"
        Write-AiOsFileNotification -Config $config
        exit 0
    }
    $payload = @{ subject = $Subject; severity = $Severity; message = $Message; sent_at_utc = Get-AiOsUtc } | ConvertTo-Json -Depth 5
    $response = Invoke-WebRequest -Uri $targetUri -Method ([string]$config.channels.webhook.method) -Body $payload -ContentType "application/json" -UseBasicParsing
    Write-AiOsNotificationLog -Channel "webhook" -Status ("HTTP_{0}" -f [int]$response.StatusCode) -Detail "body_length=$($Message.Length)"
    Write-Host "STATUS=HTTP_$([int]$response.StatusCode)"
    exit 0
}

if ($channel -eq "telegram") {
    $tokenName = [string]$config.channels.telegram.credential_name_token
    $chatName = [string]$config.channels.telegram.credential_name_chat
    $tokenCredential = Get-AiOsStoredCredential -Name $tokenName
    $chatCredential = Get-AiOsStoredCredential -Name $chatName
    $tokenSecret = Get-AiOsCredentialSecret -Credential $tokenCredential
    $chatSecret = Get-AiOsCredentialSecret -Credential $chatCredential
    if ([string]::IsNullOrWhiteSpace($tokenSecret) -or [string]::IsNullOrWhiteSpace($chatSecret)) {
        Write-AiOsNotificationLog -Channel "telegram" -Status "MISSING_CREDENTIAL_$tokenName"
        Write-AiOsFileNotification -Config $config
        exit 0
    }
    $uri = ("https://api." + "telegram.org/bot{0}/sendMessage") -f $tokenSecret
    $payload = @{ chat_id = $chatSecret; text = "$Subject`n$Severity`n$Message" }
    $response = Invoke-WebRequest -Uri $uri -Method POST -Body $payload -UseBasicParsing
    Write-AiOsNotificationLog -Channel "telegram" -Status ("HTTP_{0}" -f [int]$response.StatusCode) -Detail "body_length=$($Message.Length)"
    Write-Host "STATUS=HTTP_$([int]$response.StatusCode)"
    exit 0
}
