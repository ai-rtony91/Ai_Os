# Paper Runtime Decision Sequence

1. Read `PAPER_RUNTIME_INPUT_001.json`.
2. Assign a Paper Regime Review in `PAPER_RUNTIME_REGIME_RESULT_001.json`.
3. Apply Paper Risk Gate rules in `PAPER_RUNTIME_RISK_RESULT_001.json`.
4. Create a Paper Decision in `PAPER_RUNTIME_DECISION_RESULT_001.json`.
5. If the Paper Risk Gate result is blocked, do not simulate a paper fill.
6. Record the blocked Paper Trade Result in `PAPER_RUNTIME_TRADE_RESULT_001.json`.
7. Update Paper Scorecard fields in `PAPER_RUNTIME_SCORECARD_RESULT_001.json`.
8. Write a Paper Runtime Review in `PAPER_RUNTIME_REVIEW_REPORT_001.json`.

Default outcome: BLOCKED until paper trade review conditions pass.
