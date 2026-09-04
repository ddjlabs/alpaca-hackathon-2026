import json
from pathlib import Path
from datetime import datetime

f = Path('/mnt/agent_share/gordon/hackathon/state/orders_20260902.json')
msgs = json.loads(f.read_text())
msgs.append({
  "poll_heartbeat": True,
  "ts": datetime.now().astimezone().isoformat(timespec='seconds'),
  "action": "poll_1130",
  "account": "PA3GWO1FKED0",
  "status": "ACTIVE",
  "trading_blocked": False,
  "equity": 99835.17,
  "board": "empty at 11:30 ET — 0 cards for charlie, 0 inbound messages",
  "cards_processed": 0,
  "open_orders": 8,
  "open_orders_note": "6 day-option legs resting (21/23 XLF55.5P 0.16, 22 XLF55P 0.14, 24 XLP83P 0.28, 25/26 XLU41P 0.16) + Wolf 2 staged GTC (BTC 75800, ETH 2365); all intentional, verified live",
  "fills_since_last_poll": "NONE (only 09:43 Wolf BTC tranche today; 13:30-13:31Z cluster = 09:30 AR close-out, pre-logged)",
  "rule8_clock": "NOT ARMED (11:30 < 14:30). 14:30 watch: agents 21/22/23/24 (resting since 09:43, zero pos) + 25/26 (resting since 10:48, zero pos) = forced reprice to live bid if unfilled at 14:30 unless filled first. agent-27 exempt (filled 09:43). agents 02/04/07 exempt (survivor carried short puts).",
  "watch_flags": "XLF 55P live bid 0.06 at 11:15 is UNDER 0.10 min-rent — agent-22 forced reprice may have no legal strike at 14:30 (law outranks teeth); recompute quote live at 14:30.",
  "ar_cleanup_note": "no new AR entries this poll",
  "day_pnl_at_poll": -164.83
})
tmp = f.with_suffix('.tmp')
tmp.write_text(json.dumps(msgs, indent=1))
tmp.replace(f)
print("heartbeat appended; entries:", len(msgs))