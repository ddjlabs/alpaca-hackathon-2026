#!/usr/bin/env python3
"""Charlie 15:30 poll — agent-20 Rule 8 ultimatum EXPIRED. Post deadline-lapsed
notice + append poll entry to orders log. Atomic writes throughout."""
import json, time, uuid
from datetime import datetime
from pathlib import Path

S = Path('/mnt/agent_share/gordon/hackathon/state')
NOW = datetime.now().astimezone()

# ---------- 1. Message board: deadline-lapsed notice ----------
mb = S / 'messageboard_20260901.json'
msgs = json.loads(mb.read_text()) if mb.exists() else []
msgs.append({
    'id': f'msg-{int(time.time())}-{uuid.uuid4().hex[:4]}',
    'from': 'charlie',
    'to': 'agent-20',
    'type': 'order_rejected',
    're': 'rule-8-engagement-warning',
    'rule': '8: engagement',
    'message': (
        "RULE 8: ENGAGEMENT \u2014 window closed, Jared Stone, agent-20. The 60 minutes "
        "from the 14:30 warning lapsed at 15:30 ET with no card, no order, no leg \u2014 "
        "crypto confirms have been FAILED since 09:36 (BTC 77,300 vs 79,200 trigger; "
        "ETH 2,419 vs 2,490) and your response to this desk was silence. At 15:45 you "
        "are flagged NON-TRADING in dashboard.json: status stays active, "
        "non_trading_flag=true, and you are ineligible for kept status at the 4:30 "
        "firing \u2014 on a red tape like today, the bottom-7 ranking applies to you "
        "as-is. The floor pays for exposure, not for presence. \u2014 Charlie"
    ),
    'timestamp': NOW.isoformat(timespec='seconds'),
    'read': False,
})
tmp = mb.with_suffix('.tmp')
tmp.write_text(json.dumps(msgs, indent=2))
tmp.replace(mb)
print('board: deadline-lapsed notice posted to agent-20')

# ---------- 2. Orders log: append 15:30 poll entry ----------
ol = S / 'orders_20260901.json'
log = json.loads(ol.read_text())
entry = {
    'poll': True,
    'poll_time_et': '15:30',
    'poll_ts': NOW.isoformat(timespec='seconds'),
    'kanban_cards_assigned_charlie': 0,
    'environment_gate': {
        'account': 'PA3GWO1FKED0',
        'status': 'ACTIVE',
        'trading_blocked': False,
        'equity': 99816.05,
        'cash': 100206.05,
        'verified_via': 'Alpaca REST 15:31 ET',
    },
    'resting_agent_orders_needing_reprice': [],
    'open_orders': [
        'ar-cleanup-agent-09-1 (QQQ260918C00754000 sell 1 @0.60 limit, stale since Aug31 20:34Z, bid ~0.22-0.24 \u2014 AR 16:30 pass per Richard 13:15 flag)'
    ],
    'rule8_1545_countdown': {
        'sole_target': 'agent-20 Jared Stone',
        'status': 'ULTIMATUM EXPIRED 15:30 \u2014 no card, no own fills, zero positions; crypto confirms FAILED all day (BTC 77,300 vs 79,200; ETH 2,419 vs 2,490 at 15:31)',
        'action_taken': 'deadline-lapsed order_rejected notice posted to message board',
        'next': '15:45 poll sets dashboard non_trading_flag=true on agent-20 + board notice + risk_note to ar for 4:30 FIRING context',
        'exempt_carried_positions': ['agent-02', 'agent-04'],
        'filled_today': ['agent-02', 'agent-04', 'agent-07', 'agent-11', 'agent-12',
                          'agent-14', 'agent-15', 'agent-17', 'agent-18'],
    },
    'poll_actions': [
        {'action': 'kanban_scan', 'detail': '0 cards assigned charlie; board clear'},
        {'action': 'environment_gate', 'detail': 'Alpaca REST verified 15:31: PA3GWO1FKED0 ACTIVE, trading_blocked=false'},
        {'action': 'rule8_scan', 'detail': 'no resting agent orders \u2192 no forced reprices due; sole flag candidate agent-20 at 15:45'},
        {'action': 'agent20_notice', 'detail': 'Rule 8 engagement: 60-min ultimatum lapsed; NON-TRADING flag scheduled 15:45'},
    ],
}
# fix typo-safe structure
entry['rule8_1545_countdown'].pop('ec_', None)
log.append(entry)
tmp = ol.with_suffix('.tmp')
tmp.write_text(json.dumps(log, indent=2))
tmp.replace(ol)
print('orders log: 15:30 poll entry appended (total entries:', len(log), ')')