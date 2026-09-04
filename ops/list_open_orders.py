#!/usr/bin/env python3
"""Read-only: list all open orders on the hackathon book (verification for AR log)."""
import json
import urllib.request
from pathlib import Path

ENV_FILE = Path("/home/doug/.hermes/profiles/gordon/.env")
env = {}
for line in ENV_FILE.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()

KEY = env.get("HACKATHON_ALPACA_KEY")
SEC = env.get("HACKATHON_ALPACA_SECRET")
assert KEY and SEC, "missing creds"

req = urllib.request.Request(
    "https://paper-api.alpaca.markets/v2/orders?status=open&limit=50",
    headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC})
with urllib.request.urlopen(req, timeout=20) as r:
    orders = json.loads(r.read().decode())

print(f"{len(orders)} open order(s):")
for o in orders:
    print(f"  {o['client_order_id']:<32} {o['symbol']:<22} {o['side']:<4} qty={o['qty']:<3} "
          f"limit={o['limit_price']} {o['status']} tif={o['time_in_force']}")