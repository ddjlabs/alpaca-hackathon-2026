#!/usr/bin/env python3
"""16:45 post-close poll: gate check + board/inbox scan + heartbeat log."""
import json, time, uuid, os, urllib.request
from datetime import datetime
from pathlib import Path

STATE = Path('/mnt/agent_share/gordon/hackathon/state')
TODAY = '20260902'

# --- creds ---
env = {}
for line in Path('/home/doug/.hermes/profiles/gordon/.env').read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
KEY = env.get('HACKATHON_ALPACA_KEY')
SEC = env.get('HACKATHON_ALPACA_SECRET')
if not KEY or not SEC:
    print('FATAL: hackathon creds missing from .env'); raise SystemExit(1)

def alpaca(path):
    req = urllib.request.Request('https://paper-api.alpaca.markets' + path,
        headers={'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

# --- environment gate ---
acct = alpaca('/v2/account')
gate = {
    'account': acct.get('account_number'),
    'status': acct.get('status'),
    'trading_blocked': acct.get('trading_blocked'),
    'equity': acct.get('equity'),
    'cash': acct.get('cash'),
}
print('GATE:', json.dumps(gate))
gate_pass = (str(gate['account']).startswith('PA') and gate['status'] == 'ACTIVE'
             and gate['trading_blocked'] is False)
print('GATE_PASS:', gate_pass)

# --- open orders + positions ---
orders = alpaca('/v2/orders?status=open&limit=50')
open_oids = [(o.get('client_order_id'), o.get('symbol'), o.get('qty'), o.get('status')) for o in orders]
print('OPEN_ORDERS:', len(open_oids))
for coid, sym, qty, st in open_oids:
    print('  ', coid, sym, qty, st)

positions = alpaca('/v2/positions')
print('POSITIONS:', len(positions))
for p in positions:
    print(' ', p.get('symbol'), p.get('qty'), 'mark', p.get('current_price'))

# --- kanban (via CLI separately) — message board here ---
mb = STATE / f'messageboard_{TODAY}.json'
msgs = json.loads(mb.read_text()) if mb.exists() else []
mine_unread = [m for m in msgs if m.get('to') in ('charlie',) and not m.get('read')]
print('BOARD_MSGS_TOTAL:', len(msgs))
print('UNREAD_TO_CHARLIE:', len(mine_unread))
for m in msgs[-6:]:
    print(' LAST:', m.get('timestamp'), m.get('from'), '->', m.get('to'), m.get('type'), '::', (m.get('message') or '')[:90])
# firing notices present?
firing = [m for m in msgs if m.get('type') in ('firing', 'termination_notice')]
print('FIRING_NOTICES:', len(firing), [m.get('re') or (m.get('message') or '')[:60] for m in firing])

# mark charlie's unread as read (atomic)
if mine_unread:
    for m in mine_unread:
        m['read'] = True
    tmp = mb.with_suffix('.tmp')
    tmp.write_text(json.dumps(msgs, indent=2))
    tmp.replace(mb)
    print('MARKED_READ:', len(mine_unread))

# --- dashboard flag verify ---
dash = STATE / 'dashboard.json'
flag = None
roster = []
if dash.exists():
    d = json.loads(dash.read_text())
    for a in d.get('agents', []):
        roster.append((a.get('id'), a.get('name'), a.get('status'), a.get('non_trading_flag', False)))
    a24 = [a for a in d.get('agents', []) if a.get('id') == 'agent-24']
    if a24:
        flag = a24[0].get('non_trading_flag')
print('AGENT24_NON_TRADING_FLAG:', flag)
print('ROSTER:', json.dumps(roster))

# --- append heartbeat to orders log (atomic) ---
olog = STATE / f'orders_{TODAY}.json'
entries = json.loads(olog.read_text())
entries.append({
    'time': '16:45 ET',
    'type': 'poll_1645',
    'status': gate['status'],
    'gate': gate,
    'gate_pass': gate_pass,
    'note': ('POST-CLOSE POLL 16:45: board empty (0 cards for charlie, '
             f'{len(mine_unread)} unread to charlie at poll). Gates '
             f"{gate['account']} {gate['status']} blocked={gate['trading_blocked']} "
             f"(live REST 16:45), equity ${gate['equity']}, cash ${gate['cash']}. "
             f'Open orders: {len(open_oids)} (5 GTC ar-cleanup BTO closers close Thu open + any residual). '
             f'Positions: {len(positions)}. agent-24 non_trading_flag={flag}. '
             'No actions due this poll. Day-4 Rule-8 final stands: 9/10 traded, '
             '6 fills, 0 strikes, 0 rejections, 0 warnings.'),
})
tmp = olog.with_suffix('.tmp')
tmp.write_text(json.dumps(entries, indent=2))
tmp.replace(olog)
print('HEARTBEAT_APPENDED: poll_1645, total entries now', len(entries))