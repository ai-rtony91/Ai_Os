[CmdletBinding()]
param(
    [string]$ProfilePath = (Join-Path $PSScriptRoot "AIOS_ROBOT_HELPER_PROFILE.example.json")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$profile = Get-Content -Raw -LiteralPath $ProfilePath | ConvertFrom-Json
$preview = [ordered]@{
    schema = "AIOS_ROBOT_HELPER_PREVIEW.v1"
    mode = "DRY_RUN"
    display_preview = $profile.display_text
    voice_text_preview = $profile.voice_text
    audio_cue_label = $profile.audio_cue
    led_cue_label = $profile.led_cue
    movement_cue_label = $profile.movement_cue
    hardware_action = "BLOCKED"
    tts = "BLOCKED"
    wol = "BLOCKED"
    writes_performed = $false
    next_safe_action = $profile.next_safe_action
}
$preview | ConvertTo-Json -Depth 6
