#!/usr/bin/env python3
"""D4 FIRING 4:45 CLEANUP — liquidate the dead men's booties.
Wolf (fired #1): cancel 2 staged GTC buys, market-exit any crypto he holds.
5 fired short puts OTM>$0.05: capped GTC buy-to-close for Thu open (D2/D3 precedent).
Ray flat. Verify + log. Never prints secrets."""
import json, os, sys, time, urllib.request, urllib.error
from datetime import datetime

STATE = "/mnt/agent_share/gordon/hackathon/state"
BASE = "https://paper-api.alpaca.markets"

def env_from(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = env_from("/home/doug/.hermes/profiles/gordon/.env")
KEY = os.environ.get("HACKATHON_ALPACA_KEY") or env.get("HACKATHON_ALPACA_KEY")
SEC = os.environ.get("HACKATHON_ALPACA_SECRET") or env.get("HACKATHON_ALPACA_SECRET")
if not KEY or not SEC:
    sys.exit("NO CREDS — abort, never guess")

def req(path, method="GET", body=None):
    r = urllib.request.Request(BASE + path, method=method,
        headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC,
                 "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body else None
    try:
        with urllib.request.urlopen(r, data, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {"_status": resp.status}
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode()[:300]}

# environment gate
acct = req("/v2/account")
assert acct.get("status") == "ACTIVE" and not acct.get("trading_blocked", True), f"ACCOUNT GATE FAIL: {acct.get('status')}"
print("GATE PASS — equity", acct["equity"], "cash", acct["cash"])

results = {"canceled": [], "crypto_exit": [], "option_closers": [], "errors": []}

# ---- 1. cancel Wolf's staged GTC buys ----
open_orders = req("/v2/orders?status=open&limit=100")
for o in open_orders:
    if str(o.get("client_order_id", "")).startswith("agent-27"):
        d = req(f"/v2/orders/{o['id']}", "DELETE")
        ok = isinstance(d, dict) and "_http_error" not in d
        results["canceled"].append({"coid": o["client_order_id"], "order_id": o["id"],
                                    "symbol": o["symbol"], "qty": o["qty"],
                                    "result": "canceled_204" if ok else d})
        print(("CANCELED " if ok else "CANCEL-FAIL ") + o["client_order_id"], o["symbol"], o["qty"])

# ---- 2. crypto market exit for Wolf (any BTC/ETH long remaining) ----
positions = req("/v2/positions")
wolf_px = {}
for p in positions:
    if p["asset_class"] == "crypto":
        sym = "BTC/USD" if p["symbol"].startswith("BTC") else ("ETH/USD" if p["symbol"].startswith("ETH") else None)
        if not sym:
            continue
        entry = float(p["avg_entry_price"]) * abs(float(p["qty"]))
        body = {"symbol": sym, "qty": p["qty"], "side": "sell", "type": "market",
                "time_in_force": "gtc", "client_order_id": f"ar-cleanup-agent-27-1-20260902",
                "position_intent": "sell_to_close"}
        o = req("/v2/orders", "POST", body)
        if "_http_error" in o:
            results["errors"].append({"crypto_exit": sym, "err": o})
            print("CRYPTO-EXIT FAIL", sym, o)
        else:
            oid = o["id"]
            for _ in range(15):
                time.sleep(3)
                st = req(f"/v2/orders/{oid}")
                if st.get("status") in ("filled", "canceled", "rejected", "expired"):
                    break
            fill_px = st.get("filled_avg_price")
            wolf_px[sym] = {"filled_qty": st.get("filled_qty"), "avg_px": fill_px,
                            "status": st.get("status"), "entry_cost_usd": round(entry, 2),
                            "proceeds_usd": round(float(fill_px) * float(st.get("filled_qty") or 0), 2) if fill_px else None}
            results["crypto_exit"].append({"coid": body["client_order_id"], "order_id": oid,
                                           "symbol": sym, "qty": p["qty"], **wolf_px[sym]})
            print(f"CRYPTO-EXIT {sym} qty={p['qty']} -> {st.get('status')} @ {fill_px} (entry ${round(entry,2)})")

# ---- 3. five fired short puts: capped GTC buy-to-close for Thu open ----
CLOSERS = [
    ("agent-21", "XLF260918P00055500", 0.15, 0.19),   # Dave Roma 55.5P
    ("agent-22", "XLF260918P00055000", 0.11, 0.13),   # Lou Roma 55P
    ("agent-23", "XLF260918P00055500", 0.15, 0.19),   # Jake Blues 55.5P (co-held)
    ("agent-25", "XLU260918P00041000", 0.11, 0.13),   # Tommy Levene 41P
    ("agent-26", "XLU260918P00041000", 0.11, 0.13),   # Marvin Levene 41P (co-held)
]
live_syms = {p["symbol"] for p in positions}
for agent_id, sym, mark, cap in CLOSERS:
    if sym not in live_syms:
        results["errors"].append({"closer": agent_id, "sym": sym, "err": "position not found — skip"})
        print("SKIP (no position)", agent_id, sym)
        continue
    coid = f"ar-cleanup-{agent_id}-1-20260902"
    body = {"symbol": sym, "qty": "1", "side": "buy", "type": "limit",
            "time_in_force": "gtc", "limit_price": f"{cap:.2f}",
            "client_order_id": coid, "position_intent": "buy_to_close"}
    o = req("/v2/orders", "POST", body)
    if "_http_error" in o:
        results["errors"].append({"closer": coid, "err": o})
        print("FAILED", coid, o)
    else:
        results["option_closers"].append({"agent": agent_id, "symbol": sym, "side": "buy_to_close",
                                          "qty": 1, "limit": cap, "mark": mark,
                                          "client_order_id": coid, "order_id": o["id"],
                                          "status": o["status"], "tif": "gtc"})
        print(f"FILED {coid:38s} BTO {sym} cap {cap:.2f} (mark {mark}) -> {o['status']}")

# ---- 4. verification ----
time.sleep(3)
final_pos = req("/v2/positions")
final_open = req("/v2/orders?status=open&limit=100")
print("\nVERIFY — POSITIONS NOW:", len(final_pos))
for p in final_pos:
    print(f"  {p['symbol']} qty={p['qty']} mkt={p['market_value']}")
fired_syms = {"XLF260918P00055500", "XLF260918P00055000", "XLU260918P00041000", "BTCUSD", "ETHUSD"}
remaining = [p["symbol"] for p in final_pos if p["symbol"] in fired_syms]
print("FIRED-AGENT RESIDUAL:", remaining if remaining else "NONE — all gone or documented (option shorts carried by GTC closers)")
print("OPEN ORDERS NOW:", len(final_open))
for o in final_open:
    print(f"  {o['client_order_id'][:40]:40s} {o['side']:4s} {o['qty']} {o['symbol']} lmt={o.get('limit_price')} {o['time_in_force']}")

results["verify"] = {"positions_remaining": [p["symbol"] for p in final_pos],
                     "fired_residual": remaining,
                     "open_orders": [o["client_order_id"] for o in final_open],
                     "equity_after": req("/v2/account")["equity"]}

# ---- 5. log ----
log_path = f"{STATE}/orders_20260902.json"
log = json.load(open(log_path))
log.append({
    "firing_cleanup": True,
    "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
    "context": "D4 4:30 firing: 7 tryouts terminated (survivor law: Levene/Blues/Roma NEVER leave). "
               "Wolf fired #1 (+$9.37, only green book): 2 staged GTC buys canceled, crypto liquidated at market. "
               "5 fired short puts all OTM>$0.05 -> capped GTC BTO closers for Thu open. agent-24 Ray flat.",
    "orders": results,
    "residual_note": "6PM REALLOCATION OPERATOR: do NOT refile the 5 GTC ar-cleanup BTOs — they close at Thu open. "
                     "Fired-book residual at marks ≈ −$22. Survivor books (XLF 57P/56P, XLU 9/4 42P) carry untouched. "
                     "Wolf BTC exit proceeds return to cash pool tonight. Pool = equity − residual.",
})
tmp = log_path + ".tmp"
json.dump(log, open(tmp, "w"), indent=2)
os.replace(tmp, log_path)
print("\norders_20260902.json: cleanup block appended | equity after:", results["verify"]["equity_after"])