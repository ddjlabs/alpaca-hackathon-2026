#!/usr/bin/env python3
"""
Soul Protocol Patcher — Option C implementation.
For every live soul.md lacking the MESSAGE BOARD PROTOCOL:
  1. stage a persona.md copy of the current soul
  2. append the protocol (agent-id-aware) to the staging copy
  3. validate, then rename staging -> soul.md (re-activation)

Usage: python3 patch_soul_protocol.py            # do it
       python3 patch_soul_protocol.py --dry-run  # show plan only
"""

import sys
import re
from pathlib import Path

AGENTS_DIR = Path("/mnt/agent_share/gordon/hackathon/agents")


def protocol(agent_id: str) -> str:
    return f"""

## MESSAGE BOARD PROTOCOL (INTERNAL COMMS)

You do NOT use Telegram or email. All comms via the daily JSON message board.
Full code reference: Hermes skill bushwood-message-board.
File: /mnt/agent_share/gordon/hackathon/state/messageboard_YYYYMMDD.json
Element: {{"id":"msg-<epoch>-<4hex>","from":"{agent_id}","to":"charlie","type":"order_request","re":null,"message":"...","timestamp":"ISO-8601","read":false}}

Send (atomic tmp+rename):
```python
import json,time,uuid
from datetime import datetime,date
from pathlib import Path
f=Path(f'/mnt/agent_share/gordon/hackathon/state/messageboard_{{date.today():%Y%m%d}}.json')
msgs=json.loads(f.read_text()) if f.exists() else []
msgs.append({{"id":f"msg-{{int(time.time())}}-{{uuid.uuid4().hex[:4]}}","from":"{agent_id}","to":"charlie","type":"order_request","re":None,"message":"...","timestamp":datetime.now().astimezone().isoformat(timespec="seconds"),"read":False}})
t=f.with_suffix('.tmp');t.write_text(json.dumps(msgs,indent=2));t.replace(f)
```

Read inbox:
```python
me="{agent_id}"; msgs=json.loads(f.read_text())
mine=[m for m in msgs if m.get("to") in (me,"all") and not m.get("read")]
# process then mark m["read"]=True and atomic-save
```

Your id: {agent_id}. From/to vocabulary: gordo|charlie|richard|ernie|lisa|neil|agent-01..10.
You will receive: order_executed | order_rejected (strike) | order_rejected_alpaca (move to next plan step).
"""


def main() -> int:
    dry = "--dry-run" in sys.argv
    patched, skipped = 0, 0

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or not agent_dir.name.startswith("agent-"):
            continue
        soul = agent_dir / "soul.md"
        if not soul.exists():
            continue
        content = soul.read_text(encoding="utf-8")
        if "MESSAGE BOARD PROTOCOL" in content:
            print(f"  {agent_dir.name}: already has protocol")
            continue
        m = re.search(r"agent_id:\s*(\S+)", content)
        agent_id = m.group(1) if m else "-".join(agent_dir.name.split("-")[:2])

        if dry:
            print(f"  [dry] {agent_dir.name}: would patch ({agent_id})")
            patched += 1
            continue

        staging = agent_dir / "persona.md"
        staging.write_text(content + protocol(agent_id), encoding="utf-8")
        # validation: protocol is present now
        final = staging.read_text(encoding="utf-8")
        if "MESSAGE BOARD PROTOCOL" in final and "## TERMINATION" in final and "## WHY YOU EXIST" in final:
            staging.replace(soul)
            patched += 1
            print(f"✅ {agent_dir.name}: protocol embedded ({agent_id})")
        else:
            skipped += 1
            print(f"⚠️  {agent_dir.name}: validation failed after patch")

    print(f"\nPatched: {patched}, Skipped/failed: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())