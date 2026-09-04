#!/usr/bin/env python3
"""Charlie's 13:30 D7 poll — env gate, open orders (age), fills TODAY by agent, positions."""
import json, os, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

STATE = Path('/mnt/agent_share/gordon/hackathon/state')
KEY = os.environ.get('HACKATHON_ALPACA_KEY', '')
SEC = os.environ.get('HACKATHON_ALPACA_SECRET', '')
BASE = 'https://paper-api.alpaca.markets'
HDRS = {'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC}
TODAY = '2026-09-03'

def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {'_error': e.code, '_body': e.read().decode()[:300]}
    except Exception as e:
        return {'_error': str(e)}

# --- env gate ---
acct = get(f'{BASE}/v2/account')
gate = {
    'account': acct.get('account_number'),
    'starts_PA': str(acct.get('account_number', '')).startswith('PA'),
    'status': acct.get('status'),
    'trading_blocked': acct.get('trading_blocked'),
    'equity': acct.get('equity'),
    'cash': acct.get('cash'),
    'gate_pass': str(acct.get('account_number', '')).startswith('PA')
                 and acct.get('status') == 'ACTIVE'
                 and acct.get('trading_blocked') is False,
}
print('ENV GATE:', json.dumps(gate))

# --- open orders with age ---
orders = get(f'{BASE}/v2/orders?status=open&limit=100&nested=false')
if isinstance(orders, dict):
    print('ORDERS ERROR:', orders)
    orders = []
print(f'\nOPEN ORDERS: {len(orders)}')
now = datetime.now(timezone(timedelta(hours=-4)))
for o in orders:
    sub = o.get('submitted_at', '')
    age_min = ''
    if sub:
        try:
            subdt = datetime.fromisoformat(sub.replace('Z', '+00:00'))
            age_min = f'age={int((now - subdt).total_seconds() / 60)}min'
        except Exception:
            pass
    legs = ''
    if o.get('type') == 'mleg' or o.get('order_class') == 'mleg':
        legs = ' | legs=' + json.dumps(o.get('legs', []))[:200]
    print(f"  {sub} {age_min} | {o.get('client_order_id')} | {o.get('symbol')} "
          f"{o.get('side')} {o.get('qty')} @ {o.get('limit_price')} | {o.get('status')} "
          f"| tif={o.get('time_in_force')} | type={o.get('type')} | id={o.get('id')}{legs}")

# --- per-agent executed fills today ---
acts = get(f'{BASE}/v2/account/activities/FILL?date={TODAY}&page_size=100')
if isinstance(acts, dict):
    print('ACTIVITIES ERROR:', acts)
    acts = []
fills_by_agent = {}
for a in acts:
    coid = a.get('order_client_order_id', '') or ''
    if coid.startswith('agent-'):
        agent = '-'.join(coid.split('-')[:2])
    else:
        agent = 'other:' + coid[:30]
    fills_by_agent.setdefault(agent, []).append(
        f"{a.get('symbol')} {a.get('side')} {a.get('qty')} @ {a.get('price')} id={a.get('order_id','')[:8]}")
print(f'\nFILLS TODAY ({TODAY}, {len(acts)} total):')
for ag in sorted(fills_by_agent):
    print(f'  {ag}: {fills_by_agent[ag]}')

# --- positions (survivor carve-out check) ---
pos = get(f'{BASE}/v2/positions')
if isinstance(pos, dict):
    print('POSITIONS ERROR:', pos)
    pos = []
print(f'\nPOSITIONS: {len(pos)}')
for p in pos:
    print(f"  {p.get('symbol')} qty={p.get('qty')} side={p.get('side')} "
          f"mv={p.get('market_value')} cb={p.get('cost_basis')}")

json.dump({'gate': gate, 'open_orders': orders, 'open_orders_n': len(orders),
           'fills_by_agent': fills_by_agent, 'fills_n': len(acts),
           'positions': pos, 'poll_ts': now.isoformat()},
          open(STATE / 'poll_1330_d7.json', 'w'), indent=1)
print('\nSaved -> poll_1330_d7.json')