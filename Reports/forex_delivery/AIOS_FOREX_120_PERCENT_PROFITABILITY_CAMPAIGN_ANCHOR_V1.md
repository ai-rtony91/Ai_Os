# AIOS Forex 120 Percent Profitability Campaign Anchor V1

## Purpose

This report anchors the campaign target language without creating trading authority.

AIOS does not guarantee 120% return. AIOS is not proven profitable until evidence proves it.

## Runtime Equity Rule

Starting campaign equity is an owner-supplied runtime value. It must not be committed to the repo.

Target campaign equity is starting campaign equity multiplied by 2.20.

Target campaign equity equals 2.20x starting campaign equity.

The net campaign return target is +120%.

This is a +120% net campaign return target, not a guaranteed outcome.

## Campaign Structure

The campaign is multiple sequential trades, not one trade.

The 120% target is not a one-trade requirement.

Compounding is conditional, not automatic.

Withdrawal is conditional, not automatic.

Trade continuation can occur only after post-trade evidence and result-bucket classification.

## Stop Conditions Before Next Allocation

No next allocation after unresolved broker rejection.

No next allocation after missing post-trade evidence.

No next allocation after daily stop breach.

No next allocation after kill switch failure.

No next allocation after max drawdown breach.

No next allocation after unauthorized live endpoint detection.

## Required Campaign Sequence

```text
BROKER_GATE
VAULT_PREFLIGHT
ONE_GOVERNED_DEMO_TRADE
POST_TRADE_EVIDENCE
RESULT_BUCKET
NEXT_ALLOCATION
COMPOUND_OR_WITHDRAW_DECISION
REPEAT_OR_STOP
TARGET_REACHED_OR_CAMPAIGN_STOPPED
```

## Explicit Non-Claims

No claim that the 120% target is guaranteed.

No claim that AIOS is profitable until evidence proves it.

No claim that one trade must or can achieve the target.

No claim that compounding or withdrawal is automatic.

No claim that live trading is authorized by this campaign anchor.
