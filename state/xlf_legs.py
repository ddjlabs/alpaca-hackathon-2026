#!/usr/bin/env python3
"""Extract exact OCC contracts + clean quotes for gauntlet plan legs."""
import json

snaps = json.load(open("/tmp/chain_XLF.json"))
WANT = {
    "260904": {"C": [58.0, 59.0, 60.0, 60.5, 61.0, 62.0], "P": [55.0, 55.5, 56.0, 56.5, 57.0, 57.5, 58.0]},
    "260918": {"C": [58.0, 59.0, 60.0, 60.5, 61.0, 62.0, 63.0, 64.0], "P": [55.0, 55.5, 56.0, 56.5, 57.0, 57.5, 58.0]},
}
for exp, types in WANT.items():
    for typ, strikes in types.items():
        print(f"--- {exp} {typ}")
        for st in strikes:
            occ = f"XLF{exp}{typ}{int(round(st*1000)):08d}"
            s = snaps.get(occ)
            if not s:
                print(f"  {occ}: NOT FOUND")
                continue
            q = s.get("latestQuote") or {}
            bp, ap = q.get("bp") or 0, q.get("ap") or 0
            tr = (s.get("latestTrade") or {}).get("p")
            mid = round((bp + ap) / 2, 2) if (bp and ap) else None
            print(f"  {occ}: bid {bp} ask {ap} mid {mid} lastTrade {tr}")