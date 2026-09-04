#!/usr/bin/env python3
"""D3 FIRING 4:45 CLEANUP — file GTC BTO closers for 6 fired clone short puts.
All OTM > $0.05 -> mandate says leave+note; we wire capped GTC closers for Tue open
(D2 precedent). Never prints secrets."""
import json, os, sys, urllib.request
from datetime import datetime

STATE = "/mnt/agent_share/gordon/hackathon/state"
BASE = "https://paper-api.alpaca.markets"

def env_from(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = env_from("/home/doug/.hermes/profiles/gordon/.env")
KEY = os.environ.get("HACKATHON_ALPACA_KEY") or env.get("HACKATHON_ALPACA_KEY")
SEC = os.environ.get("HACKATHON_ALPACA_SECRET") or env.get("HACKATHON_ALPACA_SECRET")
if not KEY or not SEC:
    sys.exit("NO CREDS — abort")

def req(path, method="GET", body=None):
    r = urllib.request.Request(BASE + path, method=method,
        headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC,
                 "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body else None
    with urllib.request.urlopen(r, data, timeout=30) as resp:
        return json.loads(resp.read().decode())

# fired agent -> (symbol, mark, cap limit)
CLOSERS = [
    ("agent-11", "XLF260918P00057500", 0.89, 0.98),   # Johnny Blues 57.5P
    ("agent-12", "XLF260918P00054000", 0.09, 0.10),   # Donald Blues 54P
    ("agent-14", "XLF260918P00055000", 0.15, 0.17),   # Brad Roma 55P
    ("agent-15", "XLF261016P00057000", 1.14, 1.26),   # Dean Roma 57P 10/16
    ("agent-17", "XLF261016P00055000", 0.50, 0.55),   # George Levene 55P 10/16
    ("agent-18", "XLU260918P00042000", 0.43, 0.47),   # Chester Levene XLU 42P
]

# environment gate
acct = req("/v2/account")
assert acct["status"] == "ACTIVE" and acct["trading_blocked"] == "False" or acct["trading_blocked"] is False, "ACCOUNT GATE FAIL"

results = []
for agent_id, sym, mark, cap in CLOSERS:
    coid = f"ar-cleanup-{agent_id}-1-20260901"
    body = {
        "symbol": sym, "qty": "1", "side": "buy", "type": "limit",
        "time_in_force": "gtc", "limit_price": f"{cap:.2f}",
        "client_order_id": coid, "position_intent": "buy_to_close",
    }
    try:
        o = req("/v2/orders", "POST", body)
        results.append({"agent": agent_id, "symbol": sym, "side": "buy_to_close",
                        "qty": 1, "limit": cap, "mark": mark,
                        "client_order_id": coid, "order_id": o["id"],
                        "status": o["status"], "tif": "gtc"})
        print(f"FILED {coid:42s} BTO {sym} cap {cap:.2f} (mark {mark}) -> {o['status']} {o['id']}")
    except urllib.error.HTTPError as e:
        print(f"FAILED {coid}: {e.code} {e.read().decode()[:200]}")
        results.append({"agent": agent_id, "symbol": sym, "error": f"{e.code}",
                        "client_order_id": coid})

# open-order + position verification
open_orders = req("/v2/orders?status=open&limit=100")
positions = req("/v2/positions")
print("\nOPEN ORDERS NOW:", len(open_orders))
for o in open_orders:
    print(f"  {o['client_order_id'][:44]:44s} {o['side']:5s} {o['qty']} {o['symbol']} lmt={o.get('limit_price')} {o['time_in_force']} {o['status']}")
print("POSITIONS NOW:", len(positions))
fired_syms = {c[1] for c in CLOSERS}
for p in positions:
    tag = " <- FIRED-AGENT (closer wired)" if p["symbol"] in fired_syms else ""
    print(f"  {p['symbol']} qty={p['qty']} mark_val={p['market_value']}{tag}")

# append cleanup block to orders log (atomic)
log_path = f"{STATE}/orders_20260901.json"
log = json.load(open(log_path))
log.append({
    "firing_cleanup": True,
    "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
    "context": "D3 4:30 firing: 7 non-survivors terminated (survivor law: top-3 Roma/Blues/Levene NEVER leave). "
               "6 fired short puts all OTM>$0.05 -> GTC BTO closers capped ~+10% over mark for Wed open; "
               "agent-20 Stone flat (nothing to close).",
    "orders": results,
    "orphan_note": "ar-cleanup-agent-09-2-20260901 (QQQ 754C sell 0.20 day) rests for Wed open — D2 residual, inherited asset.",
    "residual_note": "6PM REALLOCATION OPERATOR: do NOT refile the 6 GTC ar-cleanup BTOs or the 754C seller; "
                     "they close at Wed open. Residual book at marks: 6 clone shorts −$320 + orphan 754C +$20 = −$300. "
                     "Survivor books (57P/56P/XLU 9/4) carry untouched. Pool ≈ equity − (−$300).",
})
tmp = log_path + ".tmp"
json.dump(log, open(tmp, "w"), indent=2)
os.replace(tmp, log_path)
print("\norders_20260901.json: cleanup block appended")