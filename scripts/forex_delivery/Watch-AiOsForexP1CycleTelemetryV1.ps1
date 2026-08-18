param(
    [Parameter(Mandatory=$true)][string]$TelemetryPath
)

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
$freshness = if ($record.history_freshness_result -eq 'FRESH' -and $record.snapshot_freshness_result -eq 'FRESH') { 'FRESH' } elseif ($record.cycle_action -eq 'WAIT_FOR_DATA') { 'STALE' } else { 'UNAVAILABLE' }
$direction = if ($record.supertrend_direction) { $record.supertrend_direction } else { 'NONE' }
$rejection = if ($record.rejection_reasons) { ($record.rejection_reasons -join ',') } else { 'NONE' }
@(
    "🚀 RUN  PAPER_ONLY",
    "🔄 CYCLE $($record.cycle_number)/$($record.maximum_cycles)",
    "🎯 QUALIFYING unavailable/30",
    "🌐 DATA $freshness",
    "📈 DIRECTION $direction",
    "📏 ATR $($record.atr_actual)/$($record.minimum_atr)",
    "🕯 BODY $($record.candle_body_ratio)/$($record.minimum_candle_body_ratio)",
    "🎯 R:R $($record.reward_risk_actual)/$($record.minimum_reward_risk)",
    "💼 POSITION $($record.active_position_status)",
    "💰 PAPER P/L telemetry-only",
    "🚫 REJECTION $rejection",
    "🔐 PID $($record.runtime_pid) / LOCK $($record.lock_owner_identity)",
    "🛡 PAPER ONLY",
    "RUN AGE: session-local | CYCLE AGE: session-local | NEXT CYCLE: $($record.next_check_at_utc)",
    "M5 TIMER: unavailable | DATA AGE: $(Format-Age $record.history_age_seconds) | LOCK AGE: session-local"
) -join [Environment]::NewLine
