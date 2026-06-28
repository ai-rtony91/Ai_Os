# AIOS Forex Full Overnight Work Runner External Gate Stop V1

## Active Gate Stop Rules
- gate_id: OWNER_INPUT_REQUIRED
  reason: Owner action and attestation are required before repo-safe loop advances.
  owner_action_required: Supply owner_attestation and the requested action in host input.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True

- gate_id: BROKER_SNAPSHOT_REQUIRED
  reason: Flow 2 evidence workflow may require a supervisor-led broker snapshot.
  owner_action_required: Run Flow 2 packet and supply snapshot evidence package.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True

- gate_id: BROKER_CONNECTION_REQUIRED
  reason: Live exception path requires broker connection authorization outside this runner.
  owner_action_required: Prepare external broker-connection proof packet outside repo-safe runner.
  repo_safe_work_completed: False
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
  do_not_cross_inside_runner: True

- gate_id: CREDENTIAL_GATE_REQUIRED
  reason: Credential proof remains external to this packet.
  owner_action_required: Run external credential gate packet before live exception.
  repo_safe_work_completed: False
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
  do_not_cross_inside_runner: True

- gate_id: DEMO_EXECUTION_AUTHORITY_REQUIRED
  reason: Flow 2 supervised evidence remains owner-directed and not auto-executed.
  owner_action_required: Run Flow 2 evidence packet with owner supervision.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True

- gate_id: TRADE_EVIDENCE_REQUIRED
  reason: Trade evidence bundle is needed before Flow 3 readiness actions.
  owner_action_required: Supply evidence from supervised demo output packet.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True

- gate_id: REALIZED_PL_REQUIRED
  reason: Flow 3 readiness controls depend on realized P/L inputs.
  owner_action_required: Run follow-up evidence packet with realized P/L proof.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True

- gate_id: LIVE_EXCEPTION_REQUIRED
  reason: Live exception packet is an external bridge with explicit owner and policy gates.
  owner_action_required: Run AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1 when ready.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
  do_not_cross_inside_runner: True

- gate_id: REAL_MONEY_APPROVAL_REQUIRED
  reason: Capital transition cannot be inferred by repo-only automation.
  owner_action_required: Obtain explicit owner approval packet for live capital movement.
  repo_safe_work_completed: False
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1
  do_not_cross_inside_runner: True

- gate_id: RUNTIME_SUPERVISOR_REQUIRED
  reason: Runtime supervisor proof is required for sustained objective operation.
  owner_action_required: Run external runtime supervisor packet and return evidence.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True

- gate_id: SOS_ALERT_PROOF_REQUIRED
  reason: SOS alert proof must be externally asserted before gate crossing.
  owner_action_required: Collect SOS proof from escalation packet output.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True

- gate_id: VACATION_MODE_PROOF_REQUIRED
  reason: Vacation-mode target status cannot be set by runner alone.
  owner_action_required: Collect vacation-mode readiness proof packet.
  repo_safe_work_completed: True
  next_packet_after_gate: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
  do_not_cross_inside_runner: True
