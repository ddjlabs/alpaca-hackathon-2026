#!/usr/bin/env python3
"""Message board: order_executed per fill + order_rejected_alpaca for failed legs."""
import json, time, uuid, os
from datetime import datetime
from pathlib import Path

BOARD = Path('/mnt/agent_share/gordon/hackathon/state')
today = BOARD / 'messageboard_20260831.json'
msgs = json.loads(today.read_text()) if today.exists() else []

def send(from_id, to_id, mtype, message, re=None):
    msgs.append({
        'id': f'msg-{int(time.time())}-{uuid.uuid4().hex[:4]}',
        'from': from_id, 'to': to_id, 'type': mtype, 're': re,
        'message': message,
        'timestamp': datetime.now().astimezone().isoformat(timespec='seconds'),
        'read': False,
    })
    time.sleep(1.1)  # keep ids unique under epoch-second granularity

FILLS = json.load(open(f'{BOARD}/fills_20260831.json'))
BY_AGENT = {}
for f in FILLS:
    BY_AGENT.setdefault(f['agent'], []).append(f)

NOTES = {
    'agent-01': '100 XLT... XLF shares @ 57.85. Your 61C credit is resting at 0.08 — let it come to you.',
    'agent-02': '57P STO filled 0.36 — 2c better than your plan limit. Reserve noted: $5,700.',
    'agent-03': '58P STO filled 0.43 (fat), seatbelt 57P BTO filled 0.14. Net credit 0.29 vs plan 0.25 — you beat your own quote. Defined risk: max loss $44/ct. (Two earlier belt limits 0.07/0.12 canceled chasing a running ask — final print wins.)',
    'agent-04': '56P STO filled 0.19 — a tick over plan. Mission intact. Reserve noted: $5,600.',
    'agent-05': '100 XLF shares @ 57.85. Weekly 59C credit resting 0.12.',
    'agent-06': 'Long leg filled: 60C BTO 0.15.',
    'agent-08': '100 XLP shares @ 85.2875 (11c under your 85.60 cap). 90C credit resting 0.11.',
    'agent-09': 'Long call wing filled: QQQ 754C BTO 0.72.',
    'agent-10': '100 XLF shares @ 57.85, under your 58.20 ground. 60.5C credit resting 0.14.',
}
for agent, fills in BY_AGENT.items():
    lines = '; '.join(f"{f['sym']} {f['side'].upper()} @ {f['avg']}" for f in fills)
    send('charlie', agent, 'order_executed',
         f"OPENING DEPLOYMENT D2 — FILLED: {lines}. {NOTES.get(agent, '')} Stop levels live in triggers.json. Do not retry canceled belt legs.", re='opening-deployment-D2')

send('charlie', 'agent-03', 'order_executed',
     'Correction to the record: your bull put 58/57 is COMPLETE — short 58P @ 0.43, long 57P @ 0.14, net credit 0.29, defined risk intact.', re='opening-deployment-D2')

send('charlie', 'agent-06', 'order_rejected_alpaca',
     'ALPACA REJECT (40310000): STO XLF260918C00059000 — "account not eligible to trade uncovered option contracts". Mleg route also unsupported on XLF (422). You hold a naked LONG 60C @ 0.15 — that is your defined-risk book until refiled. Your plan step 2 is pre-authorized: file a kanban card "refile 59/61 bear call, width $2, credit limit 0.33" and I will pair it. Do NOT market-buy premium to force it.', re='opening-deployment-D2')

send('charlie', 'agent-09', 'order_rejected_alpaca',
     'ALPACA REJECTS (40310000 x2): short wings QQQ 678P ("insufficient options buying power for cash-secured put, required $67,534") and 744C ("not eligible to trade uncovered option contracts"). Mleg route unsupported on QQQ (422). The condor as designed cannot be sequenced on this account. You hold long 754C @ 0.72; your 668P BTO @ 1.67 limit is still resting — it is defined risk and doubles as AVGO-Wed downside armor; decide by 11am whether to keep or I cancel it. Plan step 2 is pre-authorized: file a kanban card for the 676/666P + 746/756C condor and I will attempt sequenced entry only if shorts clear eligibility.', re='opening-deployment-D2')

tmp = today.with_suffix('.tmp')
tmp.write_text(json.dumps(msgs, indent=2))
os.replace(tmp, today)
print(f'message board now has {len(msgs)} messages; wrote 10 fills + 2 rejections + 1 correction')