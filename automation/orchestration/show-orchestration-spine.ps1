Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$spinePath = Join-Path $orchestrationRoot "orchestration_spine_v1.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-List {
    param(
        [Parameter(Mandatory = $true)]
        [object[]]$Items
    )

    if ($Items.Count -eq 0) {
        Write-Host "    - None"
        return
    }

    foreach ($item in $Items) {
        Write-Host "    - $item"
    }
}

$spine = Read-JsonFile -Path $spinePath
$sections = @($spine.spine_sections)
$nextSafeAction = $spine.next_safe_action

Write-Host "AI_OS Orchestration Spine v1 Display"
Write-Host "Mode: $($spine.mode)"
Write-Host "Spine: $($spine.spine_name)"
Write-Host "Purpose: $($spine.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No workers, validators, packets, startup tasks, or scheduled tasks are launched."
Write-Host ""

if ($sections.Count -eq 0) {
    Write-Host "Spine sections: none found in orchestration_spine_v1.example.json"
    exit 0
}

Write-Host "Spine summary:"
Write-Host "  Total sections: $($sections.Count)"
Write-Host "  Display-ready sections: $(@($sections | Where-Object { $_.status -eq 'display_ready' }).Count)"
Write-Host "  Blocked/display-only sections: $(@($sections | Where-Object { $_.status -ne 'display_ready' }).Count)"
Write-Host ""

Write-Host "Spine order:"
foreach ($section in ($sections | Sort-Object order)) {
    Write-Host "  $($section.order). $($section.section_name) [$($section.status)]"
}
Write-Host ""

foreach ($section in ($sections | Sort-Object order)) {
    Write-Host "$($section.order). $($section.section_name)"
    Write-Host "  ID: $($section.section_id)"
    Write-Host "  Status: $($section.status)"
    Write-Host "  Source example: $($section.source_example)"
    Write-Host "  Purpose: $($section.plain_english_purpose)"
    Write-Host "  Allowed display actions:"
    Write-List -Items @($section.allowed_actions)
    Write-Host "  Blocked actions:"
    Write-List -Items @($section.blocked_actions)
    Write-Host "  Next safe action: $($section.next_safe_action)"
    Write-Host ""
}

Write-Host "Global safety rules:"
Write-List -Items @($spine.global_safety_rules)
Write-Host ""

Write-Host "Next safe action:"
Write-Host "  Action: $($nextSafeAction.action)"
Write-Host "  Command: $($nextSafeAction.command)"
Write-Host "  Stop condition: $($nextSafeAction.stop_condition)"
Write-Host ""

Write-Host "Next safe action: review this display and git status before any separate APPLY, commit, or push approval."
