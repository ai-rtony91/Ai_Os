param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        'AI_OS MAIN CONTROL',
        'CODEX BUILD LANE',
        'VALIDATOR WORKER',
        'PACKET QUEUE',
        'APPROVAL INBOX',
        'RECOVERY HEALTH',
        'STANDBY WORKER'
    )]
    [string]$Marker
)

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # Older hosts may reject output encoding changes; the marker still works.
}

$emoji = @{
    Compass = [char]::ConvertFromUtf32(0x1F9ED)
    Tools = [char]::ConvertFromUtf32(0x1F6E0)
    Check = [char]::ConvertFromUtf32(0x2705)
    Package = [char]::ConvertFromUtf32(0x1F4E6)
    Inbox = [char]::ConvertFromUtf32(0x1F4E5)
    Health = [char]::ConvertFromUtf32(0x1FA7A)
    Pause = [char]::ConvertFromUtf32(0x23F8)
}

$markers = @{
    'AI_OS MAIN CONTROL' = [ordered]@{
        Emoji = $emoji.Compass
        Color = 'Cyan'
        Role = 'Primary operator terminal for runtime spine commands and final coordination.'
        Allowed = @(
            'Run .\aios.ps1 -Mode runtime',
            'Run .\aios.ps1 -Mode supervisor',
            'Check repo status and review validator output',
            'Paste approved git commands with explicit file paths'
        )
        Blocked = @(
            'No live trading, broker, OANDA, API key, or secret actions',
            'No startup tasks or scheduled tasks',
            'No destructive cleanup',
            'No git add .'
        )
        NextCommand = '.\aios.ps1 -Mode runtime'
    }
    'CODEX BUILD LANE' = [ordered]@{
        Emoji = $emoji.Tools
        Color = 'Yellow'
        Role = 'Focused build window for approved repo-scoped implementation work.'
        Allowed = @(
            'Edit only approved files',
            'Run targeted local validators',
            'Report files created, changed, validation, git status, commit, and push state'
        )
        Blocked = @(
            'No protected root governance edits unless explicitly approved',
            'No dashboard or Trading Lab changes unless scoped',
            'No broad commits or pushes',
            'No secrets or credential handling'
        )
        NextCommand = 'git status --short --branch'
    }
    'VALIDATOR WORKER' = [ordered]@{
        Emoji = $emoji.Check
        Color = 'Green'
        Role = 'Validation-only window for checks, parser tests, and read-only verification.'
        Allowed = @(
            'Run git diff --check',
            'Run scoped validators',
            'Parse changed JSON or PowerShell files',
            'Report PASS, WARN, or FAIL plainly'
        )
        Blocked = @(
            'No file edits',
            'No staging, commits, or pushes',
            'No external app launches',
            'No live trading or broker paths'
        )
        NextCommand = 'git diff --check'
    }
    'PACKET QUEUE' = [ordered]@{
        Emoji = $emoji.Package
        Color = 'Magenta'
        Role = 'Queue review window for workload packets, command packs, and next safe tasks.'
        Allowed = @(
            'Review queued packet text',
            'Sort next work by runtime-spine value',
            'Prepare DRY_RUN prompts for approval'
        )
        Blocked = @(
            'No APPLY without approval',
            'No random dashboard or tool expansion',
            'No destructive cleanup',
            'No broker or trading execution actions'
        )
        NextCommand = 'Get-ChildItem automation\packets'
    }
    'APPROVAL INBOX' = [ordered]@{
        Emoji = $emoji.Inbox
        Color = 'Blue'
        Role = 'Decision window for approvals, stop conditions, and user-controlled checkpoints.'
        Allowed = @(
            'Review DRY_RUN reports',
            'Approve or reject exact APPLY scopes',
            'Confirm explicit git add, commit, push, or PR steps'
        )
        Blocked = @(
            'No silent APPLY',
            'No implicit commits or pushes',
            'No merge, delete, move, rename, reset, clean, or auth changes without direct approval'
        )
        NextCommand = 'git status --short --branch'
    }
    'RECOVERY HEALTH' = [ordered]@{
        Emoji = $emoji.Health
        Color = 'Red'
        Role = 'Recovery and health-check window for failures, mismatches, and blocked states.'
        Allowed = @(
            'Run repo health checks',
            'Capture exact error output',
            'Mark UNKNOWN, MISMATCH, or INVALID DATA when evidence requires it'
        )
        Blocked = @(
            'No destructive repair commands',
            'No credential or security setting changes',
            'No startup or scheduled task changes',
            'No live trading paths'
        )
        NextCommand = 'git status --short --branch'
    }
    'STANDBY WORKER' = [ordered]@{
        Emoji = $emoji.Pause
        Color = 'DarkGray'
        Role = 'Idle worker window reserved for approved next tasks only.'
        Allowed = @(
            'Wait for a scoped task',
            'Run read-only status checks when asked',
            'Stay parked until assigned'
        )
        Blocked = @(
            'No speculative edits',
            'No autonomous cleanup',
            'No staging, commits, pushes, or external launches',
            'No broker or trading execution actions'
        )
        NextCommand = 'git status --short --branch'
    }
}

$repoPath = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
$identity = $markers[$Marker]

$windowTitle = "$($identity.Emoji) $Marker"
$Host.UI.RawUI.WindowTitle = $windowTitle

$bannerWidth = 100
try {
    if ($Host.UI.RawUI.WindowSize.Width -gt 0) {
        $bannerWidth = [Math]::Max(60, [Math]::Min(160, $Host.UI.RawUI.WindowSize.Width))
    }
} catch {
    $bannerWidth = 100
}

$divider = '=' * $bannerWidth

Write-Host ''
Write-Host $divider -ForegroundColor $identity.Color
Write-Host $windowTitle -ForegroundColor $identity.Color
Write-Host $divider -ForegroundColor $identity.Color
Write-Host "Role: $($identity.Role)"
Write-Host "Repo path: $repoPath"
Write-Host ''
Write-Host 'Allowed actions:' -ForegroundColor $identity.Color
foreach ($item in $identity.Allowed) {
    Write-Host "  - $item"
}
Write-Host ''
Write-Host 'Blocked actions:' -ForegroundColor $identity.Color
foreach ($item in $identity.Blocked) {
    Write-Host "  - $item"
}
Write-Host ''
Write-Host 'Next command hint:' -ForegroundColor $identity.Color
Write-Host "  $($identity.NextCommand)"
Write-Host ''
Write-Host 'Safety: repo-scoped marker only. No files, tasks, apps, brokers, keys, or trades are touched.'
Write-Host ''
