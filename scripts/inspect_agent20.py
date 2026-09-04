#!/usr/bin/env python3
"""Inspect message board + dashboard for agent-20 context."""
import json
from pathlib import Path

f = Path('/mnt/agent_share/gordon/hackathon/state/messageboard_20260901.json')
msgs = json.loads(f.read_text())
print(f"--- {len(msgs)} messages today ---")
for m in msgs:
    print(f"{m['timestamp'][11:19]} [{m['from']}->{m['to']}] {m['type']} re={str(m.get('re'))[:40]} :: {m['message'][:110]}")

print("\n--- agent-20 mentions ---")
hits = 0
for m in msgs:
    blob = json.dumps(m)
    if 'agent-20' in blob:
        hits += 1
        print(m['timestamp'], m['from'], '->', m['to'], m['type'], '::', m['message'][:250])
print('total hits:', hits)

print("\n--- dashboard keys / day ---")
d = json.loads(Path('/mnt/agent_share/gordon/hackathon/state/dashboard.json').read_text())
print('keys:', list(d.keys()))
for k in list(d.keys()):
    v = d[k]
    if isinstance(v, (str, int, float, bool)):
        print(k, '=', v)

print("\n--- agent-20 full entry ---")
for ag in d.get('agents', []):
    if ag.get('id') == 'agent-20':
        print(json.dumps(ag, indent=1))

print("\n--- AR log tail (agent-20 hires) ---")
ar = Path('/mnt/agent_share/gordon/hackathon/state/ar_log.md')
if ar.exists():
    lines = ar.read_text().splitlines()
    for ln in lines:
        if 'agent-20' in ln or 'Jared Stone' in ln:
            print(ln[:220])
else:
    print('no ar_log.md')