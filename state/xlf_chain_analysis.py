#!/usr/bin/env python3
"""XLF chain analysis for Options Gauntlet — Sunday 2026-08-."""
import json
from collections import defaultdict

snaps = json.load(open("/tmp/chain_XLF.json"))
spot = 58.09
by = defaultdict(lambda: {"C": [], "P": []})
for k, s in snaps.items():
    exp, typ = k[3:9], k[9]
    try:
        strike = int(k[10:]) / 1000
    except Exception:
        continue
    q = s.get("latestQuote") or {}
    bp, ap = q.get("bp") or 0, q.get("ap") or 0
    mid = (bp + ap) / 2 if (bp and ap) else None
    width = (ap - bp) if (bp and ap) else None
    by[exp][typ].append({"strike": strike, "bp": bp, "ap": ap, "mid": mid,
                         "width": width, "trade": (s.get("latestTrade") or {}).get("p")})

for exp in sorted(by):
    cs = sorted(by[exp]["C"], key=lambda r: r["strike"])
    ps = sorted(by[exp]["P"], key=lambda r: r["strike"])
    if not cs and not ps:
        continue
    ac = min(cs, key=lambda r: abs(r["strike"] - spot)) if cs else None
    apb = min(ps, key=lambda r: abs(r["strike"] - spot)) if ps else None

    def fmt(r):
        if not r:
            return "n/a"
        m = r["mid"] if r["mid"] else (r["trade"] or 0)
        return "$%.0f mid ~%.2f (%.2f/%.2f)" % (r["strike"], m, r["bp"], r["ap"])

    print(f"{exp}: {len(cs)}C/{len(ps)}P | ATM call {fmt(ac)} | ATM put {fmt(apb)}")

for exp in ["260901", "260918"]:
    print(f"--- {exp} strikes 52-64:")
    for typ in ["C", "P"]:
        legs = [r for r in by[exp][typ] if 52 <= r["strike"] <= 64]
        line = " ".join(
            "%.0f:%.2f" % (r["strike"], (r["mid"] if r["mid"] else (r["trade"] or 0)))
            for r in sorted(legs, key=lambda r: r["strike"]))
        print(f"   {typ}: {line}")

widest = []
for exp in by:
    for typ in ["C", "P"]:
        for r in by[exp][typ]:
            if r["width"] and 50 < r["strike"] < 70:
                widest.append((round(r["width"], 3), exp, typ, r["strike"], r["bp"], r["ap"]))
widest.sort(reverse=True)
print("widest near-money spreads (kill list):")
for w in widest[:8]:
    print("  ", w)

# credit spread math for the spike artists (1x, credit in $, max loss, ROC)
W = 1.0  # width
print("\n=== credit-spread candidates (width $1, 1 contract) ===")
for exp in ["260901", "260918"]:
    if exp not in by:
        continue
    # BEAR CALL: sell lower call, buy higher call
    cs = {r["strike"]: r for r in by[exp]["C"]}
    pairs = [(60, 61), (60, 62), (61, 62)]
    for lo, hi in pairs:
        if lo in cs and hi in cs:
            slo, shi = cs[lo], cs[hi]
            lo_m = slo["mid"] if slo["mid"] else (slo["trade"] or 0)
            hi_m = shi["mid"] if shi["mid"] else (shi["trade"] or 0)
            credit = round(lo_m - hi_m, 2)
            print(f"{exp} BEAR CALL {lo:.0f}/{hi:.0f}: credit ~{credit:.2f} | max prof {credit}/ct | max loss {round(W-credit,2)}/ct | occ {int(hi*1000):08d}")
    # BULL PUT: sell higher put, buy lower put
    ps = {r["strike"]: r for r in by[exp]["P"]}
    for hi, lo in [(57, 56), (56, 55), (55, 54), (58, 57)]:
        if hi in ps and lo in ps:
            shi, slo = ps[hi], ps[lo]
            hi_m = shi["mid"] if shi["mid"] else (shi["trade"] or 0)
            lo_m = slo["mid"] if slo["mid"] else (slo["trade"] or 0)
            credit = round(hi_m - lo_m, 2)
            print(f"{exp} BULL PUT {hi:.0f}/{lo:.0f}: credit ~{credit:.2f} | max prof {credit}/ct | max loss {round(W-credit,2)}/ct | occ {int(lo*1000):08d}")

# put-sell candidates (CSP per agent, cash reserve = strike*100)
print("\n=== single-leg candidates ===")
for exp in ["260901", "260918"]:
    for typ, coll in [("C", by[exp]["C"]), ("P", by[exp]["P"])]:
        for r in sorted(coll, key=lambda r: r["strike"]):
            s = r["strike"]
            if typ == "P" and 54 <= s <= 57 or (typ == "C" and 60 <= s <= 64) or (typ == "C" and s == 62):
                m = r["mid"] if r["mid"] else (r["trade"] or 0)
                print(f"{exp} STO {'PUT' if typ=='P' else 'CALL'} ${s:.0f}: mid ~{m:.2f} ({r['bp']:.2f}/{r['ap']:.2f}) width {r['width']} | occ {int(s*1000):08d}")