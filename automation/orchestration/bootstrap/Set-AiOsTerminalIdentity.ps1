param(
    [object]$Lane,
    [string]$LaneJsonBase64,
    [string]$WorkerId = "",
    [string]$WorkerZone = "",
    [string]$WorkerRole = "",
    [string]$WorkerIcon = "",
    [string]$Mode = "DRY_RUN",
    [string]$RepoRoot = "",
    [string]$WindowTitle = "",
    [string]$PromptPrefix = ""
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsDefaultWorkerIdentity {
    param(
        [string]$RequestedWorkerId,
        [string]$RequestedWorkerZone,
        [string]$RequestedWorkerRole,
        [string]$RequestedWorkerIcon,
        [string]$RequestedMode
    )

    $map = @{
        CODEX_EAST = @{
            Zone = "EAST"
            Role = "CODEX"
            Icon = [char]::ConvertFromUtf32(0x2699)
            Title = "CODEX EAST | AI_OS | $RequestedMode"
            Prompt = "EAST"
        }
        CODEX_WEST = @{
            Zone = "WEST"
            Role = "CODEX"
            Icon = [char]::ConvertFromUtf32(0x2692)
            Title = "CODEX WEST | AI_OS | $RequestedMode"
            Prompt = "WEST"
        }
        VALIDATOR = @{
            Zone = "VALIDATOR"
            Role = "VALIDATOR"
            Icon = [char]::ConvertFromUtf32(0x1F6E1)
            Title = "VALIDATOR | AI_OS"
            Prompt = "VALIDATOR"
        }
        APPROVAL = @{
            Zone = "APPROVAL"
            Role = "APPROVAL"
            Icon = [char]::ConvertFromUtf32(0x1F512)
            Title = "APPROVAL INBOX | AI_OS"
            Prompt = "APPROVAL"
        }
        PACKET_QUEUE = @{
            Zone = "QUEUE"
            Role = "PACKET_QUEUE"
            Icon = [char]::ConvertFromUtf32(0x1F4E6)
            Title = "PACKET QUEUE | AI_OS"
            Prompt = "PACKETS"
        }
        LOCK_MANAGER = @{
            Zone = "LOCKS"
            Role = "LOCK_MANAGER"
            Icon = [char]::ConvertFromUtf32(0x1F511)
            Title = "LOCK MANAGER | AI_OS"
            Prompt = "LOCKS"
        }
        NIGHT_SUPERVISOR = @{
            Zone = "NIGHT"
            Role = "SUPERVISOR"
            Icon = [char]::ConvertFromUtf32(0x1F319)
            Title = "NIGHT SUPERVISOR | AI_OS"
            Prompt = "NIGHT"
        }
        MAIN_CONTROL = @{
            Zone = "CONTROL"
            Role = "MAIN_CONTROL"
            Icon = ""
            Title = "AI_OS MAIN CONTROL"
            Prompt = "AI_OS"
        }
    }

    $key = if ([string]::IsNullOrWhiteSpace($RequestedWorkerId)) { "MAIN_CONTROL" } else { $RequestedWorkerId.ToUpperInvariant() }
    $defaults = if ($map.ContainsKey($key)) { $map[$key] } else {
        @{
            Zone = if ([string]::IsNullOrWhiteSpace($RequestedWorkerZone)) { "EAST" } else { $RequestedWorkerZone }
            Role = if ([string]::IsNullOrWhiteSpace($RequestedWorkerRole)) { "CODEX" } else { $RequestedWorkerRole }
            Icon = if ([string]::IsNullOrWhiteSpace($RequestedWorkerIcon)) { [char]::ConvertFromUtf32(0x2699) } else { $RequestedWorkerIcon }
            Title = "$key | AI_OS | $RequestedMode"
            Prompt = $key
        }
    }

    [pscustomobject]@{
        WorkerId = $key
        WorkerZone = if ([string]::IsNullOrWhiteSpace($RequestedWorkerZone)) { [string]$defaults.Zone } else { $RequestedWorkerZone }
        WorkerRole = if ([string]::IsNullOrWhiteSpace($RequestedWorkerRole)) { [string]$defaults.Role } else { $RequestedWorkerRole }
        WorkerIcon = if ([string]::IsNullOrWhiteSpace($RequestedWorkerIcon)) { [string]$defaults.Icon } else { $RequestedWorkerIcon }
        Mode = if ([string]::IsNullOrWhiteSpace($RequestedMode)) { "DRY_RUN" } else { $RequestedMode }
        Title = [string]$defaults.Title
        Prompt = [string]$defaults.Prompt
    }
}

function Set-AiOsTerminalIdentity {
    param(
        [object]$Lane,
        [string]$LaneJsonBase64,
        [string]$WorkerId = "",
        [string]$WorkerZone = "",
        [string]$WorkerRole = "",
        [string]$WorkerIcon = "",
        [string]$Mode = "DRY_RUN",
        [string]$RepoRoot = "",
        [string]$WindowTitle = "",
        [string]$PromptPrefix = ""
    )

    if ($null -eq $Lane -and -not [string]::IsNullOrWhiteSpace($LaneJsonBase64)) {
        $laneJson = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($LaneJsonBase64))
        $Lane = $laneJson | ConvertFrom-Json
    }

    if ($null -ne $Lane) {
        if ($Lane.PSObject.Properties.Name -contains "worker_id" -and [string]::IsNullOrWhiteSpace($WorkerId)) {
            $WorkerId = [string]$Lane.worker_id
        }
        if ($Lane.PSObject.Properties.Name -contains "lane_id" -and [string]::IsNullOrWhiteSpace($WorkerZone)) {
            $WorkerZone = [string]$Lane.lane_id
        }
        if ($Lane.PSObject.Properties.Name -contains "role" -and [string]::IsNullOrWhiteSpace($WorkerRole)) {
            $WorkerRole = [string]$Lane.role
        }
        if ($Lane.PSObject.Properties.Name -contains "emoji_marker" -and [string]::IsNullOrWhiteSpace($WorkerIcon)) {
            $WorkerIcon = [string]$Lane.emoji_marker
        }
        if ($Lane.PSObject.Properties.Name -contains "mode" -and [string]::IsNullOrWhiteSpace($Mode)) {
            $Mode = [string]$Lane.mode
        }
        if ($Lane.PSObject.Properties.Name -contains "path" -and [string]::IsNullOrWhiteSpace($RepoRoot)) {
            $RepoRoot = [string]$Lane.path
        }
        if ($Lane.PSObject.Properties.Name -contains "window_title" -and [string]::IsNullOrWhiteSpace($WindowTitle)) {
            $WindowTitle = [string]$Lane.window_title
        }
        if ($Lane.PSObject.Properties.Name -contains "display_title" -and [string]::IsNullOrWhiteSpace($PromptPrefix)) {
            $PromptPrefix = [string]$Lane.display_title
        }
    }

    $identity = Get-AiOsDefaultWorkerIdentity `
        -RequestedWorkerId $WorkerId `
        -RequestedWorkerZone $WorkerZone `
        -RequestedWorkerRole $WorkerRole `
        -RequestedWorkerIcon $WorkerIcon `
        -RequestedMode $Mode

    if ([string]::IsNullOrWhiteSpace($WindowTitle)) {
        $WindowTitle = if ([string]::IsNullOrWhiteSpace($identity.WorkerIcon)) {
            $identity.Title
        } else {
            "$($identity.WorkerIcon) $($identity.Title)"
        }
    }

    if ([string]::IsNullOrWhiteSpace($PromptPrefix)) {
        $PromptPrefix = if ([string]::IsNullOrWhiteSpace($identity.WorkerIcon)) {
            "$($identity.Prompt) [$($identity.WorkerId)]"
        } else {
            "$($identity.WorkerIcon) $($identity.Prompt) [$($identity.WorkerId)]"
        }
    }

    $env:AIOS_WORKER_ID = $identity.WorkerId
    $env:AIOS_WORKER_ZONE = $identity.WorkerZone
    $env:AIOS_WORKER_ROLE = $identity.WorkerRole
    $env:AIOS_WORKER_ICON = $identity.WorkerIcon
    $env:AIOS_WORKER_MODE = $identity.Mode
    if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
        $env:AIOS_REPO_ROOT = $RepoRoot
    }

    $Host.UI.RawUI.WindowTitle = $WindowTitle
    $escape = [char]27
    $bell = [char]7
    Write-Host -NoNewline ("$escape]0;$WindowTitle$bell")

    $global:AIOS_PROMPT_PREFIX = $PromptPrefix
    function global:prompt {
        "$global:AIOS_PROMPT_PREFIX > "
    }

    Write-Host "ACTIVE WORKER:" -ForegroundColor Cyan
    Write-Host "worker_id: $env:AIOS_WORKER_ID"
    Write-Host "worker_zone: $env:AIOS_WORKER_ZONE"
    Write-Host "worker_role: $env:AIOS_WORKER_ROLE"
    Write-Host "mode: $env:AIOS_WORKER_MODE"
    Write-Host "title: $WindowTitle"
}

if ($MyInvocation.InvocationName -ne ".") {
    Set-AiOsTerminalIdentity `
        -Lane $Lane `
        -LaneJsonBase64 $LaneJsonBase64 `
        -WorkerId $WorkerId `
        -WorkerZone $WorkerZone `
        -WorkerRole $WorkerRole `
        -WorkerIcon $WorkerIcon `
        -Mode $Mode `
        -RepoRoot $RepoRoot `
        -WindowTitle $WindowTitle `
        -PromptPrefix $PromptPrefix
}
