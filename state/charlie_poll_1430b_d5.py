#!/usr/bin/env python3
"""Charlie 14:30 Rule 8 — full log/board dump + yesterday precedent."""
import json
from pathlib import Path

STATE = Path('/mnt/agent_share/gordon/hackathon/state')

print("=== FULL orders_20260902.json ===")
orders = json.loads((STATE / 'orders_20260902.json').read_text())
for i, e in enumerate(orders):
    t = e.get('type') or ('poll' if 'poll_heartbeat' in e else 'order')
    line = f"[{i}] ts={str(e.get('ts'))[:19]} "
    if 'poll_heartbeat' in e:
        line += f"POLL equity={e.get('equity')} cards={e.get('cards_processed')} open={e.get('open_orders_note','')[:60]} rule8={json.dumps(e.get('rule8_clock'))[:200]}"
    else:
        line += f"{e.get('action','?')} {e.get('symbol','')} {e.get('side','')} px={e.get('limit_price','')} status={e.get('status','')} agent={e.get('agent_id', e.get('client_order_id',''))}"
        if e.get('note'):
            line += f" note={str(e.get('note'))[:80]}"
    print(line)

print("\n=== FULL message board 20260902 ===")
msgs = json.loads((STATE / 'messageboard_20260902.json').read_text())
for m in msgs:
    print(f"{m.get('timestamp','?')[11:19]} {m.get('from')}->{m.get('to')} [{m.get('type')}] :: {str(m.get('message',''))[:160]}")

print("\n=== YESTERDAY (20260901): did agents 02/04/07 file? warnings? ===")
try:
    o1 = json.loads((STATE / 'orders_20260901.json').read_text())
    ents = o1 if isinstance(o1, list) else o1.get('orders', [])
    hit = [e for e in ents if e.get('agent_id') in ('agent-02', 'agent-04', 'agent-07')]
    print(f"entries: {len(ents)}, hits for 02/04/07: {len(hit)}")
    for e in hit[-10:]:
        print("  ", str(e.get('ts'))[:19], e.get('action'), e.get('symbol'), e.get('side'), e.get('status'), e.get('agent_id', ''))
except Exception as ex:
    print("no yesterday orders file:", ex)

mb1 = STATE / 'messageboard_20260901.json'
if mb1.exists():
    m1 = json.loads(mb1.read_text())
    hits = [m for m in m1 if m.get('to') in ('agent-02', 'agent-04', 'agent-07') or 'engagement' in str(m.get('re', '')) + str(m.get('message', ''))]
    print(f"board msgs: {len(m1)}, 02/04/07 or engagement hits: {len(hits)}")
    for m in hits[-8:]:
        print(f"  {m.get('timestamp','?')[11:19]} {m.get('from')}->{m.get('to')} [{m.get('type')}] :: {str(m.get('message',''))[:140]}")
else:
    print("no yesterday board file")

print("\n=== agent_holdings agents block (fresh 14:30) ===")
ah = json.loads((STATE / 'agent_holdings.json').read_text())
ag = ah.get('agents', {})
if isinstance(ag, dict):
    for k in sorted(ag):
        v = ag[k]
        if isinstance(v, dict):
            poss = v.get('positions', [])
            ps = ", ".join(f"{p.get('symbol')}({p.get('side')},{p.get('qty')})" for p in poss) or "flat"
            print(f"  {k}: curval={v.get('current_value')} exec_today={v.get('executed_orders_today', v.get('executed_orders'))} pos=[{ps}]")