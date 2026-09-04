#!/usr/bin/env python3
"""D2 OPENING DEPLOYMENT executor — Aug 31, 2026.
Executes trade_plans_D2.json opening positions on Alpaca paper PA3GWO1FKED0.
Logs every order to orders_20260831.json. Prints full audit trail."""
import os, sys, json, time
import requests
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
BASE = 'https://paper-api.alpaca.markets'
STATE = '/mnt/agent_share/gordon/hackathon/state'
TODAY = '20260831'
LOGF = f'{STATE}/orders_{TODAY}.json'

def log_order(entry):
    try:
        log = json.load(open(LOGF))
    except Exception:
        log = []
    log.append(entry)
    tmp = LOGF + '.tmp'
    json.dump(log, open(tmp, 'w'), indent=2)
    os.replace(tmp, LOGF)

def log_entry(agent, leg, symbol, side, qty, limit, resp_body, status):
    e = {'agent_id': agent, 'plan_leg': leg, 'symbol': symbol, 'side': side,
         'qty': qty, 'limit_price': limit, 'status': status, 'ts': time.strftime('%H:%M:%S')}
    if isinstance(resp_body, dict):
        e['order_id'] = resp_body.get('id')
        e['client_order_id'] = resp_body.get('client_order_id')
        e['alpaca_status'] = resp_body.get('status')
        if resp_body.get('code') or resp_body.get('message'):
            e['error'] = {'code': resp_body.get('code'), 'message': resp_body.get('message')}
    else:
        e['raw'] = str(resp_body)[:300]
    log_order(e)
    return e

# client_order_id per plan template: <agent_id>-<yyyymmdd>-<leg>-<seq>
def coid(agent, legtype, seq=1):
    return f'{agent}-{TODAY}-{legtype}-{seq}'

plans = json.load(open(f'{STATE}/trade_plans_D2.json'))['plans']
results = {}   # agent_id -> list of order outcomes
pending_stock = {}  # agent -> (coid, plan)

# ---------- PHASE 1: stock legs (covered_call plans) ----------
for p in plans:
    if p['strategy'] != 'covered_call':
        continue
    stock_leg = next(l for l in p['legs'] if l['side'] == 'buy')
    sym = stock_leg['symbol_or_contract']
    qty = str(stock_leg['qty']); lim = stock_leg['limit_price']
    o = f'{p["agent_id"]}-{TODAY}-stock-1'
    body = {'symbol': sym, 'qty': qty, 'side': 'buy', 'type': 'limit',
            'limit_price': lim, 'time_in_force': 'day', 'client_order_id': o}
    r = requests.post(f'{BASE}/v2/orders', headers={**H, 'content-type': 'application/json'}, data=json.dumps(body), timeout=20)
    try:
        resp = r.json()
    except Exception:
        resp = {'raw': r.text[:300]}
    print(f"[{p['agent_id']}] STOCK {sym} buy {qty} @ {lim} -> {r.status_code} :: {json.dumps(resp)[:220]}")
    if r.status_code == 200:
        e = log_order({'agent_id': p['agent_id'], 'plan_leg': 'stock', 'symbol': sym, 'side': 'buy',
                       'qty': qty, 'limit_price': lim, 'status': resp.get('status'),
                       'order_id': resp.get('id'), 'client_order_id': o, 'ts': time.strftime('%H:%M:%S')})
        pending_stock[p['agent_id']] = resp
        results.setdefault(p['agent_id'], []).append({'leg': 'stock', 'symbol': sym, 'side': 'buy',
            'qty': qty, 'limit': lim, 'order_id': resp.get('id'), 'status': resp.get('status')})
    else:
        log_order({'agent_id': p['agent_id'], 'plan_leg': 'stock', 'symbol': sym, 'side': 'buy',
                   'qty': qty, 'limit_price': lim, 'status': f'HTTP_{r.status_code}',
                   'error': resp, 'ts': time.strftime('%H:%M:%S')})
        results.setdefault(p['agent_id'], []).append({'leg': 'stock', 'symbol': sym, 'side': 'buy',
            'qty': qty, 'limit': lim, 'status': 'REJECTED', 'error': resp})
    time.sleep(0.4)

# ---------- PHASE 2: wait for stock fills (max 75s) ----------
filled_stock = {}
deadline = time.time() + 75
while time.time() < deadline and pending_stock:
    time.sleep(6)
    opened = requests.get(f'{BASE}/v2/orders?status=all&after=2026-08-31T13:30:00Z', headers=H, timeout=20).json()
    for a_id, o in list(pending_stock.items()):
        match = next((x for x in opened if x.get('id') == o['id']), None)
        st = match.get('status') if match else '?'
        fp = (match or {}).get('filled_avg_price')
        print(f"  fill-poll {a_id} stock: {st} avg={fp}")
        if st in ('filled', 'canceled', 'rejected', 'expired'):
            filled_stock[a_id] = {'status': st, 'avg': fp}
            del pending_stock[a_id]

# place filled-stock CC STOs
for p in plans:
    if p['strategy'] != 'covered_call':
        continue
    a_id = p['agent_id']
    if a_id not in filled_stock or filled_stock[a_id]['status'] != 'filled':
        print(f"[{a_id}] stock not filled -> SKIPPING naked call STO (compliance: shares first)")
        results.setdefault(a_id, []).append({'leg': 'opt-SKIPPED(shares not confirmed)', 'symbol': '', 'status': 'DEFERRED'})
        continue
    call_leg = next(l for l in p['legs'] if l['side'] == 'sell_to_open')
    occ = call_leg['symbol_or_contract']; lim = call_leg['limit_price']
    o = coid(a_id, 'opt', 1)
    body = {'symbol': occ, 'qty': '1', 'side': 'sell', 'type': 'limit', 'limit_price': lim,
            'time_in_force': 'day', 'position_intent': 'sell_to_open', 'client_order_id': o}
    r = requests.post(f'{BASE}/v2/orders', headers={**H, 'content-type': 'application/json'}, data=json.dumps(body), timeout=20)
    try:
        resp = r.json()
    except Exception:
        resp = {'raw': r.text[:300]}
    print(f"[{a_id}] CC STO {occ} sell 1 @ {lim} -> {r.status_code} :: {json.dumps(resp)[:220]}")
    if r.status_code == 200:
        log_order({'agent_id': a_id, 'plan_leg': 'call', 'symbol': occ, 'side': 'sell_to_open',
                   'qty': 1, 'limit_price': lim, 'status': resp.get('status'), 'order_id': resp.get('id'),
                   'client_order_id': o, 'ts': time.strftime('%H:%M:%S')})
        results.setdefault(a_id, []).append({'leg': 'call', 'symbol': occ, 'side': 'STO',
            'qty': 1, 'limit': lim, 'order_id': resp.get('id'), 'status': resp.get('status')})
    else:
        log_order({'agent_id': a_id, 'plan_leg': 'call', 'symbol': occ, 'side': 'sell_to_open',
                   'qty': 1, 'limit_price': lim, 'status': f'HTTP_{r.status_code}', 'error': resp,
                   'ts': time.strftime('%H:%M:%S')})
        results.setdefault(a_id, []).append({'leg': 'call', 'symbol': occ, 'side': 'STO',
            'qty': 1, 'limit': lim, 'status': 'REJECTED', 'error': resp})
    time.sleep(0.4)

# ---------- PHASE 3: single-leg options (CSPs) + multilegs (spreads, condor) ----------
NET_LIMITS = {  # combo net-credit limits (from plans)
    'agent-03': 0.25,   # Donnie 58/57P 9/4  ("0.25 combo limit")
    'agent-06': 0.22,   # Blaze 59/60C 9/18  ("0.22 combo limit")
    'agent-09': 1.87,   # Voss QQQ condor    (net credit 1.87)
}
for p in plans:
    a_id = p['agent_id']; strat = p['strategy']
    if strat == 'cash_secured_put':
        leg = p['legs'][0]; occ = leg['symbol_or_contract']; lim = leg['limit_price']
        o = coid(a_id, 'opt', 1)
        body = {'symbol': occ, 'qty': '1', 'side': 'sell', 'type': 'limit', 'limit_price': lim,
                'time_in_force': 'day', 'position_intent': 'sell_to_open', 'client_order_id': o}
        r = requests.post(f'{BASE}/v2/orders', headers={**H, 'content-type': 'application/json'}, data=json.dumps(body), timeout=20)
        try:
            resp = r.json()
        except Exception:
            resp = {'raw': r.text[:300]}
        print(f"[{a_id}] CSP STO {occ} sell 1 @ {lim} -> {r.status_code} :: {json.dumps(resp)[:220]}")
        if r.status_code == 200:
            log_order({'agent_id': a_id, 'plan_leg': 'put', 'symbol': occ, 'side': 'sell_to_open',
                       'qty': 1, 'limit_price': lim, 'status': resp.get('status'), 'order_id': resp.get('id'),
                       'client_order_id': o, 'ts': time.strftime('%H:%M:%S')})
            results.setdefault(a_id, []).append({'leg': 'put', 'symbol': occ, 'side': 'STO', 'qty': 1,
                'limit': lim, 'order_id': resp.get('id'), 'status': resp.get('status')})
        else:
            log_order({'agent_id': a_id, 'plan_leg': 'put', 'symbol': occ, 'side': 'sell_to_open',
                       'qty': 1, 'limit_price': lim, 'status': f'HTTP_{r.status_code}', 'error': resp,
                       'ts': time.strftime('%H:%M:%S')})
            results.setdefault(a_id, []).append({'leg': 'put', 'symbol': occ, 'side': 'STO', 'qty': 1,
                'limit': lim, 'status': 'REJECTED', 'error': resp})
        time.sleep(0.4)
    elif strat == 'credit_spread':
        legs = []
        for l in p['legs']:
            legs.append({'symbol': l['symbol_or_contract'],
                         'ratio_qty': 1,
                         'side': 'sell' if l['side'] == 'sell_to_open' else 'buy',
                         'position_intent': l['side']})
        o = coid(a_id, 'opt', 1)
        body = {'symbol': p['symbol'], 'qty': '1', 'side': 'sell', 'type': 'limit',
                'limit_price': NET_LIMITS[a_id], 'time_in_force': 'day',
                'order_class': 'mleg', 'client_order_id': o, 'legs': legs}
        r = requests.post(f'{BASE}/v2/orders', headers={**H, 'content-type': 'application/json'}, data=json.dumps(body), timeout=20)
        try:
            resp = r.json()
        except Exception:
            resp = {'raw': r.text[:300]}
        combo = '+'.join(l['symbol'] for l in legs)
        print(f"[{a_id}] MLEG {combo} net credit {NET_LIMITS[a_id]} -> {r.status_code} :: {json.dumps(resp)[:260]}")
        if r.status_code == 200:
            log_order({'agent_id': a_id, 'plan_leg': 'mleg', 'symbol': combo, 'side': 'credit_combo',
                       'qty': 1, 'limit_price': NET_LIMITS[a_id], 'status': resp.get('status'),
                       'order_id': resp.get('id'), 'client_order_id': o, 'ts': time.strftime('%H:%M:%S')})
            results.setdefault(a_id, []).append({'leg': 'mleg', 'symbol': combo, 'side': 'STO combo',
                'qty': 1, 'limit': NET_LIMITS[a_id], 'order_id': resp.get('id'), 'status': resp.get('status')})
        else:
            log_order({'agent_id': a_id, 'plan_leg': 'mleg', 'symbol': combo, 'side': 'credit_combo',
                       'qty': 1, 'limit_price': NET_LIMITS[a_id], 'status': f'HTTP_{r.status_code}',
                       'error': resp, 'ts': time.strftime('%H:%M:%S')})
            results.setdefault(a_id, []).append({'leg': 'mleg', 'symbol': combo, 'side': 'combo',
                'qty': 1, 'limit': NET_LIMITS[a_id], 'status': 'REJECTED', 'error': resp})
        time.sleep(0.4)

# ---------- PHASE 4: final book state ----------
time.sleep(20)
orders_now = requests.get(f'{BASE}/v2/orders?status=all&after=2026-08-31T13:30:00Z&limit=100', headers=H, timeout=20).json()
print('\n===== FINAL ORDER BOARD =====')
final = []
for x in orders_now:
    if x.get('asset_class') == 'us_equity' and x.get('symbol') not in ('XLF', 'XLP', 'QQQ'):
        continue
    row = {'agent_coid': x.get('client_order_id'), 'symbol': x.get('symbol'), 'side': x.get('side'),
           'qty': x.get('qty'), 'type': x.get('type'), 'limit': x.get('limit_price'),
           'status': x.get('status'), 'filled_avg': x.get('filled_avg_price'),
           'order_id': x.get('id')}
    final.append(row)
    print(row)
json.dump(final, open(f'{STATE}/final_orders_{TODAY}.json', 'w'), indent=2)

ps = requests.get(f'{BASE}/v2/positions', headers=H, timeout=20).json()
print('\nPOSITIONS:')
tp = []
for pp in ps:
    row = {'symbol': pp['symbol'], 'qty': pp['qty'], 'avg': pp['avg_entry_price'], 'mkt': pp['current_price']}
    tp.append(row); print(row)
json.dump(tp, open(f'{STATE}/positions_after_open_{TODAY}.json', 'w'), indent=2)
acct = requests.get(f'{BASE}/v2/account', headers=H, timeout=20).json()
print('\nACCOUNT: equity', acct['equity'], '| cash', acct['cash'], '| positions', len(ps))
print('DEPLOY DONE')