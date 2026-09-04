#!/usr/bin/env python3
"""Fresh book poll + triggers.json update + verify orders log."""
import os, json, time, requests
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
BASE = 'https://paper-api.alpaca.markets'
STATE = '/mnt/agent_share/gordon/hackathon/state'
TODAY = '20260831'

book = requests.get(f'{BASE}/v2/orders?status=all&after=2026-08-31T13:30:00Z&limit=100', headers=H, timeout=20).json()
print('== LIVE BOOK (latest poll) ==')
for x in sorted(book, key=lambda z: z.get('created_at') or ''):
    print(f"{x.get('client_order_id'):38} {x.get('symbol'):24} {x.get('side'):5} lim={x.get('limit_price')} status={x.get('status'):12} avg={x.get('filled_avg_price')}")

ps = requests.get(f'{BASE}/v2/positions', headers=H, timeout=20).json()
acct = requests.get(f'{BASE}/v2/account', headers=H, timeout=20).json()
print('\n== POSITIONS ==')
for pp in sorted(ps, key=lambda z: z['symbol']):
    print(f"{pp['symbol']:24} qty={pp['qty']:>4} avg={pp['avg_entry_price']:>10} mkt={pp['current_price']:>10} mktval={pp['market_value']:>12}")
print(f"\n== ACCOUNT == equity={acct.get('equity')} cash={acct.get('cash')} last_mkt_val={acct.get('last_equity')}")

json.dump([{k: x.get(k) for k in ('client_order_id', 'symbol', 'side', 'qty', 'limit_price', 'status', 'filled_avg_price', 'id', 'position_intent')}
           for x in book], open(f'{STATE}/final_orders_{TODAY}.json', 'w'), indent=2)
json.dump([{'symbol': pp['symbol'], 'qty': pp['qty'], 'avg': pp['avg_entry_price'], 'mkt': pp['current_price']} for pp in ps],
          open(f'{STATE}/positions_after_open_{TODAY}.json', 'w'), indent=2)
json.dump({'equity': acct['equity'], 'cash': acct['cash'], 'positions_count': len(ps), 'ts': time.strftime('%H:%M:%S')},
          open(f'{STATE}/account_snapshot_{TODAY}.json', 'w'), indent=2)

# -------- triggers.json update: stop levels from D2 plan stop_loss fields --------
trig = json.load(open(f'{STATE}/triggers.json'))
trig['price_triggers']['XLF'] = {
    'stop_loss': 56.00,           # lowest protective intraday stop across XLF books (Roma 57P)
    'profit_target': 61.00,       # highest assignment strike in the book (Bud 61C)
    'alert_above': 59.50,         # first CC buy-back trigger zone (Bud/Seth)
    'alert_below': 57.25,         # Donnie's spread stop — first tripwire under spot
    'per_agent_stops': {
        'agent-01': 'BTC 61C @ 0.24 OR XLF>59.50',
        'agent-02': 'BTC 57P @ 1.02 OR XLF<=56.00',
        'agent-03': 'close SPREAD @ 0.75 d OR XLF<=57.25',
        'agent-04': 'BTC 56P @ 0.54 OR XLF<=55.25',
        'agent-05': 'BTC 59C @ 0.36 OR XLF>59.50',
        'agent-06': 'close 60C position per plan OR XLF>=58.75 (combo died)',
        'agent-07': 'BTC 54.5P @ 0.30 OR XLF<=53.50',
        'agent-10': 'BTC 60.5C @ 0.42 OR XLF>=59.75',
    },
    'source': 'trade_plans_D2.json stop_loss fields, deployed 2026-08-31 09:45 ET',
}
trig['price_triggers']['XLP'] = {
    'stop_loss': 83.00,
    'profit_target': 90.00,
    'alert_above': 87.50,         # agent-08 BTC trigger
    'per_agent_stops': {'agent-08': 'BTC 90C @ 0.33 OR XLP>=87.50'},
    'source': 'trade_plans_D2.json, deployed 2026-08-31 09:45 ET',
}
trig['price_triggers']['QQQ'] = {
    'stop_loss': 672.0,           # Voss condor lower breach — condor died; residual long wings use range as watch level
    'profit_target': 754.0,
    'alert_above': 744.0,         # short call wing strike (leg rejected) — monitor
    'per_agent_stops': {'agent-09': 'condor NOT established (Alpaca 403 x2); residual long 754C + 668P pending; watch 672-754 range; AVGO Wed 9/2 exposure'},
    'source': 'trade_plans_D2.json, deployed 2026-08-31 09:45 ET',
}
tmp = f'{STATE}/triggers.json.tmp'
json.dump(trig, open(tmp, 'w'), indent=2)
import os; os.replace(tmp, f'{STATE}/triggers.json')
print('\ntriggers.json updated: XLF/XLP/QQQ stop levels + per-agent stop table')

# verify orders log integrity
log = json.load(open(f'{STATE}/orders_{TODAY}.json'))
print(f'\norders_{TODAY}.json entries: {len(log)}')
for e in log:
    print(f"  {e.get('ts')} {e.get('agent_id')} {e.get('plan_leg'):18} {e.get('symbol'):24} {e.get('side'):12} lim={e.get('limit_price')} status={e.get('status')}")