\# AI\_OS Orchestration State Machine 001



\## Required Flow



QUEUED -> CLAIMED -> LOCKED -> RUNNING -> VALIDATING -> APPROVAL\_PENDING -> APPROVED -> COMMITTED -> COMPLETE



\## Failure Flow



FAILED -> RECOVERY\_REQUIRED

COLLISION -> RECOVERY\_REQUIRED

STALE\_LOCK -> RECOVERY\_REQUIRED

RECOVERY\_REQUIRED -> QUEUED



\## Hard Rules



\- No worker may edit files before CLAIMED.

\- No worker may edit files before LOCKED.

\- No work may commit before VALIDATING.

\- No work may commit before APPROVED.

\- Blocked paths may never be approved.

\- Failed validation must stop the workflow.



\## Blocked Paths



\- apps/

\- services/

\- core/

\- package.json

\- tsconfig.json

\- .git/

\- .codex\_backups/

\- broker/OANDA/API/live trading files



\## Production Goal



One safe automation loop:



task -> claim -> lock -> validate -> approve -> commit package -> report

