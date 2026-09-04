import json, os
from pathlib import Path
from datetime import datetime

f = Path('/mnt/agent_share/gordon/hackathon/state/orders_20260902.json')
msgs = json.loads(f.read_text())
msgs.append({
  "poll_heartbeat": True,
  "ts": datetime.now().astimezone().isoformat(timespec='seconds'),
  "action": "poll_0930",
  "account": "PA3GWO1FKED0",
  "status": "ACTIVE",
  "trading_blocked": False,
  "equity": 99798.57,
  "cards_processed": 0,
  "board": "empty at 09:30 ET — no cards assigned to charlie (pre-deploy; Day 4 roster deploys 09:35)",
  "inbox": "clean (ernie 07:00 wire only)",
  "rule8_clock": "not armed (arms 14:30 ET)",
  "ar_cleanup_note": "AR close-out completed 09:30:04-09:31:32 ET: 6 survivor short-put covers filled (XLU260918P00042000 @0.43, XLF261016P00055000 @0.49, XLF260918P00057500 @0.85, XLF261016P00057000 @1.09, XLF260918P00055000 @0.15, XLF260918P00054000 @0.09) + agent-09 QQQ260918C00754000 sold @0.20. Book FLAT: 0 positions, 0 open orders. Executed_orders tally unchanged (agent books carry to 4:30 tally, not these cleanup fills).",
  "day_pnl_at_poll": -24.15
})
tmp = f.with_suffix('.tmp')
tmp.write_text(json.dumps(msgs, indent=1))
tmp.replace(f)
print("heartbeat appended; entries:", len(msgs))