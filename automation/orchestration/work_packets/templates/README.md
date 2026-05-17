# AIOS Job Automation Packets

Automation packets turn an operator goal into a controlled unit of work that AIOS can inspect, report on, and recommend next commands for.

## Operator Workflow

1. Capture the goal, trigger, inputs, and manual steps that should be reduced.
2. Define allowed actions and blocked actions before any script runs.
3. Keep packet status visible through runtime reports and next-command recommendations.
4. Run DRY_RUN validators first unless the packet explicitly has operator approval for APPLY.
5. Record the next recommended command so Anthony can continue from the same point later.

## Approval Boundaries

Packets must keep dangerous actions explicit. Secrets, live trading, broker execution, external sends, deletes, commits, pushes, startup task changes, and scheduled task changes require separate operator approval.

## DRY_RUN vs APPLY

DRY_RUN means inspect, report, and validate only. APPLY means create or edit only the files approved for that packet. A packet may recommend an APPLY command, but AIOS must not run it automatically.
