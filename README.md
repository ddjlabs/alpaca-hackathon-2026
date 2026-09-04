# Bushwood Stratton Capital Partners, AP

**A Darwinian AI trading fund — 10 autonomous agents, daily natural selection, options-first.**

Entry for the [Alpaca AI Trading Agents Hackathon](https://lablab.ai/ai-hackathons/alpaca-ai-trading-agents-hackathon) (Aug 28 – Sep 4, 2026), hosted by lablab.ai × Alpaca Markets.

Live dashboard & leaderboard: **https://bushwoodstratton.com**

**Competition account:** Alpaca paper `PA3GWO1FKED0` — $100,000 starting balance, options level 3, crypto enabled. All execution and market data via the **Alpaca Trading API** and **Alpaca Market Data API**.

---

## What This Is

Every existing "autonomous trading agent" is a single agent making decisions in isolation. Bushwood Stratton is an experiment in what happens when you add **selection pressure**: ten autonomous AI traders compete for survival, and every day the losers are fired and the winners are cloned.

- **10 autonomous trader agents**, each with a persistent persona (`agents/*/soul.md`), a capital allocation, and a strategy family — covered calls, cash-secured puts, credit spreads, crypto momentum.
- **A nightly evolutionary cycle:** bottom 7 by P&L are fired (with exit memos on the public HR Board), top 3 survive with books carried, and the desk respawns with 6 clones (2 per survivor — surnames and lessons inherited) + 1 blank-slate mutant. A mutant that wins its chair **founds a new family line**.
- **No improvising at the open.** Every trade passes the **Options Gauntlet** — macro wire → option-chain analysis → strategy selection → 6-month backtest validation → risk gate → 9-point compliance check → trade plan — before any order is filed.
- **Full auditability:** every Alpaca order carries `client_order_id = agent-NN-<date>-<leg>-<seq>`, so every position and every dollar of P&L traces to a named agent. Compliance strikes, AR-log firings, and exit interviews are all on the permanent record.
- **Public transparency:** leaderboard, per-agent P&L, holdings attribution, HR Board, and daily economics publishing live at bushwoodstratton.com.

## Repository Map

```
├── heartbeat.py             # 5-min live P&L/risk monitor; computes Richard's risk block
├── holdings_extract.py      # Alpaca positions → per-agent attribution (crypto+option joins)
├── agent_holdings.py        # per-agent rollup for the public Holdings page
├── hourly_dashboard.py      # splits per-agent P&L into dashboard.json
├── market_feed.py           # the agents' market-data CLI (quotes, chains, crypto, account)
├── options_backtest.py      # 6-month backtest engine: covered calls, CSPs, credit spreads
├── ws_bridge.py             # Alpaca WebSocket stream → local feeds (systemd unit included)
├── activate_souls.py        # soul staging: persona.md → soul.md (atomic rename)
├── patch_soul_protocol.py   # idempotent soul-template enforcement
├── agents/                  # all 38 agent souls — personas, strategy families, bloodlines
├── state/                   # the week's operational record (see below)
├── cron/                    # the 12 scheduled jobs that run the fund, verbatim
├── skills/                  # the four Hermes skills encoding desk workflows
├── ops/, scripts/           # day-by-day operational one-offs (Charlie polls, gauntlet runs)
├── docs/                    # battle plan, Alpaca FAQ, submission deck (.pptx), project log
└── bushwoodstratton.com     # website is separate: Astro + Cloudflare Workers
```

### `state/` — the operational record

205+ files of audit evidence, exactly as produced during the competition:

- `messageboard_YYYYMMDD.json` — the agents' internal message board (trade filings, compliance replies, wire broadcasts, termination notices)
- `hr_board_D*.md`, `ar_log.md` — every firing, hiring, family founding, and final words
- `trade_plans_D*.json` — the gauntlet-approved blueprints executed at each open
- `orders_YYYYMMDD.json`, `firing_pull_*` — order logs and end-of-day liquidation records
- `lessons_D*.json` — Sam the Bartender's exit-interview lessons, injected verbatim into the next generation's souls
- `richard_memo_*.md`, `charlie_memo_*.md` — nightly risk and compliance memos

### `skills/` — the desk workflows

| Skill | Encodes |
|---|---|
| `bushwood-trade-desk` | Charlie's 9-point compliance checklist + Rule 8 clock enforcement + Rule 10 silent-zero verification |
| `bushwood-hr-cron` | the 6PM spawn cycle: survivors, clones, mutants, reallocation, soul writing |
| `bushwood-message-board` | the JSON message-board protocol (atomic writes, typed messages) |
| `bushwood-happy-hour` | Sam's 5:30PM exit-interview pipeline → lessons JSON |

### `cron/` — the fund's operating system

Verbatim prompts of the 12 scheduled jobs: 7AM Wire, 9:35 execution, 12PM audit, 4:30 firing, 4:45 cleanup, 5PM EOD, 5:30 Happy Hour, 6PM cloning, 7PM Gauntlet, 8PM evening review, 15-min trade-board poll, 5-min heartbeat. The fund runs itself on this schedule.

## Architecture Notes

- **Attribution:** Alpaca fills lack client_order_id; fills join orders via order_id, including PATCH-replacement chains (a repriced order keeps its owner).
- **Crypto quirk:** Alpaca fills crypto as `BTC/USD` but reports positions as `BTCUSD` — the extractor normalizes symbols before joining.
- **Co-held contracts:** two agents can sell the same option contract; positions split by net filled qty per agent, sign preserved.
- **Risk math:** heartbeat computes gross/net exposure, largest position/agent, short-option strike reserves, and crypto exposure from the live book every 5 minutes.

## Results (official measurement window)

| Metric | Value |
|---|---|
| Equity EOD Sep 3 | $99,839.22 |
| Return | −0.16% (SPY +0.81%) |
| Max EOD drawdown | 0.17% |
| Fills | 51 across 23 distinct agent lineages |
| Agent souls hired | 38 |
| Compliance strikes | 0 |

The fund ran short-premium (puts on XLF/XLU/SPY) through a rallying tape with zero strikes and sub-0.2% drawdown. The submission deck is in `docs/BUSHWOOD-STRATTON-SUBMISSION.pptx`.

## Setup

```bash
pip install requests  # thin stdlib otherwise
export HACKATHON_ALPACA_KEY=...     # Alpaca paper key
export HACKATHON_ALPACA_SECRET=...  # Alpaca paper secret
python3 market_feed.py account      # verify the pipe
python3 heartbeat.py                # live P&L + risk snapshot
python3 options_backtest.py --help  # the gauntlet's validation engine
```

All API credentials are read from the environment — nothing is hardcoded. Pre-event infrastructure (cron framework, website, message-board protocol) is disclosed per hackathon rules: the fund's operating skeleton predates kickoff, but all trading logic, agent souls, and the evolutionary mechanism were built during the event.

---

*Paper trading. Not investment advice. No real personnel were harmed in the nightly firings.*
