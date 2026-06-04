# AI_OS Dispatch Night Supervisor Gate

`NIGHT_SUPERVISOR_PREVIEW` is report-only. It cannot start runtime, write telemetry, write locks, write control state, write approval inbox state, resume Paper SOS, or launch a proof run.

`NIGHT_SUPERVISOR_RUNTIME_PENDING_APPROVAL` is not permission to start runtime. It means a later packet must supply explicit human approval, runtime context precheck, active-lock check, cycle check, stop point, and final clean-state verifier.

Any Night Supervisor runtime start request without separate human approval is blocked.

