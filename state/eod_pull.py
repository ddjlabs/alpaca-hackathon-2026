#!/usr/bin/env python3
"""EOD 5PM pull: account, positions, orders, activities from hackathon paper acct."""
import json, os, requests
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
key = os.environ['HACKATHON_ALPACA_KEY']
sec = os.environ['HACKATHON_ALPACA_SECRET']
H = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': sec}
base = 'https://paper-api.alpaca.markets'
OUT = '/mnt/agent_share/gordon/hackathon/state/eod_pull'

os.makedirs(OUT, exist_ok=True)

acct = requests.get(f'{base}/v2/account', headers=H, timeout=30).json()
positions = requests.get(f'{base}/v2/positions', headers=H, timeout=30).json()
orders = requests.get(f'{base}/v2/orders?status=filled&limit=100', headers=H, timeout=30).json()
openords = requests.get(f'{base}/v2/orders?status=open&limit=100', headers=H, timeout=30).json()
acts = requests.get(f'{base}/v2/account/activities/FILL?pageSize=100', headers=H, timeout=30).json()

for name, data in [('account', acct), ('positions', positions), ('orders_filled', orders),
                   ('orders_open', openords), ('activities', acts)]:
    with open(f'{OUT}/{name}.json', 'w') as f:
        json.dump(data, f, indent=1, default=str)

print("ACCOUNT:")
print("  equity:", acct.get('equity'), "| last_equity:", acct.get('last_equity'), "| cash:", acct.get('cash'))
try:
    print("  day_pnl:", float(acct['equity']) - float(acct['last_equity']))
except Exception as e:
    print("  day_pnl err:", e)

print("\nPOSITIONS:", len(positions))
for p in positions:
    print(f"  {p['symbol']:>8} qty={p.get('qty'):>10} entry={p.get('avg_entry_price'):>10} px={p.get('current_price'):>10} pnl={p.get('unrealized_pl'):>10} plpc={p.get('unrealized_plpc')}")

print("\nFILLED ORDERS:", len(orders))
print("OPEN ORDERS:", len(openords))
print("FILL ACTIVITIES:", len(acts) if isinstance(acts, list) else acts)