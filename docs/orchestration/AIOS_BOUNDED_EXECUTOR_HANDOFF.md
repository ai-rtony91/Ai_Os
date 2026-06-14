# AIOS Bounded Executor Handoff

`aios_bounded_executor_handoff.py` converts an `AIOS_NEXT_BUILD_PLAN.v1`
dictionary into a deterministic `AIOS_BOUNDED_EXECUTOR_HANDOFF.v1` contract.

The handoff is a preview contract only. It does not run subprocesses, write
files, mutate queues or approvals, dispatch workers, launch runtime, start a
scheduler or daemon, connect to brokers, use credentials, place real orders,
call webhooks, stage, commit, push, or merge.

For `forex_risk_controls`, the contract lists the exact bounded source, test,
documentation, and orchestration files a future human-approved APPLY packet may
touch. It also lists the pytest validator preview for that future packet.

Routes that stop or carry no component produce `handoff_status: stopped`.
Unsupported components produce `handoff_status: blocked` with
`reason_code: unsupported_component`.

This artifact advances the autonomy chain from:

```text
build -> test -> score/report -> decision -> next_build_plan
```

to:

```text
build -> test -> score/report -> decision -> next_build_plan -> bounded executor handoff
```

The next step is a separate, human-approved local executor packet that consumes
this handoff and applies only the allowlisted paper-only Forex risk-controls
build action.
