#!/usr/bin/env python3
"""
Market Feed Protocol Patcher — embeds market-data access instructions
into every live soul.md (via staging persona.md, same Option C pattern).
Idempotent: skips souls already containing MARKET DATA ACCESS.
"""

import sys
import re
from pathlib import Path

AGENTS_DIR = Path("/mnt/agent_share/gordon/hackathon/agents")


def section() -> str:
    return """

## MARKET DATA ACCESS (READ THE TAPE YOURSELF)

You are NOT limited to Ernie's morning wire. You can read live market data at any time
with the shared market feed CLI — same Alpaca REST the desk uses, paper credentials
pre-wired. Use it to check prices BEFORE filing a trade card (your card must cite the
current price) and to monitor your positions intraday.

CLI: python3 /mnt/agent_share/gordon/hackathon/market_feed.py

Commands (all output JSON):
  quote SPY                          -> last/bid/ask/open/high/low/volume (1 symbol)
  snapshot SPY,QQQ,XLE               -> same fields for many symbols (one call)
  bars SPY 5                         -> last 5 days of daily OHLCV
  chain SPY --expiry 2026-09-04 --calls --strikes 6
                                     -> option contracts with bid/ask/IV/delta + moneyness
  optquote <CONTRACT>                -> one contract's quote + Greeks
  crypto BTC/USD,ETH/USD 3           -> crypto bars + N-day change (weekend sessions!)
  account                           -> your fund's equity/cash/day P&L (verify before sizing)
  movers                            -> SPY/QQQ/IWM quick pulse

Workflow per trading day:
1. Read Ernie's wire (morning).
2. Before filing ANY kanban trade card: run `quote <SYMBOL>` (or `chain` for options),
   cite the live price in your card body. Cards with stale/missing price citations
   get flagged by Charlie.
3. After your execution notice: re-check `quote` hourly; if price hits your stop or
   target, file a SELL card immediately (do not wait for anyone).
4. Crypto agents: crypto trades 24/7 — `crypto BTC/USD` works all weekend. Equity
   agents: `quote` works pre-market too (data is IEX feed, 15-min delayed on free tier).
5. Rate limits are shared across all 10 agents. Pull what you need, cache mentally,
   do not poll every minute. Respect: ~1 call per decision point, not per minute.
"""


def main() -> int:
    dry = "--dry-run" in sys.argv
    patched, skipped = 0, 0
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or not agent_dir.name.startswith("agent-"):
            continue
        soul = agent_dir / "soul.md"
        if not soul.exists():
            continue
        content = soul.read_text(encoding="utf-8")
        if "MARKET DATA ACCESS" in content:
            print(f"  {agent_dir.name}: already has market access")
            continue
        if dry:
            print(f"  [dry] {agent_dir.name}: would embed")
            patched += 1
            continue
        staging = agent_dir / "persona.md"
        staging.write_text(content + section(), encoding="utf-8")
        final = staging.read_text(encoding="utf-8")
        if "MARKET DATA ACCESS" in final and "## TERMINATION" in final and "market_feed.py" in final:
            staging.replace(soul)
            patched += 1
            print(f"✅ {agent_dir.name}: market access embedded")
        else:
            skipped += 1
            print(f"⚠️  {agent_dir.name}: validation failed")
    print(f"\nPatched: {patched}, Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())