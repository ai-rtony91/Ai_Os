AIOS Live Watchlist And Pair Discovery Contract V1



Status: DESIGN\_CONTRACT



Purpose



Define how AIOS discovers, ranks, presents, and hands off forex trading opportunities to the operator dashboard.



AIOS finds opportunities.

AIOS explains opportunities.

Human reviews opportunities.

Human remains approval authority.



The watchlist does not place trades.



Core Principle



Minimal input → governed AIOS decision → clear output.



The watchlist exists to reduce operator workload and focus attention on the highest-quality opportunities.



Watchlist Objectives

Discover candidate forex pairs

Rank candidate forex pairs

Surface highest-quality opportunities

Provide chart handoff

Support future autonomous decision systems

Reduce operator scanning workload

Improve consistency of opportunity selection

Discovery Universe



Initial scope:



EUR\_USD

GBP\_USD

USD\_JPY

AUD\_USD

USD\_CAD

NZD\_USD

EUR\_GBP

EUR\_JPY

GBP\_JPY



Future pairs may be added through separate approval.



Ranking Model



Every candidate pair receives:



Opportunity Score

Confidence Score

Trend Direction

Volatility Context

Session Context

Supertrend Status



Pairs are sorted from highest score to lowest score.



Scoring Model



Score Range:



0–100



Interpretation:



90–100 = Exceptional

80–89 = Strong

70–79 = Good

60–69 = Watch

Below 60 = Low Priority



AIOS must provide a reason for the score.



Confidence Model



Confidence must be displayed separately from score.



Example:



Opportunity Score: 84

Confidence: 91



High score without confidence should not automatically rank first.



Data Quality Requirements



Watchlist must reject:



stale data

incomplete data

corrupted data

unsupported sources



Only approved and licensed data sources may be used.



Refresh Rules



Future implementation must define:



refresh cadence

stale-data timeout

update status



Watchlist must display last update timestamp.



Watchlist Display Requirements



Display:



Rank

Pair

Opportunity Score

Confidence

Trend Direction

Supertrend Status

Volatility Context

Session Context

Last Updated



Operator action:



View Chart



Supertrend Visibility Rules



Supertrend is approved as a watchlist signal.



Display:



Bullish

Bearish

Neutral



Future indicators may be added through separate authority.



Indicators must explain why they contribute to ranking.



Operator Workflow

AIOS ranks pairs

Watchlist displays ranked pairs

Operator selects pair

Chart opens

AIOS explains opportunity

Human decides

Chart Handoff Contract



Selecting a pair opens:



Single-pair chart

Current ranking information

Current signal information

Current risk information

Current exit-readiness information



Chart does not automatically place trades.



Dashboard Integration



Dashboard contains:



Watchlist panel

Chart panel

P/L panel

Risk panel

Exit Brain panel



Dashboard remains display-only.



Dashboard displays truth.



Dashboard never creates truth.



Watchlist Restrictions



Watchlist cannot:



place trades

bypass risk controls

bypass exit controls

bypass secret controls

bypass approval authority

Future Autonomy Support



The watchlist should eventually support:



opportunity ranking

signal aggregation

pair recommendation

risk-aware prioritization



without bypassing governance.



Success Criteria



The watchlist succeeds when:



operator scanning time decreases

pair selection becomes easier

opportunity visibility improves

signal clarity improves

chart handoff is immediate

operator burden decreases

Out Of Scope



Not included:



trade execution

broker order routing

secret handling

live autonomous trading

approval bypasses

Final Principle



AIOS discovers opportunities.



AIOS ranks opportunities.



AIOS explains opportunities.



Humans remain approval authority.

