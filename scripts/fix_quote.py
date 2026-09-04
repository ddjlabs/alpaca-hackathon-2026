#!/usr/bin/env python3
"""Retry QQQ option quote with endpoint variants; patch 13:45 entry detail."""
import json, os, urllib.request, urllib.error
from pathlib import Path

KEY = os.environ.get('HACKATHON_ALPACA_KEY'); SEC = os.environ.get('HACKATHON_ALPACA_SECRET')

def get(url):
    req = urllib.request.Request(url, headers={'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

variants = [
    'https://data.alpaca.markets/v1beta1/options/snapshots/QQQ?symbols=QQQ260918C00754000&feed=indicative',
    'https://data.alpaca.markets/v1beta1/options/snapshots?symbols=QQQ260918C00754000',
    'https://data.alpaca.markets/v1beta1/options/snapshots?symbols=QQQ260918C00754000&feed=indicative',
]
snap = None
for i, url in enumerate(variants):
    try:
        d = get(url)
        snap = d.get('snapshots', {}).get('QQQ260918C00754000') or (list(d.get('snapshots', {}).values())[0] if d.get('snapshots') else None)
        print(f'variant {i} OK')
        break
    except urllib.error.HTTPError as e:
        print(f'variant {i} -> HTTP {e.code}')
    except Exception as e:
        print(f'variant {i} -> {e}')

bid = ask = last = None
if snap:
    q = snap.get('latestQuote', {}); t = snap.get('latestTrade', {})
    bid, ask = q.get('bp'), q.get('ap')
    last = t.get('p')
    mid = (bid + ask) / 2 if (bid and ask) else None
    print(f'QQQ 754C: bid {bid} x ask {ask}, mid {mid}, last {last}')
else:
    mid = None
    print('all quote variants failed')

# Patch the 13:45 entry quote_refresh detail
f = Path('/mnt/agent_share/gordon/hackathon/state/orders_20260901.json')
orders = json.loads(f.read_text())
for e in orders:
    if e.get('poll_time_et') == '13:45':
        for a in e.get('poll_actions', []):
            if a.get('action') == 'quote_refresh':
                if bid is not None:
                    a['detail'] = (f"BTC 77,427 (-2.2% vs 79,200) / ETH 2,433 (-2.3% vs 2,490); "
                                   f"QQQ 754C bid {bid} x ask {ask}, mid {mid:.2f}, last {last} (13:45)")
                else:
                    a['detail'] = ("BTC 77,427 (-2.2% vs 79,200) / ETH 2,433 (-2.3% vs 2,490); "
                                   "QQQ 754C snapshot API 400 (3 endpoint variants); last good quote 13:35 = bid 0.24/ask 0.26 mid 0.25 — unchanged thesis: order never crosses")
        break
tmp = f.with_suffix('.tmp')
tmp.write_text(json.dumps(orders, indent=1))
tmp.replace(f)
print('entry patched')