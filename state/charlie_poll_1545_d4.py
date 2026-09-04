#!/usr/bin/env python3
"""Charlie 15:45 poll Day 4 (Sep 2) — Rule 8 teeth: agent-24 close-out already
executed 15:18; fallback unfilled at 15:45 -> NON-TRADING FLAG + board notices
+ AR/orders log. Atomic writes throughout. No strike (engagement flag)."""
import json, time, uuid
from datetime import datetime
from pathlib import Path

S = Path('/mnt/agent_share/gordon/hackathon/state')
NOW = datetime.now().astimezone()
NOW_S = NOW.isoformat(timespec='seconds')
TARGET = 'agent-24'

def atomic_write(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)

# ---------- 1. dashboard.json: non_trading_flag ----------
dp = S / 'dashboard.json'
d = json.loads(dp.read_text())
flagged = []
for a in d.get('agents', []):
    if a['id'] == TARGET:
        a['non_trading_flag'] = True
        a['status'] = 'active'  # stays active per directive
        flagged.append(a['id'])
assert flagged == [TARGET], f'unexpected flag set: {flagged}'
atomic_write(dp, d)
print('dashboard: non_trading_flag=true ->', flagged, '(status active preserved)')

# ---------- 2. message board: agent notice + firing context ----------
mb = S / 'messageboard_20260902.json'
msgs = json.loads(mb.read_text())
msgs.append({
    'id': f'msg-{int(time.time())}-{uuid.uuid4().hex[:4]}',
    'from': 'charlie',
    'to': TARGET,
    'type': 'order_rejected',
    're': 'rule-8-non-trading-flag',
    'rule': '8: engagement',
    'message': (
        "RULE 8: NON-TRADING FLAG \u2014 Ray Blues, agent-24. 15:45 ET: zero executions, "
        "zero positions, no survivor exemption. The trail: filed the 83P at 0.28 against "
        "a 0.23 bid at 09:43 \u2014 you spent the open asking five cents over what the market "
        "was already paying \u2014 then aged through both reprice touches (13:33 to 0.20, "
        "14:04 to 0.18) and the 15:18 close-out, and the fallback at 0.19 has sat AT the "
        "live bid for 28 minutes with zero fills. The desk walked your price 9 cents and "
        "the tape still said no. dashboard.json: non_trading_flag=true, status active. "
        "At the 4:30 firing you are ineligible for kept, and on a tape like today \u2014 "
        "Iran overnight, WTI +8.4%, VIX +15% \u2014 the bottom-7 ranking applies to you "
        "as-is. The fallback stays working; a fill before the bell lifts the flag. "
        "The floor pays for exposure, not for presence. \u2014 Charlie"
    ),
    'timestamp': NOW_S,
    'read': False,
})
msgs.append({
    'id': f'msg-{int(time.time())}-{uuid.uuid4().hex[:4]}',
    'from': 'charlie',
    'to': 'ar',
    'type': 'risk_note',
    're': 'rule-8-non-trading-agent-24',
    'message': (
        "FIRING CONTEXT 15:45 ET \u2014 agent-24 Ray Blues flagged NON-TRADING "
        "(non_trading_flag=true in dashboard.json): zero fills, zero positions D4. "
        "Filed XLP260918P00083000 STO 0.28 vs 0.23 bid 09:43; both Rule-8 reprice "
        "touches consumed (13:33 \u2192 0.20, 14:04 \u2192 0.18); Rule-8 close-out executed "
        "15:18 \u2014 resting order canceled, plan_step_2 fallback STO same contract 1 @ 0.19 "
        "filed \u2014 zero fills at 15:45. Per Rule 8 amendment: ineligible for kept status "
        "at the 4:30 firing; on a directional tape (Iran overnight, WTI +8.4%, VIX +15%) "
        "the bottom-7 ranking applies as-is. No strike (engagement flag, not compliance). "
        "All other 9 agents met the options-per-day requirement by execution (22/25/26 at "
        "13:33, 23/21 at 14:04, 27 at 09:43) or carried book (02/04/07 survivor short puts). "
        "\u2014 Charlie"
    ),
    'timestamp': NOW_S,
    'read': False,
})
atomic_write(mb, msgs)
print('board: 2 notices posted (agent-24 flag + ar firing context)')

# ---------- 3. AR log ----------
ar = S / 'ar_log.md'
entry = f"""
## {NOW_S.split('T')[0]}T15:45 ET \u2014 Charlie 15:45 poll \u2014 RULE 8 TEETH: agent-24 NON-TRADING FLAG
- Board: EMPTY \u2014 0 cards for charlie, 0 inbound order_requests (kanban rescanned 15:46). Gates: PA3GWO1FKED0 ACTIVE, trading_blocked=false, equity $99,836, cash $93,580.59 (Alpaca REST 15:46). Rule 10 re-verified: 9/9 positions attributed to active agents, risk block real values (gross 2.64% / net 2.38% / largest BTCUSD 2.51% / short-op reserve $40,300), holdings rollup fresh 15:45:19.
- 15:45 CHECKPOINT EXECUTED: agent-24 Ray Blues \u2014 sole zero-execution agent. Fallback (agent-24-20260902-opt-1-fallback, STO XLP260918P00083000 1 @ 0.19, filed 15:17:49 per the 15:18 close-out) verified live: status=new, filled 0, quote 0.19x0.21, last 0.17, delta -0.145. Zero fills at 15:45 \u2192 dashboard.json non_trading_flag=true (status active preserved), Day-4 format matched (no strike \u2014 engagement flag, not compliance).
- Timeline: 09:43 filed 0.28 vs 0.23 bid \u2192 13:33 reprice #1 to 0.20 (timing-deviation window) \u2192 14:04 reprice #2 to 0.18 (bid) \u2192 15:18 close-out: cancel + plan_step_2 fallback at mid 0.19 \u2192 15:45 flag. Both reprice touches consumed per the ONE-rule as executed. Fallback stays working into the close; a fill lifts the flag.
- Board notices: 2 posted (agent-24 order_rejected flag notice; ar risk_note FIRING CONTEXT for the 4:30). Exempt: 02/04/07 (survivor carried short puts). Met by execution: 22/25/26 (13:33), 23/21 (14:04 fills @ 0.13), 27 (BTC 09:43). Warnings issued today: NONE (every zero-fill hire held a resting order all day).
- Strikes: 0. Rejections: 0. Fills today: 6 (Wolf BTC + 13:33 trio + 21/23 @ 0.13). Resting: fallback 0.19 DAY + Wolf 2 GTC (crypto).
- Standing line: 0.00 on a live book is a question, not an answer \u2014 verified again this poll.
"""
with ar.open('a') as f:
    f.write(entry)
print('ar_log: 15:45 entry appended')

# ---------- 4. orders log ----------
ol = S / 'orders_20260902.json'
log = json.loads(ol.read_text())
log.append({
    'poll': True,
    'poll_time_et': '15:45',
    'poll_ts': NOW_S,
    'kanban_cards_assigned_charlie': 0,
    'environment_gate': {
        'account': 'PA3GWO1FKED0',
        'status': 'ACTIVE',
        'trading_blocked': False,
        'equity': 99836.0,
        'cash': 93580.59,
        'verified_via': 'Alpaca REST 15:46 ET',
    },
    'resting_agent_orders_needing_reprice': [],
    'open_orders': [
        'agent-24-20260902-opt-1-fallback (XLP260918P00083000 sell 1 @0.19 limit, DAY, filed 15:17:49Z close-out, zero fills at 15:45)',
        'agent-27-20260902-lim-1/lim-2 (Wolf BTC/ETH GTC limits \u2014 crypto, not Rule-8 scope)',
    ],
    'rule8_1545_checkpoint': {
        'sole_target': 'agent-24 Ray Blues',
        'status': 'NON-TRADING FLAG SET \u2014 zero fills, zero positions, no exemption; fallback 0.19 at live bid unfilled at 15:45',
        'actions': [
            'dashboard.json non_trading_flag=true (status active preserved)',
            'message board order_rejected flag notice to agent-24',
            'message board risk_note FIRING CONTEXT to ar for 4:30 firing',
            'no strike (engagement flag, not compliance)',
        ],
        'exempt_carried_positions': ['agent-02', 'agent-04', 'agent-07'],
        'filled_today': ['agent-21', 'agent-22', 'agent-23', 'agent-25', 'agent-26', 'agent-27'],
    },
    'poll_actions': [
        {'action': 'kanban_scan', 'detail': '0 cards assigned charlie; board clear'},
        {'action': 'environment_gate', 'detail': 'Alpaca REST 15:46: PA3GWO1FKED0 ACTIVE, trading_blocked=false, equity 99836.00'},
        {'action': 'fallback_verification', 'detail': 'live order status + indicative snapshot pulled; agent-24 fallback new/unfilled @ 0.19 vs quote 0.19x0.21'},
        {'action': 'rule8_1545_flag', 'detail': 'agent-24 flagged NON-TRADING; board notices posted; AR + orders log updated'},
    ],
})
atomic_write(ol, log)
print('orders log: 15:45 poll entry appended (total entries:', len(log), ')')

# ---------- verify ----------
d2 = json.loads(dp.read_text())
a24 = next(a for a in d2['agents'] if a['id'] == TARGET)
assert a24.get('non_trading_flag') is True and a24['status'] == 'active'
mb2 = json.loads(mb.read_text())
tail = [m for m in mb2 if m.get('ts', m.get('timestamp', '')).startswith('2026-09-02T15:5')]
print('VERIFY: agent-24 flag', a24['non_trading_flag'], '| status', a24['status'], '| board msgs now', len(mb2), '| latest:', [m['to'] + ':' + m['type'] for m in mb2[-2:]])