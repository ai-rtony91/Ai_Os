# AI_OS Workflow Orchestrator V1

## Purpose

The AI_OS Workflow Orchestrator connects the operator workflow into one readable packet so the operator does not have to manually copy and paste every small status check.

It is DRY_RUN and operator-approved only. Every APPLY, commit, or push action still requires explicit operator approval. It does not APPLY changes, stage files, commit, push, connect to brokers, use API keys, store secrets, or enable live trading.

## Connected Inputs

The orchestrator reads these local files when they exist:

- worker registry: `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json`
- work queue: `apps/dashboard/mock-data/work-intelligence-queue-v1.example.json`
- approval inbox: `apps/dashboard/mock-data/aios-approval-inbox-v1.example.json`
- validator chain: `apps/dashboard/mock-data/aios-validator-chain-v1.example.json`
- controlled APPLY queue: `automation/operator/AIOS_CONTROLLED_APPLY_QUEUE.example.json`
- commit package: `automation/operator/AIOS_PHASE_27_COMMIT_PACKAGE.example.json`
- worker reports: `Reports/operator/worker-reports`
- current git status: `git status --short --branch`

## Output

The orchestrator writes one operator packet:

```text
Reports/operator/AIOS_OPERATOR_NEXT_ACTION_PACKET.md
```

The packet shows:

- current repo status
- active worker lanes
- work queue items
- DRY_RUN report collection status
- pending approvals
- validation status
- blocked reasons
- next safe action
- exact files ready for APPLY or commit if any are declared by the source fixtures

## Safety Boundary

The orchestrator is not an APPLY lane. It only reports what the next safe action should be.

APPLY remains blocked unless the operator explicitly approves the exact files and scope.

Commit remains blocked unless the operator explicitly approves the exact commit package.

Push remains blocked unless the operator explicitly approves the push after validation and commit review.

The orchestrator must not use `git add .`.

## How To Run

From the active repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1
```

Then review:

```text
Reports/operator/AIOS_OPERATOR_NEXT_ACTION_PACKET.md
```

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsWorkflowOrchestrator.DRY_RUN.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1
git diff --check
git status --short --branch
```

Expected result:

- validator passes
- operator packet is created
- no APPLY is performed
- no commit is performed
- no push is performed
- no broker, secret, API key, or live trading action is performed
