"""10:15 trade board poll: account gate, open orders, fills since 09:43 deploy, positions, Rule 8 pre-watch."""
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
gate = {k: acct.get(k) for k in ('account_number','status','trading_blocked','equity','cash','buying_power','portfolio_value')}
print('ACCT GATE:', json.dumps(gate))
assert gate['account_number'].startswith('PA'), "WRONG ACCOUNT"
assert gate['status'] == 'ACTIVE' and not gate['trading_blocked'], "ENVIRONMENT GATE FAIL"

pos = req('https://paper-api.alpaca.markets/v2/positions')
print('POSITIONS:', len(pos))
for p in pos:
    print('  ', p['symbol'], 'qty', p['qty'], 'entry', p['avg_entry_price'], 'mkt', p['current_price'], p.get('asset_class'))

# everything since 09:30 today — catches 09:43 filings, any 09:52 reprice, fills
oo_all = req('https://paper-api.alpaca.markets/v2/orders?status=all&after=2026-09-02T09:30:00-04:00&limit=100')
print('ORDERS SINCE 09:30:', len(oo_all))
for o in oo_all:
    print(f"  {o['id'][:8]} | {o['status']:10} | {o.get('type',''):6} {o.get('side',''):4} {o['symbol']:24} qty {o.get('qty')} lmt {o.get('limit_price')} tif {o.get('time_in_force','')} filed {o.get('created_at','')[11:19]} | coid {o.get('client_order_id')} | filled {o.get('filled_qty')} @ {o.get('filled_avg_price')}")
    if o.get('status') in ('canceled','expired','rejected'):
        print('     -> status_note:', o.get('status_note') or o.get('cancel_reason') or '')

# live quotes for resting underlyings + contracts
try:
    snaps = req('https://data.alpaca.markets/v2/stocks/snapshots?symbols=SPY,QQQ,XLF,XLP,XLU,BTC/USD,ETH/BTC&feed=iex')
except Exception:
    snaps = req('https://data.alpaca.markets/v2/stocks/snapshots?symbols=SPY,QQQ,XLF,XLP,XLU&feed=iex')
print('--- UNDERLYING SNAPS ---')
for s, d in snaps.items():
    q = d.get('latestQuote') or {}
    prev = (d.get('prevDailyBar') or {}).get('c')
    lt = (d.get('latestTrade') or {}).get('p')
    px = lt or q.get('bp')
    gap = ((px/prev)-1)*100 if prev and px else None
    print(f"{s}: {px} gap {gap if gap is None else round(gap,2)}% quote {q.get('bp')}x{q.get('ap')}")

contracts = 'XLF260918P00055500,XLF260918P00055000,XLP260918P00083000'
osnaps = req(f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={contracts}&feed=iex')
print('--- RESTING CONTRACT SNAPS ---')
for s, d in osnaps.items():
    q = d.get('latestQuote') or {}
    g = d.get('greeks') or {}
    print(f"{s}: bid {q.get('bid_price')} x ask {q.get('ask_price')} | delta {g.get('delta')}")

# dashboard roster + today's fills bookkeeping
dash = json.load(open('/mnt/agent_share/gordon/hackathon/state/dashboard.json'))
agents = dash.get('agents', [])
print('--- ROSTER ---')
for a in agents:
    print('  ', a.get('agent_id'), a.get('name'), '| status', a.get('status'), '| strikes', a.get('strikes'), '| exec_today', a.get('executed_orders'), '| carried_pos', bool(a.get('positions') or a.get('carried_portfolio')))