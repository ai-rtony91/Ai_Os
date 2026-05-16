param(
    [object]$Lane,
    [string]$LaneJsonBase64
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

if ($null -eq $Lane -and -not [string]::IsNullOrWhiteSpace($LaneJsonBase64)) {
    $laneJson = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($LaneJsonBase64))
    $Lane = $laneJson | ConvertFrom-Json
}

if ($null -eq $Lane) {
    throw "Lane object is required."
}

@("lane_id", "display_title", "window_title", "tab_title", "emoji_marker", "path", "branch", "truth_source") | ForEach-Object {
    $field = $_
    if (-not ($Lane.PSObject.Properties.Name -contains $field)) {
        throw "Lane object missing field: $field"
    }
}

$Host.UI.RawUI.WindowTitle = $Lane.window_title
$escape = [char]27
$bell = [char]7
Write-Host -NoNewline ("$escape]0;$($Lane.tab_title)$bell")

Write-Host "ACTIVE LANE:" -ForegroundColor Cyan
Write-Host "$($Lane.emoji_marker) $($Lane.display_title)" -ForegroundColor Cyan
Write-Host "lane_id: $($Lane.lane_id)"
Write-Host "display_title: $($Lane.display_title)"
Write-Host "path: $($Lane.path)"
Write-Host "branch: $($Lane.branch)"
Write-Host "truth_source: $($Lane.truth_source)"
