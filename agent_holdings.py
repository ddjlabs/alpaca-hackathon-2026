#!/usr/bin/env python3
"""
Per-Agent Holdings Aggregator — builds agent_holdings.json for the website.
Groups portfolio_holdings.json by agent, computes per-agent book value +
unrealized P&L + tenure (days since the agent (or its bloodline root) was hired).

Tenure source: dashboard.json agents[].generation + hire dates tracked in
state/hire_log.json (written by the spawning process; Generation 1 chartered Aug 28).

Usage:
  python3 agent_holdings.py            # write state/agent_holdings.json
  python3 agent_holdings.py --dry
"""

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

STATE_DIR = Path("/mnt/agent_share/gordon/hackathon/state")
OUT = STATE_DIR / "agent_holdings.json"
HIRE_LOG = STATE_DIR / "hire_log.json"
DRY = "--dry" in sys.argv

# Generation 1 charter date (founding souls) — tenure counts trading days since hire
CHARTER_DATE = date(2026, 8, 28)


def main():
    holdings = json.loads((STATE_DIR / "portfolio_holdings.json").read_text())
    dash = json.loads((STATE_DIR / "dashboard.json").read_text())

    hire_dates = {}
    if HIRE_LOG.exists():
        hire_dates = {h["agent_id"]: h.get("hired") for h in json.loads(HIRE_LOG.read_text())}

    agents_out = []
    by_agent = {}
    for pos in holdings.get("holdings", []):
        a = pos.get("agent") or "desk"
        by_agent.setdefault(a, []).append(pos)

    for agent in dash.get("agents", []):
        aid = agent.get("id")
        positions = by_agent.get(aid, [])
        total_mv = round(sum(p["market_value"] for p in positions), 2)
        total_unreal = round(sum(p["unrealized_pl"] for p in positions), 2)
        equity_qty = sum(abs(p["qty"]) for p in positions if p["asset_class"] == "equity")
        option_qty = sum(abs(p["qty"]) for p in positions if p["asset_class"] == "option")

        # tenure: days since hire (bloodline charter date, else today)
        hired = hire_dates.get(aid)
        if hired:
            hired_date = datetime.fromisoformat(hired).date() if isinstance(hired, str) else hired
        else:
            hired_date = CHARTER_DATE
        tenure_days = (date.today() - hired_date).days

        agents_out.append({
            "agent_id": aid,
            "name": agent.get("name"),
            "generation": agent.get("generation", 1),
            "status": agent.get("status"),
            "tenure_days": tenure_days,
            "allocation": agent.get("allocation"),
            "positions_count": len(positions),
            "equity_count": sum(1 for p in positions if p["asset_class"] == "equity"),
            "option_count": sum(1 for p in positions if p["asset_class"] == "option"),
            "total_market_value": total_mv,
            "unrealized_pl": total_unreal,
            "daily_pnl": agent.get("daily_pnl", 0),
            "executed_orders": (holdings.get("executed_by_agent") or {}).get(aid, 0),
            "positions": positions,
        })

    # desk/unattributed bucket
    desk_positions = by_agent.get("desk", [])
    if desk_positions:
        agents_out.append({
            "agent_id": "desk",
            "name": "House Desk (unattributed)",
            "generation": None,
            "status": "internal",
            "tenure_days": None,
            "allocation": None,
            "positions_count": len(desk_positions),
            "total_market_value": round(sum(p["market_value"] for p in desk_positions), 2),
            "unrealized_pl": round(sum(p["unrealized_pl"] for p in desk_positions), 2),
            "daily_pnl": 0,
            "executed_orders": 0,
            "positions": desk_positions,
        })

    snap = {
        "schemaVersion": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "equity": holdings.get("equity"),
        "cash": holdings.get("cash"),
        "agents": agents_out,
    }
    if DRY:
        print(json.dumps(snap, indent=1)[:2000])
        return
    with open(OUT, "w") as f:
        json.dump(snap, f, indent=2)
    print(f"agent holdings: {len(agents_out)} agents | {sum(a['positions_count'] for a in agents_out)} positions", file=sys.stderr)


if __name__ == "__main__":
    main()