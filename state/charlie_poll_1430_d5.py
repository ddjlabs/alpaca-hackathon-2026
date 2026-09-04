#!/usr/bin/env python3
"""Charlie 14:30 Rule 8 unfilled-watch poll — read-only analysis pass."""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

STATE = Path('/mnt/agent_share/gordon/hackathon/state')
TODAY = '20260902'

# 1. Today's order log
orders = json.loads((STATE / f'orders_{TODAY}.json').read_text())
print("=== orders_20260902.json:", type(orders).__name__)
entries = orders.get('orders', []) if isinstance(orders, dict) else orders
print("entries:", len(entries))
if entries:
    print("sample keys:", sorted(entries[0].keys()))
    st = defaultdict(lambda: {'filled': 0, 'resting': 0, 'rejected': 0, 'other': 0})
    for e in entries:
        a = e.get('agent_id') or e.get('agent') or '?'
        s = str(e.get('status') or e.get('order_status') or '?').lower()
        if s == 'filled':
            st[a]['filled'] += 1
        elif s in ('new', 'accepted', 'pending_new', 'held'):
            st[a]['resting'] += 1
        elif s in ('rejected', 'canceled', 'cancelled', 'expired'):
            st[a]['rejected'] += 1
        else:
            st[a]['other'] += 1
    for a in sorted(st):
        print(f"  {a}: {dict(st[a])}")
    print("\n--- resting order details (filed ts, symbol, side, price) ---")
    for e in entries:
        s = str(e.get('status') or e.get('order_status') or '?').lower()
        if s in ('new', 'accepted', 'pending_new', 'held'):
            print("  ", e.get('agent_id'), s, e.get('symbol'), e.get('side'),
                  e.get('limit_price') or e.get('filled_avg_price'),
                  "submitted:", e.get('submitted_at') or e.get('created_at'),
                  "id:", (e.get('order_id') or e.get('id') or '')[:8],
                  "client_oid:", e.get('client_order_id', '')[:40])
    print("\n--- last 6 log entries (any status) ---")
    for e in entries[-6:]:
        print("  ", e.get('timestamp') or e.get('created_at'), e.get('agent_id'),
              str(e.get('status')), e.get('symbol'), e.get('side'),
              e.get('limit_price') or e.get('filled_avg_price'))

# 2. dashboard roster
dash = json.loads((STATE / 'dashboard.json').read_text())
print("\n=== dashboard.json top keys:", list(dash.keys()))
ag = dash.get('agents', [])
print("roster:", len(ag))
for x in ag:
    print(f"  {x.get('agent_id') or x.get('id')} status={x.get('status')} "
          f"curval={x.get('current_value')} strikes={x.get('strikes')} "
          f"non_trading={x.get('non_trading_flag')} day={x.get('day', dash.get('day'))}")

# 3. agent_holdings snapshot (fresh at 14:30) — who has positions?
ah = json.loads((STATE / 'agent_holdings.json').read_text())
print("\n=== agent_holdings.json keys:", list(ah.keys()) if isinstance(ah, dict) else type(ah).__name__)
pos = ah.get('positions_by_agent') or ah.get('agents') or ah.get('holdings') or ah
if isinstance(pos, dict):
    for k in sorted(pos):
        v = pos[k]
        if isinstance(v, dict):
            n = len(v.get('positions', v.get('holdings', [])))
        elif isinstance(v, list):
            n = len(v)
        else:
            n = v
        print(f"  {k}: {n} position entries")
elif isinstance(pos, list):
    for p in pos:
        print("  ", p.get('agent'), p.get('symbol'), p.get('side'), p.get('qty'))

# 4. message board today — last 12 messages (any unread for charlie?)
mb = STATE / f'messageboard_{TODAY}.json'
if mb.exists():
    msgs = json.loads(mb.read_text())
    print(f"\n=== message board {TODAY}: {len(msgs)} messages")
    for m in msgs[-12:]:
        print(f"  {m.get('timestamp','?')[11:19]} {m.get('from')}->{m.get('to')} [{m.get('type')}] read={m.get('read')} :: {str(m.get('message',''))[:90]}")
else:
    print("\n=== no message board file today")