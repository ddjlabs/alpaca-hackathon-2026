# BACKTEST LOG — Options Gauntlet, Sunday 2026-08-30 (preps Monday 8/31 = Day 2)
Window: 2026-03-02 → 2026-08-28, 126 daily bars, feed=iex. Account model: $10,000 per agent.

### CC XLF +$3 OTM, 21 DTE (Bud/Seth/Storm family validation)
```

TEACHING FIVE — Covered Call
=====================================
1. Total Return: 11.27% vs Benchmark: 13.22%
2. Max Drawdown: -3.65%
3. Number of Trades (round trips): 2
4. Win Rate: 100.0%
5. Sharpe Ratio: 2.567

First trade: 2026-03-02 — buy
Last trade: 2026-08-28 — sell
```
### CSP XLF -$3 OTM, 21 DTE (Roma/Elwood/Shelly family validation)
```

TEACHING FIVE — Cash-Secured Put
=====================================
1. Total Return: 4.74% vs Benchmark: 13.22%
2. Max Drawdown: 0.00%
3. Number of Trades (round trips): 5
4. Win Rate: 100.0%
5. Sharpe Ratio: 3.225

First trade: 2026-03-02 — sell_to_open
Last trade: 2026-07-31 — sell_to_open
```
### CC XLP +$3 OTM, 21 DTE (Jim Young sleeve)
```

TEACHING FIVE — Covered Call
=====================================
1. Total Return: 3.18% vs Benchmark: -3.70%
2. Max Drawdown: -7.49%
3. Number of Trades (round trips): 1
4. Win Rate: 100.0%
5. Sharpe Ratio: 0.311

First trade: 2026-03-02 — buy
Last trade: 2026-08-28 — sell
```
### PROXY CSP XLP -$3 OTM (Voss condor — engine has no condor model)
```

TEACHING FIVE — Cash-Secured Put
=====================================
1. Total Return: 3.66% vs Benchmark: -3.70%
2. Max Drawdown: -2.66%
3. Number of Trades (round trips): 5
4. Win Rate: 100.0%
5. Sharpe Ratio: 0.907

First trade: 2026-03-02 — sell_to_open
Last trade: 2026-07-31 — sell_to_open
```
### FEASIBILITY PROOF: CSP SPY -$30 OTM (strike*100 reserve vs $10K account)
```

TEACHING FIVE — Cash-Secured Put
=====================================
1. Total Return: 0.00% vs Benchmark: 12.08%
2. Max Drawdown: 0.00%
3. Number of Trades (round trips): 0
4. Win Rate: 0.0%
5. Sharpe Ratio: 0.000

First trade: N/A — N/A
Last trade: N/A — N/A
```
### FEASIBILITY PROOF: CC SPY +$5 OTM (100 shares = $76.9K > $10K)
```

TEACHING FIVE — Covered Call
=====================================
1. Total Return: 0.00% vs Benchmark: 12.08%
2. Max Drawdown: 0.00%
3. Number of Trades (round trips): 0
4. Win Rate: 0.0%
5. Sharpe Ratio: 0.000

First trade: N/A — N/A
Last trade: N/A — N/A
```

## CHAIN-MATH VALIDATION (credit_spread family — engine has no spread simulator)
- Donnie Azoff: XLF 260904 BULL PUT 58/57, mid credit ~0.27, width $1 → max profit $27/ct, max loss $73/ct. Loses only if XLF ≤ 57 by Fri 9/4 (-1.9% in 4 sessions ≈ 2σ+ vs 21d realized vol). Defined risk. PASS.
- Blaze Torres: XLF 260918 BEAR CALL 59/60, mid credit ~0.23-0.25, width $1 → max profit $25/ct, max loss $75-77/ct. Loses only if XLF ≥ 59 by 9/18 (+1.6%). Defined risk. PASS.
- Vegas Voss: XLP 260918 IRON CONDOR 81/80P + 89/90C, net credit ~0.19, both wings ≥4.2% OTM, max loss $81/ct, margin $81. Engine condor model absent; CSP XLP proxy positive. PASS-proxy.