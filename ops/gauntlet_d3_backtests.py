#!/usr/bin/env python3
"""D3 GAUNTLET part 2: Teaching Five with desk-calibrated position_pct (reserve <= full allocation)."""
import json, sys
from pathlib import Path

env = {}
for line in Path("/home/doug/.hermes/profiles/gordon/.env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1); env[k.strip()] = v.strip()
K, S = env["HACKATHON_ALPACA_KEY"], env["HACKATHON_ALPACA_SECRET"]
sys.path.insert(0, "/mnt/agent_share/gordon/hackathon")
from options_backtest import backtest_cash_secured_put, teaching_five

bars = json.loads(Path("/mnt/agent_share/gordon/hackathon/state/eod_pull/bars_20260831.json").read_text())

runs = [
    ("XLF-25d-21DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=2.5, days_to_expiry=21, position_pct=100)),
    ("XLF-30d-21DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=3.0, days_to_expiry=21, position_pct=100)),
    ("XLF-40d-21DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=4.0, days_to_expiry=21, position_pct=100)),
    ("XLF-27d-46DTE", backtest_cash_secured_put(bars["XLF"], "XLF", 10000, strike_offset=2.7, days_to_expiry=46, position_pct=100)),
    ("XLU-20d-21DTE", backtest_cash_secured_put(bars["XLU"], "XLU", 10000, strike_offset=2.0, days_to_expiry=21, position_pct=100)),
]
res = {}
for name, r in runs:
    print(f"##### {name}")
    print(teaching_five(r).strip())
    res[name] = {"total_return_pct": round(r.total_return_pct, 2), "benchmark_return": round(r.benchmark_return, 2),
                 "max_drawdown_pct": round(r.max_drawdown_pct, 2), "round_trips": r.num_round_trips,
                 "win_rate": round(r.win_rate, 1), "sharpe": round(r.sharpe_ratio, 3)}
Path("/mnt/agent_share/gordon/hackathon/state/backtest_log_D3_results.json").write_text(json.dumps(res, indent=2))
print("saved")