# AIOS Forex Paper Bot

This generated scaffold is paper-only. It models a local Forex paper decision for
review and does not connect to a broker, credential store, real webhook, live
market feed, scheduler, worker dispatcher, or order route.

Supported pairs are EURUSD, GBPUSD, and USDJPY. Supported directions are buy and
sell. The bot blocks missing stop loss values, unsupported pairs, unsupported
directions, risk above the local paper limit, credentials, broker orders, live
execution, real orders, and real webhook routing.

The scaffold exists to prove that AIOS can apply one safe local build action,
run the focused validator, attempt one bounded repair when requested, and report
the result without staging, committing, pushing, dispatching workers, mutating
queues, or enabling live trading.
