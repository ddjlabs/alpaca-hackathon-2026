#!/usr/bin/env python3
"""SPY 7-day daily bars from Alpaca IEX feed for benchmark."""
import json, os, requests
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv('/home/doug/.hermes/profiles/gordon/.env')
key = os.environ['HACKATHON_ALPACA_KEY']
sec = os.environ['HACKATHON_ALPACA_SECRET']
H = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': sec}

start = (date.today() - timedelta(days=7)).isoformat()
end = date.today().isoformat()
url = f'https://data.alpaca.markets/v2/stocks/SPY/bars?timeframe=1Day&start={start}&end={end}&feed=iex'
r = requests.get(url, headers=H, timeout=30)
data = r.json()
with open('/mnt/agent_share/gordon/hackathon/state/eod_pull/spy_bars.json', 'w') as f:
    json.dump(data, f, indent=1)

bars = data.get('bars', [])
print("SPY daily bars:", len(bars))
prev_close = None
for b in bars:
    t = b['t'][:10]
    o, h, l, c, v = b['o'], b['h'], b['l'], b['c'], b['v']
    chg = f"{(c - prev_close) / prev_close * 100:+.2f}%" if prev_close else "n/a"
    print(f"  {t}  O={o:.2f} H={h:.2f} L={l:.2f} C={c:.2f} V={v:>10}  {chg}")
    prev_close = c