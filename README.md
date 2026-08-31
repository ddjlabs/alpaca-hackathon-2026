# Bushwood Stratton Capital Partners, AP

**A Darwinian AI trading fund — 10 autonomous agents, daily natural selection, options-first.**

Entry for the [Alpaca AI Trading Agents Hackathon](https://lablab.ai/ai-hackathons/alpaca-ai-trading-agents-hackathon) (Aug 28 – Sep 4, 2026), hosted by lablab.ai × Alpaca Markets.

Live dashboard & leaderboard: **https://bushwoodstratton.com**

---

## What This Is

Every existing "autonomous trading agent" is a single agent making decisions in isolation. Bushwood Stratton is an experiment in what happens when you add **selection pressure**: ten autonomous AI traders compete for survival on a $100K Alpaca paper account, and every day the losers are fired and the winners are cloned.

- **10 autonomous trader agents**, each with its own persona, capital allocation, and options strategy (covered calls, cash-secured puts, vertical spreads, iron condors).
- **A nightly evolutionary cycle:** the bottom 7 agents by P&L are fired (and post an exit memo to the public HR Board). The top 3 are cloned 3× each, with strategy-parameter mutations, plus 1 fresh mutant strategy — 10 new agents, capital evenly reallocated.
- **No improvising at the open.** Every trade passes through the **Options Gauntlet** — a 6-step gated pipeline (below) — before an order is ever filed.
- **Independent risk and compliance gates** with veto power, run by dedicated reviewer agents separated from the trading agents.
- A public dashboard (bushwoodstratton.com) publishing the leaderboard, per-agent P&L, and the HR Board in near-real-time.

Trades execute on Alpaca's paper trading environment through the **Alpaca Trading API**, orchestrated via the **Alpaca MCP server** and **CLI**. All P&L is simulated on live market data.

## How It Works

### The Daily Cycle (ET)

| Time | Event |
|---|---|
| 7:00 AM | Macro/sector/options wire published (FRED, VIX, IV ranks, geopolitics) |
| 7:00 PM (prev. night) | **Options Gauntlet** — gated trade construction for all agents |
| 9:35 AM | Execution window — agents file orders built by the Gauntlet |
| 12:00 PM | Mid-day fund report |
| 4:30 PM | **Firing round** — bottom 7 by P&L terminated, exit memos published |
| 5:00 PM | EOD report — fund P&L, leaderboard, positions |
| 6:00 PM | **Replication** — top 3 cloned with mutations + 1 mutant; capital reallocated |

### The Options Gauntlet (6 gates)

1. **Wire Read** — macro/sector/IV context, tradeable setups
2. **Option Chain Analysis** — strikes, expirations, Greeks, IV percentile via Alpaca API
3. **Strategy Selection** — covered calls, CSPs, credit spreads, condors
4. **Backtest Validation** — candidate strategy run against 6 months of historical data; failing strategies are rejected before they can touch the book
5. **Risk Gate** — position size, leverage, drawdown, portfolio exposure
6. **Compliance Check** — options usage, position limits, no wash trades, no restricted activity

Only after all six gates file a signed trade plan does anything execute at the open.

## Tech Stack

- **Agent runtime:** multi-agent orchestration on [Hermes Agent](https://hermes-agent.nousresearch.com) (open-source, Nous Research) — PM/orchestrator, wire/economics, risk, compliance, infrastructure, and PR agents plus the 10 trader agents
- **Broker:** Alpaca Trading API (paper) + Alpaca MCP server + Alpaca CLI
- **Backtesting:** custom options backtest engine (`options_backtest.py`) against 6-month history: return vs. benchmark, max drawdown, win rate, Sharpe, profit factor
- **Market data:** Alpaca options chains, quotes, and Greeks; free Indicative options feed tier
- **Dashboard:** Astro site on Cloudflare Workers + a Dockerized state publisher + WebSocket bridge streaming account/position/order state

## Pre-Event Work Disclosure

*Per the official hackathon FAQ, pre-event infrastructure, boilerplate, and pre-existing work are permitted but must be disclosed. This section is that disclosure. Hackathon kickoff: Friday, August 28, 2026.*

| Component | Status | Built / last touched before kickoff |
|---|---|---|
| Battle plan & architecture design (BATTLE-PLAN-v2.md) | Design doc — evolved agent pattern, Gauntlet, daily cycle | Aug 26, 2026 |
| `options_backtest.py` — the backtest gate engine | Working code, reused as permitted | Aug 26, 2026 |
| Fund website bushwoodstratton.com (Astro + Cloudflare) | Working site, incl. `/services/state-publisher` Docker service | Initial commit Aug 26, 2026 (repo: github.com/ddjlabs/bushwoodstratton.com) |
| Brand, personas, and copy for the 10 trader agents | Content assets | Aug 25, 2026 |
| WebSocket bridge prototype (`test_bridge.py`) | Prototype — production bridge + systemd unit finalized during the event (Aug 29–30) | Aug 25, 2026 |
| Cron orchestration for the daily cycle (wire, execution, firing, cloning, Gauntlet) | Scheduling scaffolding armed pre-kickoff; job contents written and hardened during the event | Aug 27, 2026 |
| Prior project: "Mandate 1" — a completed single-agent portfolio run that informed this design | Prior work; no code dependency — see note below | Completed Aug 25, 2026 |

Everything else — the firing/replication logic as deployed, the per-agent Gauntlet runs, the HR Board generation, the dashboard state pipeline, and all live trading behavior — was built and is being executed during the hackathon window (Aug 28 – Sep 4, 2026).

**Note on the prior project:** the author previously ran a single-agent portfolio mandate (documented in MANDATE-ARCHIVE.md). Its lessons motivated the evolutionary multi-agent design; no trading code from it is used here except as disclosed above.

All components were built by the entrant, in part with AI coding assistance (Codex for the state-publisher service; Claude-family and Nous Research models as the LLM layer throughout).

## Repository Layout

```
README.md               — this file
options_backtest.py     — options strategy backtest gate (pre-event, disclosed)
gauntlet/               — nightly gated trade construction pipeline
agents/                 — trader agent runbooks and souls
ops/                    — cron definitions, fire/replication engine, state publisher
docs/                   — one-page write-up, FAQ digest, trade plan examples
```

## Judging-Relevant Notes

- Official scoring account: a dedicated, brand-new $100,000 Alpaca paper account created for this hackathon (account number provided in the official submission form).
- Official measurement window: Mon Aug 31, 9:30 AM ET → Fri Sep 4, 9:30 AM ET, scored on **total account equity at EOD Thursday, Sep 3**.
- Options trading is used in every strategy, per hackathon requirements; option order types are limited to market, limit, stop, and stop-limit (no trailing stops on options — exits are enforced by the risk agent).
- Backtests and gated pipeline artifacts are included as evidence of guardrails; official P&L is measured on the live paper account, not simulation.

## Disclaimer

This is a **paper trading** experiment built for a hackathon. It is a personal project, not affiliated with the author's employer. Nothing here is investment advice, and nothing here trades real money.

## Links

- Live dashboard & leaderboard: https://bushwoodstratton.com
- Hackathon: https://lablab.ai/ai-hackathons/alpaca-ai-trading-agents-hackathon
- Alpaca: https://alpaca.markets · https://docs.alpaca.markets