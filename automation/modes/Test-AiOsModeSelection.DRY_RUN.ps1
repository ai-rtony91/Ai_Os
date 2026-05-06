param(
    [Parameter(Mandatory = $true)]
    [string]$ModeName
)

$ErrorActionPreference = 'Stop'
$scriptMode = 'DRY_RUN'
$validModes = @(
    'WORK_MODE',
    'TRADING_MODE',
    'RETIRE_MODE',
    'RETURN_TO_WORK_MODE',
    'MORNING_BRIEF_MODE'
)

function Write-List {
    param(
        [string]$Title,
        [string[]]$Items
    )

    Write-Host "${Title}:"
    foreach ($item in $Items) {
        Write-Host "- $item"
    }
}

$normalizedModeName = $ModeName.ToUpperInvariant()

Write-Host 'Task name: AI_OS Stage 9F Mode Selection Dry Run'
Write-Host "Mode: $scriptMode"
Write-Host "Selected mode: $normalizedModeName"
Write-Host 'Safety: Console-output only. No apps are launched, no startup settings are changed, and no files are edited.'
Write-Host ''

if ($validModes -notcontains $normalizedModeName) {
    Write-Host 'Final summary: FAIL'
    Write-Host "Unknown mode: $ModeName"
    Write-List -Title 'Valid modes' -Items $validModes
    Write-Host ('DRY_RUN COMPLETE {0} NO MODE ACTION EXECUTED.' -f [char]0x2014)
    exit 1
}

$modeRules = @{
    WORK_MODE = @{
        Allowed = @(
            'Read repo context.',
            'Run approved DRY_RUN checks.',
            'Prepare scoped work-order reports.'
        )
        Blocked = @(
            'No app launch without separate approval.',
            'No git add, commit, or push.',
            'No protected file edit without backup and approval.'
        )
        Approval = 'Human approval required before APPLY changes or git checkpoint.'
    }
    TRADING_MODE = @{
        Allowed = @(
            'Read approved planning documents.',
            'Review trading safety boundaries as documentation only.',
            'Report blocked broker/live-trading status.'
        )
        Blocked = @(
            'No broker orders.',
            'No live trading.',
            'No credential, token, or API key handling.',
            'No trading execution changes.'
        )
        Approval = 'Trading and broker actions remain blocked even when this mode is selected.'
    }
    RETIRE_MODE = @{
        Allowed = @(
            'Run approved final DRY_RUN status checks.',
            'Prepare end-of-session summary text.',
            'Recommend a human checkpoint command.'
        )
        Blocked = @(
            'No shutdown automation.',
            'No startup setting changes.',
            'No git commit or push without approval.'
        )
        Approval = 'Human approval required before any file-writing report or git checkpoint.'
    }
    RETURN_TO_WORK_MODE = @{
        Allowed = @(
            'Confirm active repo path.',
            'Run approved DRY_RUN health checks.',
            'Review latest known checkpoint or report.'
        )
        Blocked = @(
            'No automatic resume actions.',
            'No app launch.',
            'No file edits before scoped approval.'
        )
        Approval = 'Human approval required before continuing APPLY work.'
    }
    MORNING_BRIEF_MODE = @{
        Allowed = @(
            'Print a text-only morning brief plan.',
            'Run approved DRY_RUN repo checks.',
            'List next safe actions.'
        )
        Blocked = @(
            'No browser launch.',
            'No app launch.',
            'No startup task changes.',
            'No uncontrolled evidence capture.'
        )
        Approval = 'Human approval required before any Morning Launch or file-writing action.'
    }
}

$selectedRules = $modeRules[$normalizedModeName]
Write-List -Title 'Allowed actions' -Items $selectedRules.Allowed
Write-Host ''
Write-List -Title 'Blocked actions' -Items $selectedRules.Blocked
Write-Host ''
Write-Host "Approval requirement: $($selectedRules.Approval)"
Write-Host 'Final summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO MODE ACTION EXECUTED.' -f [char]0x2014)
