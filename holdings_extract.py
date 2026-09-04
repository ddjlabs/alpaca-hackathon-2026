#!/usr/bin/env python3
"""
Bushwood Holdings Extractor — builds portfolio_holdings.json for the website.
Pulls the complete hackathon-book portfolio: all positions (equities + options),
executed fills with agent attribution (via order_id join), and open orders.

Agent attribution: fills carry order_id → joined against orders' client_order_id
prefix agent-NN (the universal attribution convention).

Usage:
  python3 holdings_extract.py            # write state/portfolio_holdings.json
  python3 holdings_extract.py --dry      # print JSON to stdout
"""

import os
import sys
import re
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path("/mnt/agent_share/gordon/hackathon/state")
OUT = STATE_DIR / "portfolio_holdings.json"
ENV_FILE = Path("/home/doug/.hermes/profiles/gordon/.env")
BASE = "https://paper-api.alpaca.markets/v2"  # literal paper URL
DRY = "--dry" in sys.argv


def load_creds():
    key = os.environ.get("HACKATHON_ALPACA_KEY")
    sec = os.environ.get("HACKATHON_ALPACA_SECRET")
    if key and sec:
        return key, sec
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
        return env.get("HACKATHON_ALPACA_KEY"), env.get("HACKATHON_ALPACA_SECRET")
    return None, None


def get(path, key, sec):
    req = urllib.request.Request(BASE + path, headers={
        "APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def classify(symbol):
    """OCC option symbol: UNDERLYING(1-6) + YYMMDD + C/P + strike*1000 (8 digits)."""
    m = re.match(r"^([A-Z]{1,6})(\d{6})([CP])(\d{8})$", symbol)
    if m:
        return {
            "asset_class": "option",
            "underlying": m.group(1),
            "expiry": f"20{m.group(2)[:2]}-{m.group(2)[2:4]}-{m.group(2)[4:6]}",
            "otype": "call" if m.group(3) == "C" else "put",
            "strike": int(m.group(4)) / 1000.0,
        }
    # Crypto: Alpaca fills use BTC/USD; positions report BTCUSD. Classify both.
    s = symbol or ""
    if "/" in s or (s.endswith("USD") and s[:3] in ("BTC", "ETH", "SOL", "LTC") or s[:4] in ("DOGE", "AVAX", "LINK")) and s.replace("/", "").isalpha():
        return {"asset_class": "crypto"}
    return {"asset_class": "equity"}


def agent_of_client_id(cid):
    cid = (cid or "").lower()
    if cid.startswith("agent-"):
        parts = cid.split("-")
        return parts[0] + "-" + parts[1]
    # cleanup/ops orders: e.g. ar-cleanup-agent-14-1-20260901 -> agent-14
    m = re.search(r"agent-\d+", cid)
    if m:
        return m.group(0)
    return None


def main():
    key, sec = load_creds()
    if not key or not sec:
        print("missing creds", file=sys.stderr)
        sys.exit(1)

    account = get("/account", key, sec)
    account_id = account.get("account_number", "")
    if not account_id.startswith("PA"):
        print("SAFETY ABORT: not paper", file=sys.stderr)
        sys.exit(1)

    positions = get("/positions", key, sec) or []
    fills = get("/account/activities?activity_types=FILL&direction=desc&pageSize=100", key, sec) or []
    orders = get("/orders?status=all&limit=200&direction=desc", key, sec) or []

    # order_id -> agent (from client_order_id)
    oid2agent = {}
    for o in orders:
        a = agent_of_client_id(o.get("client_order_id"))
        if a:
            oid2agent[o["id"]] = a

    # Replacement-chain resolution: Alpaca PATCH /orders strips client_order_id from the
    # replacement order, and FILL activities carry the (new) order_id. Walk replaced_by
    # forward from the original to map replacement ids back to the owning agent.
    orders_by_id = {o["id"]: o for o in orders}
    replaced_by_idx = {}
    for o in orders:
        rb = o.get("replaced_by")
        if rb:
            replaced_by_idx[o["id"]] = rb

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
            back = next((o2 for o2 in orders if o2.get("replaced_by") == oid), None)
            if back:
                oid = back["id"]
                seen += 1
                continue
            return None
        return None

    # executed fills attribution (fills lack client_order_id; join via order_id incl. replacement chain)
    executed_by_agent = {}
    notional_by_agent = {}
    total_executed = 0
    for f in fills:
        a = agent_of_order(f.get("order_id"))
        if a:
            total_executed += 1
            executed_by_agent[a] = executed_by_agent.get(a, 0) + 1
            try:
                notional_by_agent[a] = round(
                    notional_by_agent.get(a, 0.0) + float(f.get("price", 0) or 0) * float(f.get("qty", 0) or 0), 2)
            except (ValueError, TypeError):
                pass

    # holdings with classification + agent attribution
    # Co-held symbols: multiple agents can own the same equity (covered-call legs).
    # Attribute PROPORTIONALLY by each agent's filled buy qty for that symbol.
    # Options CAN be co-held (same contract STO by two agents, e.g. XLU 9/18 41P by
    # agents 25+26) — attribute FILLED SELL qty per agent, split position qty proportionally.
    symbol_agent = {}      # single-owner fallback (normalization: BTC/USD -> BTCUSD)
    symbol_owners = {}     # sym -> {agent: NET filled buy qty}
    option_sellers = {}    # option contract -> {agent: NET filled qty (sell minus buy)}
    option_order = []      # option contract -> creation order (open STOs win)
    for o in sorted(orders, key=lambda x: x.get("created_at") or ""):
        sym = o.get("symbol")
        if not sym:
            continue
        a = agent_of_client_id(o.get("client_order_id")) or agent_of_order(o.get("id"))
        if not a or o.get("status") not in ("filled", "partially_filled"):
            continue
        if classify(sym)["asset_class"] == "option":
            # option contract (e.g. XLF260918P00057000): per-agent NET filled qty
            # (sell minus buy) — buy-to-closes reduce the seller's book.
            sellers = option_sellers.setdefault(sym, {})
            filled = float(o.get("filled_qty", 0) or 0)
            signed = -filled if o.get("side") == "sell" else filled
            sellers[a] = sellers.get(a, 0) + signed
            if sym not in option_order:
                option_order.append(sym)
        else:
            key = sym.replace("/", "")  # crypto: orders say BTC/USD, positions say BTCUSD — one key
            symbol_agent[key] = a  # latest wins (single-owner fallback)
            buyers = symbol_owners.setdefault(key, {})
            try:
                buyers[a] = buyers.get(a, 0) + float(o.get("filled_qty", 0) or 0)
            except (ValueError, TypeError):
                pass

    holdings = []
    for p in positions:
        sym = p.get("symbol", "")
        cls = classify(sym)
        total_qty = abs(float(p.get("qty", 0)))
        owners = symbol_owners.get(sym)
        is_option = cls["asset_class"] == "option"
        pnl = float(p.get("unrealized_pl", 0))

        def make_entry(qty_share, owner=None):
            frac = qty_share / total_qty if (owners and total_qty > 0) else 1.0
            entry = {
                "symbol": sym,
                "asset_class": cls["asset_class"],
                "side": p.get("side", "long"),
                "qty": float(p.get("qty", 0)) * frac,
                "avg_entry": float(p.get("avg_entry_price", 0)),
                "current_price": float(p.get("current_price", 0)),
                "market_value": round((float(p.get("market_value", 0))) * frac, 2),
                "cost_basis": round((float(p.get("cost_basis", 0))) * frac, 2),
                "unrealized_pl": round(pnl * frac, 2),
                "unrealized_plpc": float(p.get("unrealized_plpc", 0)),
                "change_today": round(float(p.get("change_today", 0)), 4),
                "agent": owner if (owner := agent_of_client_id("")) else None,
            }
            entry["agent"] = owner or symbol_agent.get(sym)
            if cls["asset_class"] == "option":
                entry["underlying"] = cls["underlying"]
                entry["expiry"] = cls["expiry"]
                entry["otype"] = cls["otype"]
                entry["strike"] = cls["strike"]
            return entry

        # Options: split by each agent's NET short book (sell minus buy — buy-to-closes
        # shrink the seller's share). Contracts can be co-held (e.g. XLU 9/18 41P by
        # both agent-25 and agent-26). Position sign (short) is preserved.
        if is_option:
            sellers = option_sellers.get(sym) or {}
            shorts = {a: -q for a, q in sellers.items() if q < 0}  # net sold qty per agent
            if len(shorts) > 1:
                total_sold = sum(shorts.values())
                pos_mv = float(p.get("market_value", 0))
                pos_cb = float(p.get("cost_basis", 0))
                for owner, sold_qty in shorts.items():
                    frac = sold_qty / total_sold if total_sold else 0
                    entry = make_entry(total_qty * frac)
                    entry["agent"] = owner
                    entry["qty"] = float(p.get("qty", 0)) * frac
                    entry["market_value"] = round(pos_mv * frac, 2)
                    entry["cost_basis"] = round(pos_cb * frac, 2)
                    entry["unrealized_pl"] = round(pnl * frac, 2)
                    holdings.append(entry)
            else:
                entry = make_entry(total_qty)
                entry["agent"] = (list(shorts.keys())[0] if shorts else symbol_agent.get(sym)) or None
                holdings.append(entry)
        elif not owners or len(owners) <= 1:
            entry = make_entry(total_qty)
            entry["agent"] = (list(owners.keys())[0] if owners else symbol_agent.get(sym)) or entry.get("agent")
            holdings.append(entry)
        else:
            # proportional split for co-held equities
            for owner, bought_qty in sorted(owners.items()):
                if bought_qty <= 0:
                    continue
                share = min(bought_qty, total_qty)
                if share <= 0:
                    continue
                entry = make_entry(share)
                entry["agent"] = owner
                entry["qty"] = share
                # per-share unrealized for accurate split
                per_share_pl = pnl / total_qty if total_qty else 0
                entry["unrealized_pl"] = round(per_share_pl * share, 2)
                holdings.append(entry)

    snap = {
        "schemaVersion": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "account_id": account_id,
        "equity": round(float(account.get("equity", 0)), 2),
        "cash": round(float(account.get("cash", 0)), 2),
        "day_pnl": round(float(account.get("equity", 0)) - float(account.get("last_equity", 0)), 2),
        "total_executed_orders": total_executed,
        "executed_by_agent": executed_by_agent,
        "notional_by_agent": notional_by_agent,
        "positions_count": len(holdings),
        "holdings": holdings,
    }

    if DRY:
        print(json.dumps(snap, indent=1))
        return

    with open(OUT, "w") as f:
        json.dump(snap, f, indent=2)
    print(f"holdings: {len(holdings)} positions | executed: {total_executed} | saved {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()