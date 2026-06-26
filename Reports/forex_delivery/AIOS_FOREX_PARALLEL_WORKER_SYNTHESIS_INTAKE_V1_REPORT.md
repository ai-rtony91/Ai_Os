# AIOS Forex Parallel Worker Synthesis Intake V1

## Scope

This report prepares intake for merging active parallel Forex worker outputs into one final execution plan after the workers finish.

This is a reports-only synthesis artifact. It does not create governance authority, approve APPLY work, approve protected actions, approve live trading, or replace `AGENTS.md`, `RISK_POLICY.md`, or canonical workflow documents.

## Expected Input Reports

| Input | Expected evidence | Intake question |
| --- | --- | --- |
| EPC004 22H/6D augmentation | Report mapping the 22-hour and 6-day production-transition package additions, changed assumptions, and remaining gaps | Which additions directly improve final Forex delivery readiness? |
| Governance consolidation | Report consolidating applicable AIOS governance, packet, lane, approval, and protected-action rules | Which rules constrain the final execution plan and next packets? |
| Final gap analysis | Report listing remaining delivery gaps after current branch work and parallel reports are considered | Which gaps block execution, validation, or operator decision-making? |
| Report index classifier | Report classifying generated reports by type, authority status, maturity, and usefulness | Which reports should feed the final plan, and which are reference-only? |
| OANDA evidence spine | Report describing OANDA-related evidence, account/API constraints, paper-only status, and live blockers | What OANDA facts are proven, missing, or blocked? |
| Profitability evidence spine | Report organizing backtest, simulation, paper, or other profitability evidence | What profitability claims are evidence-backed versus speculative? |
| Demo readiness spine | Report defining demo readiness evidence, demo flow, operator-facing proof, and validation needs | What must be true before a demo can be called ready? |
| Live blocker spine | Report listing all blockers to live broker execution, live routing, real orders, secrets, or production mutation | What keeps live trading blocked, and which blockers are policy-level versus implementation-level? |
| Operator confidence spine | Report organizing operator-visible proof, confidence signals, decision points, and plain-language status | What will let Anthony decide the next action without manual reconstruction? |
| Branch preservation / merge prep | Report preserving current branch work, dirty-file context, merge risks, and PR-lane considerations | What must be protected before merge prep or cross-branch synthesis starts? |

## Duplicate Recommendation Comparison

Duplicate recommendations should be compared by substance, not wording.

Use this comparison order:

1. Normalize the recommendation into one action sentence.
2. Identify the evidence source that supports it.
3. Classify it as governance, evidence, implementation, validation, operator guidance, merge prep, or blocked live-trading scope.
4. Check whether another report recommends the same action with stronger evidence, narrower scope, or clearer validation.
5. Keep the strongest version and retain weaker versions only as supporting citations.

When two recommendations are duplicates, the surviving action should use the narrowest safe scope and the clearest validator. If one version requires APPLY and another only requires DRY_RUN, prefer the DRY_RUN version unless APPLY is required to unblock the next packet.

## ROI Ranking Method

Rank next packets by practical delivery return, not document volume.

Scoring dimensions:

| Dimension | Score 1 | Score 3 | Score 5 |
| --- | --- | --- | --- |
| Delivery impact | Nice-to-have cleanup | Improves readiness or clarity | Removes a direct blocker to final execution planning |
| Risk reduction | Minor wording improvement | Clarifies one policy, evidence, or merge risk | Prevents unsafe execution, duplicate authority, live-trading confusion, or branch loss |
| Evidence value | Adds reference context | Consolidates scattered evidence | Produces decision-grade proof for OANDA, profitability, demo, or blockers |
| Operator value | Internal-only improvement | Makes a decision easier | Gives Anthony a clear approve, reject, stop, or next-packet decision |
| Effort control | Broad or unclear scope | Moderate bounded scope | Small, exact, validator-backed packet |

Recommended packet priority:

1. Highest total score.
2. Highest blocker removal score if tied.
3. Narrowest safe allowed path if still tied.
4. DRY_RUN before APPLY when evidence is still incomplete.

## Conflict Detection

Flag a conflict when two reports disagree about:

| Conflict type | Detection rule | Required synthesis response |
| --- | --- | --- |
| Authority | One report treats a generated artifact as governance while another treats it as evidence only | Defer to `AGENTS.md` and canonical governance files; mark generated artifact as subordinate unless explicitly delegated |
| Trading safety | Any report implies live trading is allowed while another says paper-only or blocked | Treat live trading as blocked; defer to `RISK_POLICY.md` and require explicit Human Owner-approved exception |
| Branch state | Reports name different active branches, dirty states, or merge assumptions | Use current observed branch state at synthesis time; preserve dirty work before merge prep |
| Scope | One report recommends broad APPLY while another recommends narrow DRY_RUN | Prefer narrow DRY_RUN unless a validated blocker requires APPLY |
| Evidence | One report makes a profitability, readiness, or OANDA claim without evidence while another requires proof | Treat unsupported claims as unproven until source evidence is linked or reproduced |
| Packet order | Reports disagree on which work should happen next | Rank by blocker removal, operator value, validation readiness, and risk reduction |

Each conflict should produce one of these outcomes:

| Outcome | Meaning |
| --- | --- |
| Adopt | One conclusion is evidence-backed and governance-aligned |
| Merge | Conclusions are compatible and can become one action |
| Split | Conclusions require separate packets because scopes differ |
| Block | Conclusion cannot proceed without missing evidence, approval, or current-state verification |
| Reject | Conclusion conflicts with repo authority or safety policy |

## Final Action Queue Collapse

Collapse all worker outputs into one final action queue using this sequence:

1. Ingest all expected reports and record their file paths, branch assumptions, and stated status.
2. Extract every recommendation into a flat action list.
3. Tag each action by lane, risk tier, allowed path, validator, evidence source, and stop condition.
4. Remove duplicates using the duplicate comparison method above.
5. Resolve or block conflicts using the conflict detection table.
6. Promote only action-ready items into the final queue.
7. Keep evidence-only findings in a separate supporting section.
8. Rank queue items by ROI score.
9. Select the next 10 packet candidates using the decision rule below.
10. Stop before protected actions, commits, pushes, PR creation, merge, live trading, broker/API use, or secrets.

## Final Synthesis Table Template

| Rank | Proposed packet | Source reports | Problem solved | Mode | Allowed path scope | Risk tier | Evidence status | Validator chain | Conflict status | Stop point | Recommended outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 2 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 3 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 4 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 5 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 6 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 7 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 8 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 9 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |
| 10 |  |  |  | DRY_RUN or APPLY |  |  | Proven, partial, or missing |  | Adopt, merge, split, block, or reject |  | Execute, inspect, defer, or block |

## Recommended Decision Rule For The Next 10 Packets

Choose the next 10 packets by this rule:

1. First, select packets that remove final-plan blockers for paper-only Forex delivery.
2. Second, select packets that reconcile governance, authority, or branch-preservation conflicts.
3. Third, select packets that convert OANDA, profitability, demo readiness, live blocker, or operator confidence evidence into decision-grade summaries.
4. Fourth, select the smallest APPLY packets needed to update canonical or report artifacts after evidence is stable.
5. Exclude any packet that requires live trading, broker execution, secrets, direct push to `main`, merge, or production mutation unless a separate protected approval process exists.

Default next-packet shape:

| Packet slot | Preferred purpose | Preferred mode |
| --- | --- | --- |
| 1 | Final worker-output inventory and status readback | DRY_RUN |
| 2 | Duplicate recommendation collapse | DRY_RUN |
| 3 | Conflict matrix and authority reconciliation | DRY_RUN |
| 4 | OANDA and paper-only evidence synthesis | DRY_RUN |
| 5 | Profitability evidence synthesis | DRY_RUN |
| 6 | Demo readiness proof synthesis | DRY_RUN |
| 7 | Live blocker consolidation | DRY_RUN |
| 8 | Operator confidence decision card | DRY_RUN or reports-only APPLY |
| 9 | Branch preservation and PR-lane preparation | DRY_RUN |
| 10 | Final execution-plan packet generator | DRY_RUN before APPLY |

## Next Best Synthesis Packet

The next best synthesis packet is a read-only final worker-output inventory that verifies all expected reports exist, captures their branch assumptions, extracts their recommendations, and lists conflicts before any final action queue is generated.

Recommended packet name:

`AIOS-FOREX-PARALLEL-WORKER-FINAL-INVENTORY-AND-CONFLICT-MATRIX-V1`

Recommended mode:

`DRY_RUN`

Recommended safe stop point:

Report only; no file changes, no staging, no commit, no push, no PR, no merge, no broker/API use, no secrets, and no live trading.
