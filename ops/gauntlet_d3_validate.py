#!/usr/bin/env python3
"""D3 GAUNTLET (Mon 8/31 19:xx ET): verify book + refresh bars + Teaching Five per (symbol, family).
Preps Tuesday 9/1 = Day 3. Never prints secrets."""
import json, sys, urllib.request
from pathlib import Path

env = {}
for line in Path("/home/doug/.hermes/profiles/gordon/.env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1); env[k.strip()] = v.strip()
K, S = env["HACKATHON_ALPACA_KEY"], env["HACKATHON_ALPACA_SECRET"]
assert K and S
sys.path.insert(0, "/mnt/agent_share/gordon/hackathon")
from options_backtest import fetch_stock_bars, backtest_cash_secured_put, teaching_five

def get(url):
    req = urllib.request.Request(url, headers={"APCA-API-KEY-ID": K, "APCA-API-SECRET-KEY": S})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

# 1) Account identity
a = get("https://paper-api.alpaca.markets/v2/account")
print("ACCOUNT:", a.get("account_number"), "| status", a.get("status"), "| blocked", a.get("trading_blocked"),
      "| equity", a.get("equity"), "| cash", a.get("cash"))

# 2) Open orders (orphan closers should rest here)
ords = get("https://paper-api.alpaca.markets/v2/orders?status=open&limit=100")
print("OPEN ORDERS:", len(ords))
for o in ords:
    print("  ", o.get("client_order_id"), "|", o.get("symbol"), o.get("side"), o.get("qty"), o.get("type"),
          o.get("time_in_force"), "| created", (o.get("created_at") or "")[:16])

# 3) Positions
try:
    pos = get("https://paper-api.alpaca.markets/v2/positions")
    print("POSITIONS:", len(pos))
    for p in pos:
        print("  ", p.get("symbol"), p.get("qty"), "@avg", p.get("avg_entry_price"), "| mkt", p.get("market_value"))
except Exception as e:
    print("positions:", e)

# 4) Bars through Monday close
bars = {}
for sym in ["XLF", "XLU", "XLP"]:
    bars[sym] = fetch_stock_bars(K, S, sym, "2026-03-02", "2026-08-31")
    b = bars[sym]
    print(f"BARS {sym}: {len(b)}  first {b[0]['t'][:10]}  last {b[-1]['t'][:10]}  lastclose {b[-1]['c']}")
Path("/mnt/agent_share/gordon/hackathon/state/eod_pull/bars_20260831.json").write_text(json.dumps(bars))

# 5) Teaching Five per distinct (symbol, strategy) combo
runs = [
    ("XLF-25d-21DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=2.5, days_to_expiry=21)),
    ("XLF-30d-21DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=3.0, days_to_expiry=21)),
    ("XLF-40d-21DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=4.0, days_to_expiry=21)),
    ("XLF-27d-46DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=2.7, days_to_expiry=46)),
    ("XLU-20d-21DTE", backtest_cash_secured_put(bars["XLU"], "XLU", 10000, strike_offset=2.0, days_to_expiry=21)),
]
res = {}
for name, r in runs:
    print(f"\n##### {name}")
    print(teaching_five(r).strip())
    res[name] = {"total_return_pct": round(r.total_return_pct, 2), "benchmark_return": round(r.benchmark_return, 2),
                 "max_drawdown_pct": round(r.max_drawdown_pct, 2), "round_trips": r.num_round_trips,
                 "win_rate": round(r.win_rate, 1), "sharpe": round(r.sharpe_ratio, 3)}
print("\nCOMPACT:", json.dumps(res, indent=1))
Path("/mnt/agent_share/gordon/hackathon/state/backtest_log_D3_results.json").write_text(json.dumps(res, indent=2))
print("saved state/backtest_log_D3_results.json")