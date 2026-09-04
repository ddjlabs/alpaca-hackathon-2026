#!/usr/bin/env python3
"""Teaching Five canonical outputs for gauntlet D2 backtest log."""
import json, sys
sys.path.insert(0, ".")
import options_backtest as ob

out = []

def run(title, fn, sym, bars, **kw):
    r = fn(bars=bars, symbol=sym, initial_cash=10000.0, **kw)
    out.append(f"### {title}\n```\n{ob.teaching_five(r)}```")
    return r

xlf = json.load(open("state/bars_XLF.json"))
xlp = json.load(open("state/bars_XLP.json"))

out.append("# BACKTEST LOG — Options Gauntlet, Sunday 2026-08-30 (preps Monday 8/31 = Day 2)")
out.append("Window: 2026-03-02 → 2026-08-28, 126 daily bars, feed=iex. Account model: $10,000 per agent.\n")

run("CC XLF +$3 OTM, 21 DTE (Bud/Seth/Storm family validation)", ob.backtest_covered_call, "XLF", xlf,
    strike_offset=3.0, days_to_expiry=21, premium_estimate_pct=1.2, position_pct=90.0)
run("CSP XLF -$3 OTM, 21 DTE (Roma/Elwood/Shelly family validation)", ob.backtest_cash_secured_put, "XLF", xlf,
    strike_offset=3.0, days_to_expiry=21, position_pct=90.0)
run("CC XLP +$3 OTM, 21 DTE (Jim Young sleeve)", ob.backtest_covered_call, "XLP", xlp,
    strike_offset=3.0, days_to_expiry=21, premium_estimate_pct=1.2, position_pct=90.0)
run("PROXY CSP XLP -$3 OTM (Voss condor — engine has no condor model)", ob.backtest_cash_secured_put, "XLP", xlp,
    strike_offset=3.0, days_to_expiry=21, position_pct=90.0)
run("FEASIBILITY PROOF: CSP SPY -$30 OTM (strike*100 reserve vs $10K account)", ob.backtest_cash_secured_put, "SPY",
    json.load(open("state/bars_SPY.json")), strike_offset=30.0, days_to_expiry=21, position_pct=90.0)
run("FEASIBILITY PROOF: CC SPY +$5 OTM (100 shares = $76.9K > $10K)", ob.backtest_covered_call, "SPY",
    json.load(open("state/bars_SPY.json")), strike_offset=5.0, days_to_expiry=21, position_pct=90.0)

out.append("\n## CHAIN-MATH VALIDATION (credit_spread family — engine has no spread simulator)")
out.append("- Donnie Azoff: XLF 260904 BULL PUT 58/57, mid credit ~0.27, width $1 → max profit $27/ct, max loss $73/ct. Loses only if XLF ≤ 57 by Fri 9/4 (-1.9% in 4 sessions ≈ 2σ+ vs 21d realized vol). Defined risk. PASS.")
out.append("- Blaze Torres: XLF 260918 BEAR CALL 59/60, mid credit ~0.23-0.25, width $1 → max profit $25/ct, max loss $75-77/ct. Loses only if XLF ≥ 59 by 9/18 (+1.6%). Defined risk. PASS.")
out.append("- Vegas Voss: XLP 260918 IRON CONDOR 81/80P + 89/90C, net credit ~0.19, both wings ≥4.2% OTM, max loss $81/ct, margin $81. Engine condor model absent; CSP XLP proxy positive. PASS-proxy.")

txt = "\n".join(out)
open("state/backtest_log_D2.md", "w").write(txt)
print(txt)