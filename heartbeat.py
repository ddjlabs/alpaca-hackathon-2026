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
import re
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

    # executed fills with agent attribution (fills carry order_id; join orders → client_order_id)
    # INCL. replacement chain: Alpaca PATCH strips client_order_id from replacement orders,
    # and fills land with the replacement's order_id — walk replaced_by to find the owner.
    all_orders = get_json("/orders?status=all&limit=500") or []
    fills = get_json("/account/activities?activity_types=FILL&direction=desc&pageSize=100") or []
    oid2agent = {}
    orders_by_id = {}
    for o in all_orders:
        cid = (o.get("client_order_id") or "").lower()
        if cid.startswith("agent-"):
            parts = cid.split("-")
            oid2agent[o.get("id")] = parts[0] + "-" + parts[1]
        orders_by_id[o.get("id")] = o

    def agent_of_order(oid):
        seen = 0
        while oid and seen < 10:
            a = oid2agent.get(oid)
            if a:
                return a
            o = orders_by_id.get(oid)
            if not o:
                return None
            nxt = o.get("replaced_by")
            if nxt:
                oid = nxt
                seen += 1
                continue
            back = next((o2 for o2 in all_orders if o2.get("replaced_by") == oid), None)
            if back:
                oid = back.get("id")
                seen += 1
                continue
            return None
        return None

    executed_by_agent = {}
    for fl in fills:
        a = agent_of_order(fl.get("order_id"))
        if a:
            executed_by_agent[a] = executed_by_agent.get(a, 0) + 1
    total_executed = sum(executed_by_agent.values())

    # Write live positions snapshot
    live = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "account_id": account.get("account_number"),
        "equity": equity,
        "cash": cash,
        "day_pnl": day_pnl,
        "positions_count": len(positions),
        "total_executed_orders": total_executed,
        "executed_by_agent": executed_by_agent,
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

        # ---- Richard's risk block: computed from the live book, not left at defaults.
        # gross = sum |market_value|; short-option notional = strike*100 per contract
        # (max loss if assigned). Largest position/agent computed off the same book.
        try:
            attr_holdings = json.loads((STATE_DIR / "portfolio_holdings.json").read_text()).get("holdings", [])
        except Exception:
            attr_holdings = []
        sym_to_agent = {}
        for hp in attr_holdings:
            if hp.get("agent"):
                sym_to_agent.setdefault(hp.get("symbol"), hp["agent"])

        gross_mv = 0.0
        short_option_reserve = 0.0
        by_symbol_mv = {}
        by_agent_notional = {}
        crypto_mv = 0.0
        for pos in positions:
            mv = abs(float(pos.get("market_value", 0) or 0))
            sym = pos.get("symbol", "")
            qty = float(pos.get("qty", 0) or 0)
            gross_mv += mv
            by_symbol_mv[sym] = by_symbol_mv.get(sym, 0.0) + mv
            agent = sym_to_agent.get(sym)
            if sym.replace("/", "") in ("BTCUSD", "ETHUSD"):
                crypto_mv += mv
            notional = mv
            # OCC option: 1-6 letter root + 6-digit date + C/P + 8-digit strike
            m_opt = re.match(r"^([A-Z]{1,6})(\d{6})([CP])(\d{8})$", sym)
            if m_opt and qty < 0:
                # short option: reserve = strike * 100 (max loss if assigned)
                strike = int(m_opt.group(4)) / 1000.0
                short_option_reserve += strike * 100 * abs(qty)
                notional = strike * 100 * abs(qty)
            if agent:
                by_agent_notional[agent] = by_agent_notional.get(agent, 0.0) + notional

        gross_exposure_pct = round(gross_mv / equity * 100, 2) if equity else 0
        # net = sum of signed market values (longs minus shorts) as % of equity
        net_pct = round((sum(float(p.get("market_value", 0) or 0) for p in positions)) / equity * 100, 2) if equity else 0
        largest_sym = max(by_symbol_mv, key=lambda s: by_symbol_mv[s]) if by_symbol_mv else None
        largest_position_pct = round(by_symbol_mv[largest_sym] / equity * 100, 2) if largest_sym and equity else 0
        largest_agent = max(by_agent_notional, key=lambda a: by_agent_notional[a]) if by_agent_notional else None
        largest_agent_pct = round(by_agent_notional[largest_agent] / equity * 100, 2) if largest_agent and equity else 0
        # drawdown: fund-level vs last close (heartbeat cadence)
        day_dd_pct = round(-day_pnl / last_equity * 100, 2) if last_equity and day_pnl < 0 else 0

        risk_limits = dash.get("risk", {})
        risk_limits.update({
            "current_drawdown_pct": day_dd_pct,
            "current_leverage": round(gross_exposure_pct / 100, 4),
            "gross_exposure_pct": gross_exposure_pct,
            "net_exposure_pct": net_pct,
            "largest_position_pct": largest_position_pct,
            "largest_position_symbol": largest_sym,
            "largest_agent_pct": largest_agent_pct,
            "largest_agent": largest_agent,
            "short_option_reserve_usd": round(short_option_reserve, 2),
            "crypto_exposure_usd": round(crypto_mv, 2),
            "computed_at": live["timestamp"],
        })
        dash["risk"] = risk_limits
        with open(DASHBOARD, "w") as f:
            json.dump(dash, f, indent=2)


if __name__ == "__main__":
    main()
    # Refresh the holdings snapshot too (website portfolio page reads it)
    try:
        import subprocess
        subprocess.run([sys.executable, "/mnt/agent_share/gordon/hackathon/holdings_extract.py"], check=False, capture_output=True)
        # per-agent rollup (website portfolio page) — must never go stale after firings
        subprocess.run([sys.executable, "/mnt/agent_share/gordon/hackathon/agent_holdings.py"], check=False, capture_output=True)
    except Exception as e:
        print(f"holdings refresh failed: {e}", file=sys.stderr)