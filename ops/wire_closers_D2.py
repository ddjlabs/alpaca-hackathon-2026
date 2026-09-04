#!/usr/bin/env python3
"""Wire GTC closing (buy-to-close) orders for the two survivor-orphaned short puts.
Marks seat transfer to clones at tonight's replication: agent-02 57P, agent-04 56P.
Mirrors the D2 ar-cleanup pattern: client_order_id ar-... , GTC limit, Tue open fill.
Prints API responses verbatim for the AR log."""
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

ORDERS = [
    # (client_order_id, limit, contract) — BTO shorts closed at ~2x mark for certainty at open
    ("ar-cleanup-agent-02-p57c", 0.52, "XLF260918P00057000"),
    ("ar-cleanup-agent-04-p56c", 0.30, "XLF260918P00056000"),
]

for coid, lim, sym in ORDERS:
    body = json.dumps({
        "symbol": sym, "qty": "1", "side": "buy", "type": "limit",
        "limit_price": str(lim), "time_in_force": "gtc", "client_order_id": coid,
    }).encode()
    req = urllib.request.Request(
        "https://paper-api.alpaca.markets/v2/orders", data=body,
        headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC,
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode())
            print(f"OK  {coid}: status={d.get('status')} limit={d.get('limit_price')} coid={d.get('client_order_id')}")
    except urllib.error.HTTPError as e:
        print(f"ERR {coid}: HTTP {e.code} {e.read().decode()[:300]}")