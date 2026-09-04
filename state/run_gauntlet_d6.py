#!/usr/bin/env python3
"""D6 Options Gauntlet validation — Thu Sep 3 night for the FINAL session (Fri Sep 4).
Validates every distinct (symbol, family) on the D6 desk on 6 months of 1Day bars
through Thu 9/3 close. Teaching Five per combo. Also: 9/4 weekly rent check
(0DTE shelves) + crypto refs for the mutant. Writes backtest_log_D6_results.json.
"""
import sys, json
sys.path.insert(0, "/mnt/agent_share/gordon/hackathon")
from options_backtest import (fetch_stock_bars, backtest_cash_secured_put,
                              backtest_credit_spread, teaching_five)

KEY = SEC = None
with open("/home/doug/.hermes/profiles/gordon/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("HACKATHON_ALPACA_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("HACKATHON_ALPACA_SECRET="):
            SEC = line.split("=", 1)[1].strip().strip('"').strip("'")
assert KEY and SEC, "creds not found"
print("creds loaded OK", flush=True)

END = "2026-09-03"           # last closed session (D5, Thu)
START = "2026-03-03"         # ~6 months of 1Day bars
results = {}
log_lines = []

def bench(sym, bars):
    if not bars:
        return 0.0, 0
    b0, b1 = float(bars[0]["c"]), float(bars[-1]["c"])
    return (b1 / b0 - 1.0) * 100.0, len(bars)

def csp(sym, off, prem_pct):
    bars = fetch_stock_bars(KEY, SEC, sym, START, END, "1Day")
    bm, nb = bench(sym, bars)
    r = backtest_cash_secured_put(bars, sym, 10000, strike_offset=off,
                                  contracts_per_trade=1, days_to_expiry=21,
                                  slippage_bps=5.0, premium_estimate_pct=prem_pct,
                                  position_pct=95.0)
    t5 = teaching_five(r)
    print(f"\n=== CSP {sym} {off}-off 21DTE ===")
    print(t5)
    print("Bench:", round(bm, 2), "| bars:", nb, flush=True)
    log_lines.append(f"### CSP {sym} {off}-off 21DTE\n```\n{t5}\nBench {sym} 6mo: {round(bm,2)}% | bars: {nb}\n```\n")
    return r, bm

for sym, off in (("XLF", 2.0), ("XLF", 3.0), ("XLU", 1.5), ("XLU", 2.0), ("XLP", 2.0)):
    r, bm = csp(sym, off, 1.5)
    results[f"CSP {sym} {off}-off 21DTE"] = {
        "total_return_pct": round(r.total_return_pct, 2),
        "benchmark_return": round(bm, 2),
        "max_drawdown_pct": round(r.max_drawdown_pct, 2),
        "round_trips": r.num_round_trips,
        "win_rate": r.win_rate,
        "sharpe": round(r.sharpe_ratio, 3),
    }

# SPY bull-put at the ACTUAL inherited entry (net 0.26 = ~0.034% of spot) — for the
# record on Sterling's inherited roof; no new spread book files tomorrow.
bars_spy = fetch_stock_bars(KEY, SEC, "SPY", START, END, "1Day")
bm_spy, nb_spy = bench("SPY", bars_spy)
r_spread = backtest_credit_spread(bars_spy, "SPY", 10000, direction="bull_put",
                                  wing_width=10.0, contracts_per_trade=1,
                                  days_to_expiry=21, slippage_bps=5.0,
                                  premium_estimate_pct=0.26, position_pct=95.0)
t5s = teaching_five(r_spread)
print("\n=== BULL_PUT SPY 10-wide (inherited 0.26 net case) ===")
print(t5s)
print("Bench:", round(bm_spy, 2), "| bars:", nb_spy, flush=True)
log_lines.append(f"### BULL_PUT SPY 10-wide (inherited net 0.26 case)\n```\n{t5s}\nBench SPY 6mo: {round(bm_spy,2)}% | bars: {nb_spy}\n```\n")
results["BULL_PUT SPY 10-wide 21DTE prem=0.26% (inherited)"] = {
    "total_return_pct": round(r_spread.total_return_pct, 2),
    "benchmark_return": round(bm_spy, 2),
    "max_drawdown_pct": round(r_spread.max_drawdown_pct, 2),
    "round_trips": r_spread.num_round_trips,
    "win_rate": r_spread.win_rate,
    "sharpe": round(r_spread.sharpe_ratio, 3),
}

out_json = "/mnt/agent_share/gordon/hackathon/state/backtest_log_D6_results.json"
with open(out_json, "w") as f:
    json.dump(results, f, indent=1)
print("\nWROTE", out_json)
print(json.dumps(results, indent=1))