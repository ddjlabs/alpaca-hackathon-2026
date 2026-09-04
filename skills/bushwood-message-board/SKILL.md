---
name: bushwood-message-board
description: "Read/write the daily JSON message board for agent comms."
version: 1.0.0
---

# Bushwood Message Board — Daily JSON Comms Protocol

The internal comms channel for ALL Bushwood Stratton agents (trading subagents, Ernie,
Richard, Charlie, Gordo). Every agent reads and writes messages here instead of Telegram
or email.

## File Location & Naming

`/mnt/agent_share/gordon/hackathon/state/messageboard_YYYYMMDD.json`

One file per calendar day. Current day's file is THE live board. Yesterday's file is
history — read for context, never write.

## JSON Schema

A LIST of message objects. Create the file with `[]` if it doesn't exist.

```
[
  {
    "id": "msg-<unix-seconds>-<4-random-hex>",
    "from": "charlie",
    "to": "agent-03",
    "type": "strike",
    "re": "trade-card-123",
    "message": "Strike 1: position limit breach on QQQ put. See hr_board.",
    "timestamp": "2026-08-31T09:41:22-04:00",
    "read": false
  }
]
```

Field rules:
- `id` — required. msg-<unix-epoch>-<4 hex chars>. Never reuse.
- `from` — required. One of: gordo | charlie | richard | ernie | lisa | neil |
  agent-01 .. agent-10 (or clone ids agent-NNRk)
- `to` — required. Same vocabulary, or "all", or "ar".
- `type` — required. Allowed: order_request | order_executed | order_rejected |
  order_rejected_alpaca | strike | risk_note | wire | hr_notice | firing | clone |
  desk_greeting | question | reply | mutant_spawn | termination_notice
- `re` — optional. Kanban card id or subject.
- `message` — required. In-character body.
- `timestamp` — required, ISO 8601 with offset. Set when WRITING.
- `read` — false on write; readers set true on their messages after reading.

## Read (your inbox)

```python
import json
from pathlib import Path
from datetime import date
BOARD = Path('/mnt/agent_share/gordon/hackathon/state')
today = BOARD / f'messageboard_{date.today().strftime("%Y%m%d")}.json'
msgs = json.loads(today.read_text()) if today.exists() else []
me = 'agent-03'
mine = [m for m in msgs if m['to'] in (me, 'all') and not m.get('read')]
for m in mine:
    print(m['from'], '::', m['type'], '::', m['message'])
for m in mine:
    m['read'] = True
if mine:
    tmp = today.with_suffix('.tmp'); tmp.write_text(json.dumps(msgs, indent=2)); tmp.replace(today)
```

## Write (send)

```python
import json, time, uuid
from datetime import datetime, date
from pathlib import Path

def send(from_id, to_id, mtype, message, re=None):
    f = Path('/mnt/agent_share/gordon/hackathon/state') / f'messageboard_{date.today().strftime("%Y%m%d")}.json'
    msgs = json.loads(f.read_text()) if f.exists() else []
    msgs.append({
        'id': f'msg-{int(time.time())}-{uuid.uuid4().hex[:4]}',
        'from': from_id, 'to': to_id, 'type': mtype, 're': re,
        'message': message,
        'timestamp': datetime.now().astimezone().isoformat(timespec='seconds'),
        'read': False,
    })
    tmp = f.with_suffix('.tmp'); tmp.write_text(json.dumps(msgs, indent=2)); tmp.replace(f)
```

ALWAYS atomic write (tmp + rename) — 10+ agents share this file concurrently.
Keep id uniqueness safe under concurrency (epoch + 4 hex random chars).

## Routing Conventions

- Agents → Charlie: type=order_request, to=charlie, re=card id. The kanban card
  `bushwoodstratton_trading` is the canonical approval record; the message board notifies + archives.
- Charlie → agents: order_executed / order_rejected / order_rejected_alpaca / strike.
- Richard → agent/all: risk_note (post-trade review only — he never gates execution).
- Ernie → all: wire + publishes macro-pulse file, dashboard wire, website blog.
- Gordo → all: firing, clone, mutant_spawn, termination_notice, hr notices.
- AR actions (hire/fire) still append to state/ar_log.md — message board supplements,
  never replaces, the AR log and the kanban board.

## Retention
Keep 10 days; the 1AM kanban archive cron prunes older. Not published to the website.

## Integration
- Kanban board `bushwoodstratton_trading`: canonical trade workflow (file → Charlie
  pass/reject → execute → card comment result + message board reply).
- dashboard.json: website display only. Not a comms channel.
- The Support Matrix Telegram: humans only. Agents do NOT read Telegram.
