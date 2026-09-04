#!/usr/bin/env python3
"""QQQ 260918 wing quotes for Voss's condor (margin-based, 1-wide)."""
import os, json, urllib.request
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
key = os.getenv('HACKATHON_ALPACA_KEY'); sec = os.getenv('HACKATHON_ALPACA_SECRET')
H = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec}

def get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())

all_snaps = {}
token = None
for page in range(10):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/QQQ?limit=1000&feed=indicative" + (f"&page_token={token}" if token else "")
    d = get(url)
    all_snaps.update(d.get("snapshots", {}))
    token = d.get("next_page_token")
    if not token: break
print("QQQ total snapshots:", len(all_snaps))
json.dump(all_snaps, open("/tmp/chain_QQQ.json", "w"))

spot = 716.44
lo, hi = spot * 0.90, spot * 1.10
found = []
for k, s in all_snaps.items():
    if not k.startswith("QQQ260918"): continue
    typ = k[9]
    try: strike = int(k[10:]) / 1000
    except Exception: continue
    if not (lo <= strike <= hi): continue
    q = s.get("latestQuote") or {}
    bp, ap = q.get("bp") or 0, q.get("ap") or 0
    mid = round((bp + ap) / 2, 2) if (bp and ap) else None
    if mid and mid > 0.005:
        found.append((typ, strike, mid, bp, ap, (s.get("latestTrade") or {}).get("p")))

print("=== QQQ 260918 puts 90-110% of spot ===")
for t, st, m, bp, ap, tr in sorted([x for x in found if x[0] == "P"], key=lambda x: x[1]):
    print(f"  {st:8.1f} mid {m:6.2f} ({bp}/{ap}) last {tr}")
print("=== QQQ 260918 calls ===")
for t, st, m, bp, ap, tr in sorted([x for x in found if x[0] == "C"], key=lambda x: x[1]):
    print(f"  {st:8.1f} mid {m:6.2f} ({bp}/{ap}) last {tr}")