#!/usr/bin/env python3
"""Live quote for QQQ260918C00754000 (stale ar-cleanup liquidation)."""
import json, os, urllib.request
KEY = os.environ.get('HACKATHON_ALPACA_KEY', '')
SEC = os.environ.get('HACKATHON_ALPACA_SECRET', '')
HDRS = {'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC}
sym = 'QQQ260918C00754000'
req = urllib.request.Request(
    f'https://data.alpaca.markets/v1beta1/options/snapshots?symbols={sym}&feed=indicative',
    headers=HDRS)
with urllib.request.urlopen(req, timeout=20) as r:
    data = json.loads(r.read().decode())
snaps = data.get('snapshots', {})
for s, v in snaps.items():
    g = v.get('latestQuote', {})
    t = v.get('latestTrade', {})
    print(f"{s}: bid={g.get('bp')}x{g.get('bs')} ask={g.get('ap')}x{g.get('as')} "
          f"mid={( (g.get('bp') or 0) + (g.get('ap') or 0))/2:.2f} last={t.get('p')} @ {t.get('t','')[:19]}")