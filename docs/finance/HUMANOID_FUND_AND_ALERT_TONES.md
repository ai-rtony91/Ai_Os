# Humanoid Fund + Alert Tones (Owner Guide)

## The goal
Buy a humanoid robot. Default target: **Unitree G1 (~$16,000)**. Options: R1 (~$6k) sooner, G1 EDU (~$40k) or H1 (~$90k+) later. Target is owner-editable in `control/humanoid/humanoid_fund_config.json`.

## The water-drip bucket (how money flows)
Same tipping-bucket pattern as the forex profit sweep — one mental model everywhere:

1. **Drips** — every verified deposit (personal transfer, windfall, and later verified live forex profit) drips into the bucket.
2. **Bucket tips at $200** — the bucket empties into the fund ledger and your phone plays the **money-counter sound**: running total + percent-to-target + what to do next. No money moves by itself — the alert tells you what to do; you do it.
3. **Jackpot milestones** — at 25% ($4k), 50% ($8k), 75% ($12k), 100% ($16k) your phone plays the **casino jackpot sound**. At 100%: purchase decision alert. You buy the robot; automation never does.

## Funding lanes
| Lane | What | Status |
| --- | --- | --- |
| A — Personal | Fixed monthly auto-transfer you set | ON (amount: fill in) |
| B — Forex | 50% of REALIZED live profits, only after the machine earns its record and you arm live | **OFF until proven** |
| C — Windfalls | Anything extra you throw in | ON |

Lane B is the bridge between the forex machine and the robot: the machine's profits buy the humanoid — but only real, realized, verified profits. $0 until then, no exceptions.

## The two sounds (they are two different events)
- 💵 **BUCKET_TIP → money counter**: bill-counter shuffle whirr ending in a double high-pitch beep. Meaning: "counting complete — payout decision ready."
- 🎰 **JACKPOT_MILESTONE → casino jackpot**: slot-machine coin cascade + fanfare. Meaning: "you crossed a milestone."
- 💧 **DRIP → silent/default**: routine deposits shouldn't make noise.

## One-time phone setup (ntfy — the channel that works 100%)
1. Fill the three topic names in `control/secrets/humanoid_ntfy_topics.json` (gitignored — the topic name IS the key; use long random strings).
2. In the ntfy app, subscribe to all three topics.
3. Download two sounds once (any source you like — search "money counter sound effect mp3" and "slot machine jackpot sound effect mp3") and save them to your phone.
4. ntfy app → each subscribed topic → ⚙ → **Notification sound** → pick the money-counter file for the tip topic, the jackpot file for the jackpot topic, silent for drip.
5. Test: `curl -d "TEST TIP" ntfy.sh/<your-tip-topic>` — your phone should play the money counter.

## Safety posture
`money_movement_allowed: false`, `bank_access_allowed: false` — this system tracks and alerts only. Every transfer and the final purchase are owner-performed. Ledger: `telemetry/humanoid/humanoid_fund_ledger.jsonl` (append-only, created by the future ledger lane).

## Future lanes (not built yet — candidates for a later campaign)
- Ledger writer + drip/tip/jackpot sender module (reuse the forex ntfy sender)
- Dashboard tile: fund total, percent bar, ETA-to-robot at current drip rate
- Lane B wiring into the forex profit sweep once live is legitimately armed
