# Phase 18.13-18.18 Stage Map

| Phase | Stage | Status | Execution boundary |
| --- | --- | --- | --- |
| 18.13 | Dispatcher to Night Supervisor preview | `PREVIEW_ONLY` | No runtime start, no writes. |
| 18.14 | Corrected Paper SOS resume packet | `DRAFT_ONLY` | Fails closed unless runtime context matches `C:\Dev\aios-paper-sos-runtime-closeout`. |
| 18.15 | Controlled Night Supervisor run | `FUTURE_BOUNDARY_ONLY` | One cycle or max 10 minutes, not 12h. |
| 18.16 | Controlled run review | `FUTURE_TEMPLATE_ONLY` | Red-team and failure review before any longer run. |
| 18.17 | Longer supervised run | `FUTURE_BOUNDARY_ONLY` | 1-2 hours, operator available, not all night. |
| 18.18 | Full overnight candidate | `CANDIDATE_CRITERIA_ONLY` | Requires all prior gates and explicit approval. |

All stages preserve `TRUSTED_PROVEN_PROFITABILITY`.

