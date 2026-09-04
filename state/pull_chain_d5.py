#!/usr/bin/env python3
"""Pull live option snapshots for exact D5 contracts (indicative feed)."""
import json, urllib.request

KEY = SEC = None
with open("/home/doug/.hermes/profiles/gordon/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("HACKATHON_ALPACA_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("HACKATHON_ALPACA_SECRET="):
            SEC = line.split("=", 1)[1].strip().strip('"').strip("'")

contracts = [
    "XLF260918P00057000", "XLF260918P00056000", "XLF260918P00055500", "XLF260918P00055000",
    "XLU260904P00042000", "XLU260918P00041000", "XLU260904P00042500", "XLU260918P00041500",
    "SPY260918P00735000", "SPY260918P00725000", "XLP260918P00083000",
]
url = ("https://data.alpaca.markets/v1beta1/options/snapshots"
       f"?feed=indicative&symbols={','.join(contracts)}")
req = urllib.request.Request(url, headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC})
with urllib.request.urlopen(req, timeout=45) as r:
    d = json.loads(r.read().decode())

out = {}
for c in contracts:
    s = (d.get("snapshots") or {}).get(c)
    if not s:
        out[c] = None
        print(c, "NO SNAPSHOT")
        continue
    q = s.get("latestQuote") or {}
    g = s.get("greeks") or {}
    iv = s.get("impliedVolatility")
    bid, ask = q.get("bid"), q.get("ask")
    mid = round((bid + ask) / 2, 3) if bid is not None and ask is not None else None
    out[c] = {"bid": bid, "ask": ask, "mid": mid, "delta": g.get("delta"),
              "iv": round(iv, 4) if iv else None,
              "bid_sz": q.get("bid_size"), "ask_sz": q.get("ask_size")}
    print(c, out[c])

with open("/mnt/agent_share/gordon/hackathon/state/chain_d5_board.json", "w") as f:
    json.dump(out, f, indent=1)
print("saved chain_d5_board.json")