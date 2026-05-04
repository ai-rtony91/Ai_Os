<!-- STATUS: ACTIVE | OWNER: AI_OS | SYNC: Fix #2 clean -->

# AI-OS: Technical White Paper
**Complete Specification, APIs, Roadmap, and Scaling Architecture**

---

## EXECUTIVE SUMMARY

AI-OS is a modular autonomous financial operating system comprising:
1. **Trading Engine V1** - Live signal executor (OANDA practice, EUR_USD 45m, 2.5x leverage)
2. **Trading Bot** - Decision validation brain (under development)
3. **AI-OS Node** - Central orchestrator & dashboard
4. **Screener.py** - Signal generator (5-point confluence)

**Current Scale:** 1 trading pair, 5 signals, ~288 decisions/day (every 5 min on 45m timeframe)  
**Target Scale (Phase 2):** 5+ pairs, 50+ components, 1000+ decisions/day, voice-controlled  
**Performance Goal:** $100k → $485.7k in 12 months (Sharpe 1.40, 57% win rate, -55% max DD)

---

## PART 1: COMPONENT SPECIFICATIONS

### 1.1 Trading Engine V1

**Purpose:** Live signal executor + decision brain for EUR_USD pair

**Deployment:**
- **URL:** https://trading-engine-v1.azurewebsites.net
- **Azure RG:** TradingEngineV1-RG
- **SKU:** Standard_B1 ($11.60/mo)
- **Runtime:** Python 3.11
- **Location:** `C:\TradingEngineV1`

**Architecture:**
```
TradingView Webhook (EUR_USD 45m alert)
  ↓ [WEBHOOK_TOKEN validation]
main.py (entry point)
  ├─ Receive webhook payload
  ├─ Call screener.py (signal validation)
  └─ Execute trade via OANDA API
```

**Key Files:**
- `main.py` - Webhook listener + Flask app (port 8000)
- `screener.py` - Signal generator (5 confluence points)
- `trade_executor.py` - OANDA API calls (TBD: extract from main.py)
- `requirements.txt` - Python dependencies
- `.env` - Secrets (WEBHOOK_TOKEN, OANDA_KEY, OANDA_ACCOUNT)

**Signals (5-Point Confluence Engine):**
```json
{
  "signals": [
    {"type": "RSI", "period": 14, "thresholds": {"oversold": 30, "overbought": 70}},
    {"type": "EMA_CROSS", "fast": 20, "slow": 50},
    {"type": "VWAP", "usage": "support/resistance"},
    {"type": "MOMENTUM", "period": 10},
    {"type": "VOLUME", "period": 20, "threshold": "above_average"}
  ],
  "confluence_threshold": 4,
  "decision_frequency": "5_minutes",
  "pair": "EUR_USD",
  "timeframe": "45m"
}
```

**Trading Parameters:**
```json
{
  "account_type": "OANDA_PRACTICE",
  "account_currency": "USD",
  "initial_balance": "$100,000",
  "leverage": 2.5,
  "position_sizing": "fixed_percentage",
  "position_size": 2.5,
  "risk_per_trade": "2%",
  "stop_loss_pips": 57,
  "take_profit_pips": 58,
  "max_open_positions": 1,
  "trailing_stop": false
}
```

**Decision Log Schema:**
```json
{
  "timestamp": "2026-05-02T14:35:00Z",
  "epoch_millis": 1714750500000,
  "component": "Trading_Engine_V1",
  "version": "1.0.0",
  "webhook_id": "tradingview_001",
  "pair": "EUR_USD",
  "timeframe": "45m",
  "action": "TRADE_EXECUTED",
  "direction": "BUY",
  "signal_source": "Screener.py",
  "signals": {
    "RSI_14": {"value": 28, "status": "OVERSOLD", "matched": true},
    "EMA_20": {"value": 1.0945, "status": "BELOW_EMA50", "matched": true},
    "EMA_50": {"value": 1.0952, "status": "ABOVE_EMA20", "matched": true},
    "VWAP": {"value": 1.0950, "status": "SUPPORT", "matched": true},
    "MOMENTUM": {"value": 0.85, "status": "POSITIVE", "matched": true}
  },
  "confluence_score": 5,
  "confluence_threshold": 4,
  "decision": "EXECUTE",
  "position": {
    "size": 2.5,
    "leverage": 2.5,
    "entry_price": 1.0952,
    "stop_loss": 1.0895,
    "take_profit": 1.1010
  },
  "execution": {
    "broker": "OANDA",
    "order_id": "123456789",
    "status": "FILLED",
    "execution_time_ms": 145
  },
  "metadata": {
    "user_agent": "TradingView",
    "ip_source": "TradingView_webhook",
    "trace_id": "abc123def456"
  },
  "hash": "SHA256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "checksum_valid": true
}
```

**REST API (for Trading Bot communication):**
```
GET /health
  Response: { "status": "healthy", "uptime_minutes": 1234 }

POST /signal
  Body: { "pair": "EUR_USD", "direction": "BUY", "confluence": 5 }
  Response: { "order_id": "123", "status": "FILLED", "entry": 1.0952 }

GET /logs?limit=100&pair=EUR_USD
  Response: [{ decision log entries }]

GET /metrics
  Response: { "trades_today": 45, "win_rate": 0.57, "pnl": 2345.67 }
```

---

### 1.2 Trading Bot (Development)

**Purpose:** Decision validation brain + market regime analysis

**Status:** Under development (Phase 1.5)

**Planned Functionality:**
- Receives signals from Trading Engine V1
- Validates signal quality before execution (optional gate)
- Analyzes market regime (trending vs ranging)
- Provides second opinion (agree/disagree with Trade Engine)
- Logs disagreements for learning
- Future: Multi-pair orchestration

**Planned Deployment:**
- **URL:** https://algotradez-tradingbot-dev.azurewebsites.net (dev tier)
- **Azure RG:** TradingBot-RG
- **SKU:** Standard_B1
- **Runtime:** Python 3.11
- **Location:** `C:\TradingBot` (local) → `C:\Users\mylab\OneDrive\Desktop\TradingBot\` (staging)

**Architecture (Proposed):**
```
Trading Engine V1 (sends signal)
  ↓ POST /validate
Trading Bot (decision brain)
  ├─ Validate signal schema
  ├─ Analyze market regime
  ├─ Check portfolio state
  └─ Return: { "approved": true/false, "confidence": 0.95 }
```

**API (Planned):**
```
POST /validate-signal
  Body: { signal object from Trading Engine }
  Response: {
    "approved": true,
    "confidence": 0.95,
    "regime": "TRENDING_UP",
    "comment": "RSI oversold in uptrend = buy",
    "timestamp": "2026-05-02T14:35:00Z"
  }

POST /analyze-regime
  Body: { "pair": "EUR_USD", "timeframe": "45m" }
  Response: {
    "regime": "RANGING",
    "volatility": "HIGH",
    "trend_strength": 0.34,
    "confidence": 0.87
  }
```

---

### 1.3 AI-OS Node (Dashboard & Orchestrator)

**Purpose:** Central dashboard, status monitoring, command center

**Deployment:**
- **URL:** https://algotradez-aios.azurewebsites.net
- **Azure RG:** AI-OS-Node-RG
- **SKU:** Standard_B1
- **Location:** `C:\Users\mylab\OneDrive\Desktop\ai_Os\index.html`

**Frontend:**
- **Framework:** Vanilla HTML/CSS/JS (no framework overhead)
- **Theme:** Burgundy (#8B3A3A) background, green (#00FF00) text (terminal aesthetic)
- **Responsive:** Works on Z Fold 6 (375px width), desktop (1920px)

**Tabs:**
1. **Trading Engine** - Live trades, P&L, signal history
2. **Trading Bot** (renamed from "Mean Machine") - Validation decisions, disagreements
3. **Admin** - Deployment controls, logs, settings
4. **Apps+** - MCP connectors (Asana, Slack, Notion, future agents)

**Data Sources:**
- Trading Engine API (`/logs`, `/metrics`)
- Trading Bot API (`/decisions`)
- AlgoTradez_AI-OS_Roadmap_1.csv (daily progress widget)
- Azure App Insights (logs, errors)

**UI Components (Current):**
```
Header: "AI-OS Node v1.0 | EUR_USD Live"
├─ Tab 1: Trading Engine
│  ├─ Live PnL: $2,345.67 (+2.3%)
│  ├─ Trades Today: 45
│  ├─ Win Rate: 57%
│  ├─ Signal History (last 10)
│  └─ Chart: Daily equity curve
├─ Tab 2: Trading Bot
│  ├─ Validation Decisions (last 10)
│  ├─ Disagreement Rate: 3%
│  ├─ Regime Analysis
│  └─ Confidence Scores
├─ Tab 3: Admin
│  ├─ Deployment Log
│  ├─ System Health
│  ├─ Config Editor
│  └─ Backup/Restore
└─ Tab 4: Apps+
   ├─ Asana (tasks)
   ├─ Slack (alerts)
   ├─ Notion (docs)
   └─ Future MCP connectors
```

**Data Refresh:**
- Real-time WebSocket (future) or polling every 5 sec
- CSV roadmap refreshes daily (12 AM UTC)

---

### 1.4 Screener.py (Signal Generator Tool)

**Purpose:** Generate trading signals via 5-point confluence

**Status:** 🟢 Live and running every 5 minutes

**Location:** `C:\TradingEngineV1\screener.py`

**Functionality:**
- Receives EUR_USD 45m candle data (from TradingView webhook or OANDA API)
- Calculates 5 signals: RSI, EMA20, EMA50, VWAP, Momentum
- Scores each signal (match = 1, no match = 0)
- Returns confluence score (0-5)
- Only fires signal if confluence ≥ 4

**Not a bot:** Screener generates signals but doesn't execute. Trading Engine V1 executes.

**Code Structure:**
```python
def screener(open, high, low, close, volume, pair="EUR_USD"):
    """
    Returns:
    {
      "confluence_score": 5,
      "signals": [
        {"name": "RSI_14", "value": 28, "status": "OVERSOLD"},
        {"name": "EMA_CROSS", "value": True, "status": "BULLISH"}
      ],
      "fire_signal": True  # ≥ 4 confluence
    }
    """
    rsi = calculate_rsi(close, 14)
    ema20 = calculate_ema(close, 20)
    ema50 = calculate_ema(close, 50)
    vwap = calculate_vwap(high, low, close, volume)
    momentum = calculate_momentum(close, 10)
    
    score = 0
    signals = []
    
    if rsi < 30:
        score += 1
        signals.append({"name": "RSI_14", "status": "OVERSOLD"})
    if ema20 < ema50:
        score += 1
        signals.append({"name": "EMA_CROSS", "status": "BULLISH"})
    # ... etc
    
    return {
        "confluence_score": score,
        "signals": signals,
        "fire_signal": score >= 4
    }
```

---

## PART 2: DATA MODEL & SCHEMAS

### 2.1 Signal Schema (Single Source of Truth)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TradingSignal",
  "type": "object",
  "required": [
    "timestamp", "pair", "direction", "confluence_score",
    "signal_source", "signals", "validated"
  ],
  "properties": {
    "timestamp": {"type": "string", "format": "date-time"},
    "pair": {"enum": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"]},
    "direction": {"enum": ["BUY", "SELL"]},
    "confluence_score": {"type": "integer", "minimum": 0, "maximum": 5},
    "signal_source": {"enum": ["Screener.py", "Trading_Engine_V1", "Trading_Bot"]},
    "signals": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "value": {"type": "number"},
          "status": {"type": "string"},
          "matched": {"type": "boolean"}
        }
      }
    },
    "validated": {"type": "boolean"},
    "trade_executed": {"type": "boolean"}
  }
}
```

### 2.2 Trade Execution Schema
```json
{
  "timestamp": "2026-05-02T14:35:00Z",
  "order_id": "123456789",
  "pair": "EUR_USD",
  "direction": "BUY",
  "entry_price": 1.0952,
  "position_size": 2.5,
  "leverage": 2.5,
  "stop_loss": 1.0895,
  "take_profit": 1.1010,
  "status": "FILLED",
  "execution_time_ms": 145,
  "pnl": 58.00,
  "win": true
}
```

### 2.3 Decision Log Schema (with Hash)
```json
{
  "timestamp": "2026-05-02T14:35:00Z",
  "component": "Trading_Engine_V1",
  "action": "TRADE_EXECUTED",
  "signal_data": { /* full signal schema */ },
  "trade_data": { /* full trade schema */ },
  "metadata": {
    "version": "1.0.0",
    "user_agent": "TradingView",
    "trace_id": "abc123def456"
  },
  "hash": "SHA256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "checksum_valid": true
}
```

---

## PART 3: DEPLOYMENT ARCHITECTURE

### 3.1 Azure Resource Group Hierarchy

```
Subscription: "AI-OS Development" (my.laboratory@outlook.com)

├── RG: TradingEngineV1-RG (Production)
│   ├── App Service: trading-engine-v1 (B1, Python 3.11)
│   ├── App Service Plan: trading-engine-v1-plan
│   ├── Application Insights: trading-engine-v1-logs
│   ├── Storage Account: tradeenginestorage (decision logs)
│   └── Key Vault Ref: AI_OANDA_KEY, WEBHOOK_TOKEN
│
├── RG: AI-OS-Node-RG (Staging + Dashboard)
│   ├── App Service: algotradez-aios (B1, Static HTML)
│   ├── App Service Plan: algotradez-aios-plan
│   └── CDN (future): For dashboard caching
│
├── RG: TradingBot-RG (Development)
│   ├── App Service: algotradez-tradingbot-dev (B1, Python 3.11)
│   ├── App Service Plan: algotradez-tradingbot-plan
│   └── Application Insights: tradingbot-logs
│
└── RG: Infrastructure-RG (Shared)
    ├── Key Vault: ai-os-keyvault
    │   ├── Secret: OANDA_API_KEY
    │   ├── Secret: WEBHOOK_TOKEN
    │   ├── Secret: BITWARDEN_SYNC_KEY
    │   └── Secret: DB_CONNECTION_STRING (future)
    │
    ├── Log Analytics: ai-os-central-logs
    │   └── Queries: Trade decisions, errors, deployments
    │
    └── Storage Account: ai-os-backups
        ├── Container: decision-logs (immutable)
        └── Container: daily-snapshots (for restore)
```

### 3.2 Deployment Sequence (Local → Staging → Prod)

**Step 1: Local Development**
```bash
cd C:\TradingEngineV1
git checkout -b feature/webhook-timeout-fix
# Edit main.py, screener.py, etc.
python -m pytest tests/
# All tests pass locally
git add .
git commit -m "[Trading-Engine] Fix webhook timeout - 2026-05-02"
git push origin feature/webhook-timeout-fix
```

**Step 2: Staging (24-48 Hr Validation)**
```bash
# GitHub PR review (optional)
git checkout develop
git pull origin feature/webhook-timeout-fix
git merge feature/webhook-timeout-fix

# Deploy to staging (B1 SKU)
az webapp up --sku B1 --name trading-engine-v1-staging --resource-group TradingEngineV1-Staging-RG --runtime "PYTHON:3.11"

# Monitor staging logs for 24-48 hours
# Check: Webhook latency, trade execution rate, error logs
# If OK → proceed to Step 3
# If fails → rollback, git revert, iterate
```

**Step 3: Production Promotion**
```bash
# Full stop/start sequence (never restart)
az webapp stop --name trading-engine-v1 --resource-group TradingEngineV1-RG
Start-Sleep -Seconds 5
az webapp start --name trading-engine-v1 --resource-group TradingEngineV1-RG

# Tag release
git tag v-prod-2026-05-02-14-35
git push origin v-prod-2026-05-02-14-35

# Monitor production (check App Insights immediately)
```

**Rollback (if needed):**
```bash
# Quick rollback to previous version
git checkout v-prod-2026-05-01-10-00
az webapp up --sku B1 --name trading-engine-v1 --resource-group TradingEngineV1-RG --runtime "PYTHON:3.11"
```

---

## PART 4: ROADMAP (AlgoTradez_AI-OS_Roadmap_1.csv)

**OFFICIAL PLAN** — Never deviate from this roadmap.

```csv
Phase,Component,Task,Status,Target Date,Owner,Dependencies
Phase 1,Trading Engine V1,EUR_USD 45m webhook,COMPLETE,2026-04-28,Tony,OANDA API
Phase 1,Trading Engine V1,5-point confluence screener,COMPLETE,2026-04-28,Tony,TradingView
Phase 1,Screener.py,Signal generator tool,COMPLETE,2026-04-28,Tony,Trading Engine V1
Phase 1,AI-OS Node,Dashboard v1 (4 tabs),COMPLETE,2026-04-28,Tony,Trading Engine V1
Phase 1.5,Trading Bot,Decision brain skeleton,IN PROGRESS,2026-05-10,Tony,Trading Engine V1
Phase 1.5,Trading Bot,Signal validation logic,IN PROGRESS,2026-05-15,Tony,Decision brain
Phase 2,Trading Bot,Multi-pair orchestration,PLANNED,2026-06-30,Tony,Phase 1.5 complete
Phase 2,AI-OS Node,Voice control (Alexa),PLANNED,2026-07-15,Tony,AWS Alexa SDK
Phase 2,Infrastructure,Microsoft 365 Copilot agent,PLANNED,2026-07-30,Tony,$30/mo license
Phase 3,Multi-Pair,GBP/USD live trading,PLANNED,2026-08-30,Tony,Phase 2 complete
Phase 3,Multi-Pair,USD/JPY live trading,PLANNED,2026-09-15,Tony,Phase 2 complete
Phase 4,Advanced,Regime analysis + ML,PLANNED,2026-10-31,Tony,Historical data
Phase 5,Enterprise,Team collaboration UI,PLANNED,2026-12-31,Team,Phase 4 complete
```

**Current: Phase 1 ✅ Complete | Phase 1.5 🟡 In Progress**

---

## PART 5: SCALING ARCHITECTURE (Future)

### 5.1 Multi-Pair Expansion (Phase 2)
**Current:** 1 pair (EUR_USD)  
**Target:** 5 pairs (EUR, GBP, JPY, AUD, CAD)

**Architecture Change:**
```
Before (Single-pair):
Screener.py (hardcoded EUR_USD)
  ↓
Trading Engine V1 (executes EUR_USD only)

After (Multi-pair):
Screener.py (loops 5 pairs)
  ├─ EUR_USD → Signal?
  ├─ GBP_USD → Signal?
  ├─ USD_JPY → Signal?
  ├─ AUD_USD → Signal?
  └─ USD_CAD → Signal?
     ↓
Trading Bot (coordinate & prioritize)
  ├─ Validate EUR_USD signal
  ├─ Validate GBP_USD signal
  ├─ Check correlation (EUR & GBP together = too risky?)
  └─ Execute max 2 concurrent trades
```

**Database Schema (needed for multi-pair):**
```sql
CREATE TABLE signals (
  id INT PRIMARY KEY,
  timestamp DATETIME,
  pair VARCHAR(10),
  direction VARCHAR(5),
  confluence INT,
  signals JSON,
  validated BOOL,
  trade_executed BOOL,
  order_id VARCHAR(50)
);

CREATE TABLE trades (
  id INT PRIMARY KEY,
  order_id VARCHAR(50),
  pair VARCHAR(10),
  direction VARCHAR(5),
  entry_price DECIMAL(10, 5),
  exit_price DECIMAL(10, 5),
  pnl DECIMAL(12, 2),
  win BOOL,
  timestamp_open DATETIME,
  timestamp_close DATETIME
);
```

### 5.2 Multi-Agent Orchestration (Phase 2+)
**Future:** Trading Engine V1, Trading Bot, Microsoft 365 Copilot, Notion AI, custom agents

```
AI-OS Node (Central Orchestrator)
├─ Agent 1: Trading Engine V1 (executes)
├─ Agent 2: Trading Bot (validates)
├─ Agent 3: Microsoft 365 Copilot (reads email, calendar, documents)
├─ Agent 4: Notion AI (knowledge base, research)
├─ Agent 5: Custom Agent (future)
└─ Conflict Resolution: If agents disagree, log + alert
```

### 5.3 Voice Control (Phase 2)
**Planned:** Alexa/Siri integration for hands-free commands

```
User: "Alexa, what's my portfolio performance?"
  ↓
Alexa Skill (calls AI-OS Node API)
  ↓
AI-OS Node (/voice/portfolio-summary)
  ↓
Response: "You're up $2,345 on 45 trades today. Win rate 57%."
```

---

## PART 6: MONITORING & OBSERVABILITY

### 6.1 Key Metrics to Track
```json
{
  "daily_metrics": {
    "trades_executed": 45,
    "win_rate": 0.57,
    "pnl": 2345.67,
    "sharpe_ratio": 1.40,
    "max_drawdown": -0.55,
    "webhook_latency_ms": 145,
    "signal_confluence_avg": 4.2,
    "api_availability": 0.9999
  }
}
```

### 6.2 Alert Rules
```
IF webhook_latency > 500ms THEN alert("Webhook timeout")
IF win_rate < 0.50 THEN alert("Win rate below target")
IF api_availability < 0.99 THEN alert("Service degradation")
IF signal_error_rate > 0.01 THEN alert("Signal quality issue")
```

### 6.3 Logging Standards
```
Every decision logged to:
  1. Local file: C:\TradingEngineV1\logs\decisions.json
  2. Azure App Insights (custom event: "trade_executed")
  3. Decision log CSV (daily: AlgoTradez_DailyProgress_YYYY-MM-DD.csv)
```

---

## PART 7: SECURITY & COMPLIANCE

### 7.1 Authentication
- **YubiKey (FIDO2):** Local development + Azure login
- **Webhook Token:** WEBHOOK_TOKEN in Key Vault (rotated monthly)
- **API Key:** OANDA_API_KEY in Key Vault (never in code)

### 7.2 Data Protection
- **Decision logs:** SHA-256 hash + immutable storage (blob)
- **Trade execution:** Signed with webhook token
- **Rollback:** Git tags + blob snapshots

### 7.3 Compliance Audit Trail
```
Every trade decision includes:
✓ Timestamp (UTC)
✓ Signal source (Screener, Engine, Bot)
✓ Confluence score (0-5)
✓ Execution price
✓ Hash (prevents tampering)
✓ User/component ID (attribution)
```

---

## PART 8: CAVEATS, WORKAROUNDS & KNOWN ISSUES

### 8.1 Current Limitations

| Issue | Workaround | Target Fix |
|-------|-----------|-----------|
| Single pair (EUR_USD only) | Manual trades on other pairs | Phase 2: Multi-pair |
| No portfolio correlation check | Check manually before opening GBP while EUR open | Phase 2: Trading Bot logic |
| Webhook latency spikes (>500ms) | Implemented retry logic + caching | Upgrade to B2 SKU (future) |
| No voice control | Dashboard manually (Z Fold 6) | Phase 2: Alexa skill |
| Trading Bot not yet validating | Trust Screener 5/5 confluence (high accuracy) | Phase 1.5: Complete validation layer |
| CSV manual updates error-prone | Duplicate before editing (Option A pattern) | Phase 3: API-driven updates |

### 8.2 Known Bugs
```
BUG #1: CSV encoding issues on Windows (UTF-8 vs ANSI)
  Status: CLOSED
  Fix: Use UTF-8 BOM in all CSVs
  File: AlgoTradez_AI-OS_Roadmap_1.csv

BUG #2: Azure webhook timeout on high-volatility events
  Status: OPEN
  Workaround: Webhook token refresh + retry logic
  Fix: Planned for B2 SKU upgrade (Phase 2)

BUG #3: Screener.py occasionally skips VWAP calculation
  Status: OPEN
  Workaround: Confluence ≥ 4 (other signals catch it)
  Fix: Add explicit VWAP validation + unit test
```

### 8.3 File Corruption Scenarios & Prevention

| Scenario | Risk | Prevention |
|----------|------|-----------|
| Overwrite CSV without backup | Data loss | Always duplicate before editing |
| Direct push to production | Broken trades | Use staging (24-48 hrs) |
| Simultaneous writes to logs | Corrupted JSON | Use Azure Blob (append-only) |
| Git force push on main | History lost | Use git reflog to recover |
| API key leaked in code | Account compromise | All secrets in Key Vault |
| Signal schema mismatch | Invalid trades | Validate against JSON schema |

---

## PART 9: FREQUENTLY ASKED QUESTIONS

**Q: What if Trading Engine crashes mid-trade?**  
A: Decision log marks trade as "PENDING." Webhook re-fires on next alert. Logs show gap.

**Q: Can Trading Bot override Trading Engine?**  
A: No—Trading Bot validates, doesn't override. Both agree or bot logs disagreement for learning.

**Q: What's the Max Drawdown policy?**  
A: -55% is the target limit. If portfolio drops > -60%, Trading Engine pauses (manual intervention required).

**Q: How do we prevent hallucinating bad trades?**  
A: Schema validation + 4/5 confluence threshold. No signal executed below 4.

**Q: What happens if OANDA API is down?**  
A: Webhook still arrives. Signal logged. Trade queued. Retry on next webhook.

**Q: Can screener.py execute trades directly?**  
A: No—it's a tool only. Trading Engine V1 decides execution.

---

## PART 10: SUCCESS METRICS & PERFORMANCE TARGETS

**12-Month Goal (from $100k to $485.7k):**
```
Return: +385.7%
Sharpe Ratio: 1.40
Max Drawdown: -55%
Win Rate: 57%
Leverage: 2.5x
Trades/Month: ~1,000
```

**Current Baseline (May 2, 2026):**
```
Trades/Day: ~45 (EUR_USD only, 5-min intervals)
Win Rate: Tracking (need 30-day history)
Sharpe: TBD (insufficient data)
Max Drawdown: TBD
```

---

## GLOSSARY

- **Confluence:** Number of signals agreeing (0-5). ≥4 fires trade.
- **Trading Engine V1:** Live executor. Brain of the system.
- **Trading Bot:** Decision validator. Upcoming enhancement.
- **Screener.py:** Signal generator. Tool, not bot.
- **AI-OS Node:** Dashboard + orchestrator.
- **Decision Log:** Audit trail of every trade decision.
- **Webhook:** TradingView alert that triggers signal check.
- **OANDA:** Forex broker (practice account for backtesting).
- **Leverage:** 2.5x = trading $250k with $100k capital.
- **Max Drawdown:** Worst peak-to-trough loss (-55% = $55k loss from $100k).

---

**Document Version:** 1.0  
**Last Updated:** May 2, 2026  
**Next Review:** May 9, 2026 (Trading Bot Phase 1.5 milestone)  
**Maintainer:** Anthony Meza (my.laboratory@outlook.com)
