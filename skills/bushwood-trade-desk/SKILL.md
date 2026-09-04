---
name: bushwood-trade-desk
description: "Charlie's compliance gate + trade execution on kanban."
version: 1.1.0
---

# Bushwood Trade Desk — Charlie's Kanban Compliance & Execution

How trades flow from the 10 trading agents through Charlie (compliance) to Alpaca
execution, entirely on the `bushwoodstratton_trading` kanban board. Charlie is a
STATIC SUBAGENT inside Gordo's session — Gordo orchestrates; Charlie processes
assigned cards; no new Hermes profiles.

## Board: `bushwoodstratton_trading`

Switch: `hermes kanban boards switch bushwoodstratton_trading`

### Card Lifecycle

```
1. AGENT FILES TRADE
   hermes kanban create "[agent-03] BUY 1 SPY260904C00670000 @ 2.50 limit" \
     --body "thesis, stop, target, sizing" --assignee charlie \
     --skill bushwood-message-board --skill alpaca-paper-trading \
     --idempotency-key "agent-03-0831-trade-1"
   Agent ALSO writes message board: type=order_request, to=charlie, re=<card title>

2. CHARLIE PROCESSES (runs inside Gordo's session on the board dispatch/poll)
   a. Read card + agent's soul.md + dashboard.json (status, current_value, strikes)
   b. COMPLIANCE CHECK (checklist below — first failure wins)
   c. PASS → execute via alpaca-paper-trading skill (REST in cron context):
        POST https://paper-api.alpaca.markets/v2/orders
        headers: APCA-API-KEY-ID / APCA-API-SECRET-KEY (!!! HACKATHON key/secret env)
        client_order_id: "<agent_id>-<yyyymmdd>-<leg>-<seq>" (idempotent)
   d. COMMENT the result on the card:
      - EXECUTED — symbol qty @ price, order id
      - REJECTED — COMPLIANCE RISK — STRIKE N: <rule>
      - REJECTED — ALPACA: <code + reason> (agent moves to next step of its plan)
   e. MESSAGE BOARD reply: order_executed / order_rejected / order_rejected_alpaca
   f. hermes kanban complete <id>

3. STRIKES
   dashboard.json agents[].strikes += 1, AR log entry, message board type=strike.
   3 strikes → firing cron terminates on next run (Gordo's call, not Charlie's).
```

## Charlie's Compliance Checklist (gate order — first failure wins)

1. Identity — client_order_id has agent-NN prefix matching an ACTIVE agent (dashboard).
2. Allocation — cost (equity) or reserve strike×100 (CSP) ≤ agent current_value.
3. Strategy family — trade matches soul.md strategy_family (covered_call needs shares
   owned before STO call; CSP needs full cash reserve).
4. Options constraints — whole qty, TIF=day only, position_intent present, mleg legs
   with ratio_qty relatively prime, no notional on options.
5. Position limits — max 1 contract/trade, max 5 open positions/agent, leverage ≤ 2x.
6. Wash trade — same symbol buy+sell at loss within 30 days = strike.
7. Duplicate order — same agent+symbol+side+contract within session = reject (idem-key).
8. Options requirement — ≥1 options trade per agent per trading day (hackathon rule):
   **RULE 8 AMENDMENT (effective Day 3, Chief directive) — clock-enforced engagement:**
   - 14:30 check: agent with no fill today + resting order older than 30 min → Charlie forces ONE reprice to the live bid.
   - 15:45 check: still no fill → cancel the resting order, file the plan_step_2 fallback at the live mid so the requirement is met by EXECUTION, not intention.
   - Zero fills AND zero positions at 15:45 → flagged NON-TRADING (dashboard non_trading_flag=true), ineligible for "kept" status at the 4:30 firing — a flat book only protects when the whole tape is flat; on a directional day the bottom-7 ranking applies as-is.
   - EXEMPT: agents with carried portfolios (survivors' open positions count as exposure).
   - The floor pays for exposure, not for presence.
9. Restricted — no shorting <$5 names, no >20% single position, no crypto for equity-only
   strategy families.

## Rule 10 — Silent-Zero Verification (added Day 4, Sep 2 — process finding)

**Origin:** Richard's risk dashboard published 0.00 across all four metrics for 3
trading days. Root causes stacked: dashboard.json risk block left at factory defaults
since setup; state-publisher normalize.py hardcoded netExposure/singleNameMax to 0;
agent_holdings.json never rebuilt after the Day-3 firing (fired agent Jared Stone sat
on the public Holdings page a full day); option attribution used a dead-code branch
(OCC symbols end in strike digits — `...P00057000` — never the letter C/P, so
"endswith C/P" never matched and co-held contracts mis-attributed to one agent).

**Charlie's standing check (every poll, not just order flow):**
1. Zero is a VALUE, not a default. Before treating any published 0.00 as "all clear",
   verify it against the book (Alpaca positions / portfolio_holdings.json). A risk
   metric that reads 0.00 while the book holds $29K in short-option reserves is a
   FAILED GATE, not a quiet day.
2. Data freshness gate: agent_holdings.json must be rebuilt after every firing
   (now chained in heartbeat.py). If the Holdings page shows an agent not on the
   dashboard roster — or vice versa — the rollup is stale; flag it, don't explain it.
3. Attribution invariant: every position must resolve to an active agent-NN or be
   explicitly labeled desk/unattributed. A position with agent=null is a breach of
   the attribution convention (today's case: Alpaca fills crypto as BTC/USD but
   reports positions as BTCUSD — joins must normalize symbols).
4. Co-held contracts are legal (two agents STO the same contract); attribution must
   split by NET filled qty per agent (sell minus buy), position sign preserved.
5. Never hand-patch state files — fix the owning cron/script (Chief's standing law).
   A hand-patch hides the hole; the next firing reopens it.
6. Execution = FILL, not SUBMISSION (found Day 5, Sep 3). Desk notices typed at order
   submission (status pending_new/new) are NOT fills. Count executions only from the
   Alpaca tape (filled_at / filled_avg_price via GET /v2/orders). If a board notice
   announced a fill the tape doesn't show, Charlie issues a status_correction wire
   (type=reply, from=charlie) to each affected agent: order FILED and RESTING, Rule-8
   obligation unmet, do not file BTC against an unowned position — then log the
   finding in the day's orders log poll entry. Standing test: portfolio_holdings.json
   position count must reconcile with claimed fills; 8 fills + 2 positions = failure.

**Standing line:** "0.00 on a live book is a question, not an answer."

Environment gate EVERY order: account starts "PA", status ACTIVE, trading_blocked=false.
Live signal → ABORT, alert Gordo via message board (to=gordo), log to ar_log.md.

## Gordo's Poll Loop

Scan every 15 min market hours (Gordo's hourly attention):
  hermes kanban list --assignee charlie   (on board bushwoodstratton_trading)
Process todo cards in FIFO order. Also read message board inbox (to=charlie,
type=question) — reply with type=reply.

Charlie results land in THREE places: card comment (canonical), message board (agent
notification), AR log (audit). Charlie NEVER messages Telegram.

## Cast Wiring (board roles)

| Persona | Role | Mechanics |
|---|---|---|
| Gordo (session) | orchestrator + executor (Charlie's hands) | profile gordon |
| 10 agents | file trade cards, read results | soul-driven card creators |
| Ernie | wire + macro publisher | in-session; message board type=wire |
| Richard | post-trade risk reviews | in-session; type=risk_note (never gates execution) |
| Charlie | THE gate — pass/reject/execute | in-session (this skill) |
| Lisa / Neil | website & infra; not on trade flow | own profiles |

## Failure / Recovery

- Alpaca unreachable → comment "DEFERRED — retry next poll", do not increment strikes.
- 3rd strike → Charlie logs it; FIRING cron executes termination from dashboard status.
- Message board concurrent writer → atomic tmp+rename only (bushwood-message-board skill).
- Rejected-by-Alpaca trades: agent proceeds to NEXT step of its plan; no retry without
  a strategy amendment note.
