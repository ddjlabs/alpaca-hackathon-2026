#!/usr/bin/env python3
"""Probe option quote endpoints on data.alpaca.markets."""
import os, requests, json
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
D = 'https://data.alpaca.markets'
occs = ','.join(['XLF260918C00061000','XLF260904C00059000','QQQ260918P00678000'])

for name, url in [
    ('snapshots-bulk', f'{D}/v1beta1/options/snapshots?symbols={occs}'),
    ('snapshots-bulk-indicative', f'{D}/v1beta1/options/snapshots?symbols={occs}&feed=indicative'),
    ('snapshots-byunderlying', f'{D}/v1beta1/options/snapshots/XLF'),
    ('quotes-latest', f'{D}/v1beta1/options/quotes/latest?symbols={occs}'),
    ('bars-latest', f'{D}/v1beta1/options/bars/latest?symbols={occs}'),
]:
    r = requests.get(url, headers=H, timeout=20)
    body = r.text[:200].replace('\n', ' ')
    print(f'--- {name}: {r.status_code} :: {body}')

# peek at Sunday's bars file for structure
try:
    b = json.load(open('/mnt/agent_share/gordon/hackathon/state/bars_XLF.json'))
    print('bars_XLF.json keys:', list(b.keys())[:5] if isinstance(b, dict) else type(b))
    s = json.dumps(b)[:600]
    print('head:', s)
except Exception as e:
    print('bars read err:', e)