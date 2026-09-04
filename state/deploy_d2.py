#!/usr/bin/env python3
"""D2 opening deployment — preflight quotes + order execution."""
import os, sys, json, time, requests
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
if not K or not S:
    print('FATAL: no creds'); sys.exit(1)
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
BASE = 'https://paper-api.alpaca.markets'
STATE = '/mnt/agent_share/gordon/hackathon/state'

def get(path, **kw):
    return requests.get(f'{BASE}{path}', headers=H, timeout=20, **kw)

a = get('/v2/account').json()
print('acct:', a['account_number'], '| status:', a['status'], '| blocked:', a['trading_blocked'])
print('options_approvals:', {k: v for k, v in a.items() if 'option' in k.lower()})
print('equity:', a['equity'], '| cash:', a['cash'])
pos = get('/v2/positions').json()
print('positions:', len(pos))
oo = get('/v2/orders?status=open').json()
print('open orders:', len(oo), [o.get('client_order_id') for o in oo])

# --- stock quotes ---
syms = 'XLF,XLP,QQQ'
r = requests.get(f'https://data.alpaca.markets/v2/stocks/snapshots?symbols={syms}&feed=iex', headers=H, timeout=20)
print('stock snapshots status:', r.status_code)
stocks = {}
for s, snap in (r.json() if r.ok else {}).items():
    lt = snap.get('latestTrade') or {}; lq = snap.get('latestQuote') or {}
    stocks[s] = {'trade': lt.get('p'), 'bid': lq.get('bp'), 'ask': lq.get('ap')}
    print('STOCK', s, stocks[s])

# --- option quotes ---
occs = ['XLF260918C00061000','XLF260904C00059000','XLP260918C00090000','XLF260918C00060500',
        'XLF260918P00057000','XLF260918P00056000','XLF260918P00054500','XLF260904P00058000',
        'XLF260904P00057000','XLF260918C00059000','XLF260918C00060000','QQQ260918P00678000',
        'QQQ260918P00668000','QQQ260918C00744000','QQQ260918C00754000']
opts = {}
try:
    r = requests.get(f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={",".join(occs)}', headers=H, timeout=20)
    print('opt snapshots status:', r.status_code)
    if r.ok:
        data = r.json().get('snapshots') or {}
        for occ in occs:
            sn = data.get(occ) or {}
            lq = sn.get('latestQuote') or {}; lt = sn.get('latestTrade') or {}
            opts[occ] = {'bid': lq.get('bp'), 'ask': lq.get('ap'), 'trade': lt.get('p'), 't': lq.get('t')}
            print('OPT', occ, opts[occ])
    else:
        print('OPT SNAPSHOT NON-JSON/BODY:', r.text[:300])
except Exception as e:
    print('OPT SNAPSHOT ERROR:', e)

json.dump({'stocks': stocks, 'options': opts, 'ts': time.strftime('%Y-%m-%d %H:%M:%S')},
          open(f'{STATE}/quotes_20260831.json', 'w'), indent=2)
print('quotes saved -> quotes_20260831.json')