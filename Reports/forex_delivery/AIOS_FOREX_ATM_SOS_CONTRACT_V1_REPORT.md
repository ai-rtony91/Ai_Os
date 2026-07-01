# AIOS Forex ATM SOS Contract V1 Report

Packet: AIOS-P26B

This contract is instruction-only. No money moved and no broker, bank, live, credential, order, or webhook path was used.

```json
{
  "bank_access_allowed": false,
  "contract": {
    "bank_access_allowed": false,
    "generated_at": "2026-07-01T09:51:01Z",
    "live_capital_action_authorized": false,
    "milestone": "ATM_MILESTONE",
    "min_profit_to_sweep_usd": 200.0,
    "money_movement_allowed": false,
    "owner_next_step": "[AIOS SOS - ATM MILESTONE REACHED]  #AIOS_SOS\nYour demo profit bucket tipped: $250.00 (threshold $200.00).\nTarget band 100-120% reached on baseline $1000.00.\nNOTHING HAS MOVED. This is an instruction, not an action.\n\nWHAT TO DO NEXT - reply with ONE:\n  APPROVE  -> AIOS logs an owner-reviewed withdrawal proposal (still no money moves;\n              it queues a proposal you action by hand at your broker/bank).\n  HOLD     -> keep compounding in-account; bucket keeps filling.\n  ADJUST   -> reply ADJUST <number> to set a new tip threshold in USD.\n\nNothing further happens until you reply. Money movement stays OFF by policy.\n",
    "profit_bucket_usd": 250.0,
    "schema": "aios.forex.atm_milestone_contract.v1",
    "sos_alert_integration_status": "SOS_CONTRACT_READY_FOR_FLOW2",
    "target_band": "100_TO_120_PERCENT",
    "tip_detected": true
  },
  "contract_status": "SOS_CONTRACT_READY_FOR_FLOW2",
  "followup_notes": [
    "F2: S3 may need a separate owned packet to honor this contract directly."
  ],
  "followups": [
    "F2"
  ],
  "live_capital_action_authorized": false,
  "message_rendered": true,
  "message_written": false,
  "mode": "APPLY",
  "money_movement_allowed": false,
  "notifier_plan": {
    "alert_level": "critical",
    "alert_message": "SOS policy requires escalation.; Critical severity was reported. Next safe action: Owner reviews APPROVE, HOLD, or ADJUST instruction. No money moves.",
    "alert_reason": "SOS policy requires escalation.; Critical severity was reported.",
    "alert_title": "AIOS SOS Local Alert - CRITICAL",
    "beep_plan_preview": {
      "enabled": false,
      "execution": "blocked_in_v1_preview_only",
      "pattern": "preview: three short beeps",
      "would_beep": true
    },
    "commands_executed": [],
    "detected_risks": {
      "broker_live_trading": false,
      "credentials": false,
      "destructive_action": false,
      "protected_action_attempt": false,
      "real_orders_or_webhooks": false,
      "stuck_loop_or_repeated_failure": false,
      "validator_failure_after_repair_budget": false
    },
    "detected_triggers": [
      {
        "id": "sos_required",
        "level": "warning",
        "reason": "SOS policy requires escalation."
      },
      {
        "id": "severity_critical",
        "level": "critical",
        "reason": "Critical severity was reported."
      }
    ],
    "external_notifications_blocked": false,
    "external_notifications_requested": false,
    "files_written": [],
    "next_safe_action": "Owner reviews APPROVE, HOLD, or ADJUST instruction. No money moves.",
    "notifier_status": "alert_ready",
    "rejection_reasons": [],
    "repeat_policy": {
      "mode": "preview_only_no_runtime_repeat",
      "repeat_allowed": false,
      "repeat_blocked": false,
      "repeat_requested": false
    },
    "safety": {
      "approval_mutation": false,
      "broker": false,
      "commands_executed": false,
      "credentials": false,
      "daemon_activation": false,
      "destructive_cleanup": false,
      "external_notifications_blocked": false,
      "external_services_woken": false,
      "files_written": false,
      "git_add": false,
      "git_commit": false,
      "git_push": false,
      "live_trading": false,
      "local_only": true,
      "merge": false,
      "mode": "LOCAL_PREVIEW_ONLY",
      "network_access_requested": false,
      "network_access_used": false,
      "powershell_notification_executed": false,
      "preview_only": true,
      "queue_mutation": false,
      "real_orders": false,
      "real_toast_executed": false,
      "real_webhooks": false,
      "reports_written": false,
      "scheduler_activation": false,
      "sound_played": false,
      "worker_dispatch": false
    },
    "schema": "AIOS_SOS_LOCAL_NOTIFIER.v1",
    "should_alert": true,
    "terminal_banner_preview": [
      "========================================",
      "AIOS SOS LOCAL ALERT PREVIEW",
      "LEVEL: CRITICAL",
      "TITLE: AIOS SOS Local Alert - CRITICAL",
      "REASON: SOS policy requires escalation.; Critical severity was reported.",
      "NEXT: Owner reviews APPROVE, HOLD, or ADJUST instruction. No money moves.",
      "PREVIEW ONLY: no toast, sound, network, file write, or PowerShell command was executed.",
      "========================================"
    ],
    "windows_toast_preview": {
      "command": null,
      "enabled": false,
      "execution": "blocked_in_v1_preview_only",
      "message": "SOS policy requires escalation.; Critical severity was reported. Next safe action: Owner reviews APPROVE, HOLD, or ADJUST instruction. No money moves.",
      "title": "AIOS SOS Local Alert - CRITICAL",
      "would_show": true
    }
  },
  "owner_ack_present": true,
  "report_written": false,
  "schema": "aios.forex.atm_milestone_contract.v1",
  "sos_routed_file_first": true,
  "sos_sent": false,
  "tip_detected": true
}
```
