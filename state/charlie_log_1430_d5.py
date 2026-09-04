#!/usr/bin/env python3
"""Charlie 14:30 — XLP quote retry (symbols= param) + poll heartbeat log append."""
import json, os, urllib.request
from pathlib import Path
from datetime import datetime

ENV = Path('/home/doug/.hermes/profiles/gordon/.env')
creds = {}
for line in ENV.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")

KEY, SEC = creds['HACKATHON_ALPACA_KEY'], creds['HACKATHON_ALPACA_SECRET']

def get(url):
    req = urllib.request.Request(url)
    req.add_header('APCA-API-KEY-ID', KEY)
    req.add_header('APCA-API-SECRET-KEY', SEC)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

OUT = Path('/mnt/agent_share/gordon/hackathon/state')

# XLP 83P quote for the 15:45 fallback record
try:
    snap = get('https://data.alpaca.markets/v1beta1/options/snapshots?feed=indicative&symbols=XLP260918P00083000')
    (OUT / '_xlp83_snap_1430.json').write_text(json.dumps(snap, indent=2))
    s = snap.get('snapshots', {}).get('XLP260918P00083000', {})
    q = s.get('latestQuote', {})
    g = s.get('greeks', {})
    print(f"XLP260918P00083000: bid={q.get('bp')} x ask={q.get('ap')} last={s.get('latestTrade',{}).get('p')} "
          f"delta={g.get('delta')} iv={round(s.get('impliedVolatility') or 0, 4)}")
    mid = None
    if q.get('bp') is not None and q.get('ap') is not None:
        mid = round((q['bp'] + q['ap']) / 2, 2)
    print(f"live mid for fallback record: {mid}")
except Exception as e:
    print("XLP QUOTE RETRY FAIL:", e)
    mid = None

# Heartbeat append to orders log (atomic)
f = OUT / 'orders_20260902.json'
orders = json.loads(f.read_text())
now = datetime.now().astimezone().isoformat(timespec='seconds')
orders.append({
    "type": "poll_1430",
    "ts": now,
    "account": "PA3GWO1FKED0",
    "status": "ACTIVE",
    "trading_blocked": False,
    "equity": 99837.84,
    "cards_processed": 0,
    "open_orders": ["agent-24 XLP260918P00083000 STO 1 LMT 0.18 DAY (reprice 1-of-1 consumed 14:04)",
                    "agent-27 BTC/USD buy 0.0325 LMT 75800 GTC (staged powder)",
                    "agent-27 ETH/USD buy 0.6 LMT 2365 GTC (staged powder)"],
    "xlp83_live_quote": {"bid": (q or {}).get('bp'), "ask": (q or {}).get('ap'), "mid": mid} if (q or {}).get('bp') is not None else None,
    "rule8_clock": ("ARMED 14:30 ET — no teeth actions due: 21/22/23/25/26/27 FILLED today; "
                    "02/04/07 survivors EXEMPT (carried short puts); agent-24 resting since 14:04 "
                    "(post-14:00, reprice quota consumed) -> 15:45 fallback: cancel + file plan_step_2 "
                    "at live mid if unfilled. Warnings due: NONE. non_trading candidates: NONE at 14:30."),
    "board": "bushwoodstratton_trading",
    "kanban_cards_for_charlie": 0,
    "note": "board empty all day; gates green; Rule 10 standing check passed (holdings fresh 14:30:10, attribution 7/7)"
})
tmp = f.with_suffix('.tmp')
tmp.write_text(json.dumps(orders, indent=2))
tmp.replace(f)
print(f"heartbeat appended: entry #{len(orders)}")