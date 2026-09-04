#!/usr/bin/env python3
"""Charlie 14:30 poll — RULE 8 TEETH: formal engagement warning to agent-20 (no card, no fill, no positions)."""
import json, time, uuid, os, urllib.request
from pathlib import Path
from datetime import datetime

STATE = Path('/mnt/agent_share/gordon/hackathon/state')

# creds from profile .env (never assume exported)
env = {}
for line in Path('/home/doug/.hermes/profiles/gordon/.env').read_text().splitlines():
    line = line.strip()
    if line.startswith('HACKATHON_ALPACA_') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
KEY, SEC = env.get('HACKATHON_ALPACA_KEY'), env.get('HACKATHON_ALPACA_SECRET')
print('creds:', bool(KEY), bool(SEC))

def get(url):
    req = urllib.request.Request(url, headers={'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

# 1. Environment gate
gate = {}
try:
    a = get('https://paper-api.alpaca.markets/v2/account')
    gate = {'account': a.get('account_number'), 'status': a.get('status'),
            'trading_blocked': a.get('trading_blocked'), 'equity': a.get('equity'), 'cash': a.get('cash')}
    ok = a.get('account_number', '').startswith('PA') and a.get('status') == 'ACTIVE' and not a.get('trading_blocked')
    print('GATE', 'PASS' if ok else 'FAIL', json.dumps(gate))
except Exception as e:
    print('GATE FAIL — alpaca unreachable:', e)
    raise SystemExit(1)

# 2. Resting orders — any roster agent orders needing the 14:30 forced reprice?
resting_agents = []
try:
    oo = get('https://paper-api.alpaca.markets/v2/orders?status=open&limit=100')
    now = datetime.utcnow()
    for o in oo:
        cid = o.get('client_order_id', '')
        is_agent = cid.startswith('agent-')
        if is_agent:
            resting_agents.append({'client_order_id': cid, 'symbol': o['symbol'], 'side': o['side'],
                                   'qty': o['qty'], 'limit_price': o.get('limit_price'),
                                   'submitted_at': o.get('submitted_at'), 'status': o.get('status')})
        print(f"OPEN: {cid} | {o['symbol']} {o['side']} x{o['qty']} lim={o.get('limit_price')} | {o.get('submitted_at')}")
except Exception as e:
    print('open orders fetch failed:', e)
print('resting AGENT orders (reprice candidates):', resting_agents or 'NONE')

# 3. Crypto quotes for the warning (agent-20 triggers: BTC 79,200 / ETH 2,490)
btc = eth = None
try:
    c = get('https://data.alpaca.markets/v1beta3/crypto/us/latest/trades?symbols=BTC%2FUSD,ETH%2FUSD')
    tr = c.get('trades', {})
    btc = float(tr.get('BTC/USD', {}).get('p', 0))
    eth = float(tr.get('ETH/USD', {}).get('p', 0))
    print(f"BTC {btc:,.0f} ({(btc/79200-1)*100:+.1f}% vs 79,200) | ETH {eth:,.0f} ({(eth/2490-1)*100:+.1f}% vs 2,490)")
except Exception as e:
    print('crypto fetch failed:', e)

# 4. Holdings check — agent-20 zero executed orders / zero positions (authoritative)
h = json.loads((STATE / 'portfolio_holdings.json').read_text())
a20_fills = h.get('executed_by_agent', {}).get('agent-20', 0)
a20_pos = [x for x in h.get('holdings', []) if x.get('agent') == 'agent-20']
print(f"agent-20: executed_orders={a20_fills} positions={len(a20_pos)} -> WARNING DUE: {a20_fills == 0 and len(a20_pos) == 0}")

# 5. FORMAL WARNING — Rule 8: engagement (type=order_rejected), Charlie's voice
now_et = datetime.now().astimezone()
deadline = now_et.replace(hour=15, minute=30, second=0, microsecond=0).isoformat(timespec='minutes')
msg = ("RULE 8: ENGAGEMENT — formal warning, Jared Stone, agent-20. "
       f"Your crypto confirms failed at 09:36 (BTC {btc:,.0f} vs 79,200, ETH {eth:,.0f} vs 2,490) and you have filed "
       "NOTHING since: no card, no order, no plan_step_2. You have 60 minutes — file a plan-compliant leg through the "
       "desk by 15:30 ET. At 15:45 with zero fills and zero positions you are flagged NON-TRADING: ineligible for kept "
       "status at the 4:30 firing, and on a day like this — SPX red, ISM printing, tape directional — the bottom-7 "
       "ranking applies to you as-is. Flat is a morning decision; absent is just flat. "
       "The floor pays for exposure, not for presence. — Charlie")
mb = STATE / 'messageboard_20260901.json'
msgs = json.loads(mb.read_text())
warn = {
    'id': f'msg-{int(time.time())}-{uuid.uuid4().hex[:4]}',
    'from': 'charlie', 'to': 'agent-20', 'type': 'order_rejected',
    're': 'rule-8-engagement-warning', 'rule': '8: engagement',
    'message': msg,
    'timestamp': now_et.isoformat(timespec='seconds'), 'read': False,
}
msgs.append(warn)
tmp = mb.with_suffix('.tmp'); tmp.write_text(json.dumps(msgs, indent=2)); tmp.replace(mb)
print('WARNING posted:', warn['id'])

# 6. Poll entry -> orders log (atomic)
of = STATE / 'orders_20260901.json'
orders = json.loads(of.read_text())
entry = {
    'poll': True,
    'poll_time_et': '14:30',
    'poll_ts': now_et.isoformat(timespec='seconds'),
    'kanban_cards_assigned_charlie': 0,
    'environment_gate': gate,
    'resting_agent_orders_needing_reprice': resting_agents,
    'rule8_1430_teeth_fired': {
        'agent': 'agent-20 Jared Stone',
        'condition': 'no card filed today + zero own fills + zero positions at 14:30 (holdings executed_by_agent.agent-20 absent; holdings positions: none)',
        'crypto_at_warning': {'BTC': btc, 'ETH': eth, 'triggers': {'BTC': 79200, 'ETH': 2490}, 'confirms': 'FAILED since 09:36'},
        'action': 'formal WARNING posted to message board (type=order_rejected, rule="8: engagement") — 60-min ultimatum: plan-compliant leg by 15:30 ET or NON-TRADING flag at 15:45',
        'warning_msg_id': warn['id'],
        'exempt_survivors_carried': ['agent-02', 'agent-04'],
        'filled_today_all_others': ['agent-02', 'agent-04', 'agent-07', 'agent-11', 'agent-12', 'agent-14', 'agent-15', 'agent-17', 'agent-18'],
        'forced_reprices_due': [],
    },
    'poll_actions': [
        {'action': 'kanban_scan', 'detail': '0 cards assigned charlie (todo/ready/running/review); board idle'},
        {'action': 'environment_gate', 'detail': f"Alpaca REST 14:30: {gate.get('account')} {gate.get('status')}, trading_blocked={gate.get('trading_blocked')}"},
        {'action': 'rule8_teeth', 'detail': 'agent-20 formal engagement warning posted; no resting roster orders -> no forced bid reprices due; 15:45 NON-TRADING flag armed'},
        {'action': 'open_orders', 'detail': 'ar-cleanup-agent-09-1 QQQ260918C00754000 sell 1 @0.60 limit still stale — AR 16:30 pass, desk does not touch'},
    ],
}
orders.append(entry)
tmp = of.with_suffix('.tmp'); tmp.write_text(json.dumps(orders, indent=1)); tmp.replace(of)
print(f'poll entry appended; orders file now {len(orders)} entries')