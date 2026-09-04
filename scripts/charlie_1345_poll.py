#!/usr/bin/env python3
"""Charlie 13:45 poll: refresh quotes, append poll entry atomically."""
import json, os, urllib.request
from pathlib import Path
from datetime import datetime, timezone

STATE = Path('/mnt/agent_share/gordon/hackathon/state')
KEY = os.environ.get('HACKATHON_ALPACA_KEY'); SEC = os.environ.get('HACKATHON_ALPACA_SECRET')

def get(url):
    req = urllib.request.Request(url, headers={'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SEC})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

# 1. Crypto latest trades (agent-20 trigger levels)
try:
    c = get('https://data.alpaca.markets/v1beta3/crypto/us/latest/trades?symbols=BTC%2FUSD,ETH%2FUSD')
    tr = c.get('trades', {})
    btc = float(tr.get('BTC/USD', {}).get('p', 0))
    eth = float(tr.get('ETH/USD', {}).get('p', 0))
    btc_gap = (btc / 79200 - 1) * 100
    eth_gap = (eth / 2490 - 1) * 100
    print(f"BTC {btc:,.0f} ({btc_gap:+.1f}% vs 79,200 trigger) | ETH {eth:,.0f} ({eth_gap:+.1f}% vs 2,490)")
except Exception as e:
    btc = eth = None
    print('crypto fetch failed:', e)

# 2. QQQ260918C00754000 quote (stale ar-cleanup-agent-09-1)
try:
    q = get('https://data.alpaca.markets/v1beta1/options/snapshots/QQQ?symbols=QQQ260918C00754000')
    snap = q.get('snapshots', {}).get('QQQ260918C00754000', {})
    g = snap.get('greeks', {}); quote = snap.get('latestQuote', {})
    bid, ask = quote.get('bp', 0), quote.get('ap', 0)
    mid = (bid + ask) / 2 if bid and ask else 0
    print(f"QQQ 754C: bid {bid} x ask {ask}, mid {mid:.2f}, iv {g.get('iv')}")
except Exception as e:
    bid = ask = mid = None
    print('option quote failed:', e)

# 3. Append poll entry
f = STATE / 'orders_20260901.json'
orders = json.loads(f.read_text())
now_et = datetime.now().astimezone()
entry = {
    "poll": True,
    "poll_time_et": "13:45",
    "poll_ts": now_et.isoformat(timespec='seconds'),
    "kanban_cards_assigned_charlie": 0,
    "environment_gate": {
        "account": "PA3GWO1FKED0",
        "status": "ACTIVE",
        "trading_blocked": False,
        "equity": 99826.05,
        "cash": 100206.05
    },
    "fills_today_total": 11,
    "fills_attribution": {
        "agent_legs": 7,
        "agents_filled": ["agent-02", "agent-04", "agent-07", "agent-11", "agent-12",
                          "agent-14", "agent-15", "agent-17", "agent-18"],
        "ar_cleanup_legs": 4,
        "ar_cleanup_note": "documented carry-over liquidations (AR log); agent-09 QQQ 754C SELL 1 @0.60 still resting"
    },
    "rule8_1430_preview": {
        "exempt_carried_positions": ["agent-02", "agent-04"],
        "filled_today": ["agent-02", "agent-04", "agent-07", "agent-11", "agent-12",
                         "agent-14", "agent-15", "agent-17", "agent-18"],
        "zero_fill_zero_position": ["agent-20"],
        "note": (f"agent-20 Jared Stone: sole Rule 8 target at 14:30. Crypto still below triggers: "
                 f"BTC {btc:,.0f} ({btc_gap:+.1f}% vs 79,200), ETH {eth:,.0f} ({eth_gap:+.1f}% vs 2,490) "
                 f"at 13:45. No card filed. Pre-warning 12:59 stands. AT 14:30: formal WARNING "
                 f"(order_rejected, rule='8: engagement') — 60-min ultimatum. NON-TRADING flag 15:45 if still flat."),
        "resting_order_agents": [],
        "teeth_note": "No roster agent has a resting unfilled order; agent-17 filled 12:32. Only teeth candidate = agent-20 (no card, no order)."
    },
    "poll_actions": [
        {"action": "inbox_read", "detail": "0 unread for charlie; board quiet since 13:18 risk_note"},
        {"action": "desk_idle", "detail": "no cards; gates PASS; agent-20 warning due 14:30 poll; stale ar-cleanup-agent-09-1 left for 16:30 AR pass"},
        {"action": "quote_refresh", "detail": f"QQQ 754C bid {bid}/ask {ask} mid {mid}; BTC {btc:,.0f} ETH {eth:,.0f}"}
    ],
    "open_orders": [
        "ar-cleanup-agent-09-1 (QQQ260918C00754000 sell 1 @0.60 limit, stale, bid ~0.24 — AR 16:30)"
    ]
}
orders.append(entry)
tmp = f.with_suffix('.tmp')
tmp.write_text(json.dumps(orders, indent=1))
tmp.replace(f)
print(f"appended 13:45 poll entry; file now {len(orders)} entries")