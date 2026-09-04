#!/usr/bin/env python3
"""Charlie's trade-desk poll: inbox, account gates, open orders, today's flow."""
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone, date
import urllib.request

STATE = Path('/mnt/agent_share/gordon/hackathon/state')
KEY = os.environ.get('HACKATHON_ALPACA_KEY')
SEC = os.environ.get('HACKATHON_ALPACA_SECRET')
BASE = 'https://paper-api.alpaca.markets'

def alpaca(path):
    req = urllib.request.Request(BASE + path, headers={
        'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

print('=== ENV ===')
print('key set:', bool(KEY), '| secret set:', bool(SEC))

print('\n=== ACCOUNT GATE ===')
try:
    a = alpaca('/v2/account')
    for k in ['account_number', 'status', 'trading_blocked', 'equity', 'cash', 'daytrade_count']:
        print(f'{k}: {a.get(k)}')
    print('GATE PASS' if a.get('account_number','').startswith('PA') and a.get('status')=='ACTIVE' and not a.get('trading_blocked') else 'GATE FAIL')
except Exception as e:
    print('ALPACA UNREACHABLE:', e)
    sys.exit(0)

print('\n=== OPEN ORDERS (resting) ===')
try:
    oo = alpaca('/v2/orders?status=open&limit=100')
    print(len(oo), 'open')
    now = datetime.now(timezone.utc)
    for o in oo:
        sub = o['submitted_at'].replace('Z', '+00:00')
        age_min = (now - datetime.fromisoformat(sub)).total_seconds()/60
        print(f"{o['client_order_id']} | {o['symbol']} {o['side']} x{o['qty']} {o['type']} lim={o.get('limit_price')} | submitted {o['submitted_at']} | age {age_min:.0f}min | status={o['status']}")
except Exception as e:
    print('orders fetch failed:', e)

print('\n=== TODAY ORDERS (all statuses, newest first) ===')
try:
    tod = date.today().isoformat()
    allo = alpaca(f'/v2/orders?status=all&after={tod}T04:00:00Z&limit=100&direction=desc')
    print(len(allo), 'orders since 00:00 ET')
    for o in allo[:40]:
        print(f"{o['client_order_id']} | {o['symbol']} {o['side']} x{o['qty']} {o['type']} lim={o.get('limit_price')} | {o['status']} | filled {o.get('filled_avg_price')} | submitted {o['submitted_at']}")
except Exception as e:
    print('orders fetch failed:', e)

print('\n=== MESSAGE BOARD INBOX (charlie) ===')
today = datetime.now().strftime('%Y%m%d')
f = STATE / f'messageboard_{today}.json'
msgs = json.loads(f.read_text()) if f.exists() else []
print(f'{len(msgs)} messages on board {today}')
mine = [m for m in msgs if m.get('to') in ('charlie', 'all') and not m.get('read')]
print(f'{len(mine)} unread for charlie/all:')
for m in mine:
    print(f"  [{m['from']} -> {m['to']}] {m['type']} :: re={m.get('re')} :: {m['message'][:220]}")

print('\n=== STATE FILES ===')
for name in ['orders_20260901.json', 'dashboard.json']:
    p = STATE / name
    if p.exists():
        print(name, 'exists,', p.stat().st_size, 'bytes, mtime',
              datetime.fromtimestamp(p.stat().st_mtime).strftime('%H:%M:%S'))
    else:
        print(name, 'MISSING')
od = STATE / 'orders_20260901.json'
if od.exists():
    try:
        oj = json.loads(od.read_text())
        entries = oj if isinstance(oj, list) else oj.get('orders', oj.get('entries', []))
        print('orders file entries:', len(entries) if isinstance(entries, list) else '?')
        if isinstance(entries, list):
            for e in entries[-15:]:
                print('  ', json.dumps(e)[:200])
    except Exception as e:
        print('orders parse fail:', e)

print('\n=== DASHBOARD AGENT STATUS (strikes / flags) ===')
dj = STATE / 'dashboard.json'
if dj.exists():
    d = json.loads(dj.read_text())
    ags = d.get('agents', [])
    print(len(ags), 'agents; day', d.get('day'))
    for ag in ags:
        print(f"  {ag.get('id')} {ag.get('name','')[:20]:20s} status={ag.get('status')} strikes={ag.get('strikes')} non_trading_flag={ag.get('non_trading_flag')} carried_pos={ag.get('carried_positions', ag.get('has_carried_portfolio','?'))}")