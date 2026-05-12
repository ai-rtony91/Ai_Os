# TradersPost Handoff Template Guide

The local handoff payload is a ready-format placeholder. It is not sent anywhere.

Required blocked fields:
- destination: `TradersPost_READY_FORMAT_ONLY`
- quantity_mode: `paper_placeholder`
- order_type: `market_placeholder`
- live_execution_status: `BLOCKED`
- broker_status: `NOT_CONNECTED`
- webhook_status: `NOT_SENT`
- reason: `AI_OS paper validation only`

The template exists so the operator can inspect the future handoff shape while AI_OS keeps delivery and execution blocked.
