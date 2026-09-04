"""10:15 poll pt5: build Rule 8 unfilled-watch record + write state/orders_20260902.json."""
import json, os
from datetime import datetime

STATE = '/mnt/agent_share/gordon/hackathon/state'

h = json.load(open(f'{STATE}/portfolio_holdings.json'))
print('holdings ts:', h.get('timestamp'), '| equity', h.get('equity'), '| total_exec', h.get('total_executed_orders'))
print('executed_by_agent:', json.dumps(h.get('executed_by_agent')))
print('notional_by_agent:', json.dumps(h.get('notional_by_agent')))
print('positions_count:', h.get('positions_count'))
holdings = h.get('holdings')
print('holdings type:', type(holdings).__name__, 'len:', len(holdings) if holdings else 0)
if isinstance(holdings, list):
    for p in holdings:
        print('  ', json.dumps(p)[:220])
elif isinstance(holdings, dict):
    for k, p in holdings.items():
        print('  ', k, json.dumps(p)[:220])

dash = json.load(open(f'{STATE}/dashboard.json'))
print('--- DASHBOARD AGENTS ---')
for a in dash.get('agents', []):
    print(f"  {a.get('id')} {a.get('name'):26} | carried={json.dumps(a.get('carried_portfolio'))[:80]} | strategy={str(a.get('strategy'))[:70]}")

log_path = f'{STATE}/orders_20260902.json'
log = []
if os.path.exists(log_path):
    log = json.load(open(log_path))

entry = {
    'poll': '1015',
    'timestamp': datetime.now().astimezone().isoformat(timespec='seconds'),
    'board_cards_for_charlie': 0,
    'board_messages_new_since_0944': 0,
    'account_gate': {'account': 'PA3GWO1FKED0', 'status': 'ACTIVE', 'trading_blocked': False, 'PASS': True},
    'equity': 99838.67,
    'open_orders': [
        {'agent': 'agent-21', 'coid': 'agent-21-20260902-opt-1', 'symbol': 'XLF260918P00055500', 'side': 'sell', 'qty': 1, 'limit': 0.16, 'tif': 'day', 'filed': '09:43:30', 'status': 'new'},
        {'agent': 'agent-22', 'coid': 'agent-22-20260902-opt-1', 'symbol': 'XLF260918P00055000', 'side': 'sell', 'qty': 1, 'limit': 0.14, 'tif': 'day', 'filed': '09:43:30', 'status': 'new'},
        {'agent': 'agent-23', 'coid': 'agent-23-20260902-opt-1', 'symbol': 'XLF260918P00055500', 'side': 'sell', 'qty': 1, 'limit': 0.16, 'tif': 'day', 'filed': '09:43:30', 'status': 'new'},
        {'agent': 'agent-24', 'coid': 'agent-24-20260902-opt-1', 'symbol': 'XLP260918P00083000', 'side': 'sell', 'qty': 1, 'limit': 0.28, 'tif': 'day', 'filed': '09:43:30', 'status': 'new'},
    ],
    'fills_today': [
        {'agent': 'agent-27', 'symbol': 'BTC/USD', 'side': 'buy', 'qty': 0.0325, 'price': 77148.736, 'status': 'filled', 'note': 'Tranche 1 market at 09:43; engagement floor met by execution'}
    ],
    'rule8_unfilled_watch': {
        'armed_at': '14:30 ET',
        'note': 'Pre-clock poll: no teeth before 14:30. Recorded at 10:16.',
        'resting_track_reprice_at_1430': ['agent-21', 'agent-22', 'agent-23', 'agent-24'],
        'warning_track_no_card_no_fill': ['agent-25', 'agent-26'],
        'filled_exempt': ['agent-27'],
        'carried_portfolio_exempt': ['survivors with open short puts (XLF56000, XLF57000, XLU260904P42000)'],
        'agent_25_26_caveat': 'XLU chain was illegal at 09:38 (delta -0.212 > 0.20 law); re-file only if chain re-ranges legal — check delta at 14:30 before forcing warning-only path'
    },
    'data_issue': 'Alpaca options quotes unavailable 10:15+: snapshots/quotes feed=iex -> 400 invalid option feed; feed=opra -> 403 OPRA agreement not signed. Position marks OK. 14:30 forced reprice needs live bid -> use Yahoo options chain (query1.finance.yahoo.com) or BS delta from Yahoo IV as fallback.',
    'actions_taken': 'NONE — no cards, no new messages, pre-clock window. Watch recorded.',
}
entry['open_orders'] = [o for o in entry['open_orders'] if 'coid' in o]

log.append(entry)
tmp = log_path + '.tmp'
with open(tmp, 'w') as f:
    json.dump(log, f, indent=2)
os.replace(tmp, log_path)
print('LOG WRITTEN:', log_path, 'entries:', len(log))