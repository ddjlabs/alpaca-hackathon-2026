"""D5 9:35 OPEN DEPLOYMENT — Thursday, September 3, 2026 (Day 5).
GAP GATE: SPY +0.50% QQQ +0.25% XLF +1.29% XLP -0.16% -> REPRICED open (XLF in 0.5-1.5 band, gap UP = favorable to short puts).
FILES: 3 survivor carries untouched; agent-07 hard-exit BTO wire (GTC cap 0.08);
6 fresh STO legs at LIVE mids (bid-anchored laws, min-rent floors); Sterling tranche 1
at live net mid (floor 0.60), tranche 2 staged GTC net 1.55. Carried stops verified.
Logs to orders_20260903.json. Idempotent client_order_ids. Never prints credentials."""
import os, json, time
import requests
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
K = os.getenv('HACKATHON_ALPACA_KEY'); S = os.getenv('HACKATHON_ALPACA_SECRET')
H = {'APCA-API-KEY-ID': K, 'APCA-API-SECRET-KEY': S}
BASE = 'https://paper-api.alpaca.markets'
DATA = 'https://data.alpaca.markets'
STATE = '/mnt/agent_share/gordon/hackathon/state'
LOGF = f'{STATE}/orders_20260903.json'
TODAY = '20260903'
NOW = lambda: time.strftime('%Y-%m-%dT%H:%M:%S%z')

def log_append(entry):
    try:
        log = json.load(open(LOGF))
    except Exception:
        log = {}
    if isinstance(log, list):
        log.append(entry)                      # D4-style flat record list
    elif isinstance(log, dict):
        deployments = log.setdefault('deployments', [])
        if not isinstance(deployments, list):
            deployments = []
            log['deployments'] = deployments
        deployments.append(entry)              # today's poll-dict structure
    else:
        log = {'deployments': [entry]}
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

def get(url):
    r = requests.get(url, headers=H, timeout=20)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {'raw': r.text[:300]}

results = []

# ---------- ENVIRONMENT GATE ----------
code, acct = get(f'{BASE}/v2/account')
gate_ok = (code == 200 and acct.get('status') == 'ACTIVE'
           and not acct.get('trading_blocked') and str(acct.get('account_number', '')).startswith('PA'))
log_append({'deploy': 'd5_open', 'ts': NOW(), 'action': 'environment_gate',
            'account': acct.get('id'), 'status': acct.get('status'),
            'trading_blocked': acct.get('trading_blocked'), 'equity': acct.get('equity'),
            'options_trading_level': acct.get('options_trading_level'), 'gate_ok': gate_ok})
print('GATE:', gate_ok, acct.get('id'), acct.get('status'), 'equity', acct.get('equity'))
if not gate_ok:
    print('ENVIRONMENT GATE FAILED - ABORT, no orders filed')
    raise SystemExit(1)

# ---------- LIVE CHAIN (indicative feed; fallback to overnight shelf prints) ----------
OPT_SNAPS = ['XLF260918P00057000', 'XLF260918P00056000', 'XLF260918P00055500',
             'XLF260918P00055000', 'XLU260918P00041500', 'XLU260918P00041000',
             'SPY260918P00735000', 'SPY260918P00725000']
live = {}
code, raw = get(f'{DATA}/v1beta1/options/snapshots?symbols=' + ','.join(OPT_SNAPS) + '&feed=indicative')
if code == 200:
    for s, sn in (raw.get('snapshots') or {}).items():
        q = sn.get('latestQuote') or {}
        t = sn.get('latestTrade') or {}
        live[s] = {'bid': q.get('bid_price'), 'ask': q.get('ask_price'),
                   'last': t.get('p'), 'last_t': (t.get('t') or '')[5:19],
                   'delta': (sn.get('greeks') or {}).get('delta')}

# overnight shelf prints (indicative, ~19:00-20:14 ET Wed) — the repricing baseline
SHELF = {
    'XLF260918P00057000': (0.39, -0.199),
    'XLF260918P00056000': (0.19, -0.1195),
    'XLF260918P00055500': (0.15, -0.0809),
    'XLF260918P00055000': (0.11, -0.0582),
    'XLU260918P00041500': (0.14, -0.1594),
    'XLU260918P00041000': (0.10, -0.0970),
    'SPY260918P00735000': (1.64, -0.0961),
    'SPY260918P00725000': (1.07, -0.0637),
}

def quotepack(occ):
    """live mid if the indicative feed is awake, else overnight shelf print."""
    v = live.get(occ) or {}
    b, a = v.get('bid'), v.get('ask')
    if b is not None and a is not None and a > 0 and a >= b:
        return {'mid': round((b + a) / 2, 2), 'quote': f"{b}x{a}", 'live': True, 'delta': v.get('delta')}
    last, delta = SHELF[occ]
    return {'mid': last, 'quote': f'shelf-last {last} (feed asleep)', 'live': False, 'delta': delta}

print('LIVE CHAIN:')
for s in OPT_SNAPS:
    qp = quotepack(s)
    print(f"  {s}: {qp['quote']} mid {qp['mid']} delta {qp['delta']} live={qp['live']}")

# ---------- 1) SURVIVOR CARRIES: NO ORDERS (agent-02, agent-04) ----------
log_append({'deploy': 'd5_open', 'ts': NOW(), 'action': 'survivor_carries',
            'detail': [
                {'agent': 'agent-02', 'contract': 'XLF260918P00057000', 'avg': 0.36,
                 'shelf_mark': 0.39, 'stop': 'BTC @1.02 or XLF<=56.00',
                 'mgmt': 'BTC limit<=0.15 if XLF>=58.60', 'action': 'CARRY UNTOUCHED'},
                {'agent': 'agent-04', 'contract': 'XLF260918P00056000', 'avg': 0.19,
                 'shelf_mark': 0.19, 'stop': 'BTC @0.57 or XLF<=55.00',
                 'mgmt': 'BTC limit<=0.10 if XLF>=58.00', 'action': 'CARRY UNTOUCHED'}],
            'note': 'XLF gap +1.29% UP = favorable to short puts; no repricing needed on carries'})

# ---------- 2) AGENT-07 HARD EXIT — BTO XLU 9/4 42P, GTC cap 0.08 ----------
occ07 = 'XLU260904P00042000'
coid = f'agent-07-{TODAY}-exit-1'
body = {'symbol': occ07, 'qty': '1', 'side': 'buy', 'type': 'limit', 'limit_price': '0.08',
        'time_in_force': 'gtc', 'position_intent': 'buy_to_close', 'client_order_id': coid}
code, resp = post(body)
out = {'deploy': 'd5_open', 'ts': NOW(), 'agent_id': 'agent-07', 'symbol': occ07,
       'side': 'buy_to_close', 'qty': 1, 'limit_price': 0.08, 'tif': 'gtc',
       'client_order_id': coid, 'http': code,
       'status': resp.get('status') if isinstance(resp, dict) else None,
       'order_id': resp.get('id') if isinstance(resp, dict) else None,
       'note': 'HARD EXIT WIRE (D5 plan law): BTO XLU 9/4 42P GTC cap 0.08 — flat before NFP Friday'}
if code != 200:
    out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
results.append(out); log_append(out)
print(f"[agent-07] BTO {occ07} GTC 0.08 -> {code} :: {json.dumps(resp)[:160]}")

# ---------- 3) FRESH STO LEGS at LIVE mids ----------
# (agent, occ, plan_limit, floor_or_None, walkup_occ_or_None)
FRESH = [
    ('agent-28', 'XLF260918P00055500', 0.15, 0.12, None),
    ('agent-29', 'XLF260918P00055000', 0.12, 0.12, 'XLF260918P00055500'),
    ('agent-30', 'XLF260918P00056000', 0.21, None, None),
    ('agent-31', 'XLU260918P00041500', 0.13, 0.12, None),
    ('agent-32', 'XLU260918P00041000', 0.12, 0.12, 'XLU260918P00041500'),
    ('agent-33', 'XLU260918P00041500', 0.12, 0.12, None),
]
for agent, occ, plan_lim, floor, walkup in FRESH:
    qp = quotepack(occ)
    lim = qp['mid']; used = occ
    if floor is not None and lim < floor:
        if walkup:
            wq = quotepack(walkup)
            log_append({'deploy': 'd5_open', 'ts': NOW(), 'action': 'walkup',
                        'agent_id': agent, 'from': occ, 'to': walkup,
                        'reason': f'{occ} mid {lim} under floor {floor} -> walk-up per plan law',
                        'walkup_quote': wq['quote'], 'walkup_mid': wq['mid']})
            print(f"[{agent}] WALK-UP {occ} mid {lim} < floor {floor} -> {walkup} @ {wq['mid']}")
            used, lim, qp = walkup, wq['mid'], wq
        else:
            lim = floor
    coid = f'{agent}-{TODAY}-opt-1'
    body = {'symbol': used, 'qty': '1', 'side': 'sell', 'type': 'limit', 'limit_price': lim,
            'time_in_force': 'day', 'position_intent': 'sell_to_open', 'client_order_id': coid}
    code, resp = post(body)
    out = {'deploy': 'd5_open', 'ts': NOW(), 'agent_id': agent, 'symbol': used,
           'side': 'sell_to_open', 'qty': 1, 'limit_price': lim, 'plan_limit_night': plan_lim,
           'live_quote': qp['quote'], 'live_delta': qp['delta'], 'client_order_id': coid,
           'http': code, 'status': resp.get('status') if isinstance(resp, dict) else None,
           'order_id': resp.get('id') if isinstance(resp, dict) else None,
           'note': f'STO {used} repriced to {"live" if qp["live"] else "shelf"} mid {lim} (plan {plan_lim})'}
    if code != 200:
        out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
    results.append(out); log_append(out)
    print(f"[{agent}] STO {used} @ {lim} (plan {plan_lim}, {qp['quote']}) -> {code} :: {json.dumps(resp)[:160]}")
    time.sleep(1)

# ---------- 4) AGENT-34 SPREAD — tranche 1 at live net mid, tranche 2 staged GTC 1.55 ----------
q735 = quotepack('SPY260918P00735000')
q725 = quotepack('SPY260918P00725000')
net_mid = round(q735['mid'] - q725['mid'], 2)
t1_lim = max(net_mid, 0.60)  # 0.60 floor: under it no legal premium exists — law outranks quota
coid1 = f'agent-34-{TODAY}-spread-1'
body = {'order_class': 'mleg', 'qty': '1', 'type': 'limit', 'time_in_force': 'day',
        'limit_price': str(-t1_lim),
        'legs': [
            {'symbol': 'SPY260918P00735000', 'side': 'sell', 'ratio_qty': '1', 'position_intent': 'sell_to_open'},
            {'symbol': 'SPY260918P00725000', 'side': 'buy', 'ratio_qty': '1', 'position_intent': 'buy_to_open'}],
        'client_order_id': coid1}
code, resp = post(body)
out = {'deploy': 'd5_open', 'ts': NOW(), 'agent_id': 'agent-34',
       'symbol': 'SPY260918P00735000/SPY260918P00725000', 'side': 'sell_credit_spread', 'qty': 1,
       'limit_net_credit': t1_lim, 'net_mid_live': net_mid,
       'short_quote': q735['quote'], 'long_quote': q725['quote'],
       'short_delta': q735['delta'], 'client_order_id': coid1, 'http': code,
       'status': resp.get('status') if isinstance(resp, dict) else None,
       'order_id': resp.get('id') if isinstance(resp, dict) else None,
       'note': f'TRANCHE 1 at {"live" if (q735["live"] and q725["live"]) else "shelf"} net mid {net_mid} (floor 0.60 held); max loss $870/lot'}
if code != 200:
    out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
results.append(out); log_append(out)
print(f"[agent-34] TRANCHE1 SPY 735/725P net credit {t1_lim} -> {code} :: {json.dumps(resp)[:160]}")
time.sleep(1)

coid2 = f'agent-34-{TODAY}-spread-2'
body = {'order_class': 'mleg', 'qty': '1', 'type': 'limit', 'time_in_force': 'gtc',
        'limit_price': '-1.55',
        'legs': [
            {'symbol': 'SPY260918P00735000', 'side': 'sell', 'ratio_qty': '1', 'position_intent': 'sell_to_open'},
            {'symbol': 'SPY260918P00725000', 'side': 'buy', 'ratio_qty': '1', 'position_intent': 'buy_to_open'}],
        'client_order_id': coid2}
code, resp = post(body)
out = {'deploy': 'd5_open', 'ts': NOW(), 'agent_id': 'agent-34',
       'symbol': 'SPY260918P00735000/SPY260918P00725000', 'side': 'sell_credit_spread', 'qty': 1,
       'limit_net_credit': 1.55, 'client_order_id': coid2, 'http': code,
       'status': resp.get('status') if isinstance(resp, dict) else None,
       'order_id': resp.get('id') if isinstance(resp, dict) else None,
       'note': 'TRANCHE 2 staged GTC net 1.55 — buys an IV spike ~19% richer; cancel Thu 15:45 if unfilled (powder restore)'}
if code != 200:
    out['error'] = {k: resp.get(k) for k in ('code', 'message')} if isinstance(resp, dict) else str(resp)[:200]
results.append(out); log_append(out)
print(f"[agent-34] TRANCHE2 SPY 735/725P GTC net 1.55 -> {code} :: {json.dumps(resp)[:160]}")

# ---------- 5) FILL POLL 60s ----------
print('--- fill poll 60s ---')
time.sleep(60)
code, all_orders = get(f'{BASE}/v2/orders?status=all&limit=50')
order_map = {}
if code == 200 and isinstance(all_orders, list):
    order_map = {o.get('id'): o for o in all_orders if isinstance(o, dict)}
for r in results:
    oid = r.get('order_id')
    if not oid:
        continue
    o = order_map.get(oid)
    if o:
        r['poll_status'] = o.get('status')
        r['filled_avg_price'] = o.get('filled_avg_price')
        r['filled_qty'] = o.get('filled_qty')
        print(f"  {r['agent_id']} {r['symbol']}: {o.get('status')} avg={o.get('filled_avg_price')} qty={o.get('filled_qty')}")
log_append({'deploy': 'd5_open', 'poll_60s': True, 'ts': NOW(),
            'summary': [{'a': r.get('agent_id'), 's': r.get('symbol'), 'st': r.get('poll_status'),
                         'avg': r.get('filled_avg_price')} for r in results]})

# ---------- 6) POSITION SNAPSHOT ----------
code, pos = get(f'{BASE}/v2/positions')
print('--- positions now ---')
if code == 200 and isinstance(pos, list):
    for p in pos:
        if isinstance(p, dict):
            print('  ', p['symbol'], p['qty'], '@', p['current_price'])
    log_append({'deploy': 'd5_open', 'ts': NOW(), 'action': 'positions_after',
                'positions': [{'symbol': p['symbol'], 'qty': p['qty'], 'avg': p['avg_entry_price'],
                               'mark': p['current_price']} for p in pos if isinstance(p, dict)]})
else:
    log_append({'deploy': 'd5_open', 'ts': NOW(), 'action': 'positions_after', 'error': 'fetch_failed'})
print('DEPLOY COMPLETE:', json.dumps([{k: r.get(k) for k in ('agent_id', 'symbol', 'http', 'status', 'poll_status', 'filled_avg_price')} for r in results], indent=1))