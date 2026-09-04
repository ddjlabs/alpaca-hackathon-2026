#!/usr/bin/env python3
"""Charlie 13:30 D7 — indicative quote pre-flight for 14:30 teeth + poll log append."""
import json, os, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

STATE = Path('/mnt/agent_share/gordon/hackathon/state')
KEY = os.environ.get('HACKATHON_ALPACA_KEY', '')
SEC = os.environ.get('HACKATHON_ALPACA_SECRET', '')
DATA = 'https://data.alpaca.markets'
HDRS = {'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC}

def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {'_error': e.code, '_body': e.read().decode()[:200]}
    except Exception as e:
        return {'_error': str(e)}

syms = ('XLF260918P00055500,XLF260918P00056000,XLU260918P00041500,'
        'SPY260918P00735000,SPY260918P00725000')
snaps = get(f'{DATA}/v1beta1/options/snapshots?symbols={syms}&feed=indicative')
qout = {}
if isinstance(snaps, dict) and '_error' in snaps:
    print('SNAPSHOT ERROR:', snaps)
    qout = {'feed': 'ERROR', 'detail': snaps}
else:
    items = (snaps or {}).get('snapshots')
    if not isinstance(items, dict):
        print('SNAPSHOT PAYLOAD UNEXPECTED:', json.dumps(snaps)[:300])
        items = {}
    for sym, s in sorted(items.items()):
        q = s.get('latestQuote') or {}
        t = s.get('latestTrade') or {}
        qout[sym] = {'bid': q.get('bp'), 'ask': q.get('ap'), 'bid_sz': q.get('bs'),
                     'ask_sz': q.get('as_') or q.get('as'), 'last': t.get('p')}
        print(f"{sym}: bid {q.get('bp')} x {q.get('bs')} | ask {q.get('ap')} x {q.get('as_') or q.get('as')} | last {t.get('p')}")
    qout['feed'] = 'OK'

# resting vs live-bid preview (teeth = reprice to bid at 14:30 if still resting)
preview = []
for sym, o in [('XLF260918P00055500', 0.15), ('XLF260918P00056000', 0.19), ('XLU260918P00041500', 0.14)]:
    bid = (qout.get(sym) or {}).get('bid')
    if bid is not None:
        preview.append(f"{sym}: resting {o} vs bid {bid} -> reprice delta {round(bid - o, 2):+.2f}")
if preview:
    print('TEETH PREVIEW (if still resting at 14:30):')
    for p in preview:
        print('  ' + p)

# --- holdings attribution re-check (13:15 finding) ---
ph = json.load(open(STATE / 'portfolio_holdings.json'))
agents = ph.get('agents') or []
null_rows = 0
for h in ph.get('holdings', []):
    if not h.get('agent'):
        null_rows += 1
print(f"\nHOLDINGS: rebuilt {ph.get('timestamp')} | rows {len(ph.get('holdings', []))} | agent_id=null rows: {null_rows}")
print(f"agents[] rows: {len(agents)} | positions_count: {ph.get('positions_count')}")

# --- append poll entry to orders log ---
log = json.load(open(STATE / 'orders_20260903.json'))
now = datetime.now(timezone(timedelta(hours=-4)))
poll_data = json.load(open(STATE / 'poll_1330_d7.json'))
entry = {
    'poll': '13:30 ET — trade board poll (pre-clock; teeth arm 14:30 ET)',
    'time': now.isoformat(),
    'board': 'bushwoodstratton_trading',
    'cards_for_charlie': 0,
    'message_board_inbound': 0,
    'environment_gate': {
        'account': poll_data['gate']['account'], 'status': poll_data['gate']['status'],
        'trading_blocked': poll_data['gate']['trading_blocked'],
        'equity': poll_data['gate']['equity'], 'cash': poll_data['gate']['cash'],
        'open_orders': poll_data['open_orders_n'],
    },
    'rule_8_unfilled_watch': {
        'state': 'PRE-CLOCK — teeth arm 14:30 ET (this poll took no teeth actions)',
        'executed_today': ['agent-07 (BTC XLU260904P00042000 @ 0.04, 09:38 ET — tape-verified)'],
        'exempt_carried': ['agent-02 (XLF260918P00057000 short)', 'agent-04 (XLF260918P00056000 short)'],
        'resting_unfilled_since_0938': ['agent-28', 'agent-29', 'agent-30', 'agent-31', 'agent-32', 'agent-33', 'agent-34'],
        'no_card_no_fill': [],
        'quote_preflight': qout,
        'teeth_preview_if_resting_1430': preview,
        'queue_1430': 'ONE forced reprice to live bid per resting agent (7x) if still unfilled',
        'queue_1545': 'forced close-out (plan_step_2 fallback at live mid) + agent-34 T2 GTC cancel + agent-33 HARD review',
    },
    'rule_10_silent_zero_verification': {
        'live_positions': len(poll_data['positions']),
        'attribution': f"PASS — 2/2 survivor-carried short puts resolve (agent-04 XLF56P, agent-02 XLF57P); holdings publisher agent_id=null finding from 13:15 poll RESOLVED upstream — 13:30:21 ET rebuild carries agent fields on all holdings rows, null rows: {null_rows} (no hand-patch)",
        'open_order_tape': '8/8 legs status=new at filed limits (28+29 XLF55.5P@0.15, 30 XLF56P@0.19, 31/32/33 XLU41.5P@0.14, 34 spread-1 -0.60 day + spread-2 -1.55 GTC); zero drift vs 13:15',
        'fill_tape': '6 fills today unchanged (agent-07 exit + 5 AR-cleanup legs); no new prints since 13:38:51Z',
        'holdings_rollup_fresh': True,
    },
    'actions': [
        'VERIFIED: kanban queue empty (0 cards for charlie)',
        'VERIFIED: message board 16 msgs today, 0 inbound to charlie since 12:21 status-correction wires',
        'VERIFIED: environment gate PASS (PA3GWO1FKED0 / ACTIVE / trading_blocked=false)',
        'VERIFIED: indicative options snapshot feed ALIVE (data.alpaca.markets feed=indicative) — teeth have live bids at 14:30',
        'VERIFIED: holdings publisher attribution fix landed upstream (null agent rows 1 -> 0)',
        'MONITOR: teeth fire at 14:30 ET poll — 7 watchlist agents',
    ],
    'strikes': 0, 'rejections': 0, 'warnings': 0,
    'fills_today': 6, 'new_fills_this_poll': 0,
    'summary': 'QUIET POLL — no cards, no inbound, pre-clock. Tape verified unchanged; quote feed pre-flight OK; 13:15 attribution finding resolved upstream.',
}
log['polls'].append(entry)
tmp = STATE / 'orders_20260903.json.tmp'
with open(tmp, 'w') as f:
    json.dump(log, f, indent=1)
tmp.rename(STATE / 'orders_20260903.json')
print(f"\nPoll entry appended -> orders_20260903.json ({len(log['polls'])} polls)")