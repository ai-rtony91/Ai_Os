# AIOS Forex Uptime Range Planner 80 22/5 22/6 V1

## Uptime Range Status
`UPTIME_RANGE_PLANNING_ONLY`

## Planning Modes
- `UPTIME_80_PLANNING`
- `RANGE_BLOCKED_BY_EVIDENCE`

## Inputs
| Field | Value |
|---|---|
| trading_hours_per_day | `0.0` |
| trading_days_per_week | `0.0` |
| maintenance_hours_per_day | `0.0` |
| requested_range | `UNSPECIFIED` |
| broker_session_proof | `MISSING` |
| market_session_proof | `MISSING` |
| incident_stop_proof | `MISSING` |
| monitoring_proof | `MISSING` |
| reconciliation_proof | `MISSING` |

## Calculations
| Field | Value |
|---|---|
| trading_hours_per_week | `0.0` |
| maintenance_hours_per_week | `0.0` |
| minimum_maintenance_budget | `168.0` |
| blocked_windows | `('BROKER_MAINTENANCE',)` |
| review_windows | `('DAILY_RISK_REVIEW', 'WEEKLY_RECONCILIATION_REVIEW')` |
| incident_recovery_windows | `('INCIDENT_STOP_RECOVERY',)` |

## Readiness Gates
| Field | Value |
|---|---|
| broker_session_proof | `False` |
| market_session_proof | `False` |
| incident_stop_proof | `False` |
| monitoring_proof | `False` |
| reconciliation_proof | `False` |
| live_evidence_proof | `False` |
| human_approval_proof | `False` |

## Blocked Reasons
- `broker_session_proof_missing_or_unproven`
- `market_session_proof_missing_or_unproven`
- `incident_stop_proof_missing_or_unproven`
- `monitoring_proof_missing_or_unproven`
- `reconciliation_proof_missing_or_unproven`

## Range Doctrine
- 22/6 is requested planning only unless broker/session evidence proves the instrument and operating window support it.
- 22/5 remains planning only unless all readiness gates pass.
- 80 percent uptime remains planning only unless all readiness gates pass.
- AIOS must calculate allowed trading range from evidence and broker/session rules instead of hardcoding 22/6.

## Activation Status
| Field | Value |
|---|---|
| uptime_80_activated | `False` |
| range_22_5_activated | `False` |
| range_22_6_activated | `False` |
| automated_trading_activated | `False` |

## Safety
| Field | Value |
|---|---|
| broker_api_called | `False` |
| network_call_performed | `False` |
| credentials_read | `False` |
| account_identifiers_read | `False` |
| env_read | `False` |
| secret_files_read | `False` |
| scheduler_started | `False` |
| daemon_started | `False` |
| webhook_started | `False` |
| uptime_80_activated | `False` |
| range_22_5_activated | `False` |
| range_22_6_activated | `False` |
| automated_trading_activated | `False` |
