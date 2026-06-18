# AIOS Forex External Proof Requirements Checklist DRY_RUN V1

Status: DRY_RUN checklist report only. This report does not enable live trading, connect to a broker, request credentials, request account identifiers, load account identifiers, activate endpoints, submit orders, place trades, start schedulers, start daemons, deploy, stage, commit, push, open a PR, or merge.

## Packet Context

- Packet ID: `AIOS-FOREX-EXTERNAL-PROOF-REQUIREMENTS-CHECKLIST-DRY-RUN-V1`
- Lane: `forex-external-proof-requirements-checklist`
- Worktree: `C:\Dev\Ai.Os`
- Branch: `feature/forex-external-proof-requirements-checklist-dry-run-v1`
- Output: `Reports/forex_delivery/AIOS_FOREX_EXTERNAL_PROOF_REQUIREMENTS_CHECKLIST_DRY_RUN_V1.md`

## Current Authorization Status

Authorization status: `NO-GO_NOT_AUTHORIZED`

The first governed live micro-trade path is not reviewable yet. The current repo state has fail-closed readiness gates and safe evidence reports, but it is missing value-free external proof for credential handling, account handling, exact demo/practice broker context, live endpoint denial, protected connector boundaries, approval window, post-trade journal, and reconciliation.

No profitability claim is made. This report makes no claim about strategy edge, expected return, win rate, risk-adjusted return, or trade profitability.

## External Proof Checklist

Every item in this section is Human Owner external proof. Codex can document the required proof shape, but Codex must not request, reveal, store, log, or validate real values.

| External proof | Required value-free evidence | Status |
| --- | --- | --- |
| Credential storage proof | Sanitized statement that broker-demo credential material exists only outside the repo in an operator-controlled store or manual operator path. No values, screenshots, command history, or secret-manager output. | `EXTERNAL_REQUIRED` |
| Account-reference proof | Sanitized statement that account identifiers remain outside repo artifacts and are referenced only by value-free labels. No account ID, partial ID, masked screenshot, or private account data. | `EXTERNAL_REQUIRED` |
| Demo/practice broker context proof | Sanitized statement that the future context is demo/practice only and has no live funds authority. No endpoint value, account ID, credential value, market/account data, or broker payload. | `EXTERNAL_REQUIRED` |
| Live endpoint denial proof | Sanitized statement that live endpoint labels, live account labels, and live routing are absent or denied for the future review path. No endpoint value required. | `EXTERNAL_REQUIRED` |
| Revocation and rotation proof | Sanitized statement that credential revocation and rotation can be performed externally if exposure occurs. No credential value or external control-plane output. | `EXTERNAL_REQUIRED` |
| Protected connector boundary proof | Sanitized statement that any future connector is one-shot, Human Owner-approved, no-account/no-order/no-market-data, no-live, no raw payload, and stops after terminal result. | `EXTERNAL_REQUIRED` |
| Approval-window proof | Human Owner names start and expiry for the one-shot exception. No live action occurs from naming a window. | `EXTERNAL_REQUIRED` |
| Risk-scope proof | Human Owner names instrument, side, size/notional limit, maximum loss, daily loss cap, stop loss, and order type. This is approval-scope data, not execution authority. | `EXTERNAL_REQUIRED` |
| One-order proof | Human Owner confirms one order only, no retry loop, no autonomous re-entry, no second order, no martingale, and no averaging down. | `EXTERNAL_REQUIRED` |
| Kill-switch proof | Human Owner confirms operator can stop before broker call and deny order placement. | `EXTERNAL_REQUIRED` |
| Timeout proof | Human Owner confirms timeout and approval expiry terminal behavior. | `EXTERNAL_REQUIRED` |
| Final-disarm proof | Human Owner confirms the exception disarms after fill, rejection, error, timeout, expiry, or manual stop. | `EXTERNAL_REQUIRED` |
| Rollback proof | Human Owner confirms repo rollback reference, external credential revocation path, connector disablement path, and post-incident review path. No secret values. | `EXTERNAL_REQUIRED` |
| Post-trade journal proof | Human Owner confirms a sanitized journal path and fields for approved scope, terminal outcome, final disarm, and follow-up. | `EXTERNAL_REQUIRED` |
| Reconciliation proof | Human Owner confirms how external terminal result will be reconciled against repo-side sanitized evidence without account IDs, broker order IDs, or raw payloads. | `EXTERNAL_REQUIRED` |

## Repo-Completable Checklist

These items can be completed by repo-only DRY_RUN work without broker access, credentials, account IDs, endpoints, orders, trades, commits, pushes, or PRs.

| Repo-completable item | Output expected | Current path |
| --- | --- | --- |
| External proof checklist | This report. | `DONE_BY_THIS_PACKET` |
| Exception-specific proof matrix | A value-free matrix mapping each required proof to `FOUND`, `MISSING`, `EXTERNAL_REQUIRED`, or `BLOCKING`. | `NEXT_PACKET` |
| Approval package reviewable draft | Harden current draft into a package that can become `REVIEWABLE` only when required proof statuses are complete or explicitly blocked. | `PENDING` |
| Final arming packet checklist | DRY_RUN checklist for a future protected final arming packet, still no execution. | `PENDING` |
| Post-trade journal template | Sanitized template excluding credentials, account IDs, broker order IDs, raw payloads, private broker data, and screenshots. | `PENDING` |
| Reconciliation template | Sanitized template for matching external terminal result to approved scope without private data. | `PENDING` |
| Status transition rules | Explicit `NO-GO`, `REVIEWABLE`, `APPROVABLE`, and `ONE-SHOT LIVE MICRO-TRADE READY` transition conditions. | `PARTIAL`, from closure and approval package reports |

## Human Owner Action Checklist

Anthony Meza must decide or provide value-free evidence for:

1. Whether a one-shot Single Live Micro-Trade Exception should be reviewed at all.
2. Exact broker path reference, without repo-stored credentials or account identifiers.
3. Exact instrument, side, size/notional limit, maximum loss, daily loss cap, stop loss, and order type.
4. Exact approval window with start and expiry.
5. Confirmation that broker context is demo/practice proofed before live arming review.
6. Confirmation that credential values remain external and are never copied into repo, chat, reports, logs, tests, fixtures, screenshots, telemetry, or command history.
7. Confirmation that account identifiers remain external and are never copied into repo, chat, reports, logs, tests, fixtures, screenshots, telemetry, or command history.
8. Confirmation that live endpoint ambiguity is denied or blocked.
9. Confirmation that kill-switch, timeout, final-disarm, rollback, journal, and reconciliation proof can be attached without values.
10. Approval or rejection of the final review package after repo-completable proof mapping is done.

## Broker / Account Proof Requirements Without Exposing Values

Allowed proof shape:

- `external_broker_context_exists: true`
- `broker_context_type: demo_or_practice`
- `live_funds_reachable: false`
- `account_identifier_repo_exposure: false`
- `account_identifier_external_only: true`
- `account_reference_label: value-free label only`
- `operator_confirmation_recorded: true`

Forbidden proof material:

- Credential values.
- Account IDs.
- Partial account IDs.
- Masked account screenshots.
- Broker account profile exports.
- Broker order identifiers.
- Raw broker payloads.
- Private broker data.
- Live endpoint URLs or values unless already allowed by governance.
- Screenshots containing private data.

## Credential-Boundary Proof Requirements Without Exposing Values

Required value-free proof:

- Credential material is held outside the repo.
- Credential material is not copied into prompts, reports, logs, tests, fixtures, screenshots, telemetry, command history, `.env`, config, or source files.
- Future runtime reference uses labels only, not values.
- Revocation and rotation path exists outside the repo.
- Exposure response requires immediate stop, revocation, rotation, scan, and new Human Owner approval.

Forbidden proof material:

- API keys.
- Tokens.
- Passwords.
- Private keys.
- Secret-manager output.
- Password-manager screenshots.
- Environment variable values.
- Credential-bearing commands.
- Credential-bearing logs.

## Live-Endpoint Denial Proof Requirements

Required value-free proof:

- Live endpoint labels are absent or denied for the future exception review path.
- Practice/demo context is separated from live context.
- Any live endpoint ambiguity fails closed.
- Connector output containing live references is rejected.
- No live endpoint activation occurs before a separate protected final arming packet.

The proof must use abstract labels and booleans. It must not add endpoint values.

## Demo / Practice Broker Proof Requirements

Required value-free proof:

- Broker context is demo/practice before any live arming review.
- No live funds are reachable by the proposed path.
- No account ID is stored, logged, printed, or committed.
- No credential value is stored, logged, printed, or committed.
- No market data, account data, order data, or raw payload is copied into repo evidence.
- Protected connector, if ever reviewed, is one-shot and separately approved.

## Approval-Window Requirements

Required Human Owner fields:

- Approval start.
- Approval expiry.
- Expiry behavior: blocked after expiry.
- Timeout behavior: stop and disarm.
- Re-entry behavior: blocked.
- Retry behavior: blocked.
- Transferability: non-transferable.
- Scope: one order only.

The approval window must not imply execution authority. It becomes meaningful only inside a complete, approved, separately protected final arming packet.

## Protected Connector Proof Requirements

Required value-free proof:

- Connector use is separately approved.
- Connector is limited to one protected attempt.
- Connector has no order route.
- Connector has no trade route.
- Connector has no account-data route.
- Connector has no market-data route unless separately approved.
- Connector rejects credentials, account IDs, live endpoint labels, raw payloads, order data, and private broker data.
- Connector stops after success, rejection, error, timeout, or manual stop.
- Connector result is sanitized before any repo artifact is created.

## Post-Trade Journal And Reconciliation Proof Requirements

Post-trade journal proof must include a sanitized template for:

- Approved scope reference.
- Approval window reference.
- Pre-action checklist result.
- Terminal outcome.
- Final disarm result.
- Rollback or revocation action, if needed.
- Human Owner post-action review.

Reconciliation proof must include a sanitized template for:

- External terminal result status.
- Repo-side approved scope comparison.
- Mismatch handling.
- Final closeout status.

Forbidden journal and reconciliation content:

- Credentials.
- Account IDs.
- Broker order IDs.
- Raw broker payloads.
- Private account data.
- Screenshots with private data.
- Live execution payloads.

## Items That Can Be Completed Tonight

- Exception-specific proof matrix.
- Approval package reviewable draft.
- Final arming packet checklist.
- Post-trade journal template.
- Reconciliation template.
- Status transition rules.

These are repo-completable DRY_RUN items only. They do not require broker access and do not authorize execution.

## Items That Require External Broker / Account Access

- External credential storage proof without values.
- External account-reference proof without values.
- Demo/practice broker context proof.
- Live endpoint denial proof tied to the operator-held broker context.
- Protected connector proof tied to the operator-held context.
- Human Owner approval-window decision.
- External terminal result evidence after any future approved attempt.
- External reconciliation evidence after any future approved attempt.

## Exact Next Packet

`AIOS-FOREX-EXCEPTION-SPECIFIC-PROOF-MATRIX-DRY-RUN-V1`

Purpose: create a value-free matrix that maps each required live-arming proof item to its current status: `FOUND`, `MISSING`, `EXTERNAL_REQUIRED`, `REPO_COMPLETABLE`, or `BLOCKING`. The packet must not request credentials, request account IDs, connect to a broker, activate endpoints, submit orders, place trades, stage, commit, push, or open a PR.

## Required Safety Conclusions

- Live execution allowed: `False`
- Order submit allowed: `False`
- Broker request sent: `False`
- Network used: `False`
- Broker connection occurred in this packet: `False`
- Credential requested or used in this packet: `False`
- Account ID requested or exposed in this packet: `False`
- Order submitted in this packet: `False`
- Live trade occurred in this packet: `False`
- Profitability claim made: `False`

## Final Checklist Conclusion

Conclusion: `EXTERNAL_PROOF_REQUIREMENTS_DEFINED_NO_GO`

The remaining path is now separated into repo-completable DRY_RUN work and Human Owner external proof. AI_OS can continue tonight with the exception-specific proof matrix, but live authorization remains blocked until required external proofs and Human Owner approval exist without exposing values.
