import json
from pathlib import Path
from datetime import date, datetime

BOARD = Path('/mnt/agent_share/gordon/hackathon/state')
today = BOARD / f'messageboard_{date.today().strftime("%Y%m%d")}.json'
msgs = json.loads(today.read_text()) if today.exists() else []
print(f"Total msgs today: {len(msgs)}")
me = 'charlie'
mine = [m for m in msgs if m['to'] in (me, 'all') and not m.get('read')]
print(f"Unread for charlie: {len(mine)}")
for m in mine:
    print("===")
    print(m['id'], '|', m['from'], '->', m['to'], '|', m['type'], '| re:', m.get('re'))
    print(m['message'][:400])

# Mark charlie's messages read
if mine:
    for m in mine:
        m['read'] = True
    out = '[]' if False else json.dumps(msgs, indent=2)
    # build replies for questions
    replies = []
    for m in mine:
        if m['type'] == 'question':
            replies.append(m)
    tmp = today.with_suffix('.tmp')
    tmp.write_text(json.dumps(msgs, indent=2))
    tmp.replace(today)
    print(f"Marked {len(mine)} read. Questions needing reply: {len(replies)}")