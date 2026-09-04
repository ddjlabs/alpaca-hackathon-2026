#!/usr/bin/env python3
"""Charlie 14:30 — Alpaca gates + open orders + XLP quote (read-only)."""
import json, os, urllib.request, base64
from pathlib import Path

ENV = Path('/home/doug/.hermes/profiles/gordon/.env')
creds = {}
for line in ENV.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")

KEY = creds.get('HACKATHON_ALPACA_KEY') or os.environ.get('HACKATHON_ALPACA_KEY')
SEC = creds.get('HACKATHON_ALPACA_SECRET') or os.environ.get('HACKATHON_ALPACA_SECRET')
print("key loaded:", bool(KEY), "secret loaded:", bool(SEC))

def get(url):
    req = urllib.request.Request(url)
    req.add_header('APCA-API-KEY-ID', KEY)
    req.add_header('APCA-API-SECRET-KEY', SEC)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

OUT = Path('/mnt/agent_share/gordon/hackathon/state')

# 1. Account gate
try:
    acct = get('https://paper-api.alpaca.markets/v2/account')
    (OUT / '_acct_1430.json').write_text(json.dumps(acct, indent=2))
    print(f"\nGATE: account={acct['account_number']} id={acct['id']} status={acct['status']} "
          f"trading_blocked={acct['trading_blocked']} equity={acct['equity']} cash={acct['cash']}")
except Exception as e:
    print("ACCOUNT FAIL:", e)

# 2. Open orders
try:
    oo = get('https://paper-api.alpaca.markets/v2/orders?status=open&limit=50')
    (OUT / '_open_orders_1430.json').write_text(json.dumps(oo, indent=2))
    print(f"\nOPEN ORDERS: {len(oo)}")
    for o in oo:
        print(f"  {o.get('submitted_at','?')[:19]}Z {o.get('symbol')} {o.get('side')} qty={o.get('qty')} "
              f"type={o.get('type')} lmt={o.get('limit_price')} tif={o.get('time_in_force')} "
              f"status={o.get('status')} coid={o.get('client_order_id','')[:40]} id={o.get('id')[:8]}")
except Exception as e:
    print("ORDERS FAIL:", e)

# 3. XLP 83P live quote (options snapshot, indicative feed)
try:
    snap = get('https://data.alpaca.markets/v1beta1/options/snapshots/XLP260918P00083000?feed=indicative')
    (OUT / '_xlp83_snap_1430.json').write_text(json.dumps(snap, indent=2))
    s = snap.get('snapshots', {}).get('XLP260918P00083000', {})
    q = s.get('latestQuote', {})
    g = s.get('greeks', {})
    print(f"\nXLP260918P00083000: bid={q.get('bp')} x ask={q.get('ap')} "
          f"last={s.get('latestTrade',{}).get('p')} delta={g.get('delta')} iv={s.get('impliedVolatility')}")
except Exception as e:
    print("XLP QUOTE FAIL:", e)

# 4. Any fills today not yet in holdings? (activities)
try:
    acts = get('https://paper-api.alpaca.markets/v2/account/activities/FILL?pageSize=20')
    (OUT / '_fills_1430.json').write_text(json.dumps(acts, indent=2))
    print(f"\nRECENT FILLS: {len(acts)}")
    for a in acts[:10]:
        print(f"  {a.get('transaction_time','?')[:19]}Z {a.get('symbol')} {a.get('side')} "
              f"qty={a.get('qty')} px={a.get('price')} coid={a.get('client_order_id','')[:40]}")
except Exception as e:
    print("ACTIVITIES FAIL:", e)