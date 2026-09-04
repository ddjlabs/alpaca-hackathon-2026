#!/usr/bin/env python3
"""D3 GAUNTLET v2: weekly 9/4 put grid via v1beta1 by explicit contract symbols (this feed requires symbols=)."""
import json, urllib.error, urllib.request
from pathlib import Path

env = {}
for line in Path("/home/doug/.hermes/profiles/gordon/.env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1); env[k.strip()] = v.strip()
K, S = env["HACKATHON_ALPACA_KEY"], env["HACKATHON_ALPACA_SECRET"]

def occ(root, ymd,Strike):  # Strike in dollars
    return f"{root}{ymd}P{round(Strike*1000):08d}"

SYMS = [occ("XLF","260904",s) for s in (54,54.5,55,55.5,56,56.5,57,57.5)] + \
       [occ("XLU","260904",s) for s in (40,40.5,41,41.5,42)]
url = "https://data.alpaca.markets/v1beta1/options/snapshots?symbols=" + ",".join(SYMS) + "&feed=indicative"
req = urllib.request.Request(url, headers={"APCA-API-KEY-ID": K, "APCA-API-SECRET-KEY": S})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:300]}"); raise SystemExit(1)
snaps = d.get("snapshots", {})
grid = {}
for root in ("XLF", "XLU"):
    print(f"=== {root} 9/4 puts (weekly fallback grid) ===")
    for sym in sorted(snaps):
        if not sym.startswith(root):
            continue
        s = snaps[sym] or {}
        g = s.get("greeks") or {}
        q = s.get("latestQuote") or {}
        bid, ask = q.get("bp"), q.get("ap")
        iv = s.get("impliedVolatility")
        strike = int(sym[-8:]) / 1000
        if bid is None and ask is None:
            print(f"  {sym}  NO MARKET"); continue
        spread = None if (bid is None or ask is None) else round(ask - bid, 3)
        print(f"  {sym}  b/a {bid}/{ask} (w {spread})  delta {g.get('delta')}  iv {iv}")
        grid[sym] = {"strike": strike, "bid": bid, "ask": ask, "spread": spread,
                     "delta": g.get("delta"), "iv": iv}
Path("/mnt/agent_share/gordon/hackathon/state/weekly_chain_20260904.json").write_text(json.dumps(grid, indent=2))
print("saved state/weekly_chain_20260904.json")