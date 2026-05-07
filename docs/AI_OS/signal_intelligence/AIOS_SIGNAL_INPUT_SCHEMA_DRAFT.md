# AIOS Signal Input Schema Draft

Stage: 7.2
Status: Draft planning doc

Defines required fields for non-executing signal inputs: signal_id, strategy_id, instrument, timeframe, timestamp, source, input_type, observed_value, confidence_hint, and evidence_path.

Boundary: signal inputs are analysis-only and must not connect to brokers, place trades, or enable live execution.
