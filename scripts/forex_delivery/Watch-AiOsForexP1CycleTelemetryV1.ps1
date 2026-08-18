param(
    [Parameter(Mandatory=$true)][string]$TelemetryPath
)
$ErrorActionPreference = "Stop"

# Read-only monitor: it reads JSONL only and never opens a network/process-control path.
function Format-Age([Nullable[double]]$Seconds) {
    if ($null -eq $Seconds) { return 'UNKNOWN' }
    $value = [Math]::Max(0, [int][Math]::Floor($Seconds))
    if ($value -lt 60) { return ('{0}s' -f $value) }
    $span = [TimeSpan]::FromSeconds($value)
    if ($value -lt 3600) { return ('{0:00}:{1:00}' -f [int]$span.TotalMinutes, $span.Seconds) }
    if ($value -lt 86400) { return ('{0:00}:{1:00}:{2:00}' -f [int]$span.TotalHours, $span.Minutes, $span.Seconds) }
    return ('{0}d {1:00}:{2:00}:{3:00}' -f [int]$span.TotalDays, $span.Hours, $span.Minutes, $span.Seconds)
}
$line = Get-Content -LiteralPath $TelemetryPath -Tail 1 -ErrorAction Stop
$record = $line | ConvertFrom-Json
$rocket = [char]::ConvertFromUtf32(0x1F680)
$cycle = [char]::ConvertFromUtf32(0x1F504)
$target = [char]::ConvertFromUtf32(0x1F3AF)
$globe = [char]::ConvertFromUtf32(0x1F310)
$chart = [char]::ConvertFromUtf32(0x1F4C8)
$ruler = [char]::ConvertFromUtf32(0x1F4CF)
$candle = [char]::ConvertFromUtf32(0x1F56F)
$briefcase = [char]::ConvertFromUtf32(0x1F4BC)
$money = [char]::ConvertFromUtf32(0x1F4B0)
$stop = [char]::ConvertFromUtf32(0x1F6AB)
$lock = [char]::ConvertFromUtf32(0x1F510)
$shield = [char]::ConvertFromUtf32(0x1F6E1)
$freshness = if ($record.history_freshness_result -eq 'FRESH' -and $record.snapshot_freshness_result -eq 'FRESH') { 'FRESH' } elseif ($record.cycle_action -eq 'WAIT_FOR_DATA') { 'STALE' } else { 'UNAVAILABLE' }
$direction = if ($record.supertrend_direction) { $record.supertrend_direction } else { 'NONE' }
$rejection = if ($record.rejection_reasons) { ($record.rejection_reasons -join ',') } else { 'NONE' }
@(
    "$rocket RUN  PAPER_ONLY",
    "$cycle CYCLE $($record.cycle_number)/$($record.maximum_cycles)",
    "$target QUALIFYING unavailable/30",
    "$globe DATA $freshness",
    "$chart DIRECTION $direction",
    "$ruler ATR $($record.atr_actual)/$($record.minimum_atr)",
    "$candle BODY $($record.candle_body_ratio)/$($record.minimum_candle_body_ratio)",
    "$target R:R $($record.reward_risk_actual)/$($record.minimum_reward_risk)",
    "$briefcase POSITION $($record.active_position_status)",
    "$money PAPER P/L telemetry-only",
    "$stop REJECTION $rejection",
    "$lock PID $($record.runtime_pid) / LOCK $($record.lock_owner_identity)",
    "$shield PAPER ONLY",
    "RUN AGE: session-local | CYCLE AGE: session-local | NEXT CYCLE: $($record.next_check_at_utc)",
    "M5 TIMER: unavailable | DATA AGE: $(Format-Age $record.history_age_seconds) | LOCK AGE: session-local"
) -join [Environment]::NewLine
