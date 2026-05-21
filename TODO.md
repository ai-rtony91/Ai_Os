\# AI\_OS\_V2 TODO



\## GOVERNANCE HARDENING



\- \[ ] Wire Invoke-AiOsExecutionRegistryGuard.ps1 into VALIDATOR\_CHAIN\_001.json

\- \[ ] Reduce STOP findings from 106 -> under 75

\- \[ ] Reclassify remaining REVIEW\_REQUIRED scripts

\- \[ ] Audit all launcher\_references\_blocked\_script findings

\- \[ ] Quarantine unsafe runtime/supervisor paths

\- \[ ] Repair DRY\_RUN scripts that mutate files

\- \[ ] Remove legacy CLEAN repo assumptions

\- \[ ] Validate ACTIVE trust boundary remains minimal



\- \[ ] Add execution registry guard into validator chain config

\- \[ ] Create VALIDATOR\_CHAIN\_002 governed flow

\- \[ ] Define validator execution order

\- \[ ] Separate report-only validators from mutation-capable validators

\- \[ ] Add validator severity levels (INFO/WARN/STOP)

\- \[ ] Create validator output normalization standard





\## VALIDATOR CHAIN



\- \[ ] Confirm validator execution order

\- \[ ] Ensure report-only validators cannot mutate state

\- \[ ] Add execution registry guard to governed validator flow

\- \[ ] Validate chain output formatting consistency



\- \[ ] Wire Invoke-AiOsExecutionRegistryGuard.ps1 into VALIDATOR\_CHAIN\_001.json

\- \[ ] Ensure execution registry guard runs before topology guard

\- \[ ] Define validator fail-closed behavior

\- \[ ] Add validator chain rollback strategy

\- \[ ] Define validator execution timeout policy





\## TERMINAL WORKSTATIONS



\- \[ ] Audit Start-AiOsWorktreeLanes.ps1

\- \[ ] Register remaining workstation helpers

\- \[ ] Remove retired lane references

\- \[ ] Standardize workstation launcher behavior



\## WORKER SAFETY



\- \[ ] Audit worker loop execution paths

\- \[ ] Audit inbox mutation paths

\- \[ ] Audit runtime routing paths

\- \[ ] Identify autonomous execution risks

\- \[ ] Restrict unsafe worker escalation paths



\## DOCUMENTATION



\- \[ ] Align AGENTS.md with execution registry

\- \[ ] Document ACTIVE vs HELPER authority model

\- \[ ] Create validator chain architecture diagram

\- \[ ] Create execution governance flow documentation



\## PHASE TARGET



Goal:

Stable governed orchestration layer with trusted validator chain and controlled execution boundaries before expanding autonomous worker/runtime systems.

