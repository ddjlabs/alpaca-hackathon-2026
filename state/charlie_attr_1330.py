#!/usr/bin/env python3
"""Attribute today's fills by client_order_id + read risk note + check orders file."""
import json, os, urllib.request
from pathlib import Path

STATE = Path('/mnt/agent_share/gordon/hackathon/state')
KEY = os.environ.get('HACKATHON_ALPACA_KEY', '')
SEC = os.environ.get('HACKATHON_ALPACA_SECRET', '')
HDRS = {'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC}

def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

acts = get('https://paper-api.alpaca.markets/v2/account/activities/FILL?date=2026-09-01&page_size=100')
print(f'=== RAW FILL ATTRIBUTION ({len(acts)}) ===')
by_agent = {}
for a in acts:
    coid = a.get('order_client_order_id', '?')
    print(f"  {a.get('id','')[-8:]} | coid={coid} | {a.get('symbol')} {a.get('side')} {a.get('qty')} @ {a.get('price')} | {a.get('transaction_time','')[:19]}")
    agent = coid.split('-2026')[0] if '-2026' in coid else coid
    by_agent.setdefault(agent, []).append(f"{a.get('symbol')} {a.get('side')} {a.get('qty')} @ {a.get('price')}")

print('\n=== FILLS BY AGENT/PROCESS ===')
for k in sorted(by_agent):
    print(f'  {k}: {len(by_agent[k])} fill(s)')

# orders file tail
o = json.loads((STATE / 'orders_20260901.json').read_text())
print(f'\n=== orders_20260901.json: {len(o)} entries ===')
for e in o:
    print(f"  {e.get('agent_id')} | {e.get('symbol')} | {e.get('alpaca_status')} | {e.get('client_order_id')} | filled {e.get('filled_avg_price')}")

# full risk note from board
msgs = json.loads((STATE / 'messageboard_20260901.json').read_text())
for m in msgs:
    if m['type'] == 'risk_note':
        print(f"\n=== RISK NOTE ({m['timestamp']}) ===\n{m['message']}")