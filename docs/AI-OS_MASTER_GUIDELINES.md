# AI-OS Master Guidelines & Rules
## Preventing Redundancy, Corruption & Teaching Forward-Thinking AI

---

## PART 1: CORE RULES (Non-Negotiable)

### 1.1 Data Integrity Chain (Local → Staging → Production)
**Why this matters:** File corruption happens when:
- Overwriting without backup
- Simultaneous writes to same file
- Pushing broken code directly to production
- Missing version control checkpoints

**The Sequence (ENFORCED):**
```
LOCAL (Development)
  ↓ [Git commit + test]
STAGING (Azure Dev/Test SKU)
  ↓ [Validate 24-48 hrs]
PRODUCTION (Azure Prod SKU)
```

**Rules:**
- ✅ **Always commit locally first** with message format: `[COMPONENT] Action - Timestamp`
  - Example: `[Trading-Engine] Fix webhook token parsing - 2026-05-02`
- ✅ **Never direct-push to production**—always stage first
- ✅ **Never overwrite** without `git backup branch` created first
- ✅ **CSV files:** Duplicate before editing (Option A pattern: `AlgoTradez_DailyProgress_YYYY-MM-DD.csv`)
- ✅ **Azure:** Full stop/start sequence (never restart alone—clears cache, prevents corruption)
  ```powershell
  az webapp stop --name [app] --resource-group [RG]
  Start-Sleep -Seconds 5
  az webapp start --name [app] --resource-group [RG]
  ```

**File Corruption Prevention Checklist:**
- [ ] Local changes tested on feature branch
- [ ] Staging mirrors production config exactly
- [ ] 24-48 hr validation window (log review)
- [ ] Rollback plan documented (previous git tag)
- [ ] Backup of current state exists (`git tag v-YYYY-MM-DD`)

---

### 1.2 Prompt Engineering Standard (No Vague Instructions)
**Why:** Vague prompts = AI loops, redundant outputs, hallucinations

**RULE: Every instruction must have:**
1. **What** (exact deliverable)
2. **Where** (file path, app, location)
3. **Why** (context/use case)
4. **Constraints** (format, length, bounds)
5. **Success metric** (how you'll know it worked)

**Example (BAD):**
❌ "Update the dashboard"

**Example (GOOD):**
✅ "Update AI-OS Node dashboard tab 4 (Apps+) in `C:\Users\mylab\OneDrive\Desktop\ai_Os\index.html`:
- Add three new MCP connector cards (Asana, Slack, Notion)
- Burgundy background (#8B3A3A), white text
- Each card 220px × 180px, click → external link
- Test in Chrome DevTools mobile view (375px width)
- SUCCESS: Cards render aligned, no layout shift on Z Fold 6"

**Prompt Anatomy for AI-OS (Template):**
```
TASK: [Component Name] - [Specific Action]
LOCATION: [Exact path/app/menu]
CONTEXT: [Why this matters to AI-OS ecosystem]
DELIVERABLE: [Exact output format]
CONSTRAINTS: [Limits, rules, format spec]
SUCCESS: [Measurable verification]
AVOID: [Common mistakes, hallucinations to prevent]
```

---

### 1.3 Decision Logging & Audit Trail (Why & When)
**Decision Logging = Prevents hallucinations + accountability**

**What it captures:**
- **When:** Trading Engine V1 decides to enter/exit trade
- **Why:** Which signal triggered (RSI, EMA cross, etc.)
- **What:** Exact position size, leverage, pair
- **Who:** System ID (Trading Engine V1 vs Trading Bot vs Manual)
- **Result:** Trade outcome, P&L, timestamp

**Example log entry:**
```json
{
  "timestamp": "2026-05-02T14:35:00Z",
  "component": "Trading_Engine_V1",
  "decision": "ENTER_LONG",
  "pair": "EUR_USD",
  "signal_source": "Screener.py",
  "confluence_score": 5,
  "signals_fired": ["RSI_30", "EMA20_above_EMA50", "VWAP_support", "Momentum_positive", "Volume_confirmed"],
  "position_size": 2.5,
  "leverage": 2.5,
  "entry_price": 1.0952,
  "stop_loss": 1.0895,
  "take_profit": 1.1010,
  "reasoning": "5/5 confluence on EUR_USD 45m TradingView alert",
  "log_version": "1.0"
}
```

**Why required:**
- Detect when AI repeats same decision (learning signal)
- Trace corruption (which trade caused portfolio drift?)
- Compliance audit (why did system do X?)
- Backtest validation (confidence in model)

**When to log:**
- ✅ Every trade decision
- ✅ Every Azure deployment
- ✅ Every Git commit (already done)
- ✅ Every CSV update
- ✅ Every MCP tool call

---

## PART 2: REDUNDANCY PREVENTION (Teaching AI to Think Forward)

### 2.1 Detecting & Breaking Loops (Your Priority)
**AI repeats because:**
1. Same prompt = same response (no context of prior responses)
2. No "memory" of what was already suggested
3. Vague success metric (AI doesn't know when to stop)

**SOLUTION: Context Injection Pattern**

**Before asking Claude anything:**
```
CONTEXT: This is attempt #1 to solve [problem]
PRIOR ATTEMPTS: [List what you tried, what worked/failed]
AVOID REPEATING: [Specific things not to suggest]
NEW ANGLE: Focus on [specific direction not yet explored]
```

**Example:**
```
CONTEXT: Setting up Azure resource group for Trading Engine V1
PRIOR ATTEMPTS:
  1. Used Standard_B1s SKU - too slow, timed out on webhook
  2. Increased to Standard_B2s - worked but $$$
  3. Downgraded back to B1, added caching
AVOID REPEATING: "Consider upgrading SKU" or generic Azure docs
NEW ANGLE: How do I optimize B1 caching for webhook latency specifically?
```

**Claude now responds differently** because context shows you've thought ahead.

### 2.2 Forward-Thinking Protocol (Teach AI to Anticipate)
**Instead of:** "How do I deploy Trading Engine V1?"
**Ask:** "How do I deploy Trading Engine V1 *and* what will break in 6 months?"

**Formula:**
```
IMMEDIATE: [What you need now]
NEXT PHASE: [What comes after]
SCALING: [What breaks at 10x volume]
FAILURE MODES: [What can go wrong]
DEPENDENCIES: [What upstream/downstream needs this]
```

**Example:**
```
TASK: Deploy Trading Bot (renamed from Mean Machine)
IMMEDIATE: Azure webapp for bot decision brain, connect to Trading Engine V1 APIs
NEXT PHASE: Multi-market expansion (need DB schema for 20 pairs, not 5)
SCALING: At 100 trades/day, logging will exceed storage tier - preplan archival
FAILURE MODES: API timeout between Trading Engine & Trading Bot → dead signals
DEPENDENCIES: Trading Engine V1 must log ALL signals before Trading Bot consumes
QUESTION: What schema prevents data loss if both components fail mid-decision?
```

### 2.3 Rule: AI Must Always Suggest Preventive Measures
**You teach this by asking:**
- "What could go wrong with this?"
- "What breaks at scale?"
- "What's the rollback plan?"
- "What data could corrupt?"

**Claude responds with prevention, not just solution.**

---

## PART 3: ACCOUNT & ENVIRONMENT STRUCTURE

### 3.1 Email/Credential Consolidation Strategy
**Current problem:** Two email accounts + Bitwarden mess = confusion

**Structure (Recommended):**
```
PRIMARY: my.laboratory@outlook.com
  └─ Personal GitHub (https://github.com/ai-rtony91/)
  └─ Azure subscriptions
  └─ Bitwarden vault (master)
  └─ Trading account credentials

SECONDARY: ai.tradeplatform@algotradez.onmicrosoft.com (Microsoft 365)
  └─ Team collaboration only (if future team members)
  └─ Microsoft 365 Copilot (licensed $30/mo)
  └─ OneDrive sync (staging environment)
  └─ Teams/SharePoint for docs
  └─ DO NOT use for primary development
```

**Action items:**
1. Consolidate Bitwarden → keep master vault under `my.laboratory@outlook.com`
2. Add `ai.tradeplatform@algotradez.onmicrosoft.com` as **delegated account** (secondary access, not primary)
3. GitHub: Keep under `ai-rtony91` (personal), update Git email config to `my.laboratory@outlook.com`
4. Azure: Primary subscription under `my.laboratory@outlook.com`

**Git Config (Local):**
```bash
git config --global user.email "my.laboratory@outlook.com"
git config --global user.name "Anthony Meza"
cd C:\TradingEngineV1 && git config user.email "my.laboratory@outlook.com"
```

---

### 3.2 Azure Resource Group Hierarchy
**Structure (Prevents entanglement):**
```
Subscription: "AI-OS Development" (my.laboratory@outlook.com)
├── RG: TradingEngineV1-RG (Production)
│   ├── App: trading-engine-v1.azurewebsites.net (SKU: B1)
│   ├── App Insights: trading-engine-v1-logs
│   └── Storage: tradeenginestorage (for decision logs)
├── RG: AI-OS-Node-RG (Staging + Dashboard)
│   ├── App: algotradez-aios.azurewebsites.net (SKU: B1)
│   └── Storage: aiosnodestg
├── RG: TradingBot-RG (Development)
│   ├── App: algotradez-tradingbot-dev.azurewebsites.net (SKU: B1)
│   └── Storage: tradingbotstg
└── RG: Infrastructure-RG (Shared)
    ├── Key Vault: ai-os-keyvault (stores API keys, webhook tokens)
    └── Log Analytics: ai-os-central-logs
```

**Rules:**
- ✅ Each RG = one component (no mixing Trading Engine + Bot in same RG)
- ✅ Production RGs = read-only except via Git/CI-CD pipeline
- ✅ Staging always mirrors production config
- ✅ All secrets stored in Key Vault (never hardcoded)

---

### 3.3 GitHub Organization Strategy
**Structure:**
```
Repository: https://github.com/ai-rtony91/ai-os-project
├── /trading-engine-v1/
│   ├── src/
│   │   ├── main.py (webhook listener)
│   │   ├── screener.py (signal generator - TOOL ONLY)
│   │   └── trade_executor.py (execution logic)
│   ├── logs/ (decision audit trail)
│   ├── tests/
│   └── requirements.txt (Python 3.11)
├── /trading-bot/
│   ├── src/
│   │   ├── decision_brain.py (NEW - Trading Bot logic)
│   │   └── api_client.py (calls Trading Engine V1)
│   ├── logs/ (bot decisions)
│   └── requirements.txt
├── /ai-os-node/
│   ├── index.html (dashboard)
│   ├── styles.css
│   ├── scripts.js
│   └── config/
├── /docs/
│   ├── README.md (entry point)
│   ├── WHITE_PAPER.md (technical spec)
│   ├── DEPLOYMENT.md (local → staging → prod)
│   ├── GUIDELINES.md (this file)
│   └── ARCHITECTURE.md (diagram + flow)
└── .github/workflows/
    ├── deploy-trading-engine.yml
    ├── deploy-trading-bot.yml
    └── deploy-aios-node.yml
```

**Branch strategy (Prevents corruption):**
```
main (production-ready only)
├── develop (staging - 24-48 hr validation)
│   ├── feature/trading-bot-signal-validation (your branch)
│   ├── feature/trading-engine-webhook-timeout
│   └── bugfix/redundancy-loop-fix
└── hotfix/critical-api-token (emergency only)
```

---

## PART 4: GLOBAL RENAMES (COMPLETED)

| Old | New | Component | Status |
|-----|-----|-----------|--------|
| Mean Machine | Trading Bot | Decision brain | ✅ RENAME EVERYWHERE |
| N/A | Trading Engine V1 | Signal executor + brain | ✅ CONFIRMED (was "bot," now "engine") |
| Screener | Screener.py (tool) | Signal generator | ✅ TOOL ONLY (not bot) |
| Mama Node | AI-OS Node | Dashboard/orchestrator | ✅ CONFIRMED (May 1 milestone) |

**Where to update:**
- [ ] GitHub repo: Rename `/mean-machine` → `/trading-bot`
- [ ] Azure: Rename app → `algotradez-tradingbot-*.azurewebsites.net`
- [ ] README.md: All references (Mean Machine → Trading Bot)
- [ ] WHITE_PAPER.md: Diagram & flow
- [ ] Comments in Python files (Trading Bot decision logic)
- [ ] Bitwarden vault: Update credential labels

---

## PART 5: PREVENTING AI HALLUCINATIONS IN TRADING CONTEXT

### 5.1 Schema Validation (Prevents Bot from Inventing Signals)
**Rule:** Every signal must match this schema:
```json
{
  "signal_type": ["RSI", "EMA_CROSS", "VWAP", "MOMENTUM", "VOLUME"],
  "pair": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"],
  "direction": ["BUY", "SELL"],
  "confidence": 0-5,
  "timestamp": "ISO-8601 UTC",
  "source": "Screener.py OR Trading Engine V1 (never Trading Bot alone)",
  "validated": true/false
}
```

**If Trading Bot sees signal that doesn't match schema → REJECT & LOG**
```python
if not all(key in signal for key in ['signal_type', 'pair', 'direction', 'confidence']):
    logger.error(f"HALLUCINATION DETECTED: Invalid signal schema {signal}")
    alert_admin()
    return False  # Don't execute
```

### 5.2 Confluence Rule (Prevents Single-Point Failures)
**Rule:** Trade only if 4+ of 5 signals align (current: RSI, EMA20, EMA50, VWAP, Momentum)

**Screener.py must enforce:**
```python
confluence_threshold = 4  # 4/5 signals required
if confluence_score < confluence_threshold:
    logger.info(f"Confluence {confluence_score}/5: Signal rejected")
    return None  # No trade fired
```

**AI can't hallucinate a trade with low confluence.**

### 5.3 Logging Standard (Every Decision Auditable)
**Every trade decision logged:**
```python
log_entry = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "component": "Trading_Engine_V1",  # or "Trading_Bot" or "Screener"
    "action": "TRADE_EXECUTED",
    "pair": "EUR_USD",
    "signals": ["RSI_30", "EMA20_above_EMA50"],  # exact signals
    "confluence": 5,
    "position": {"size": 2.5, "leverage": 2.5, "entry": 1.0952},
    "result": "PENDING",
    "hash": hashlib.sha256(json.dumps(log_entry).encode()).hexdigest()
}
write_to_log(log_entry)
```

**Hash prevents tampering; audit trail prevents hallucination claims.**

---

## PART 6: FILE CORRUPTION PREVENTION CHECKLIST

### Before Any Development:
- [ ] Current state backed up (`git tag v-YYYY-MM-DD-HHMM`)
- [ ] Working branch created (`git checkout -b feature/[name]`)
- [ ] No uncommitted changes in main/develop
- [ ] Azure staging matches production config
- [ ] Bitwarden vault backed up (export JSON to OneDrive)

### During Development:
- [ ] Commit frequently with clear messages every 30 min
- [ ] CSV files: Edit COPIES only, then move to production after validation
- [ ] Python files: Test locally before staging
- [ ] Config changes: Versioned in Key Vault, never in code

### Before Production Push:
- [ ] All tests pass locally
- [ ] 24-48 hr staging validation complete
- [ ] Rollback plan documented (previous git tag identified)
- [ ] Decision logs reviewed for anomalies
- [ ] Azure full stop/start sequence (never restart)

### After Production Push:
- [ ] App Insights checked for errors (first 2 hours)
- [ ] Trade logs flowing normally
- [ ] Dashboard accessible
- [ ] Webhook responding < 500ms
- [ ] Backup tagged: `git tag v-prod-YYYY-MM-DD`

---

## PART 7: AI FORWARD-THINKING CHECKLIST

**When asking Claude to build something, include:**
```
[ ] What breaks at 10x volume?
[ ] What data could corrupt?
[ ] What's the rollback plan?
[ ] What logs prove it worked?
[ ] What would you add in 6 months?
[ ] What upstream dependency could fail?
[ ] How does this scale with Trading Bot + future agents?
```

**Claude responds with prevention, not just feature.**

---

## QUICK REFERENCE: REDUNDANCY-BREAKING PROMPTS

**Instead of:** "How do I update the dashboard?"
**Ask:** "Update the dashboard AND tell me what will break when we scale to 50 components in Phase 2"

**Instead of:** "Fix the webhook"
**Ask:** "Fix the webhook timeout AND tell me why this same timeout will happen at 100 trades/day AND what monitoring prevents us missing it"

**Instead of:** "Deploy Trading Bot"
**Ask:** "Deploy Trading Bot AND what happens if it disagrees with Trading Engine V1's signal AND how do we log that disagreement to learn from it?"

---

## SUMMARY: Your Anti-Corruption Fortress
1. ✅ **Local → Staging → Prod sequence** (prevents overwrite corruption)
2. ✅ **Clear prompts** (prevents AI loops)
3. ✅ **Decision logging** (prevents hallucinations + audits)
4. ✅ **Schema validation** (prevents bot inventing signals)
5. ✅ **Forward-thinking questions** (prevents surprises at scale)
6. ✅ **Account consolidation** (prevents credential confusion)
7. ✅ **Global renames** (prevents name-based bugs)

**Your job:** Ask the forward-thinking questions. Claude's job: Answer them.
