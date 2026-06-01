<#
.SYNOPSIS
Executes AI_OS relay inbox task packets.

.DESCRIPTION
P10 provider-neutral worker bridge for the local AI_OS relay. The existing
relay runner owns goal and handoff intake. This worker owns inbox execution
only. Claude is the current tested default provider, not the permanent
architecture.

TIER_2 packets are hard-stopped into relay/approvals before any CLI dispatch.
#>

[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Watch,
    [ValidateRange(1, 3600)]
    [int]$IntervalSeconds = 5,
    [ValidateRange(0, 100000)]
    [int]$MaxPackets = 0,
    [switch]$Report
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$RelayRoot = Join-Path $RepoRoot "relay"
$RunnerPath = Join-Path $PSScriptRoot "Invoke-AiOsRelayRunner.ps1"
$StopFlagPath = Join-Path $RelayRoot "STOP.flag"
$CanWrite = $true
$DefaultEstimateUsd = [decimal]0.02

$RelayPaths = [ordered]@{
    approvals = Join-Path $RelayRoot "approvals"
    done = Join-Path $RelayRoot "done"
    error = Join-Path $RelayRoot "error"
    inbox = Join-Path $RelayRoot "inbox"
    logs = Join-Path $RelayRoot "logs"
    outbox = Join-Path $RelayRoot "outbox"
    reports = Join-Path $RelayRoot "reports"
    running = Join-Path $RelayRoot "running"
}

$RunnerLogPath = Join-Path $RelayPaths.logs "runner.log"

function Import-AiOsRelayRunnerHelpers {
    if (-not (Test-Path -LiteralPath $RunnerPath -PathType Leaf)) {
        throw "Relay runner helper source missing: $RunnerPath"
    }

    $tokens = $null
    $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($RunnerPath, [ref]$tokens, [ref]$errors)
    if ($errors.Count -gt 0) {
        throw "Relay runner helper source failed to parse: $($errors[0].Message)"
    }

    $required = @(
        "Get-AiOsUtcTimestamp",
        "Write-AiOsRelayLog",
        "Test-AiOsProtectedRelayText",
        "Get-AiOsRelayTier"
    )

    foreach ($name in $required) {
        $node = $ast.Find({
            param($candidate)
            $candidate -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
            $candidate.Name -eq $name
        }, $true)

        if (-not $node) {
            throw "Required relay helper missing from runner: $name"
        }

        $bodyText = $node.Body.Extent.Text.Trim()
        if ($bodyText.StartsWith("{") -and $bodyText.EndsWith("}")) {
            $bodyText = $bodyText.Substring(1, $bodyText.Length - 2)
        }

        Set-Item -Path "function:\global:$name" -Value ([scriptblock]::Create($bodyText)) -Force
    }
}

function Initialize-AiOsRelayWorkerFolders {
    foreach ($path in $RelayPaths.Values) {
        if (-not (Test-Path -LiteralPath $path -PathType Container)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }
}

function Test-AiOsStableFile {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$File)

    $first = (Get-Item -LiteralPath $File.FullName).Length
    Start-Sleep -Seconds 1
    $second = (Get-Item -LiteralPath $File.FullName).Length
    return $first -eq $second
}

function Get-AiOsTaskIdFromFile {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$File)

    return ([System.IO.Path]::GetFileNameWithoutExtension($File.Name) -replace "\.task$", "")
}

function Get-AiOsStringArray {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value) {
        return @()
    }

    if ($Value -is [array]) {
        return @($Value | ForEach-Object { [string]$_ })
    }

    return @([string]$Value)
}

function Move-AiOsRelayPacket {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$TargetFolder
    )

    $targetPath = Join-Path $TargetFolder (Split-Path -Leaf $SourcePath)
    Move-Item -LiteralPath $SourcePath -Destination $targetPath -Force
    return $targetPath
}

function Write-AiOsWorkerReport {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Worker,
        [Parameter(Mandatory = $true)][string]$Provider,
        [Parameter(Mandatory = $true)][string]$ProviderCommand,
        [Parameter(Mandatory = $true)][string]$Tier,
        [Parameter(Mandatory = $true)][datetime]$StartedAt,
        [Parameter(Mandatory = $true)][datetime]$EndedAt,
        [Parameter(Mandatory = $true)][object]$ExitCode,
        [Parameter(Mandatory = $true)][string[]]$AllowedPaths,
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string[]]$Body
    )

    $reportPath = Join-Path $RelayPaths.outbox ("{0}.report.txt" -f $Id)
    @(
        "id: $Id"
        "worker: $Worker"
        "provider: $Provider"
        "provider_command: $ProviderCommand"
        "tier: $Tier"
        "started_at: $($StartedAt.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))"
        "ended_at: $($EndedAt.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))"
        "duration_seconds: $([int]($EndedAt - $StartedAt).TotalSeconds)"
        "exit_code: $ExitCode"
        "allowed_paths: $($AllowedPaths -join ', ')"
        ""
        "----- output -----"
        $Body
    ) | Set-Content -LiteralPath $reportPath -Encoding UTF8

    return $reportPath
}

function Write-AiOsPacketError {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Reason,
        [Parameter(Mandatory = $true)][string]$Detail
    )

    $errorPath = Join-Path $RelayPaths.error ("{0}.error.txt" -f $Id)
    @(
        "id: $Id"
        "reason: $Reason"
        "detail: $Detail"
    ) | Set-Content -LiteralPath $errorPath -Encoding UTF8
}

function Add-AiOsDeferredUntil {
    param([Parameter(Mandatory = $true)][string]$PacketPath, [Parameter(Mandatory = $true)][string]$DeferredUntilUtc)
    $packet = Get-Content -Raw -LiteralPath $PacketPath | ConvertFrom-Json
    if ($packet.PSObject.Properties["deferred_until"]) { $packet.deferred_until = $DeferredUntilUtc } else { $packet | Add-Member -NotePropertyName "deferred_until" -NotePropertyValue $DeferredUntilUtc }
    $packet | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $PacketPath -Encoding UTF8
}

function Read-AiOsTaskPacket {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$File)

    $id = Get-AiOsTaskIdFromFile -File $File
    try {
        $packet = Get-Content -LiteralPath $File.FullName -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            ok = $false
            id = $id
            reason = "PACKET_INCOMPLETE"
            detail = "JSON parse failed: $($_.Exception.Message)"
        }
    }

    $missing = @()
    foreach ($field in @("id", "worker", "tier", "mission", "allowed_paths")) {
        if (-not $packet.PSObject.Properties[$field] -or [string]::IsNullOrWhiteSpace([string]$packet.$field)) {
            $missing += $field
        }
    }

    if ($missing.Count -gt 0) {
        return [pscustomobject]@{
            ok = $false
            id = if ($packet.PSObject.Properties["id"]) { [string]$packet.id } else { $id }
            reason = "PACKET_INCOMPLETE"
            detail = "Missing required field(s): $($missing -join ', ')"
        }
    }

    $worker = ([string]$packet.worker).ToLowerInvariant()
    $provider = if ($packet.PSObject.Properties["provider"] -and -not [string]::IsNullOrWhiteSpace([string]$packet.provider)) {
        ([string]$packet.provider).ToLowerInvariant()
    } else {
        $worker
    }

    if ($worker -notin @("claude", "codex", "openai", "custom", "planner", "builder")) {
        return [pscustomobject]@{
            ok = $false
            id = [string]$packet.id
            reason = "PACKET_INCOMPLETE"
            detail = "Invalid worker '$worker'. Expected a known relay worker label."
        }
    }

    $providerSpec = Resolve-AiOsProviderSpec -Packet $packet -Provider $provider -Worker $worker
    if (-not $providerSpec.ok) {
        return [pscustomobject]@{
            ok = $false
            id = [string]$packet.id
            reason = "PACKET_INCOMPLETE"
            detail = $providerSpec.detail
        }
    }

    return [pscustomobject]@{
        ok = $true
        packet = $packet
        id = [string]$packet.id
        worker = $worker
        provider = $providerSpec.provider
        provider_command = $providerSpec.command
        provider_args = $providerSpec.args
        tier = [string]$packet.tier
        mission = [string]$packet.mission
        allowed_paths = @($packet.allowed_paths | ForEach-Object { [string]$_ })
    }
}

function Resolve-AiOsProviderSpec {
    param(
        [Parameter(Mandatory = $true)][object]$Packet,
        [Parameter(Mandatory = $true)][string]$Provider,
        [Parameter(Mandatory = $true)][string]$Worker
    )

    $defaults = @{
        claude = @{
            command = "claude"
            args = @("--permission-mode", "plan", "--output-format", "text")
        }
        codex = @{
            command = "codex"
            args = @("exec", "--sandbox", "workspace-write", "-")
        }
        openai = @{
            command = ""
            args = @()
        }
        custom = @{
            command = ""
            args = @()
        }
    }

    if (-not $defaults.ContainsKey($Provider)) {
        return [pscustomobject]@{
            ok = $false
            detail = "Unknown provider '$Provider'. Supported providers: claude, codex, openai, custom."
        }
    }

    $providerCommand = if ($Packet.PSObject.Properties["provider_command"]) { [string]$Packet.provider_command } else { [string]$defaults[$Provider].command }
    $providerArgs = if ($Packet.PSObject.Properties["provider_args"]) { Get-AiOsStringArray -Value $Packet.provider_args } else { Get-AiOsStringArray -Value $defaults[$Provider].args }

    if ([string]::IsNullOrWhiteSpace($providerCommand)) {
        return [pscustomobject]@{
            ok = $false
            detail = "Provider '$Provider' requires explicit provider_command before dispatch."
        }
    }

    if ($providerCommand -match "[\r\n;&|<>]") {
        return [pscustomobject]@{
            ok = $false
            detail = "Provider command contains blocked shell metacharacters."
        }
    }

    if (@($providerArgs | Where-Object { $_ -match "[\r\n]" }).Count -gt 0) {
        return [pscustomobject]@{
            ok = $false
            detail = "Provider args contain blocked line breaks."
        }
    }

    return [pscustomobject]@{
        ok = $true
        provider = $Provider
        worker = $Worker
        command = $providerCommand
        args = $providerArgs
    }
}

function Invoke-AiOsProviderWorker {
    param(
        [Parameter(Mandatory = $true)][string]$Worker,
        [Parameter(Mandatory = $true)][string]$Provider,
        [Parameter(Mandatory = $true)][string]$ProviderCommand,
        [Parameter(Mandatory = $true)][string[]]$ProviderArgs,
        [Parameter(Mandatory = $true)][string]$Tier,
        [Parameter(Mandatory = $true)][string]$Mission,
        [Parameter(Mandatory = $true)][string[]]$AllowedPaths
    )

    if ($Provider -eq "claude") {
        $stdin = $Mission
    } else {
        $stdin = @(
            "AI_OS relay worker bounded task."
            "Provider: $Provider"
            "Worker: $Worker"
            "Allowed paths:"
            ($AllowedPaths | ForEach-Object { "- $_" })
            ""
            "Mission:"
            $Mission
        ) -join [Environment]::NewLine
    }

    $result = & "$PSScriptRoot\..\timeout\Invoke-AiOsCliWithTimeout.ps1" -FilePath $ProviderCommand -ArgumentList $ProviderArgs -TimeoutSec $script:CurrentWorkerTimeoutSec -StdIn $stdin -WorkingDirectory $RepoRoot
    $exitCode = $result.exit_code
    $output = @("stdout:", $result.stdout, "stderr:", $result.stderr)

    return [pscustomobject]@{
        exit_code = $exitCode
        output = $output
        command = "$ProviderCommand $($ProviderArgs -join ' ')"
    }
}

function Resolve-AiOsWorkerCostRecord {
    param(
        [Parameter(Mandatory = $true)][object]$ProviderResult,
        [Parameter(Mandatory = $true)][decimal]$DefaultEstimateUsd
    )

    $record = [ordered]@{
        cost_usd = $DefaultEstimateUsd
        input_tokens = 0
        output_tokens = 0
        estimated = $true
        estimate_reason = "fallback_nonzero_worker_invocation"
    }

    try {
        $lines = @($ProviderResult.output | ForEach-Object { [string]$_ })
        foreach ($line in $lines) {
            $trimmed = $line.Trim()
            if (-not ($trimmed.StartsWith("{") -and $trimmed.EndsWith("}"))) {
                continue
            }

            $json = $trimmed | ConvertFrom-Json
            $jsonCost = $null
            if ($json.PSObject.Properties["cost_usd"]) { $jsonCost = [decimal]$json.cost_usd }
            elseif ($json.PSObject.Properties["cost"]) { $jsonCost = [decimal]$json.cost }

            $inputTokens = 0
            $outputTokens = 0
            if ($json.PSObject.Properties["usage"] -and $null -ne $json.usage) {
                if ($json.usage.PSObject.Properties["input_tokens"]) { $inputTokens = [int]$json.usage.input_tokens }
                elseif ($json.usage.PSObject.Properties["prompt_tokens"]) { $inputTokens = [int]$json.usage.prompt_tokens }
                if ($json.usage.PSObject.Properties["output_tokens"]) { $outputTokens = [int]$json.usage.output_tokens }
                elseif ($json.usage.PSObject.Properties["completion_tokens"]) { $outputTokens = [int]$json.usage.completion_tokens }
            } else {
                if ($json.PSObject.Properties["input_tokens"]) { $inputTokens = [int]$json.input_tokens }
                if ($json.PSObject.Properties["output_tokens"]) { $outputTokens = [int]$json.output_tokens }
            }

            if ($null -ne $jsonCost -and $jsonCost -gt 0) {
                $record.cost_usd = $jsonCost
                $record.input_tokens = $inputTokens
                $record.output_tokens = $outputTokens
                $record.estimated = $false
                $record.estimate_reason = "cli_reported_cost"
                break
            }

            if (($inputTokens + $outputTokens) -gt 0) {
                $record.cost_usd = [decimal](($inputTokens * 0.000005) + ($outputTokens * 0.000015))
                if ($record.cost_usd -le 0) { $record.cost_usd = $DefaultEstimateUsd }
                $record.input_tokens = $inputTokens
                $record.output_tokens = $outputTokens
                $record.estimated = $true
                $record.estimate_reason = "token_rate_estimate"
                break
            }
        }
    } catch {
        $record.cost_usd = $DefaultEstimateUsd
        $record.input_tokens = 0
        $record.output_tokens = 0
        $record.estimated = $true
        $record.estimate_reason = "fallback_usage_parse_failed"
    }

    if ($record.cost_usd -le 0) {
        $record.cost_usd = $DefaultEstimateUsd
        $record.estimated = $true
        $record.estimate_reason = "fallback_nonzero_worker_invocation"
    }

    return [pscustomobject]$record
}
function Move-AiOsTier2ToApprovals {
    param(
        [Parameter(Mandatory = $true)][System.IO.FileInfo]$File,
        [Parameter(Mandatory = $true)][object]$PacketInfo
    )

    $approvalPath = Move-AiOsRelayPacket -SourcePath $File.FullName -TargetFolder $RelayPaths.approvals
    $reasonPath = Join-Path $RelayPaths.approvals ("{0}.approval-reason.txt" -f $PacketInfo.id)
    @(
        "id: $($PacketInfo.id)"
        "reason: TIER_2_HARD_STOP"
        "worker: $($PacketInfo.worker)"
        "provider: $($PacketInfo.provider)"
        "provider_command: $($PacketInfo.provider_command)"
        "declared_tier: $($PacketInfo.tier)"
        "classified_tier: $(Get-AiOsRelayTier -Text $PacketInfo.mission)"
        "action: moved to approvals without CLI dispatch"
    ) | Set-Content -LiteralPath $reasonPath -Encoding UTF8

    Write-AiOsRelayLog "[WORKER] $($PacketInfo.id) inbox -> approvals reason=TIER_2_HARD_STOP path=$approvalPath"
}

function Complete-AiOsRelayWorkerPacket {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$File)

    if (-not (Test-AiOsStableFile -File $File)) {
        Write-AiOsRelayLog "[WORKER] SKIP unstable file $($File.Name)"
        return "SKIPPED"
    }

    $parsed = Read-AiOsTaskPacket -File $File
    if (-not $parsed.ok) {
        $target = Move-AiOsRelayPacket -SourcePath $File.FullName -TargetFolder $RelayPaths.error
        Write-AiOsPacketError -Id $parsed.id -Reason $parsed.reason -Detail $parsed.detail
        Write-AiOsRelayLog "[WORKER] $($parsed.id) inbox -> error reason=$($parsed.reason) path=$target"
        return "PROCESSED"
    }

    $classifiedTier = Get-AiOsRelayTier -Text $parsed.mission
    $isTier2 = (Test-AiOsProtectedRelayText -Text $parsed.mission) -or
        ($parsed.tier -match "^TIER_2") -or
        ($classifiedTier -match "^TIER_2")

    if ($isTier2) {
        Move-AiOsTier2ToApprovals -File $File -PacketInfo $parsed
        return "PROCESSED"
    }

    $runningPath = Move-AiOsRelayPacket -SourcePath $File.FullName -TargetFolder $RelayPaths.running
    Write-AiOsRelayLog "[WORKER] $($parsed.id) inbox -> running worker=$($parsed.worker) provider=$($parsed.provider) command=$($parsed.provider_command) tier=$($parsed.tier)"

    $started = Get-Date
    $run_start = $started.ToUniversalTime(); $script:CurrentWorkerTimeoutSec = if ($parsed.packet.PSObject.Properties["timeout_sec"]) { [int]$parsed.packet.timeout_sec } else { 600 }
    $exitCode = 0
    $body = @()

    if (-not $Apply) {
        $body = @(
            "[DRY_RUN STUB]"
            "No CLI was called."
            "would_call: $($parsed.worker)"
            "provider: $($parsed.provider)"
            "provider_command: $($parsed.provider_command)"
            "provider_args: $($parsed.provider_args -join ' ')"
            "tier: $($parsed.tier)"
            "allowed_paths: $($parsed.allowed_paths -join ', ')"
            "mission_chars: $($parsed.mission.Length)"
        )
    } else {
        $cycleId = if ([string]::IsNullOrWhiteSpace($env:AIOS_CYCLE_ID)) { (Get-Date).ToUniversalTime().ToString("yyyyMMdd") } else { $env:AIOS_CYCLE_ID }
        $cost = & "$PSScriptRoot\..\cost\Test-AiOsCostCeiling.ps1" -CycleId $cycleId
        if (-not $cost.ok) {
            $target = Move-AiOsRelayPacket -SourcePath $runningPath -TargetFolder $RelayPaths.error
            Write-AiOsPacketError -Id $parsed.id -Reason "COST_CEILING_EXCEEDED" -Detail "$($cost.reason) cycle_spend=$($cost.cycle_spend) day_spend=$($cost.day_spend)"
            $notify = Join-Path $RepoRoot "automation\orchestration\notifications\Send-AiOsNotification.ps1"
            if (Test-Path -LiteralPath $notify -PathType Leaf) { & powershell -NoProfile -ExecutionPolicy Bypass -File $notify -Message "COST_CEILING_EXCEEDED packet=$($parsed.id) reason=$($cost.reason)" -Severity "CRITICAL" -Subject "AI_OS BLOCKER" -Apply | Out-Null }
            Write-AiOsRelayLog "[WORKER] $($parsed.id) running -> error reason=COST_CEILING_EXCEEDED path=$target"
            return "PROCESSED"
        }
        $lock = & "$PSScriptRoot\..\lock\Test-AiOsFileLock.ps1" -AllowedPaths $parsed.allowed_paths -RepoRoot $RepoRoot
        if ($lock.defer) {
            Add-AiOsDeferredUntil -PacketPath $runningPath -DeferredUntilUtc $lock.defer_until_utc
            $target = Move-AiOsRelayPacket -SourcePath $runningPath -TargetFolder $RelayPaths.inbox
            Write-AiOsRelayLog "[WORKER] $($parsed.id) running -> inbox reason=FILE_LOCK_DEFERRED deferred_until=$($lock.defer_until_utc) path=$target"
            return "SKIPPED"
        }
        $result = Invoke-AiOsProviderWorker -Worker $parsed.worker -Provider $parsed.provider -ProviderCommand $parsed.provider_command -ProviderArgs $parsed.provider_args -Tier $parsed.tier -Mission $parsed.mission -AllowedPaths $parsed.allowed_paths
        $costRecord = Resolve-AiOsWorkerCostRecord -ProviderResult $result -DefaultEstimateUsd $DefaultEstimateUsd
        [void](& "$PSScriptRoot\..\cost\Add-AiOsCostLedgerEntry.ps1" -CycleId $cycleId -Cost $costRecord.cost_usd -InputTokens $costRecord.input_tokens -OutputTokens $costRecord.output_tokens -PacketId $parsed.id -Worker $parsed.worker -Estimated $costRecord.estimated -EstimateReason $costRecord.estimate_reason)
        Write-AiOsRelayLog "[WORKER] $($parsed.id) cost_ledger cost_usd=$($costRecord.cost_usd) estimated=$($costRecord.estimated) estimate_reason=$($costRecord.estimate_reason) cycle_id=$cycleId"
        $exitCode = $result.exit_code
        $body = @("command: $($result.command)", "") + @($result.output)
    }

    $ended = Get-Date
    [void](Write-AiOsWorkerReport -Id $parsed.id -Worker $parsed.worker -Provider $parsed.provider -ProviderCommand $parsed.provider_command -Tier $parsed.tier -StartedAt $started -EndedAt $ended -ExitCode $exitCode -AllowedPaths $parsed.allowed_paths -Body $body)

    if ([string]$exitCode -eq "TIMEOUT_EXCEEDED") {
        $target = Move-AiOsRelayPacket -SourcePath $runningPath -TargetFolder $RelayPaths.error
        Write-AiOsPacketError -Id $parsed.id -Reason "WORKER_TIMEOUT" -Detail "Worker exceeded timeout_sec=$script:CurrentWorkerTimeoutSec. See outbox report."; Write-AiOsRelayLog "[WORKER] $($parsed.id) running -> error reason=WORKER_TIMEOUT path=$target"
    } elseif ($exitCode -eq 0) {
        $val = & "$PSScriptRoot\..\validators\output\Test-AiOsWorkerOutput.DRY_RUN.ps1" -PacketId $parsed.id -AllowedPaths $parsed.allowed_paths -RunStartUtc $run_start -RepoRoot $RepoRoot
        if (-not $val.pass) {
            $target = Move-AiOsRelayPacket -SourcePath $runningPath -TargetFolder $RelayPaths.error
            Write-AiOsPacketError -Id $parsed.id -Reason "OUTPUT_OUTSIDE_ALLOWED_PATHS" -Detail "Output validator failed: $($val.violation_reason). See relay/logs/output_validator.log."
            Write-AiOsRelayLog "[WORKER] $($parsed.id) running -> error reason=OUTPUT_OUTSIDE_ALLOWED_PATHS path=$target"
            return "PROCESSED"
        }
        $target = Move-AiOsRelayPacket -SourcePath $runningPath -TargetFolder $RelayPaths.done
        Write-AiOsRelayLog "[WORKER] $($parsed.id) running -> done exit_code=0 path=$target"
    } else {
        $target = Move-AiOsRelayPacket -SourcePath $runningPath -TargetFolder $RelayPaths.error
        Write-AiOsPacketError -Id $parsed.id -Reason "WORKER_EXIT_$exitCode" -Detail "Worker exited non-zero. See outbox report."
        Write-AiOsRelayLog "[WORKER] $($parsed.id) running -> error reason=WORKER_EXIT_$exitCode path=$target"
    }

    return "PROCESSED"
}

function Invoke-AiOsRelayWorkerPass {
    $processed = 0
    $taskFiles = @(Get-ChildItem -LiteralPath $RelayPaths.inbox -File -Filter "*.task.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime, Name)

    foreach ($file in $taskFiles) {
        if ($MaxPackets -gt 0 -and $script:ProcessedPackets -ge $MaxPackets) {
            break
        }

        $result = Complete-AiOsRelayWorkerPacket -File $file
        if ($result -eq "PROCESSED") {
            $script:ProcessedPackets++
            $processed++
        }
    }

    return $processed
}

function New-AiOsRelayWorkerReport {
    $today = (Get-Date).ToUniversalTime().Date
    $dateText = $today.ToString("yyyy-MM-dd")
    $reportPath = Join-Path $RelayPaths.reports ("{0}-summary.md" -f $dateText)

    $doneFiles = @(Get-ChildItem -LiteralPath $RelayPaths.done -File -Filter "*.task.json" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTimeUtc.Date -eq $today })
    $errorFiles = @(Get-ChildItem -LiteralPath $RelayPaths.error -File -Filter "*.task.json" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTimeUtc.Date -eq $today })
    $allFiles = @($doneFiles + $errorFiles | Sort-Object LastWriteTimeUtc, Name)

    $lines = @(
        "# AI_OS Relay Summary - $dateText"
        ""
        "done: $($doneFiles.Count)"
        "error: $($errorFiles.Count)"
        ""
        "| id | worker | tier | duration | exit_code | first_line |"
        "|---|---|---|---:|---:|---|"
    )

    foreach ($file in $allFiles) {
        $id = Get-AiOsTaskIdFromFile -File $file
        $reportFile = Join-Path $RelayPaths.outbox ("{0}.report.txt" -f $id)
        $reportText = if (Test-Path -LiteralPath $reportFile -PathType Leaf) { Get-Content -LiteralPath $reportFile -Raw } else { "" }
        $worker = if ($reportText -match "(?m)^worker:\s*(.+?)\r?$") { $Matches[1].Trim() } else { "" }
        $tier = if ($reportText -match "(?m)^tier:\s*(.+?)\r?$") { $Matches[1].Trim() } else { "" }
        $duration = if ($reportText -match "(?m)^duration_seconds:\s*(\d+)\r?$") { $Matches[1] } else { "" }
        $exitCode = if ($reportText -match "(?m)^exit_code:\s*(-?\d+)\r?$") { $Matches[1] } else { "" }
        $firstLine = (($reportText -split "\r?\n") | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
        if (-not $firstLine) { $firstLine = $file.Name }
        $safeFirstLine = ([string]$firstLine).Replace("|", "/")
        $lines += "| $id | $worker | $tier | $duration | $exitCode | $safeFirstLine |"
    }

    $lines | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-AiOsRelayLog "[WORKER] report -> $reportPath done=$($doneFiles.Count) error=$($errorFiles.Count)"
    return $reportPath
}

Import-AiOsRelayRunnerHelpers
Initialize-AiOsRelayWorkerFolders

$preflight = & "$PSScriptRoot\..\preflight\Test-AiOsToolPreflight.ps1"
if (-not $preflight.ok) {
    Write-AiOsRelayLog "PREFLIGHT_FAILED missing=$($preflight.missing -join ',') unauth=$($preflight.unauth -join ',')"
    $notify = Join-Path $RepoRoot "automation\orchestration\notifications\Send-AiOsNotification.ps1"
    if (Test-Path -LiteralPath $notify -PathType Leaf) { & powershell -NoProfile -ExecutionPolicy Bypass -File $notify -Message "PREFLIGHT_FAILED missing=$($preflight.missing -join ',') unauth=$($preflight.unauth -join ',')" -Severity "CRITICAL" -Subject "AI_OS BLOCKER" -Apply | Out-Null }
    exit 2
}

$script:ProcessedPackets = 0
Write-AiOsRelayLog ("[WORKER] start Apply={0} Watch={1} MaxPackets={2} Report={3}" -f [bool]$Apply, [bool]$Watch, $MaxPackets, [bool]$Report)

do {
    if (Test-Path -LiteralPath $StopFlagPath -PathType Leaf) {
        Write-AiOsRelayLog "[WORKER] STOP_FLAG_PRESENT path=$StopFlagPath"
        break
    }

    [void](Invoke-AiOsRelayWorkerPass)

    if ($MaxPackets -gt 0 -and $script:ProcessedPackets -ge $MaxPackets) {
        break
    }

    if ($Watch) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while ($Watch)

if ($Report) {
    [void](New-AiOsRelayWorkerReport)
}

Write-AiOsRelayLog ("[WORKER] stop processed={0}" -f $script:ProcessedPackets)
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
