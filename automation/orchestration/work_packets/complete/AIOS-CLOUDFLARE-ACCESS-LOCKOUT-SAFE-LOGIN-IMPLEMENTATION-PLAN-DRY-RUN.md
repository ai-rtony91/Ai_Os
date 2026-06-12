CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

identity marker: Codex East local executor
supervisor identity: ChatGPT Personal
packet ID: AIOS-CLOUDFLARE-ACCESS-LOCKOUT-SAFE-LOGIN-IMPLEMENTATION-PLAN-DRY-RUN-V1
mode: DRY_RUN
zone: Cloudflare Access / lockout-safe implementation planning / no provider changes
worker identity: Codex East
lane: login-security-stack-implementation-plan
worktree: C:\Dev\Ai.Os
branch: resolve after preflight

explicit human approval:
Anthony approves a DRY_RUN planning-only lane to convert the lockout-safe login design and identity inventory into a staged implementation plan. Anthony does not approve configuring Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, DNS, tunnels, Turnstile, OTP, dashboard exposure, secrets, credentials, runtime execution, queue mutation, scheduler mutation, broker action, live trading, direct push to main, merge, PR closure, or destructive cleanup.

mission:
Produce a provider-implementation plan and APPLY-packet sequence for the AI_OS lockout-safe login stack without making provider changes. The plan must preserve local Omen fallback, keep dashboard exposure blocked until Cloudflare Access is proven, separate login identity from AI_OS action authority, and store no secrets.

allowed repo write paths:
- Reports/security/login/
- automation/orchestration/work_packets/proposed/

forbidden write paths:
- .github/
- .git/
- .env
- secrets
- credentials
- telemetry/runtime/
- telemetry/night_supervisor/
- apps/dashboard/
- services/
- scripts/control/
- tools/android/
- apps/trading_lab/
- aios/modules/trader/
- automation/orchestration/work_packets/active/
- automation/orchestration/work_packets/blocked/
- automation/orchestration/work_packets/complete/
- automation/orchestration/workers/inbox/
- automation/orchestration/command_queue/
- automation/orchestration/approval_inbox/

forbidden actions:
- Do not configure Cloudflare.
- Do not configure Azure or Entra.
- Do not configure GitHub OAuth.
- Do not configure Google OAuth.
- Do not create or change DNS.
- Do not create or change tunnels.
- Do not configure Turnstile or OTP.
- Do not expose the dashboard.
- Do not access, request, write, or store secrets.
- Do not edit `.env`.
- Do not mutate runtime, scheduler, queues, approval inbox, worker inbox, command queue, or active packets.
- Do not touch broker/live trading paths.
- Do not delete files.
- Do not commit unless a future packet explicitly authorizes commit after validation.
- Do not push unless a future packet explicitly authorizes push after validation.
- Do not merge.
- Do not close PRs.

preflight:
1. Run:
   ```powershell
   cd C:\Dev\Ai.Os
   git status --short --branch
   git diff --check
   git branch --show-current
   git remote -v
   ```
2. If dirty files exist, classify whether they overlap this planning lane before continuing.
3. If the repo is not `C:\Dev\Ai.Os`, stop.

evidence to read:
- AGENTS.md
- README.md
- docs/governance/AI_OS_REPO_MEMORY.md
- docs/governance/source-of-truth-map.md
- docs/governance/aios-identity-and-lane-governance.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_STACK_DESIGN.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_STACK_DESIGN.json
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IDENTITY_INVENTORY.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IDENTITY_INVENTORY.json

planning requirements:
1. Define a staged provider implementation sequence with separate future APPLY packets for:
   - manual identity inventory completion.
   - Cloudflare account and Access application setup.
   - Microsoft/Entra primary login provider setup.
   - break-glass and recovery setup.
   - GitHub backup login setup.
   - optional Google fallback decision.
   - Cloudflare OTP emergency fallback decision.
   - Turnstile server-verification setup.
   - dashboard exposure proof gate.
2. For each future APPLY packet, define:
   - objective.
   - allowed provider surface.
   - required human approval.
   - required non-secret evidence.
   - required secret-handling rule.
   - validator chain.
   - rollback or stop condition.
   - exact stop point.
3. Keep Azure Portal identity, Cloudflare account identity, recovery email class, break-glass account details, optional Google fallback identity, subscription ID, and Azure cloud name marked unresolved until safely collected.
4. Preserve the rule that end users use their own identities and do not touch Anthony's Azure, Omen, GitHub admin, Cloudflare admin, repo, scheduler, runtime, broker, or secret-bearing identities.
5. Preserve the frontend compromise model:
   - frontend is untrusted.
   - no secrets in browser.
   - backend verifies session and role.
   - Turnstile token must be server-verified.
   - protected actions still require AI_OS approval gates.
6. Do not configure providers or store secrets.

expected outputs:
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IMPLEMENTATION_PLAN.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IMPLEMENTATION_PLAN.json
- optional future APPLY packet proposals under `automation/orchestration/work_packets/proposed/`

validation:
Run:
```powershell
git diff --check
python -m json.tool Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IMPLEMENTATION_PLAN.json
git status --short --branch
```

stop point:
Stop after producing the implementation plan and future packet sequence. Do not configure Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, OTP, Turnstile, DNS, tunnels, dashboard exposure, provider dashboards, secrets, credentials, `.env`, runtime, scheduler, queues, approval inbox, worker inbox, command queue, broker paths, or live trading.

final report format:
SUMMARY:
IMPLEMENTATION PLAN CREATED:
UNRESOLVED IDENTITY INPUTS:
LOCKOUT CONTROLS:
FILES CHANGED:
VALIDATION:
SAFE NEXT COMMAND:
STATUS: DRY_RUN IMPLEMENTATION PLAN COMPLETE, NO PROVIDER CHANGES, NO SECRETS STORED

