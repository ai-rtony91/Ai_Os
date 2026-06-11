CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

identity marker: Codex East local executor
supervisor identity: ChatGPT Personal
packet ID: AIOS-CLOUDFLARE-ACCESS-LOCKOUT-SAFE-LOGIN-INVENTORY-DRY-RUN-V1
mode: DRY_RUN
zone: Cloudflare Access / identity inventory / no provider changes
worker identity: Codex East
lane: login-security-stack-inventory
worktree: C:\Dev\Ai.Os
branch: resolve after preflight

explicit human approval:
Anthony approves a DRY_RUN inventory-only lane to collect non-secret identity, account ownership, recovery, and break-glass requirements for the AI_OS lockout-safe login/security stack. Anthony does not approve configuring Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, DNS, tunnels, dashboard exposure, secrets, credentials, runtime execution, queue mutation, scheduler mutation, broker action, live trading, commit, push, merge, PR closure, or destructive cleanup.

mission:
Collect the identity inventory needed before any Cloudflare Access, Microsoft/Entra, GitHub, Google, OTP, Turnstile, DNS, tunnel, or dashboard exposure work. Produce a review-only inventory report and a recommendation for the next design or implementation packet. Store no secrets.

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
- Do not expose the dashboard.
- Do not access, request, write, or store secrets.
- Do not edit `.env`.
- Do not mutate runtime, scheduler, queues, approval inbox, worker inbox, command queue, or active packets.
- Do not touch broker/live trading paths.
- Do not delete files.
- Do not commit.
- Do not push.
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
2. If dirty files exist, classify whether they overlap this inventory lane before continuing.
3. If the repo is not in `C:\Dev\Ai.Os`, stop.

evidence to read:
- AGENTS.md
- README.md
- docs/governance/AI_OS_REPO_MEMORY.md
- docs/governance/source-of-truth-map.md
- docs/governance/aios-identity-and-lane-governance.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_STACK_DESIGN.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_STACK_DESIGN.json

inventory requirements:
1. Collect Azure CLI identity with read-only CLI commands only:
   - current account user
   - tenant ID
   - subscription name
   - subscription ID if visible as non-secret metadata
   - default subscription flag
   - cloud name
2. Collect Azure Portal browser identity only by operator screenshot/manual input. Do not scrape browser session state and do not request passwords, tokens, cookies, MFA codes, client secrets, or refresh tokens.
3. Collect GitHub identity with read-only commands only:
   - `gh auth status` summary without tokens
   - `gh api user` login/id fields if available without exposing tokens
   - `git config user.name`
   - `git config user.email`
4. Collect Cloudflare account identity only by operator screenshot/manual input. Do not request or store Cloudflare API tokens, Turnstile secret keys, session cookies, recovery codes, or passwords.
5. Collect desired production account names:
   - Cloudflare admin account display name/email class
   - Microsoft/Entra primary admin account
   - GitHub backup operator identity
   - optional Google fallback identity
   - AI_OS app admin role name
   - AI_OS end-user role names
6. Collect recovery and break-glass requirements:
   - recovery email class, not password
   - break-glass account owner
   - independent recovery path
   - MFA/recovery separation requirement
   - emergency contact/process note
7. Store no secrets and no raw screenshots unless Anthony explicitly approves a sanitized evidence path in a later packet.

expected outputs:
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IDENTITY_INVENTORY.md
- Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IDENTITY_INVENTORY.json
- optional next proposed packet under `automation/orchestration/work_packets/proposed/`

validation:
Run:
```powershell
git diff --check
python -m json.tool Reports/security/login/AIOS_LOCKOUT_SAFE_LOGIN_IDENTITY_INVENTORY.json
git status --short --branch
```

stop point:
Stop after producing the identity inventory report and any next proposed packet. Do not configure Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, OTP, Turnstile, DNS, tunnels, dashboard exposure, provider dashboards, secrets, credentials, `.env`, runtime, scheduler, queues, approval inbox, worker inbox, command queue, broker paths, or live trading.

final report format:
SUMMARY:
IDENTITY INVENTORY COLLECTED:
RECOVERY FACTS:
LOCKOUT RISKS:
FILES CHANGED:
VALIDATION:
SAFE NEXT COMMAND:
STATUS: DRY_RUN INVENTORY COMPLETE, NO PROVIDER CHANGES, NO SECRETS STORED
