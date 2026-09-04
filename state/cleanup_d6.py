#!/usr/bin/env python3
"""D5 6PM: check open orders, then wire 6 ar-cleanup BTO GTC closers for fired books."""
import os, json, urllib.request, urllib.error
from datetime import datetime

BASE = "https://paper-api.alpaca.markets"
HDRS = {"APCA-API-KEY-ID": os.environ["HACKATHON_ALPACA_KEY"],
        "APCA-API-SECRET-KEY": os.environ["HACKATHON_ALPACA_SECRET"],
        "Content-Type": "application/json"}
OUT = "/mnt/agent_share/gordon/hackathon/state"

def req(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(BASE + path, data=data, headers=HDRS, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]

# 1) open orders check
st, orders = req("GET", "/v2/orders?status=open&limit=100")
print("open orders status:", st, "count:", len(orders) if isinstance(orders, list) else orders)
json.dump(orders, open(f"{OUT}/_orders_open_1800_d6spawn.json", "w"), indent=1)

if isinstance(orders, list) and len(orders) > 0:
    print("ABORT: open orders exist, not wiring closers")
    raise SystemExit(1)

# 2) wire the 6 closers (GTC, day-plus, capped at mark + a hair; family min-rent respected)
closers = [
    ("agent-28", "XLF260918P00055500", 0.09),   # Chris Roma — flat book, closers his shelf's risk
    ("agent-29", "XLF260918P00055000", 0.09),   # Eddie Roma
    ("agent-30", "XLF260918P00056000", 0.13),   # Walt Blues — STO 0.10, mark 0.12
    ("agent-31", "XLU260918P00041500", 0.14),   # Murph Blues — STO 0.09, mark 0.13
    ("agent-32", "XLU260918P00041500", 0.14),   # Alan Levene
    ("agent-33", "XLU260918P00041500", 0.14),   # Roy Levene
]
results = []
for agent, sym, limit in closers:
    body = {
        "symbol": sym, "qty": "1", "side": "buy", "type": "limit",
        "time_in_force": "gtc", "limit_price": f"{limit:.2f}",
        "client_order_id": f"ar-cleanup-{agent}-1-20260903",
        "extended_hours": False,
    }
    st, resp = req("POST", "/v2/orders", body)
    ok = st in (200, 201)
    results.append({"agent": agent, "symbol": sym, "limit": limit, "status_code": st,
                    "order_id": resp.get("id") if ok else None,
                    "coid": resp.get("client_order_id") if ok else str(resp)[:200]})
    print(f"  {agent} BTO {sym} @ {limit}: {st} {resp.get('id') if ok else str(resp)[:160]}")

json.dump(results, open(f"{OUT}/_cleanup_orders_1800_d6spawn.json", "w"), indent=1)
print("wired:", sum(1 for r in results if r["order_id"]), "/", len(results))
print("ts:", datetime.now().astimezone().isoformat(timespec="seconds"))