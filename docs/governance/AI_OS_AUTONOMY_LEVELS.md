# AI_OS Autonomy Levels

## Purpose

AI_OS uses autonomy levels so low-risk read-only, report, and preview work can move faster without applying the same approval burden as high-risk execution.

These levels reduce overblocking. They do not weaken protected gates, human authority, validation requirements, branch protection, security policy, or trading safety.

This document aligns with the `AGENTS.md` blast-radius tiers:

- Tier 0 - READ_ONLY maps to Level 1 - AUTO READ-ONLY.
- Tier 1 - DRY_RUN PLAN maps to Level 1 when no files are written.
- Tier 2 - SANDBOX_OUTPUT maps to Level 2 - AUTO REPORT / PREVIEW FILES.
- Tier 3 - LOCAL_APPLY maps to Level 4 - APPROVED EXECUTION for exact local file changes.
- Tier 4 - PROMOTION / REPO AUTHORITY maps to Level 5 when authority or canonical promotion is involved.
- Tier 5 - PRODUCTION_OR_LIVE maps to Level 5 - HARD GATE.

Higher-tier requirements must not be applied to lower-risk work unless the task touches protected paths, protected actions, secrets, broker/API, live trading, production mutation, canonical authority, or irreversible repo operations.

## Default Posture

If the correct autonomy level is unclear, choose the lower and safer level.

Unknown, conflicting, stale, or incomplete evidence must be treated as review-required or blocked instead of being upgraded automatically.

## No Bypass Rule

Autonomy level does not override:

- `AGENTS.md`
- `README.md`
- security policy
- branch protection
- trading safety
- protected-path rules
- explicit packet scope
- human approval gates

Validator output, controller output, dashboard output, queue state, packet state, or report state is evidence only. It is not approval for protected action.

## Level 1 - AUTO READ-ONLY

Allowed automatically:

- repo status checks
- clean-state checks
- validator previews
- controller previews
- runtime bundle previews
- morning or overnight brief summaries
- stale packet detection
- blocked-state reporting

Blocked:

- file edits
- staging
- commit
- push
- PR creation
- merge
- secrets
- broker or trading actions

Level 1 work must remain inspection-only and must not write files, mutate queues, update approvals, launch workers, schedule tasks, or persist runtime state.

## Level 2 - AUTO REPORT / PREVIEW FILES

Allowed automatically only inside approved generated-output folders:

- write report files
- write preview files
- write telemetry summaries
- write DRY_RUN evidence files

Required:

- must not overwrite protected files
- must not alter source code
- must not create approvals
- must label output as generated, report, preview, or evidence
- must stay inside the approved generated-output path

Level 2 output is evidence. It must not become approval, source-of-truth authority, or execution authority.

## Level 3 - AUTO PREP

Allowed:

- prepare exact command previews
- prepare exact git add previews
- prepare exact commit message previews
- prepare exact push previews
- prepare exact PR create previews
- prepare validator recommendations

Blocked:

- executing those commands without approval
- staging files
- committing files
- pushing branches
- creating PRs
- merging PRs
- mutating approval records

Level 3 may reduce manual relay work by preparing exact commands, but the prepared command remains inert until the correct approval gate passes.

## Level 4 - APPROVED EXECUTION

Allowed only after explicit operator approval:

- stage exact named files
- commit exact approved files
- push exact approved branch
- create exact approved PR

Required approval markers:

- `APPROVE_COMMIT`
- `APPROVE_PUSH`
- `APPROVE_PR_CREATE`

Level 4 approval must name the exact action, scope, files or branch, expected validation, and stop point. Approval for one action does not imply approval for another.

Commit approval does not approve push. Push approval does not approve PR creation. PR creation approval does not approve merge.

## Level 5 - HARD GATE

Always protected:

- merge
- secrets
- credentials
- API keys
- broker integration
- OANDA
- live trading
- real webhooks
- real orders
- destructive repo actions
- branch protection changes
- governance authority changes

Level 5 actions always require separate explicit human approval and may need a dedicated packet.

Level 5 actions must not be downgraded by convenience, validator output, controller output, packet state, branch state, report output, or prior approval for a different action.

## Why This Exists

AI_OS should reduce unnecessary operator burden while keeping protected gates strong.

Read-only checks, generated evidence, previews, and exact command preparation can move faster when clearly separated from execution. Commit, push, PR creation, merge, secrets, API access, trading, broker, OANDA, webhook, destructive repo work, and governance authority changes remain protected.
