# AIOS Forex External Gate Registry V1

## owner_input_gate
blocked_capability: Owner action acceptance is required before close-cycle continuation.
why_gate_blocks_end_to_end_completion: Without acceptance, safe enforce/proceed state is not established.
required_owner_input: overnight_action with acceptance booleans and owner_attestation.
required_external_evidence: None. Repo-safe evidence prepared by this contract.
safe_repo_work_completed: dependency order, contracts, and continuation ledger prepared.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: evaluate returns OVERNIGHT_CONTRACT_READY_TO_ENFORCE_FLOW2.
continuation_after_gate: Proceed directly to Flow 2 with host validation evidence.

## broker_snapshot_gate
blocked_capability: Flow 2 evidence bundle requires broker/demo snapshot.
why_gate_blocks_end_to_end_completion: Countdowns and contracts cannot update without snapshot input.
required_owner_input: Owner-supervised snapshot capture authority packet.
required_external_evidence: Broker snapshot artifact from supervised demo evidence packet.
safe_repo_work_completed: Flow 2 required inputs and outputs are defined.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 2 evidence_bundle output includes snapshot capture contract.
continuation_after_gate: Flow 2 evidence handoff transitions into Flow 3.

## broker_connection_gate
blocked_capability: Live exception contract cannot claim real-money readiness.
why_gate_blocks_end_to_end_completion: Proof bridge requires broker connection verification.
required_owner_input: Owner-approved broker connection packet and owner review.
required_external_evidence: Broker readiness evidence from dedicated gate packet.
safe_repo_work_completed: Live exception contract defines broker connection gate dependency.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
validator_to_confirm_gate_closed: Live exception contract checks broker_connection_gate status in evidence packet.
continuation_after_gate: Prepare live exception bridge handoff after proof.

## credential_gate
blocked_capability: Live credentials cannot be loaded in this packet.
why_gate_blocks_end_to_end_completion: No credential gate means live operations are not safe.
required_owner_input: Owner accepts credential vault review and policy control.
required_external_evidence: Credential gate handoff artifact from external packet.
safe_repo_work_completed: All external authorization flags are false.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
validator_to_confirm_gate_closed: Live exception contract remains not-authorized until external proof arrives.
continuation_after_gate: Cross into live exception packet after proof.

## supervised_demo_execution_gate
blocked_capability: Flow 2 cannot run without supervised demo execution.
why_gate_blocks_end_to_end_completion: Evidence-based promotion needs supervised evidence first.
required_owner_input: Owner attestation and supervision packet.
required_external_evidence: Supervised execution handoff artifact.
safe_repo_work_completed: Flow 2 contract and contract outputs are prepared.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 2 output contains evidence_bundle.
continuation_after_gate: Run Flow 2 handoff and move to candidate loop.

## trade_evidence_capture_gate
blocked_capability: No trade state evidence without trade packet execution.
why_gate_blocks_end_to_end_completion: Flow 3 classification requires trade evidence.
required_owner_input: Owner confirms evidence handoff readiness.
required_external_evidence: TP/SL, realized P/L, and trade state records.
safe_repo_work_completed: Flow 2 required outputs include evidence bundle and next_flow_handoff.
next_packet_to_cross_gate: AIOS_FOREX_FLOW_2
validator_to_confirm_gate_closed: Flow 2 contract lists evidence_bundle output.
continuation_after_gate: Generate countdown and classification state updates.

## realized_pl_capture_gate
blocked_capability: No realized P/L proof is available in this packet.
why_gate_blocks_end_to_end_completion: Profit loop readiness depends on closed trade P/L data.
required_owner_input: Owner confirms closed trade evidence and no duplicate order guard.
required_external_evidence: Close-result output from trusted read-only evidence packet.
safe_repo_work_completed: Realized PL capture contract included in Flow 2 dependencies.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 3 payload contains countdown_progress_update_contract.
continuation_after_gate: Flow 3 candidate and readiness contracts can proceed.

## profit_countdown_update_gate
blocked_capability: Countdown cannot update without post-trade evidence.
why_gate_blocks_end_to_end_completion: Progress controls need periodic post-trade updates.
required_owner_input: Owner review on no-runaway-exposure and duplicate checks.
required_external_evidence: Post-trade evidence bundle after Flow 2 run.
safe_repo_work_completed: Dependency output includes post_trade_countdown_update_contract.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 2 outputs include countdown_update.
continuation_after_gate: Flow 3 reads countdown_progress updates.

## flow3_candidate_selection_gate
blocked_capability: Candidate quality cannot update without score evidence.
why_gate_blocks_end_to_end_completion: Flow 3 result_classification depends on candidate scoring.
required_owner_input: Owner accepts candidate review handoff.
required_external_evidence: Flow 2 evidence bundle with candidate score inputs.
safe_repo_work_completed: Flow 3 outputs include candidate_update and next_candidate.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 3 contract validator reports next_candidate output.
continuation_after_gate: Prepare runtime and vacation readiness checks.

## live_exception_gate
blocked_capability: Live exception is an explicit external bridge.
why_gate_blocks_end_to_end_completion: No live capital execution without this bridge.
required_owner_input: Owner approves live exception checklist and governance packet.
required_external_evidence: Real-money gate evidence bundle.
safe_repo_work_completed: Live exception contract is prepared with false live authorization fields.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
validator_to_confirm_gate_closed: Live exception bridge status moves to real_money_readiness_bridge with proof.
continuation_after_gate: Owner and policy review before live exception handoff.

## real_money_gate
blocked_capability: Real money readiness is not authorized by this packet.
why_gate_blocks_end_to_end_completion: Targeted progress cannot claim real-money state without evidence.
required_owner_input: Owner approves capital transition criteria.
required_external_evidence: Evidence board and policy-ready packet.
safe_repo_work_completed: All external authorization flags are false.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
validator_to_confirm_gate_closed: Live exception contract real_money_authorized_by_this_contract remains false.
continuation_after_gate: Proceed only after proof packet and owner sign-off.

## runtime_supervisor_gate
blocked_capability: 22h/6d runtime readiness requires external supervisor proof.
why_gate_blocks_end_to_end_completion: Objective execution state is target-defined only.
required_owner_input: Owner confirms runtime controls and stop policy.
required_external_evidence: Runtime supervisor verification evidence.
safe_repo_work_completed: Flow 3 includes runtime_readiness_status output.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 3 outputs runtime_readiness_status.
continuation_after_gate: Proceed with readiness handoff.

## sos_alert_gate
blocked_capability: SOS contract requires escalation evidence.
why_gate_blocks_end_to_end_completion: Kill-switch escalation cannot be proven without SOS evidence.
required_owner_input: Owner review of pause/resume and SOS policy.
required_external_evidence: SOS escalation evidence and pause/resume handoff.
safe_repo_work_completed: sos_alert_contract_status is set to REQUIRED_GATE_PENDING.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 3 and runtime gate include sos readiness checks.
continuation_after_gate: Continue to candidate and runtime readiness.

## vacation_mode_gate
blocked_capability: Vacation-mode activation is a target state only.
why_gate_blocks_end_to_end_completion: This packet cannot activate vacation mode.
required_owner_input: Owner confirms vacation mode target intent and controls.
required_external_evidence: Vacation mode readiness packet evidence.
safe_repo_work_completed: vacation_mode_status set to TARGET_DEFINED_GATE_PENDING.
next_packet_to_cross_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
validator_to_confirm_gate_closed: Flow 3 outputs vacation_mode_readiness_status.
continuation_after_gate: Progress to readiness gate and bridge ledger.

## publish_clean_merge_gate
blocked_capability: Hosting and merge evidence has not run.
why_gate_blocks_end_to_end_completion: Packet cannot be considered landed without host validation.
required_owner_input: Owner runs validator and publish scripts.
required_external_evidence: VALIDATION_PASSED and PUBLISH_COMPLETE_CLEAN outputs.
safe_repo_work_completed: validate and publish scripts are written in script path.
next_packet_to_cross_gate: owner_publish_ready
validator_to_confirm_gate_closed: publish script output indicates clean merge handoff.
continuation_after_gate: Move to next report queue entry after merge.
