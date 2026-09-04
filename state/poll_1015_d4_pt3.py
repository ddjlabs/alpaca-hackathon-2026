"""10:15 poll pt3: roster + board first, then option quotes with diagnostics."""
import os, json, urllib.request, urllib.error
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')

def req(url):
    r = urllib.request.Request(url, headers={'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())

# --- roster + board FIRST ---
dash = json.load(open('/mnt/agent_share/gordon/hackathon/state/dashboard.json'))
print('--- ROSTER ---')
for a in dash.get('agents', []):
    print('  ', a.get('agent_id'), a.get('name'), '| status', a.get('status'), '| strikes', a.get('strikes'), '| cv', a.get('current_value'), '| exec_today', a.get('executed_orders'), '| non_trading', a.get('non_trading_flag'))

mb = json.load(open('/mnt/agent_share/gordon/hackathon/state/messageboard_20260902.json'))
print('--- BOARD SINCE 09:45 ---')
new = [m for m in mb if str(m.get('ts') or m.get('timestamp',''))[11:16] >= '09:45']
if not new:
    print('(none)')
for m in new:
    print(f"{m.get('ts', m.get('timestamp'))} | {m.get('from')} -> {m.get('to')} | {m.get('type')} | re={m.get('re')}")
    print('   ', str(m.get('message'))[:180])

# --- option quotes with diagnostics ---
contracts = 'XLF260918P00055500,XLF260918P00055000,XLP260918P00083000'
urls = [
    f'https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={contracts}&feed=iex',
    f'https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={contracts}',
    f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={contracts}&feed=iex',
]
print('--- OPTION QUOTES ---')
for url in urls:
    try:
        d = req(url)
        print('OK endpoint:', url.split('/options/')[1].split('?')[0])
        for s, v in d.items():
            q = v.get('latestQuote') if isinstance(v, dict) else None
            g = (v.get('greeks') or {}) if isinstance(v, dict) else {}
            print(f"  {s}: bid {q.get('bid_price') if q else None} x ask {q.get('ask_price') if q else None} | sz {q.get('bid_size') if q else None}x{q.get('ask_size') if q else None} | delta {g.get('delta')}")
        break
    except urllib.error.HTTPError as e:
        body = e.read()[:300]
        print('FAIL', url.split('/options/')[1], e.code, body)