# AIOS Alert Self-Test v1 Report

- Packet: AIOS-P29
- Generated UTC: 2026-07-01T19:00:05Z
- Mode: DRY_RUN
- Status: channel_not_configured
- Config source: control/secrets/alert_channels.example.json
- Outbound only: True
- Money movement allowed: False
- Broker/OANDA allowed: False
- Send requested: False
- Dry-run only: True
- Network call allowed: False
- Auth token configured: False

## Safety Boundary

- This source stack is validation-only and does not send notifications.
- The default config path is the checked-in example config.
- The real alert_channels.json path is blocked by this harness.
- Real alert channel config remains gitignored and is not required for validation.

## Planned Alert Receipts

- tip: Dry-run verifies the TIP alert receipt that would map to the tip topic. Title=AIOS TEST - TIP; Priority=4; Topic=PUT_T***; Status=channel_not_configured.
- jackpot: Dry-run verifies the JACKPOT alert receipt that would map to the jackpot topic. Title=AIOS TEST - JACKPOT; Priority=5; Topic=PUT_J***; Status=channel_not_configured.
- reply: Dry-run verifies the REPLY alert receipt that would map to the reply topic. Title=AIOS TEST - REPLY; Priority=3; Topic=PUT_R***; Status=channel_not_configured.

## Receipt

```json
{
  "schema": "AIOS_ALERT_SELFTEST_RECEIPT.v1",
  "packet_id": "AIOS-P29",
  "generated_at_utc": "2026-07-01T19:00:05Z",
  "mode": "DRY_RUN",
  "status": "channel_not_configured",
  "config_source": "control/secrets/alert_channels.example.json",
  "ntfy_base_url": "https://ntfy.sh",
  "ntfy_auth_token_configured": false,
  "outbound_only": true,
  "money_movement_allowed": false,
  "broker_or_oanda_allowed": false,
  "send_requested": false,
  "dry_run_only": true,
  "network_call_allowed": false,
  "channels": [
    {
      "channel": "tip",
      "topic_masked": "PUT_T***",
      "title": "AIOS TEST - TIP",
      "priority": 4,
      "planned": false,
      "sent": false,
      "http_status": null,
      "failed_closed": true,
      "status": "channel_not_configured",
      "what_you_should_hear": "Dry-run verifies the TIP alert receipt that would map to the tip topic."
    },
    {
      "channel": "jackpot",
      "topic_masked": "PUT_J***",
      "title": "AIOS TEST - JACKPOT",
      "priority": 5,
      "planned": false,
      "sent": false,
      "http_status": null,
      "failed_closed": true,
      "status": "channel_not_configured",
      "what_you_should_hear": "Dry-run verifies the JACKPOT alert receipt that would map to the jackpot topic."
    },
    {
      "channel": "reply",
      "topic_masked": "PUT_R***",
      "title": "AIOS TEST - REPLY",
      "priority": 3,
      "planned": false,
      "sent": false,
      "http_status": null,
      "failed_closed": true,
      "status": "channel_not_configured",
      "what_you_should_hear": "Dry-run verifies the REPLY alert receipt that would map to the reply topic."
    }
  ]
}
```
