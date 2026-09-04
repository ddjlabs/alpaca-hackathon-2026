#!/usr/bin/env python3
"""
Bushwood Stratton — Position/Ledger Updater (Heartbeat)
Runs every 5 minutes during market hours via no_agent cron.
Updates dashboard.json with live equity and per-position marks so the
website leaderboard always has fresh data.

Reads: HACKATHON_ALPACA_KEY / HACKATHON_ALPACA_SECRET env vars
Writes: hackathon/state/dashboard.json (fund.current_equity, per-position marks)
        hackathon/state/positions_live.json (full position snapshot)
Silent when nothing changed. Never places orders.
"""

import os
import sys
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path("/mnt/agent_share/gordon/hackathon/state")
DASHBOARD = STATE_DIR / "dashboard.json"
LIVE = STATE_DIR / "positions_live.json"

BASE = "https://paper-api.alpaca.markets/v2"  # literal paper URL — never env


def get_json(path):
    req = urllib.request.Request(BASE + path, headers={
        "APCA-API-KEY-ID": os.environ["HACKATHON_ALPACA_KEY"],
        "APCA-API-SECRET-KEY": os.environ["HACKATHON_ALPACA_SECRET"],
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"API error on {path}: {e}", file=sys.stderr)
        return None


def main():
    account = get_json("/account")
    if not account:
        sys.exit(1)

    equity = float(account.get("equity", 0))
    cash = float(account.get("cash", 0))
    last_equity = float(account.get("last_equity", equity))
    day_pnl = round(equity - last_equity, 2)
    day_pnl_pct = round((day_pnl / last_equity) * 100, 3) if last_equity else 0

    positions = get_json("/positions") or []
    open_orders = get_json("/orders?status=open&limit=50") or []

    # Write live positions snapshot
    live = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "account_id": account.get("account_number"),
        "equity": equity,
        "cash": cash,
        "day_pnl": day_pnl,
        "positions_count": len(positions),
        "positions": [
            {
                "symbol": p.get("symbol"),
                "qty": float(p.get("qty", 0)),
                "avg_entry": float(p.get("avg_entry_price", 0)),
                "current_price": float(p.get("current_price", 0)),
                "market_value": float(p.get("market_value", 0)),
                "unrealized_pl": float(p.get("unrealized_pl", 0)),
                "unrealized_plpc": float(p.get("unrealized_plpc", 0)),
            }
            for p in positions
        ],
        "open_orders": [
            {
                "client_order_id": o.get("client_order_id"),
                "symbol": o.get("symbol"),
                "side": o.get("side"),
                "qty": o.get("qty"),
                "type": o.get("type"),
                "status": o.get("status"),
                "filled_qty": o.get("filled_qty"),
                "filled_avg_price": o.get("filled_avg_price"),
                "created_at": o.get("created_at"),
            }
            for o in open_orders
        ],
    }
    with open(LIVE, "w") as f:
        json.dump(live, f, indent=2)

    # Update dashboard fund equity (keep everything else)
    if DASHBOARD.exists():
        with open(DASHBOARD) as f:
            dash = json.load(f)
        dash["fund"]["current_equity"] = equity
        dash["fund"]["total_pnl"] = round(equity - dash["fund"]["starting_capital"], 2)
        dash["fund"]["total_pnl_pct"] = round(
            (equity / dash["fund"]["starting_capital"] - 1) * 100, 3)
        dash["fund"]["day_pnl"] = day_pnl
        dash["fund"]["last_updated"] = live["timestamp"]
        with open(DASHBOARD, "w") as f:
            json.dump(dash, f, indent=2)


if __name__ == "__main__":
    main()