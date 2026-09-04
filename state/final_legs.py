#!/usr/bin/env python3
"""Final leg quotes: Voss XLP condor wings + Shelly XLF deep-OTM put."""
import json

xlp = json.load(open("/tmp/chain_XLP.json"))
xlf = json.load(open("/tmp/chain_XLF.json"))

print("=== XLP 260918 condor wings (Voss) ===")
for occ in ["XLP260918P00079500", "XLP260918P00080000", "XLP260918P00080500",
            "XLP260918P00081000", "XLP260918P00081500", "XLP260918P00082000",
            "XLP260918C00088500", "XLP260918C00089000", "XLP260918C00089500",
            "XLP260918C00090000", "XLP260918C00090500"]:
    s = xlp.get(occ)
    if not s:
        print(f"  {occ}: NOT FOUND")
        continue
    q = s.get("latestQuote") or {}
    tr = (s.get("latestTrade") or {}).get("p")
    print(f"  {occ}: bid {q.get('bp')} ask {q.get('ap')} lastTrade {tr}")

print("=== XLF 260918 deep-OTM puts (Shelly) ===")
for occ in ["XLF260918P00054000", "XLF260918P00054500", "XLF260918P00055000"]:
    s = xlf.get(occ)
    if not s:
        print(f"  {occ}: NOT FOUND")
        continue
    q = s.get("latestQuote") or {}
    tr = (s.get("latestTrade") or {}).get("p")
    print(f"  {occ}: bid {q.get('bp')} ask {q.get('ap')} lastTrade {tr}")

print("=== XLF 260904 P55/P55.5 (Shelly short-week alternative) ===")
for occ in ["XLF260904P00055000", "XLF260904P00055500"]:
    s = xlf.get(occ)
    q = (s or {}).get("latestQuote") or {}
    tr = ((s or {}).get("latestTrade") or {}).get("p")
    print(f"  {occ}: bid {q.get('bp')} ask {q.get('ap')} lastTrade {tr}")