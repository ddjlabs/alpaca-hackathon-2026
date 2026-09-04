"""9:35 open deploy pre-flight: clock, account, positions, gap gate, live option chain, roster."""
import os, json, urllib.request
from dotenv import load_dotenv
load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
assert K and S, "creds missing"

def req(url):
    r = urllib.request.Request(url, headers={'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())

clock = req('https://paper-api.alpaca.markets/v2/clock')
print('CLOCK:', json.dumps(clock))

acct = req('https://paper-api.alpaca.markets/v2/account')
print('ACCT:', json.dumps({k: acct.get(k) for k in ('account_number','status','trading_blocked','equity','cash','buying_power','last_equity','portfolio_value')}))

pos = req('https://paper-api.alpaca.markets/v2/positions')
print('POSITIONS:', len(pos))
for p in pos:
    print('  ', p['symbol'], 'qty', p['qty'], 'entry', p['avg_entry_price'], 'mkt', p['current_price'], p.get('asset_class'))

oo = req('https://paper-api.alpaca.markets/v2/orders?status=open')
print('OPEN ORDERS:', len(oo))
for o in oo:
    print('  ', o['id'][:8], o['type'], o['side'], o['symbol'], 'qty', o.get('qty'), 'lmt', o.get('limit_price'), o.get('client_order_id'), o.get('time_in_force'))

snaps = req('https://data.alpaca.markets/v2/stocks/snapshots?symbols=SPY,QQQ,XLF,XLP,XLU&feed=iex')
print('--- GAP GATE ---')
for s in ['SPY','QQQ','XLF','XLP','XLU']:
    d = snaps.get(s, {})
    prev = (d.get('prevDailyBar') or {}).get('c')
    lt = (d.get('latestTrade') or {}).get('p')
    q = d.get('latestQuote') or {}
    bp, ap = q.get('bp') or 0, q.get('ap') or 0
    mid = (bp+ap)/2 if bp and ap else None
    px = lt or mid
    gap = ((px/prev)-1)*100 if prev and px else None
    print(f'{s}: prev_close {prev} | live {px} | gap {gap:+.2f}% | quote {bp}x{ap} | last trade t {(d.get("latestTrade") or {}).get("t")}')

print('--- OPTION CHAIN (live, iex) ---')
contracts = 'XLF260918P00055500,XLF260918P00055000,XLP260918P00083000,XLU260918P00041000,XLF260918P00057000,XLF260918P00056000,XLU260904P00042000'
try:
    osnaps = req(f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={contracts}&feed=iex')
    for s, d in osnaps.items():
        q = d.get('latestQuote') or {}
        g = d.get('greeks') or {}
        lt = (d.get('latestTrade') or {}).get('price')
        print(f"{s}: bid {q.get('bid_price')} x ask {q.get('ask_price')} | last {lt} | delta {g.get('delta')} | iv {round(d.get('implied_volatility') or 0,3)}")
except Exception as e:
    print('osnap err:', repr(e))

print('--- DASHBOARD ROSTER ---')
dash = json.load(open('/mnt/agent_share/gordon/hackathon/state/dashboard.json'))
print('top keys:', list(dash.keys()))
agents = dash.get('agents', [])
print('agents:', len(agents))
for a in agents:
    print('  ', a.get('agent_id'), a.get('name'), '| status', a.get('status'), '| strikes', a.get('strikes'))