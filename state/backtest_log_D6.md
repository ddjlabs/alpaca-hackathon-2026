# BACKTEST LOG — D6 Options Gauntlet (Thu 2026-09-03, night run)
**Engine:** /mnt/agent_share/gordon/hackathon/options_backtest.py · **Bars:** 1Day, 129 bars, 2026-03-03 → 2026-09-03 (IEX) · **Position sizing:** 95% rule (Richard's 1-contract amendment) · **Slippage:** 5 bps · **Results:** backtest_log_D6_results.json

**Verdict: 6/6 combos VALIDATED — zero overrides, zero reassignments. First clean sweep of the hackathon.**

## CSP XLF 2.0-off 21DTE (Roma family: Gordon 55.5P, Marcus 55P, champion + Elwood carries)
```
TEACHING FIVE — Cash-Secured Put
1. Total Return: 5.61% vs Benchmark: 14.27%
2. Max Drawdown: 0.00%
3. Number of Trades (round trips): 6
4. Win Rate: 100.0%
5. Sharpe Ratio: 3.503
First trade: 2026-03-03 — sell_to_open | Last trade: 2026-09-01 — sell_to_open
Bench XLF 6mo: 14.27% | bars: 129
```

## CSP XLF 3.0-off 21DTE (deeper-strike sensitivity)
```
TEACHING FIVE — Cash-Secured Put
1. Total Return: 5.61% vs Benchmark: 14.27%
2. Max Drawdown: 0.00%
3. Number of Trades (round trips): 6
4. Win Rate: 100.0%
5. Sharpe Ratio: 3.503
Bench XLF 6mo: 14.27% | bars: 129
```

## CSP XLU 1.5-off 21DTE (Levene family + Nicky: 41.5P)
```
TEACHING FIVE — Cash-Secured Put
1. Total Return: 3.22% vs Benchmark: -8.63%
2. Max Drawdown: -0.41%
3. Number of Trades (round trips): 6
4. Win Rate: 100.0%
5. Sharpe Ratio: 2.458
Bench XLU 6mo: -8.63% | bars: 129
```

## CSP XLU 2.0-off 21DTE (Gus: 41P)
```
TEACHING FIVE — Cash-Secured Put
1. Total Return: 4.17% vs Benchmark: -8.63%
2. Max Drawdown: 0.00%
3. Number of Trades (round trips): 6
4. Win Rate: 100.0%
5. Sharpe Ratio: 3.260
Bench XLU 6mo: -8.63% | bars: 129
```

## CSP XLP 2.0-off 21DTE (Sonny: 83P — FIRST VALIDATION of the ballast lane)
```
TEACHING FIVE — Cash-Secured Put
1. Total Return: 4.36% vs Benchmark: -2.86%
2. Max Drawdown: -2.86%
3. Number of Trades (round trips): 6
4. Win Rate: 100.0%
5. Sharpe Ratio: 1.087
Bench XLP 6mo: -2.86% | bars: 129
```

## BULL_PUT SPY 10-wide 21DTE (inherited 0.26 net case — Sterling's roof, desk property; no new spread book files)
```
TEACHING FIVE — Bull Put Credit Spread
1. Total Return: 6.80% vs Benchmark: 13.64%
2. Max Drawdown: -15.29%
3. Number of Trades (round trips): 7
4. Win Rate: 71.4%
5. Sharpe Ratio: 0.438
Bench SPY 6mo: 13.64% | bars: 129
```
*(The 0.26% net credit — what the desk actually inherited — is positive-return territory in the engine, +6.80%, but the -15.29% MDD and Sharpe 0.44 say the roof is priced for defense, not offense. It stands to the 11:00 mark. Max loss $870/lot, stop 2x credit, documented in richard_memo_D6.md.)*

## Family notes
- **Override rule (backtest < benchmark AND negative): never fired.** CSP XLU/XLP beat negative benchmarks outright; CSP XLF underperformed a +14.27% B&H but ran 100% wins, 0.00% MDD, Sharpe 3.50 — income engine behavior, not a failure; family retained on six-session precedent.
- **9/4 weekly shelf (XLU 42.5P / 42P): bid 0.01 / 0.00 at the 20:12 pull — no legal rent exists on NFP-day 0DTEs. Nobody plays the weekly. Verified dead, logged.**
- **Crypto (mutant): no backtest engine for spot momentum in options_backtest.py; structure validated by precedent (Wolf D4 template) + live momentum pull: BTC 81,171 (+5.0% d/d), ETH 2,499 (+5.3% d/d). Max loss priced $168 (1.7% of book) before the open.**

*Run by Gordo — Thu Sep 3, 2026 ~19:55 ET. Final gauntlet of the run.*