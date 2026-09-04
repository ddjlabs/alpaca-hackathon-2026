#!/usr/bin/env python3
"""Fetch option quotes for the D3 trade-plan contracts (one batched snapshot call).
Refreshes state/quotes_20260831.json['options'] with live marks for the 9 new books.
Prints verbatim JSON to stdout for the AR log."""
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
assert KEY and SEC

CONTRACTS = [
    "XLF260918P00057500", "XLF260918P00054000", "XLF260918P00056000",
    "XLF260918P00055000", "XLF261016P00055000", "XLF261016P00057000",
    "XLF261016P00056000", "XLU260918P00042000", "XLU260918P00040000",
]

URL = ("https://data.alpaca.markets/v1beta1/options/snapshots?symbols="
       + ",".join(CONTRACTS) + "&feed=indicative")
req = urllib.request.Request(URL, headers={
    "APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())
    snaps = data.get("snapshots", {})
    out = {}
    for sym, s in snaps.items():
        g = s.get("greeks") or {}
        q = s.get("latestQuote") or {}
        out[sym] = {
            "bid": q.get("bp"), "ask": q.get("ap"),
            "bid_size": q.get("bs"), "ask_size": q.get("bs2") if q.get("bs2") else s.get("askSize"),
            "delta": g.get("delta"), "iv": (s.get("impliedVolatility") or g.get("iv")),
        }
    # merge into state snapshot file
    QF = Path("/mnt/agent_share/gordon/hackathon/state/quotes_20260831.json")
    allq = json.loads(QF.read_text())
    allq.setdefault("options", {}).update(out)
    allq["ts"] = "2026-09-01 pre-open (refresh for D3 plans)"
    QF.write_text(json.dumps(allq, indent=2))
    print(json.dumps(out, indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:400]}")