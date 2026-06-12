CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

identity marker: Codex East local executor
supervisor identity: ChatGPT Personal
packet ID: AIOS-CLOUDFLARE-ACCESS-PROVIDER-SETUP-REVIEW-DRY-RUN-V1
mode: DRY_RUN
zone: Cloudflare Access / provider setup checklist / no provider changes
worker identity: Codex East
lane: cloudflare-access-provider-setup-review
worktree: C:\Dev\Ai.Os
branch: resolve after preflight
approval authority: Anthony / Human Owner
validator chain: git diff --check; JSON parse if JSON output is created; git status --short --branch
stop point: Stop after producing a Cloudflare provider setup checklist. Do not change Cloudflare, DNS, tunnels, dashboard exposure, providers, secrets, runtime, scheduler, queues, broker paths, or live trading.

explicit human approval:
Anthony approves a DRY_RUN review-only checklist lane for Cloudflare Access provider setup readiness. Anthony does not approve any provider dashboard change, Cloudflare configuration, Azure or Entra configuration, GitHub OAuth configuration, Google OAuth configuration, DNS change, tunnel change, dashboard exposure, secret handling, credential storage, runtime execution, queue mutation, scheduler mutation, broker action, live trading, direct push to main, merge, PR closure, or destructive cleanup.

mission:
Prepare the exact Cloudflare Access provider setup checklist needed before a future APPLY/provider-dashboard lane. The checklist must require Anthony approval before any provider dashboard change, store no secrets, use screenshots/manual confirmation only for provider UI state, and preserve the lockout-safe design.

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
2. If dirty files exist, classify whether they overlap this review lane before continuing.
3. If the repo is not `C:\Dev\Ai.Os`, stop.

evidence to read:
- AGENTS.md
- README.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_STACK_DESIGN.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_STACK_DESIGN.json
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IDENTITY_INVENTORY.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IDENTITY_INVENTORY.json
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IMPLEMENTATION_PLAN.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IMPLEMENTATION_PLAN.json

review requirements:
1. Prepare a Cloudflare Access provider setup checklist only.
2. Require Anthony approval before any provider dashboard change.
3. Require no secrets in repo.
4. Require screenshots/manual confirmation only for provider UI state.
5. Forbid DNS, tunnel, and dashboard exposure until Access policy is proven.
6. Forbid runtime, scheduler, queue, broker, and live trading changes.
7. Preserve at least two independent admin login paths.
8. Preserve local Omen fallback.
9. Preserve AI_OS app-role and approval-gate separation.
10. Mark unresolved identity inputs explicitly.

expected outputs:
- Reports/security/login/AIOS_CLOUDFLARE_ACCESS_PROVIDER_SETUP_REVIEW.md
- Reports/security/login/AIOS_CLOUDFLARE_ACCESS_PROVIDER_SETUP_REVIEW.json
- optional next proposed APPLY packet under `automation/orchestration/work_packets/proposed/`

validation:
Run:
```powershell
git diff --check
python -m json.tool Reports/security/login/AIOS_CLOUDFLARE_ACCESS_PROVIDER_SETUP_REVIEW.json
git status --short --branch
```

final report format:
SUMMARY:
CHECKLIST CREATED:
UNRESOLVED INPUTS:
FORBIDDEN ACTIONS CONFIRMED:
FILES CHANGED:
VALIDATION:
SAFE NEXT COMMAND:
STATUS: DRY_RUN PROVIDER SETUP REVIEW COMPLETE, NO PROVIDER CHANGES, NO SECRETS STORED

