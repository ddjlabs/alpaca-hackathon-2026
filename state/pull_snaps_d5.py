#!/usr/bin/env python3
"""Pull underlying snapshots for D5 memo math. Saves state/snapshots_d5.json"""
import json, urllib.request

KEY = SEC = None
with open("/home/doug/.hermes/profiles/gordon/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("HACKATHON_ALPACA_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("HACKATHON_ALPACA_SECRET="):
            SEC = line.split("=", 1)[1].strip().strip('"').strip("'")

out = {}
for sym in ("SPY", "XLF", "XLU", "XLP"):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot?feed=iex"
    req = urllib.request.Request(url, headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode())
        ltp = (d.get("latestTrade") or {}).get("p")
        pdbc = (d.get("prevDailyBar") or {}).get("c")
        out[sym] = {"last": ltp, "prev_close": pdbc}
        print(sym, "last", ltp, "prevClose", pdbc)
    except Exception as e:
        out[sym] = {"error": str(e)}
        print(sym, "ERROR", e)

with open("/mnt/agent_share/gordon/hackathon/state/snapshots_d5.json", "w") as f:
    json.dump(out, f, indent=1)
print("saved")