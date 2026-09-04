#!/usr/bin/env python3
"""D3 FIRING — REST pull: account, positions, fills, open orders. Never prints secrets."""
import json, os, sys, urllib.request
from datetime import datetime, timezone

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

def req(path, params=""):
    url = f"{BASE}{path}"
    if params:
        url += ("&" if "?" in url else "?") + params
    r = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())

out = {"pulled_at": datetime.now(timezone.utc).isoformat()}

acct = req("/v2/account")
keep_acct = {k: acct.get(k) for k in (
    "account_number","status","equity","last_equity","cash","portfolio_value",
    "buying_power","initial_margin","long_market_value","short_market_value",
    "trading_blocked","pattern_day_trader","daytrade_count","options_buying_power",
    "options_approved_level")}
out["account"] = keep_acct

positions = req("/v2/positions")
out["positions"] = positions

fills = req("/v2/account/activities", "activity_types=FILL&direction=desc&page_size=100")
out["fills"] = fills

orders = req("/v2/orders", "status=open&limit=100")
out["open_orders"] = orders

for name, data in (("acct", [out["account"]]), ("positions", positions),
                   ("fills", fills), ("open_orders", orders)):
    with open(f"{STATE}/firing_pull_{name}_20260901.json", "w") as f:
        json.dump(data, f, indent=2)

print("EQUITY:", out["account"]["equity"], "CASH:", out["account"]["cash"])
print("POSITIONS:", len(positions))
for p in positions:
    print(f"  {p['symbol']} qty={p['qty']} avg={p['avg_entry_price']} mkt={p['market_value']} upl={p['unrealized_pl']} coid={p.get('client_order_id','')}")
print("FILLS TODAY (desc):", len(fills))
for a in fills:
    px = a.get("price"); qty = a.get("qty"); sym = a.get("symbol")
    side = a.get("side"); ts = a.get("transaction_time", "")
    print(f"  {ts[11:16]}Z {a.get('client_order_id','')[:36]:36s} {side:4s} {qty:>4s} {sym[:26]:26s} @ {px}")
print("OPEN ORDERS:", len(orders))
for o in orders:
    print(f"  {o['client_order_id'][:40]:40s} {o['side']} {o['qty']} {o['symbol']} {o['type']} lmt={o.get('limit_price')} tif={o['time_in_force']}")