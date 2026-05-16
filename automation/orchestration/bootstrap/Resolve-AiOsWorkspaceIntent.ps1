param(
    [string]$Intent = "",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Add-UniqueValue {
    param(
        [System.Collections.ArrayList]$List,
        [Parameter(Mandatory = $true)][string]$Value
    )

    if (-not $List.Contains($Value)) {
        [void]$List.Add($Value)
    }
}

$scriptName = Split-Path -Leaf $PSCommandPath
$normalizedIntent = if ([string]::IsNullOrWhiteSpace($Intent)) { "" } else { $Intent.Trim() }
$searchIntent = $normalizedIntent.ToLowerInvariant()

$selectedLaneIds = [System.Collections.ArrayList]::new()
$manualCodexLaneIds = [System.Collections.ArrayList]::new()
$validatorsSuggested = [System.Collections.ArrayList]::new()

Add-UniqueValue -List $selectedLaneIds -Value "main_control"

if ($searchIntent -match "\b(queue|dispatcher|packet|routing|route|dispatch|brainstem|daily|start)\b") {
    Add-UniqueValue -List $selectedLaneIds -Value "route_dispatch"
    Add-UniqueValue -List $selectedLaneIds -Value "watch_state"
    Add-UniqueValue -List $validatorsSuggested -Value "Route and watch preview"
}

if ($searchIntent -match "\b(validation|validator|audit|cleanup|check|supervisor|daily|start|brainstem)\b") {
    Add-UniqueValue -List $selectedLaneIds -Value "check_audit"
    Add-UniqueValue -List $validatorsSuggested -Value "Workspace DRY_RUN validator"
}

if ($searchIntent -match "\b(bootstrap|workspace|lane|window|session|daily|start|brainstem)\b") {
    Add-UniqueValue -List $selectedLaneIds -Value "save_git"
    Add-UniqueValue -List $validatorsSuggested -Value "Workspace bootstrap preview"
}

if ($searchIntent -match "\b(codex|edit|feature|implement)\b") {
    Add-UniqueValue -List $selectedLaneIds -Value "create_codex"
    Add-UniqueValue -List $manualCodexLaneIds -Value "create_codex"
    Add-UniqueValue -List $validatorsSuggested -Value "Run relevant validators after manual assistant edits"
}

if ($searchIntent -match "\b(rulebook|operator|rules|memory|instructions|brainstem)\b") {
    Add-UniqueValue -List $selectedLaneIds -Value "rulebook_codex"
    Add-UniqueValue -List $manualCodexLaneIds -Value "rulebook_codex"
    Add-UniqueValue -List $validatorsSuggested -Value "Workspace bootstrap preview"
}

if ($selectedLaneIds.Count -eq 1) {
    Add-UniqueValue -List $selectedLaneIds -Value "save_git"
    Add-UniqueValue -List $validatorsSuggested -Value "Workspace bootstrap preview"
}

if ($validatorsSuggested.Count -eq 0) {
    Add-UniqueValue -List $validatorsSuggested -Value "Workspace bootstrap preview"
}

$result = [pscustomobject]@{
    intent = if ([string]::IsNullOrWhiteSpace($normalizedIntent)) { "default fallback" } else { $normalizedIntent }
    selected_lane_ids = @($selectedLaneIds)
    manual_codex_lane_ids = @($manualCodexLaneIds)
    validators_suggested = @($validatorsSuggested)
    next_safe_action = "Review preview output, confirm selected lanes, then rerun with -LaunchManualShells only if correct."
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 5
    exit 0
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Workspace Intent Resolver" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Intent: $($result.intent)"
Write-Host ""
Write-Host "Selected lanes:"
@($result.selected_lane_ids) | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Manual Codex lane ids:"
if (@($result.manual_codex_lane_ids).Count -eq 0) {
    Write-Host "  NONE"
} else {
    @($result.manual_codex_lane_ids) | ForEach-Object { Write-Host "  $_" }
}
Write-Host ""
Write-Host "Validators suggested:"
@($result.validators_suggested) | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Next safe action: $($result.next_safe_action)"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")

