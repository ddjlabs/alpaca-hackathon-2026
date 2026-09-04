"""10:15 poll pt2: option quotes (retry w/o feed param), roster, board tail since 09:44."""
import os, json, urllib.request
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')

def req(url):
    r = urllib.request.Request(url, headers={'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())

contracts = 'XLF260918P00055500,XLF260918P00055000,XLP260918P00083000,XLU260904P00042000,XLF260918P00056000,XLF260918P00057000'
osnaps = None
for url in (f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={contracts}&feed=iex',
            f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={contracts}'):
    try:
        osnaps = req(url)
        print('snapshots OK via', url.split('?')[1][:30])
        break
    except Exception as e:
        print('attempt failed:', repr(e)[:120])
if osnaps:
    print('--- OPTION SNAPS ---')
    for s, d in osnaps.items():
        q = d.get('latestQuote') or {}
        g = d.get('greeks') or {}
        lt = (d.get('latestTrade') or {})
        print(f"{s}: bid {q.get('bid_price')} x ask {q.get('ask_price')} (sz {q.get('bid_size')}x{q.get('ask_size')}) | last {lt.get('price')} @ {str(lt.get('t',''))[11:19]} | delta {g.get('delta')}")

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