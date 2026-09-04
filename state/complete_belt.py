#!/usr/bin/env python3
"""Complete agent-03 spread: cancel resting 57P belt, refile at market ask +1 tick.
Then final full-book + fills sweep for the whole day."""
import os, json, time, requests
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
BASE = 'https://paper-api.alpaca.markets'
STATE = '/mnt/agent_share/gordon/hackathon/state'
TODAY = '20260831'
LOGF = f'{STATE}/orders_{TODAY}.json'

def log_append(entry):
    log = json.load(open(LOGF)) if os.path.exists(LOGF) else []
    log.append(entry)
    tmp = LOGF + '.tmp'
    json.dump(log, open(tmp, 'w'), indent=2)
    os.replace(tmp, LOGF)

# find live agent-03 belt order id
book = requests.get(f'{BASE}/v2/orders?status=all&after=2026-08-31T13:30:00Z&limit=100', headers=H, timeout=20).json()
belt = next((x for x in book if x['client_order_id'] == 'agent-03-20260831-opt-reprice-1' and x['status'] not in ('filled', 'canceled')), None)
if belt:
    d = requests.delete(f"{BASE}/v2/orders/{belt['id']}", headers=H, timeout=20)
    print('cancel old belt:', d.status_code)
    time.sleep(0.6)
    snap = requests.get(f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols=XLF260904P00057000', headers=H, timeout=20).json()
    lq = (snap.get('snapshots') or {}).get('XLF260904P00057000', {}).get('latestQuote') or {}
    ask = lq.get('ap') or 0.16
    lim = min(round((ask + 0.01) * 20) / 20, 0.17)
    o2 = 'agent-03-20260831-opt-reprice-2'
    body = {'symbol': 'XLF260904P00057000', 'qty': '1', 'side': 'buy', 'type': 'limit',
            'limit_price': lim, 'time_in_force': 'day', 'position_intent': 'buy_to_open',
            'client_order_id': o2}
    r = requests.post(f'{BASE}/v2/orders', headers={**H, 'content-type': 'application/json'}, data=json.dumps(body), timeout=20)
    resp = r.json()
    print(f'agent-03 BELT v3: buy 57P @ {lim} (ask {ask}) -> {r.status_code} :: {json.dumps(resp)[:160]}')
    log_append({'agent_id': 'agent-03', 'plan_leg': 'combo-leg-reprice', 'symbol': 'XLF260904P00057000',
                'side': 'buy_to_open', 'qty': 1, 'limit_price': lim,
                'status': resp.get('status') if r.status_code == 200 else f'HTTP_{r.status_code}',
                'order_id': resp.get('id'), 'client_order_id': o2,
                'note': 'seatbelt completion v2 — short 58P filled 0.43; defined-risk completion, capped 0.17',
                'ts': time.strftime('%H:%M:%S')})
else:
    print('agent-03 belt already filled or gone — no action')

time.sleep(25)  # let the tape work

# FINAL SWEEP
book = requests.get(f'{BASE}/v2/orders?status=all&after=2026-08-31T13:30:00Z&limit=100', headers=H, timeout=20).json()
print('\n== FINAL BOOK ==')
fills = []
for x in sorted(book, key=lambda z: z.get('created_at') or ''):
    st = x.get('status'); avg = x.get('filled_avg_price')
    print(f"{x.get('client_order_id'):38} {x.get('symbol'):24} {x.get('side'):5} lim={x.get('limit_price')} {st:9} avg={avg}")
    if st == 'filled' and avg:
        fills.append({'agent': (x.get('client_order_id') or '').split('-2026')[0], 'sym': x.get('symbol'),
                      'side': x.get('side'), 'lim': x.get('limit_price'), 'avg': float(avg)})
json.dump([{k: x.get(k) for k in ('client_order_id', 'symbol', 'side', 'qty', 'limit_price', 'status', 'filled_avg_price', 'id', 'position_intent')}
           for x in book], open(f'{STATE}/final_orders_{TODAY}.json', 'w'), indent=2)
json.dump(fills, open(f'{STATE}/fills_{TODAY}.json', 'w'), indent=2)
print('\nFILLS:', json.dumps(fills))
ps = requests.get(f'{BASE}/v2/positions', headers=H, timeout=20).json()
print('\n== POSITIONS ==')
for pp in sorted(ps, key=lambda z: z['symbol']):
    print(f"{pp['symbol']:24} qty={pp['qty']:>4} avg={pp['avg_entry_price']:>10} mkt={pp['current_price']}")
acct = requests.get(f'{BASE}/v2/account', headers=H, timeout=20).json()
print(f"\n== ACCOUNT == equity={acct.get('equity')} cash={acct.get('cash')}")
print('SWEEP DONE')