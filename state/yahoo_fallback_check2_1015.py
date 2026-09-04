"""Fallback test 2: CBOE delayed quotes (free, has greeks) + Alpaca feed=sip last try."""
import json, urllib.request

def get(url, hdrs=None):
    r = urllib.request.Request(url, headers=hdrs or {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())

want = {'XLF260918P00055500', 'XLF260918P00055000', 'XLP260918P00083000', 'XLU260918P00041000', 'XLU260918P00040500', 'XLU260918P00042000'}

# --- CBOE delayed quotes ---
for sym in ('XLF', 'XLP', 'XLU'):
    try:
        d = get(f'https://cdn.cboe.com/api/global/delayed_quotes/options/{sym}.json')
        data = d.get('data', {})
        print(f"{sym}: spot {data.get('current_price')} | options {len(data.get('options', []))}")
        for o in data.get('options', []):
            if o.get('option') in want:
                g = o.get('greeks') or {}
                print(f"   {o['option']}: bid {o.get('bid')} x ask {o.get('ask')} | last {o.get('last_trade_price')} | delta {g.get('delta')} | iv {o.get('iv')}")
    except Exception as e:
        print(sym, 'CBOE FAIL:', repr(e)[:140])

# --- Alpaca feed=sip last try ---
import os
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
try:
    r = urllib.request.Request('https://data.alpaca.markets/v1beta1/options/snapshots?symbols=XLF260918P00055500&feed=sip',
                               headers={'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S})
    with urllib.request.urlopen(r, timeout=20) as resp:
        print('ALPACA sip OK:', resp.read()[:200])
except Exception as e:
    body = getattr(e, 'read', lambda: b'')()[:150]
    print('ALPACA sip FAIL:', repr(e)[:100], body)