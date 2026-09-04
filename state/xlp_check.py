#!/usr/bin/env python3
"""Check XLP as second sleeve: bars, snapshot, chain liquidity."""
import os, json, urllib.request
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
key = os.getenv('HACKATHON_ALPACA_KEY'); sec = os.getenv('HACKATHON_ALPACA_SECRET')
H = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec}

def get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())

# bars 6mo
d = get("https://data.alpaca.markets/v2/stocks/XLP/bars?timeframe=1Day&start=2026-03-02&end=2026-08-28&feed=iex&adjustment=raw&limit=1000")
bars = d.get("bars") if isinstance(d, dict) else d
if isinstance(bars, dict): bars = bars.get("XLP", [])
json.dump(bars, open("state/bars_XLP.json", "w"))
c0, c1 = float(bars[0]["c"]), float(bars[-1]["c"])
print(f"XLP: {len(bars)} bars, {bars[0]['t'][:10]} {c0:.2f} -> {bars[-1]['t'][:10]} {c1:.2f} | 6mo {(c1/c0-1)*100:.2f}%")
spot = c1

# chain
all_snaps = {}
token = None
for page in range(8):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/XLP?limit=1000&feed=indicative" + (f"&page_token={token}" if token else "")
    d = get(url)
    all_snaps.update(d.get("snapshots", {}))
    token = d.get("next_page_token")
    if not token: break
print("XLP chain snapshots:", len(all_snaps))
json.dump(all_snaps, open("/tmp/chain_XLP.json", "w"))

by = defaultdict(lambda: {"C": [], "P": []})
for k, s in all_snaps.items():
    exp, typ = k[3:9], k[9]
    try: strike = int(k[10:]) / 1000
    except Exception: continue
    q = s.get("latestQuote") or {}
    bp, ap = q.get("bp") or 0, q.get("ap") or 0
    mid = (bp + ap) / 2 if (bp and ap) else None
    width = (ap - bp) if (bp and ap) else None
    by[exp][typ].append({"strike": strike, "bp": bp, "ap": ap, "mid": mid, "width": width,
                         "trade": (s.get("latestTrade") or {}).get("p")})

for exp in sorted(by):
    cs = sorted(by[exp]["C"], key=lambda r: r["strike"])
    ps = sorted(by[exp]["P"], key=lambda r: r["strike"])
    if not cs and not ps: continue
    ac = min(cs, key=lambda r: abs(r["strike"] - spot)) if cs else None
    apb = min(ps, key=lambda r: abs(r["strike"] - spot)) if ps else None
    def fmt(r):
        if not r: return "n/a"
        m = r["mid"] if r["mid"] else (r["trade"] or 0)
        return "$%.0f mid ~%.2f (%.2f/%.2f)" % (r["strike"], m, r["bp"], r["ap"])
    print(f"  {exp}: {len(cs)}C/{len(ps)}P | ATM call {fmt(ac)} | ATM put {fmt(apb)}")

for exp in ["260904", "260918"]:
    print(f"--- XLP {exp} near-money legs:")
    for typ in ["C", "P"]:
        legs = [r for r in by[exp][typ] if spot * 0.97 <= r["strike"] <= spot * 1.08]
        line = " ".join("%.1f:%.2f" % (r["strike"], (r["mid"] if r["mid"] else (r["trade"] or 0)))
                        for r in sorted(legs, key=lambda r: r["strike"]))
        print(f"   {typ}: {line}")

# quick engine check for XLP covered call
import sys
sys.path.insert(0, ".")
import options_backtest as ob
for koff, pe in [(3, 1.2), (2, 0.8), (3, 0.8)]:
    r = ob.backtest_covered_call(bars=bars, symbol="XLP", initial_cash=10000.0,
                                 strike_offset=koff, days_to_expiry=21, premium_estimate_pct=pe, position_pct=90.0)
    print(f"CC XLP +${koff} prem {pe}%: total {r.total_return_pct:.2f}% vs B&H {r.benchmark_return:.2f}% | maxDD {r.max_drawdown_pct:.2f}% | sharpe {r.sharpe_ratio:.2f}")
r = ob.backtest_cash_secured_put(bars=bars, symbol="XLP", initial_cash=10000.0, strike_offset=3, days_to_expiry=21, position_pct=90.0)
print(f"CSP XLP -$3: total {r.total_return_pct:.2f}% vs B&H {r.benchmark_return:.2f}% | maxDD {r.max_drawdown_pct:.2f}%")