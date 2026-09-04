#!/usr/bin/env python3
"""Rule 8 unfilled-watch evaluator — prints JSON verdict for Charlie.

Day-5 fix (2026-09-03 16:50): the old version read dashboard field
`executed_orders_today`, which DOES NOT EXIST — every active agent false-flagged
as zero-exec. Per Rule 10: execution = FILL, counted from the Alpaca TAPE
(client_order_id `agent-NN-*` prefix on orders with filled_at set), never from
dashboard convenience fields. Fills source = JSON array of Alpaca orders,
defaulting to state/_fills_today.json (the poll's tape snapshot).

Usage: rule8_check.py [fills_json_path]
"""
import json, sys, datetime, re, os

DAY = datetime.date.today().isoformat()
STATE = "/mnt/agent_share/gordon/hackathon/state"
HOLDINGS = os.path.join(STATE, "portfolio_holdings.json")
DASH = os.path.join(STATE, "dashboard.json")
FILLS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(STATE, "_fills_today.json")

def load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception as e:
        return {"_error": str(e)}

holdings = load(HOLDINGS)
dash = load(DASH)
fills = load(FILLS)

agents = {a["id"]: a for a in dash.get("agents", []) if a.get("status") == "active"}

# TODAY's executions from the tape: client_order_id agent-NN prefix + filled_at today (ET)
filled_agents = set()
if isinstance(fills, list) and "_error" not in fills:
    for o in fills:
        coid = o.get("client_order_id") or ""
        m = re.match(r"agent-(\d+)-", coid)
        if m and o.get("filled_at") and o.get("filled_at", "").startswith(DAY):
            filled_agents.add(f"agent-{m.group(1)}")

# carried portfolio = positions attributed to the agent on the live book
pos_agents = {h.get("agent") for h in holdings.get("holdings", []) if h.get("agent")}

zero_exec = sorted(aid for aid in agents if aid not in filled_agents)
unfilled = sorted(aid for aid in zero_exec if aid not in pos_agents)
exempt = sorted(aid for aid in zero_exec if aid in pos_agents)

verdict = {
    "now_et": datetime.datetime.now().strftime("%H:%M"),
    "day": DAY,
    "fills_source": FILLS,
    "fills_source_error": fills.get("_error") if isinstance(fills, dict) else None,
    "tape_filled_today": sorted(filled_agents),
    "active_agents": sorted(agents.keys()),
    "zero_exec_active": zero_exec,
    "unfilled_watch_no_positions": unfilled,
    "exempt_carried_portfolio": exempt,
    "carried_agents_dashboard": sorted(k for k, v in agents.items() if v.get("carried_portfolio")),
    "positions_count": holdings.get("positions_count"),
    "total_executed": holdings.get("total_executed_orders"),
}
print(json.dumps(verdict, indent=2))