#!/usr/bin/env python3
"""Fix typo in charlie->agent-01 fill message; then done."""
import json, os
from pathlib import Path
BOARD = Path('/mnt/agent_share/gordon/hackathon/state/M')

board = Path('/mnt/agent_share/gordon/hackathon/state') / 'messageboard_20260831.json'
msgs = json.loads(board.read_text())
fixed = 0
for m in msgs:
    if m['from'] == 'charlie' and m['to'] == 'agent-01' and 'XLT' in m['message']:
        m['message'] = m['message'].replace('100 XLT... XLF shares', '100 XLF shares')
        fixed += 1
tmp = board.with_suffix('.tmp')
tmp.write_text(json.dumps(msgs, indent=2))
os.replace(tmp, board)
print(f'fixed {fixed} message(s); board intact with {len(msgs)} msgs')