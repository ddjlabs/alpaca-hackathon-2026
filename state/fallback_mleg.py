#!/usr/bin/env python3
"""D2 deployment — mleg fallback: sequential single-leg execution for agents 03/06/09.
Then poll ALL open orders; pair/complete unpaired combo wings (risk-reducing only)."""
import os, json, time
import requests
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
BASE = 'https://paper-api.alpaca.markets'
STATE = '/mnt/agent_share/gordon/hackathon/state'
TODAY = '20260831'
LOGF = f'{STATE}/orders_{TODAY}.json'

def log_append(entry):
    try:
        log = json.load(open(LOGF))
    except Exception:
        log = []
    log.append(entry)
    tmp = LOGF + '.tmp'
    json.dump(log, open(tmp, 'w'), indent=2)
    os.replace(tmp, LOGF)

def post(body):
    r = requests.post(f'{BASE}/v2/orders', headers={**H, 'content-type': 'application/json'}, data=json.dumps(body), timeout=20)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {'raw': r.text[:200]}

# Combos to leg in: (agent, [(occ, side, limit)])  — credit leg(s) first
COMBOS = {
    'agent-03': [('XLF260904P00058000', 'sell_to_open', 0.33), ('XLF260904P00057000', 'buy_to_open', 0.07)],
    'agent-06': [('XLF260918C00059000', 'sell_to_open', 0.41), ('XLF260918C00060000', 'buy_to_open', 0.19)],
    'agent-09': [('QQQ260918P00678000', 'sell_to_open', 2.37), ('QQQ260918P00668000', 'buy_to_open', 1.67),
                 ('QQQ260918C00744000', 'sell_to_open', 2.02), ('QQQ260918C00754000', 'buy_to_open', 0.85)],
}
posted = {}  # (agent, occ) -> {coid, order_id}
seq = 0
for agent, legs in COMBOS.items():
    for i, (occ, side, lim) in enumerate(legs, 1):
        seq += 1
        o = f'{agent}-{TODAY}-opt-{i}'
        body = {'symbol': occ, 'qty': '1', 'side': 'sell' if side == 'sell_to_open' else 'buy',
                'type': 'limit', 'limit_price': lim, 'time_in_force': 'day',
                'position_intent': side, 'client_order_id': o}
        code, resp = post(body)
        print(f'[{agent}] LEG {occ} {side} @ {lim} -> {code} :: {json.dumps(resp)[:150]}')
        if code == 200:
            log_append({'agent_id': agent, 'plan_leg': 'combo-leg', 'symbol': occ, 'side': side,
                        'qty': 1, 'limit_price': lim, 'status': resp.get('status'),
                        'order_id': resp.get('id'), 'client_order_id': o,
                        'note': 'mleg unsupported on XLF/QQQ -> sequenced single-leg fallback',
                        'ts': time.strftime('%H:%M:%S')})
            posted[(agent, occ)] = {'coid': o, 'id': resp.get('id'), 'side': side, 'limit': lim}
        else:
            log_append({'agent_id': agent, 'plan_leg': 'combo-leg', 'symbol': occ, 'side': side,
                        'qty': 1, 'limit_price': lim, 'status': f'HTTP_{code}', 'error': resp,
                        'client_order_id': o, 'ts': time.strftime('%H:%M:%S')})
        time.sleep(0.5)

# ---------- poll all open orders from today ----------
def book_snapshot():
    orders = requests.get(f'{BASE}/v2/orders?status=all&after=2026-08-31T13:30:00Z&limit=100', headers=H, timeout=20).json()
    return {x['id']: x for x in orders}

deadline = time.time() + 90
while time.time() < deadline:
    book = book_snapshot()
    stats = {x['client_order_id']: (x['status'], x.get('filled_avg_price')) for x in book.values()}
    # unpaired wings: for each combo, if any credit leg filled and any leg unfilled
    need_reprice = []
    for (agent, occ), info in posted.items():
        st = stats.get(info['coid'], ('?', None))[0]
        if st in ('new', 'partially_filled', 'pending_new'):
            # is its combo missing at least one FILLED credit leg?
            combo_legs = [(a, o_) for (a, o_) in posted if a == agent]
            credit_filled = any(stats.get(posted[(a, o_)]['coid'], ('?',))[0] == 'filled'
                                for (a, o_) in combo_legs
                                if posted[(a, o_)]['side'] == 'sell_to_open')
            if credit_filled and info['side'] == 'buy_to_open':
                need_reprice.append((agent, occ, info))
    if pending_states := [s for s in stats.values() if s[0] in ('new', 'partially_filled', 'pending_new')]:
        time.sleep(8); continue
    break

# ---------- risk-reducing completion: re-price unpaired BUY legs to the ask ----------
book = book_snapshot()
stats = {x['id']: x for x in book.values()}
for (agent, occ, info) in need_reprice:
    st = stats.get(info['id'], {}).get('status')
    if st not in ('new', 'partially_filled', 'pending_new'):
        continue
    r = requests.get(f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={occ}', headers=H, timeout=20).json()
    lq = (r.get('snapshots') or {}).get(occ, {}).get('latestQuote') or {}
    ask = lq.get('ap')
    if not ask:
        print(f'[{agent}] {occ}: no ask available, leaving rest'); continue
    c = requests.delete(f"{BASE}/v2/orders/{info['id']}", headers=H, timeout=20)
    time.sleep(0.5)
    o2 = f"{agent}-{TODAY}-opt-reprice-1"
    body = {'symbol': occ, 'qty': '1', 'side': 'buy', 'type': 'limit', 'limit_price': ask,
            'time_in_force': 'day', 'position_intent': 'buy_to_open', 'client_order_id': o2}
    code, resp = post(body)
    print(f'[{agent}] REPRICE {occ} buy @ ask {ask} (was {info["limit"]}) -> {code} :: {json.dumps(resp)[:150]}')
    log_append({'agent_id': agent, 'plan_leg': 'combo-leg-reprice', 'symbol': occ, 'side': 'buy_to_open',
                'qty': 1, 'limit_price': ask, 'status': resp.get('status') if code == 200 else f'HTTP_{code}',
                'order_id': resp.get('id'), 'client_order_id': o2,
                'note': f'wing completion at ask after short leg filled; original limit {info["limit"]}',
                'ts': time.strftime('%H:%M:%S')})

# ---------- final snapshot ----------
time.sleep(15)
book = requests.get(f'{BASE}/v2/orders?status=all&after=2026-08-31T13:30:00Z&limit=100', headers=H, timeout=20).json()
print('\n===== ALL ORDERS TODAY =====')
for x in sorted(book, key=lambda z: z.get('created_at') or ''):
    print({'coid': x.get('client_order_id'), 'sym': x.get('symbol'), 'side': x.get('side'),
           'lim': x.get('limit_price'), 'status': x.get('status'), 'avg': x.get('filled_avg_price')})
json.dump([{k: x.get(k) for k in ('client_order_id', 'symbol', 'side', 'qty', 'limit_price', 'status', 'filled_avg_price', 'id')}
           for x in book], open(f'{STATE}/final_orders_{TODAY}.json', 'w'), indent=2)
ps = requests.get(f'{BASE}/v2/positions', headers=H, timeout=20).json()
print('\nPOSITIONS:')
for pp in ps:
    print({'sym': pp['symbol'], 'qty': pp['qty'], 'avg': pp['avg_entry_price']})
json.dump([{'symbol': pp['symbol'], 'qty': pp['qty'], 'avg': pp['avg_entry_price'], 'mkt': pp['current_price']} for pp in ps],
          open(f'{STATE}/positions_after_open_{TODAY}.json', 'w'), indent=2)
acct = requests.get(f'{BASE}/v2/account', headers=H, timeout=20).json()
print('\nACCOUNT: equity', acct['equity'], '| cash', acct['cash'], '| positions', len(ps))
print('FALLBACK DONE')