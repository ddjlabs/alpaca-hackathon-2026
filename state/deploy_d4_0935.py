"""D4 9:35 OPEN DEPLOYMENT — gap gate PASSED (repriced band on XLU only).
FILES: 4 option legs at LIVE mids (re-anchored per 0.5-1.5% regime) + Wolf crypto (market + 2 staged GTC).
HOLDS: agent-25/26 XLU 41P — live delta -0.212 > 0.20 desk law after XLU -0.85% gap; no legal strike exists.
Logs to orders_20260902.json. Idempotent client_order_ids. Never prints credentials."""
import os, json, time
import requests
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
BASE = 'https://paper-api.alpaca.markets'
STATE = '/mnt/agent_share/gordon/hackathon/state'
LOGF = f'{STATE}/orders_20260902.json'
TODAY = '20260902'

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
    r = requests.post(f'{BASE}/v2/orders', headers={**H, 'content-type': 'application/json'},
                      data=json.dumps(body), timeout=20)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {'raw': r.text[:300]}

results = []

# ---------- GAP-GATE REPRICED OPTION LEGS (live mids 09:38 ET, iex) ----------
# (agent, OCC, side, limit, plan_limit, live_quote, live_delta, note)
OPT_LEGS = [
    ('agent-21', 'XLF260918P00055500', 'sell', 0.16, 0.19, '0.11x0.21', -0.148,
     'Dave Roma XLF 55.5P — repriced to live mid 0.16 (plan 0.19 was 19:05 mid); delta improved -0.174 -> -0.148'),
    ('agent-22', 'XLF260918P00055000', 'sell', 0.14, 0.16, '0.12x0.16', -0.121,
     'Lou Roma XLF 55P — repriced to live mid 0.14 (plan 0.16 was 19:05 mid); delta -0.137 -> -0.121'),
    ('agent-23', 'XLF260918P00055500', 'sell', 0.16, 0.19, '0.11x0.21', -0.148,
     'Jake Blues XLF 55.5P — repriced to live mid 0.16; delta -0.174 -> -0.148'),
    ('agent-24', 'XLP260918P00083000', 'sell', 0.28, 0.30, '0.23x0.33', -0.183,
     'Ray Blues XLP 83P — repriced to live mid 0.28 (plan 0.30); delta -0.189 -> -0.183'),
]
for agent, occ, side, lim, plan_lim, quote, delta, note in OPT_LEGS:
    coid = f'{agent}-{TODAY}-opt-1'
    body = {'symbol': occ, 'qty': '1', 'side': side, 'type': 'limit',
            'limit_price': lim, 'time_in_force': 'day',
            'position_intent': 'sell_to_open', 'client_order_id': coid}
    code, resp = post(body)
    out = {'deploy': 'd4_open', 'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'agent_id': agent, 'symbol': occ, 'side': 'sell_to_open', 'qty': 1,
           'limit_price': lim, 'plan_limit_1905': plan_lim, 'live_quote': quote,
           'live_delta': delta, 'client_order_id': coid, 'http': code,
           'status': resp.get('status') if isinstance(resp, dict) else None,
           'order_id': resp.get('id') if isinstance(resp, dict) else None,
           'note': note}
    if code != 200:
        out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
    results.append(out)
    log_append(out)
    print(f"[{agent}] STO {occ} @ {lim} (plan {plan_lim}) -> {code} :: {json.dumps(resp)[:180]}")

# ---------- WOLF CRYPTO (agent-27) — engagement floor via market tranche ----------
# Alpaca crypto: TIF must be gtc (day is invalid for crypto).
c1 = f'agent-27-{TODAY}-mkt-1'
body = {'symbol': 'BTC/USD', 'qty': '0.0325', 'side': 'buy', 'type': 'market',
        'time_in_force': 'gtc', 'client_order_id': c1}
code, resp = post(body)
out = {'deploy': 'd4_open', 'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
       'agent_id': 'agent-27', 'symbol': 'BTC/USD', 'side': 'buy', 'qty': 0.0325,
       'type': 'market', 'client_order_id': c1, 'http': code,
       'status': resp.get('status') if isinstance(resp, dict) else None,
       'order_id': resp.get('id') if isinstance(resp, dict) else None,
       'note': 'Wolf tranche 1 MARKET at open — Rule 8 engagement by execution (crypto TIF=gtc per Alpaca)'}
if code != 200:
    out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
results.append(out); log_append(out)
print(f"[agent-27] BTC MARKET 0.0325 -> {code} :: {json.dumps(resp)[:180]}")

time.sleep(2)
c2 = f'agent-27-{TODAY}-lim-1'
body = {'symbol': 'BTC/USD', 'qty': '0.0325', 'side': 'buy', 'type': 'limit',
        'limit_price': '75800', 'time_in_force': 'gtc', 'client_order_id': c2}
code, resp = post(body)
out = {'deploy': 'd4_open', 'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
       'agent_id': 'agent-27', 'symbol': 'BTC/USD', 'side': 'buy', 'qty': 0.0325,
       'type': 'limit', 'limit_price': 75800, 'client_order_id': c2, 'http': code,
       'status': resp.get('status') if isinstance(resp, dict) else None,
       'order_id': resp.get('id') if isinstance(resp, dict) else None,
       'note': 'Wolf staged BTC limit (GTC, desk cancels Thu 15:45 if unfilled — powder restore)'}
if code != 200:
    out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
results.append(out); log_append(out)
print(f"[agent-27] BTC LIMIT 0.0325 @ 75800 -> {code} :: {json.dumps(resp)[:180]}")

time.sleep(2)
c3 = f'agent-27-{TODAY}-lim-2'
body = {'symbol': 'ETH/USD', 'qty': '0.6', 'side': 'buy', 'type': 'limit',
        'limit_price': '2365', 'time_in_force': 'gtc', 'client_order_id': c3}
code, resp = post(body)
out = {'deploy': 'd4_open', 'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
       'agent_id': 'agent-27', 'symbol': 'ETH/USD', 'side': 'buy', 'qty': 0.6,
       'type': 'limit', 'limit_price': 2365, 'client_order_id': c3, 'http': code,
       'status': resp.get('status') if isinstance(resp, dict) else None,
       'order_id': resp.get('id') if isinstance(resp, dict) else None,
       'note': 'Wolf staged ETH limit (GTC, same powder rule)'}
if code != 200:
    out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
results.append(out); log_append(out)
print(f"[agent-27] ETH LIMIT 0.6 @ 2365 -> {code} :: {json.dumps(resp)[:180]}")

# ---------- 45s fill poll (market tranche should fill immediately) ----------
print('--- fill poll 45s ---')
time.sleep(45)
oids = [r.get('order_id') for r in results if r.get('order_id')]
all_orders = requests.get(f'{BASE}/v2/orders?status=all&limit=50', headers=H, timeout=20).json()
for r in results:
    oid = r.get('order_id')
    if not oid:
        continue
    o = next((x for x in all_orders if x.get('id') == oid), None)
    if o:
        r['poll_status'] = o.get('status')
        r['filled_avg_price'] = o.get('filled_avg_price')
        r['filled_qty'] = o.get('filled_qty')
        print(f"  {r['agent_id']} {r['symbol']}: {o.get('status')} avg={o.get('filled_avg_price')} qty={o.get('filled_qty')}")
log_append({'deploy': 'd4_open', 'poll_45s': True,
            'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'summary': [{'a': r['agent_id'], 's': r['symbol'], 'st': r.get('poll_status'),
                         'avg': r.get('filled_avg_price')} for r in results]})

pos = requests.get(f'{BASE}/v2/positions', headers=H, timeout=20).json()
print('--- positions now ---')
for p in pos:
    print('  ', p['symbol'], p['qty'], '@', p['current_price'])
print('DEPLOY COMPLETE:', json.dumps([{k: r.get(k) for k in ('agent_id','symbol','http','status','poll_status','filled_avg_price')} for r in results], indent=1))