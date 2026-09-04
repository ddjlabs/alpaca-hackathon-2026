"""10:15 poll pt4: holdings map, dashboard id fields, option quotes via feed=opra."""
import os, json, urllib.request, urllib.error
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')

def req(url):
    r = urllib.request.Request(url, headers={'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())

# --- portfolio holdings structure ---
try:
    h = json.load(open('/mnt/agent_share/gordon/hackathon/state/portfolio_holdings.json'))
    print('--- HOLDINGS: type', type(h).__name__)
    if isinstance(h, dict):
        print('top keys:', list(h.keys()))
        for k, v in h.items():
            if isinstance(v, dict):
                print(f"  {k}: keys {list(v.keys())[:12]}")
                eo = v.get('executed_orders')
                print(f"     executed_orders={eo} positions={json.dumps(v.get('positions'))[:220]}")
    elif isinstance(h, list):
        print('entries:', len(h))
        for e in h:
            print('  ', json.dumps(e)[:260])
except Exception as e:
    print('holdings err:', repr(e))

# --- dashboard agent id fields ---
dash = json.load(open('/mnt/agent_share/gordon/hackathon/state/dashboard.json'))
a0 = (dash.get('agents') or [{}])[0]
print('--- DASHBOARD agent[0] keys:', list(a0.keys()))
print(json.dumps(a0)[:400])
print('fund hr_board tail:', json.dumps((dash.get('fund') or {}).get('hr_board'))[-200:] if isinstance(dash.get('fund'), dict) else 'n/a')
print('dashboard hr_board:', json.dumps(dash.get('hr_board'))[-200:] if dash.get('hr_board') else 'none')

# --- option quotes via feed=opra ---
contracts = 'XLF260918P00055500,XLF260918P00055000,XLP260918P00083000,XLU260904P00042000,XLF260918P00056000,XLF260918P00057000'
print('--- OPTION QUOTES (opra) ---')
for url in (f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={contracts}&feed=opra',
            f'https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={contracts}&feed=opra'):
    try:
        d = req(url)
        print('OK endpoint:', url.split('/options/')[1])
        items = d.get('snapshots') if isinstance(d.get('snapshots'), dict) else d.get('quotes', d)
        for s, v in (items.items() if isinstance(items, dict) else []):
            q = (v or {}).get('latestQuote') or (v or {})
            g = (v or {}).get('greeks') or {}
            print(f"  {s}: bid {q.get('bid_price')} x ask {q.get('ask_price')} sz {q.get('bid_size')}x{q.get('ask_size')} | delta {g.get('delta')}")
        break
    except urllib.error.HTTPError as e:
        print('FAIL', e.code, e.read()[:200])