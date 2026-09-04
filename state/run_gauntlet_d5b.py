#!/usr/bin/env python3
"""D5 CSP validation, corrected position_pct=95 (Richard's 1-contract/95% rule)."""
import sys, json
sys.path.insert(0, "/mnt/agent_share/gordon/hackathon")
from options_backtest import fetch_stock_bars, backtest_cash_secured_put, teaching_five

KEY = SEC = None
with open("/home/doug/.hermes/profiles/gordon/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("HACKATHON_ALPACA_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("HACKATHON_ALPACA_SECRET="):
            SEC = line.split("=", 1)[1].strip().strip('"').strip("'")

END, START = "2026-09-02", "2026-03-02"
results = {}

def bench(sym):
    bars = fetch_stock_bars(KEY, SEC, sym, START, END, "1Day")
    return (float(bars[-1]["c"]) / float(bars[0]["c"]) - 1.0) * 100.0, len(bars)

for sym, offs, prems in (("XLF", (2.0, 3.0), (1.5, 1.5)), ("XLU", (1.5, 2.0), (1.5, 1.5))):
    for off, prem in zip(offs, prems):
        bars = fetch_stock_bars(KEY, SEC, sym, START, END, "1Day")
        bm, nb = bench(sym)
        r = backtest_cash_secured_put(bars, sym, 10000, strike_offset=off,
                                      contracts_per_trade=1, days_to_expiry=21,
                                      slippage_bps=5.0, premium_estimate_pct=prem,
                                      position_pct=95.0)
        print(f"=== CSP {sym} {off}-off ==="); print(teaching_five(r))
        print("Bench:", round(bm, 2), "| bars:", nb, flush=True)
        results[f"CSP {sym} {off}-off 21DTE"] = {
            "total_return_pct": round(r.total_return_pct, 2),
            "benchmark_return": round(bm, 2),
            "max_drawdown_pct": round(r.max_drawdown_pct, 2),
            "round_trips": r.num_round_trips,
            "win_rate": r.win_rate,
            "sharpe": round(r.sharpe_ratio, 3),
        }

out = "/mnt/agent_share/gordon/hackathon/state/backtest_log_D5_results.json"
prev = json.load(open(out))
prev.update(results)
json.dump(prev, open(out, "w"), indent=1)
print("UPDATED", out); print(json.dumps(results, indent=1))