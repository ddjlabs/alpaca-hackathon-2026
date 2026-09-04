#!/usr/bin/env python3
"""
D5 Options Gauntlet validation — run Wed Sep 2 evening for Thu Sep 3 cards.
Re-validates every distinct (symbol, family) on the D5 desk + the mutant's spread.
Writes state/backtest_log_D5_results.json + state/backtest_log_D5.md
"""
import sys, json, datetime
sys.path.insert(0, "/mnt/agent_share/gordon/hackathon")
from options_backtest import (fetch_stock_bars, backtest_cash_secured_put,
                              backtest_credit_spread, teaching_five)

# creds from profile .env
KEY = SEC = None
with open("/home/doug/.hermes/profiles/gordon/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("HACKATHON_ALPACA_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("HACKATHON_ALPACA_SECRET="):
            SEC = line.split("=", 1)[1].strip().strip('"').strip("'")
assert KEY and SEC, "creds not found"
print(f"creds loaded: KEY={KEY[:6]}...", flush=True)

END = "2026-09-02"           # last closed session (D4)
START = "2026-03-02"         # ~6 months of 1Day bars
results = {}

def bench(sym):
    bars = fetch_stock_bars(KEY, SEC, sym, START, END, "1Day")
    if not bars:
        return None, 0
    b0, b1 = float(bars[0]["c"]), float(bars[-1]["c"])
    return (b1 / b0 - 1.0) * 100.0, len(bars)

def csp(sym, offset, prem_pct):
    bars = fetch_stock_bars(KEY, SEC, sym, START, END, "1Day")
    bm, nb = bench(sym)
    r = backtest_cash_secured_put(bars, sym, 10000, strike_offset=offset,
                                  contracts_per_trade=1, days_to_expiry=21,
                                  slippage_bps=5.0, premium_estimate_pct=prem_pct,
                                  position_pct=20.0)
    print(teaching_five(r)); print("Bench:", round(bm, 2), "| bars:", nb, flush=True)
    return r, bm

def spread(sym, width, prem_pct):
    bars = fetch_stock_bars(KEY, SEC, sym, START, END, "1Day")
    bm, nb = bench(sym)
    r = backtest_credit_spread(bars, sym, 10000, direction="bull_put",
                               wing_width=width, contracts_per_trade=1,
                               days_to_expiry=21, slippage_bps=5.0,
                               premium_estimate_pct=prem_pct, position_pct=20.0)
    print(teaching_five(r)); print("Bench:", round(bm, 2), "| bars:", nb, flush=True)
    return r, bm

# ---- CSP family: XLF (Roma/Blues books), XLU (Levene books) ----
for sym, offs in (("XLF", (2.0, 3.0)), ("XLU", (1.5, 2.0))):
    for off in offs:
        r, bm = csp(sym, off, 1.5)
        results[f"CSP {sym} {off}-off 21DTE"] = {
            "total_return_pct": round(r.total_return_pct, 2),
            "benchmark_return": round(bm, 2),
            "max_drawdown_pct": round(r.max_drawdown_pct, 2),
            "round_trips": r.num_round_trips,
            "win_rate": r.win_rate,
            "sharpe": round(r.sharpe_ratio, 3),
        }

# ---- Bull-put credit spread family: SPY (Mark Sterling, mutant) ----
# plan credit 1.30 on SPY ~765 = 0.17%; test engine's 0.55% default AND the
# conservative 0.17% case (what the plan actually collects)
for prem in (0.55, 0.17):
    r, bm = spread("SPY", 10.0, prem)
    results[f"BULL_PUT SPY 10-wide 21DTE prem={prem}%"] = {
        "total_return_pct": round(r.total_return_pct, 2),
        "benchmark_return": round(bm, 2),
        "max_drawdown_pct": round(r.max_drawdown_pct, 2),
        "round_trips": r.num_round_trips,
        "win_rate": r.win_rate,
        "sharpe": round(r.sharpe_ratio, 3),
        "max_loss_per_lot": 1000 - round(prem / 100.0 * 765.20 * 100, 0),
    }

out_json = "/mnt/agent_share/gordon/hackathon/state/backtest_log_D5_results.json"
with open(out_json, "w") as f:
    json.dump(results, f, indent=1)
print("\nWROTE", out_json)
print(json.dumps(results, indent=1))