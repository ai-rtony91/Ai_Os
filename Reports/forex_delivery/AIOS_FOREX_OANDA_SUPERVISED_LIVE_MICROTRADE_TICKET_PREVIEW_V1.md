# AIOS Forex OANDA Supervised Live Microtrade Ticket Preview V1

## Purpose

Create a sanitized non-executing ticket preview for one tiny supervised live microtrade.

## Preview

- Sanitized local ticket id only.
- Instrument: `EUR_USD`
- Direction: `long`
- Order type: `market_owner_manual`
- Planned units: `1`
- Max units: `1`
- Planned max loss: `1.00`
- Planned stop distance: `0.0010`
- Planned take-profit distance: `0.0015`
- Planned R risk: `1.00`
- One-shot only.
- No compounding.
- No bank movement.
- No autonomous loop.
- Owner final approval required.
- Preview only.
- No profit guarantee.
- No live approval.

## Forbidden Ticket Values

- No account ID.
- No credential value.
- No endpoint.
- No raw broker payload.
- No broker order ID.
- No executable order function.

## Boundary

No trade placed by this packet.
No broker call was made by this packet.
No live approval was granted.
No real money approval was granted.
No compounding approval was granted.
No bank movement approval was granted.
No autonomous execution was granted.
Unattended vacation mode remains blocked.
Vacation profit trial remains blocked unless Anthony separately approves.
Profit is not guaranteed.
All protected flags remain false.
Owner-run only.
One-shot only.

