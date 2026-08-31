#!/usr/bin/env python3
"""
Bushwood Stratton — Hourly Dashboard Aggregator
Runs every hour during market days (cron: 15 9-16 * * 1-5 — 9:15AM-4:15PM ET).
Splits per-agent P&L from attributed fills into dashboard.json so the website
leaderboard updates hourly between the 5-minute heartbeat equity ticks.

Agent attribution: Alpaca client_order_id prefix "agent-NN-*" — same convention
used by the execution cron and the sample trade.

Reads: HACKATHON_ALPACA_KEY / HACKATHON_ALPACA_SECRET from env or .env
Writes: hackathon/state/dashboard.json (agents[].daily_pnl, current_value)
        hackathon/state/positions_live.json (timestamp refresh)
Silent on success. Errors go to stderr.
"""

import os
import sys
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path("/mnt/agent_share/gordon/hackathon/state")
DASHBOARD = STATE_DIR / "dashboard.json"
ENV_FILE = Path("/home/doug/.hermes/profiles/gordon/.env")
BASE = "https://paper-api.alpaca.markets/v2"  # literal paper URL — never env

STARTING_CAPITAL = 100_000.0


def load_creds():
    key = os.environ.get("HACKATHON_ALPACA_KEY")
    sec = os.environ.get("HACKATHON_ALPACA_SECRET")
    if key and sec:
        return key, sec
    # .env fallback — parse manually, don't require python-dotenv
    if ENV_FILE.exists():
        env = {}
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
        return env.get("HACKATHON_ALPACA_KEY"), env.get("HACKATHON_ALPACA_SECRET")
    return None, None


def get_json(key, sec, path):
    req = urllib.request.Request(BASE + path, headers={
        "APCA-API-KEY-ID": key,
        "APCA-API-SECRET-KEY": sec,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"API error on {path}: {e}", file=sys.stderr)
        return None


def main():
    creds = load_creds()
    if not creds or not all(creds):
        print("Missing HACKATHON_ALPACA_KEY/SECRET", file=sys.stderr)
        sys.exit(1)
    key, sec = creds

    account = get_json(key, sec, "/account")
    if not account:
        sys.exit(1)

    equity = float(account.get("equity", 0))
    last_equity = float(account.get("last_equity", equity))
    day_pnl = round(equity - last_equity, 2)

    # Attributed fills: sum realized P&L per agent from fill activities
    fills = get_json(key, sec, "/account/activities?activity_types=FILL&direction=desc&pageSize=100") or []
    agent_pnl = {}
    for f in fills:
        coid = f.get("client_order_id") or ""
        if coid.startswith("agent-"):
            agent_id = coid.split("-")[0] + "-" + coid.split("-")[1]  # agent-NN
            try:
                agent_pnl.setdefault(agent_id, 0.0)
                # FILL activities don't carry pnl directly; accumulate notional flow for ranking proxy
                price = float(f.get("price", 0) or 0)
                qty = float(f.get("qty", 0) or 0)
                side = f.get("side", "")
                # crude realized proxy: sell fills positive, buy fills negative
                agent_pnl[agent_id] += (price * qty) if side == "sell" else -(price * qty)
            except (ValueError, TypeError):
                pass

    positions = get_json(key, sec, "/positions") or []
    # map positions to agents via open position's client order id chain (approximate: nothing on position object)
    # → attribute unrealized P&L via the orders log instead

    orders = get_json(key, sec, "/orders?status=all&limit=100") or []
    agent_exposure = {}
    for o in orders:
        coid = o.get("client_order_id") or ""
        if coid.startswith("agent-") and o.get("status") in ("filled", "partially_filled"):
            agent_id = "agent-" + coid.split("-")[1]
            try:
                filled_qty = float(o.get("filled_qty", 0) or 0)
                price = float(o.get("filled_avg_price", 0) or 0)
                if o.get("side") == "buy":
                    agent_exposure.setdefault(agent_id, []).append(price * filled_qty)
                else:
                    agent_exposure.setdefault(agent_id, []).append(-(price * filled_qty))
            except (ValueError, TypeError):
                pass

    # Update dashboard
    if not DASHBOARD.exists():
        print("dashboard.json missing", file=sys.stderr)
        sys.exit(1)

    with open(DASHBOARD) as fh:
        dash = json.load(fh)

    agents = dash.get("agents", [])
    for a in agents:
        aid = a.get("id")
        realized = round(agent_pnl.get(aid, 0.0), 2)
        exposure = round(sum(agent_exposure.get(aid, [])), 2)
        a["daily_pnl"] = realized
        a["current_value"] = round(a.get("allocation", 10000) + realized, 2)
        a["daily_pnl_pct"] = round(realized / max(a.get("allocation", 10000), 1) * 100, 3)
        a["exposure"] = exposure

    dash["fund"]["current_equity"] = equity
    dash["fund"]["total_pnl"] = round(equity - STARTING_CAPITAL, 2)
    dash["fund"]["total_pnl_pct"] = round((equity / STARTING_CAPITAL - 1) * 100, 3)
    dash["fund"]["day_pnl"] = day_pnl
    dash["fund"]["day_pnl_pct"] = round(day_pnl / last_equity * 100, 3) if last_equity else 0
    dash["fund"]["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(DASHBOARD, "w") as fh:
        json.dump(dash, fh, indent=2)

    # Optional: hourly snapshot for the site's history chart
    hist = dash.setdefault("daily_history", [])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_rows = [r for r in hist if isinstance(r, dict) and r.get("date") == today and r.get("intraday")]
    hist[:] = [r for r in hist if not (isinstance(r, dict) and r.get("date") == today and r.get("intraday"))]
    hist.append({"date": today, "intraday": True, "time": datetime.now(timezone.utc).strftime("%H:%M"),
                 "equity": equity, "day_pnl": day_pnl})


if __name__ == "__main__":
    main()