\# AI\_OS DRY\_RUN Contract



\## Purpose



DRY\_RUN mode exists to guarantee safe preview execution without mutation, launch, routing, persistence, commit activity, or autonomous behavior.



DRY\_RUN must simulate only.



\---



\# DRY\_RUN Rules



A DRY\_RUN script must NEVER:



\- write files

\- modify files

\- delete files

\- launch workers

\- launch terminals

\- mutate queues

\- mutate runtime memory

\- route packets

\- create commits

\- push branches

\- open pull requests

\- invoke APPLY-only execution paths

\- perform hidden side effects



\---



\# Allowed DRY\_RUN Behavior



DRY\_RUN scripts MAY:



\- inspect state

\- validate topology

\- validate configuration

\- preview planned actions

\- generate report-only output

\- simulate routing

\- simulate mutation

\- print execution plans

\- emit WARN or STOP findings



\---



\# Required DRY\_RUN Output



Every DRY\_RUN script should clearly report:



\- mode

\- scope

\- inspected targets

\- simulated actions

\- validation findings

\- mutation risk

\- blocked dependencies

\- next safe action



\---



\# Fail-Closed Principle



If uncertainty exists:

\- STOP

\- do not mutate

\- require explicit APPLY approval



\---



\# Long-Term Goal



All AI\_OS DRY\_RUN scripts become:

\- deterministic

\- report-only

\- validator compatible

\- governance-safe

\- automation-safe

