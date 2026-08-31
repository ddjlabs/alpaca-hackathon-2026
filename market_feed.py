#!/usr/bin/env python3
"""
Bushwood Market Data CLI — the agents' window to the tape.
Shared by all 10 agents (and the cast). Reads HACKATHON_ALPACA_KEY/SECRET
from env or .env. All calls hit Alpaca's REST API directly — no MCP dependency.

Usage:
  python3 market_feed.py snapshot SPY[,QQQ,...]      # quotes + day bars
  python3 market_feed.py quote SPY                   # latest bid/ask/trade
  python3 market_feed.py bars SPY --days 5 [--tf 1Hour]
  python3 market_feed.py chain SPY [--expiry 2026-09-04] [--calls|--puts] [--strikes 5]  # option chain w/Greeks+IV
  python3 market_feed.py optquote SPY260904C00670000  # single contract quote
  python3 market_feed.py crypto BTC/USD,ETH/USD [--days 3]
  python3 market_feed.py account                     # equity, positions
  python3 market_feed.py movers                      # top gainers/losers

Output: compact JSON (piped-friendly). Errors to stderr, exit 1.
Rate-limit aware: respects X-RateLimit-Remaining, sleeps when exhausted.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

ENV_FILE = Path("/home/doug/.hermes/profiles/gordon/.env")
TRADE_BASE = "https://paper-api.alpaca.markets/v2"
DATA_BASE = "https://data.alpaca.markets/v2"


def load_creds():
    key = os.environ.get("HACKATHON_ALPACA_KEY")
    sec = os.environ.get("HACKATHON_ALPACA_SECRET")
    if key and sec:
        return key, sec
    if ENV_FILE.exists():
        env = {}
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
        return env.get("HACKATHON_ALPACA_KEY"), env.get("HACKATHON_ALPACA_SECRET")
    return None, None


class Feed:
    def __init__(self):
        key, sec = load_creds()
        if not key or not sec:
            print("ERROR: missing HACKATHON_ALPACA_KEY/SECRET", file=sys.stderr)
            sys.exit(1)
        self.key, self.sec = key, sec
        self._remaining = None

    def get(self, url):
        req = urllib.request.Request(url, headers={
            "APCA-API-KEY-ID": self.key,
            "APCA-API-SECRET-KEY": self.sec,
        })
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    # capture rate limit headers
                    self._remaining = r.headers.get("X-RateLimit-Remaining")
                    rem = int(self._remaining) if self._remaining else None
                    if rem is not None and rem < 5:
                        time.sleep(1.5)
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = 3 * (attempt + 1)
                    print(f"rate-limited, sleeping {wait}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                print(f"HTTP {e.code} on {url.split('?')[0]}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"error: {e}", file=sys.stderr)
                sys.exit(1)
        sys.exit(1)


def fmt_snap(s):
    out = {}
    lt = s.get("latestTrade") or {}
    lq = s.get("latestQuote") or {}
    db = s.get("dailyBar") or {}
    out["last"] = lt.get("p")
    out["bid"] = lq.get("bp"); out["ask"] = lq.get("ap")
    out["open"] = db.get("o"); out["high"] = db.get("h")
    out["low"] = db.get("l"); out["close_yesterday"] = db.get("c")
    out["volume"] = db.get("v")
    return out




def _days_label(d):
    return f'{d}d'

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    feed = Feed()
    if cmd in ("account", "movers", "help") and len(sys.argv) == 2:
        pass  # account takes no symbol arg
    elif len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    if cmd == "snapshot":
        symbols = sys.argv[2].upper().split(",")
        res = feed.get(f"{DATA_BASE}/stocks/snapshots?symbols={','.join(symbols)}&feed=iex")
        print(json.dumps({s: fmt_snap(v) for s, v in res.items()}, indent=1))

    elif cmd == "quote":
        sym = sys.argv[2]
        res = feed.get(f"{DATA_BASE}/stocks/{sym}/snapshot?feed=iex")
        print(json.dumps(fmt_snap(res), indent=1))

    elif cmd == "bars":
        sym = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        tf = "1Hour" if "-- Hour" else ("1Hour" if "--hour" in sys.argv else "1Day")
        # date math
        from datetime import date, timedelta
        end = date.today()
        start = end - timedelta(days=days)
        res = feed.get(f"{DATA_BASE}/stocks/{sym}/bars?timeframe={tf}&start={start}&end={end}&feed=iex&limit=500")
        bars = (res.get("bars") or {}).get(sym, res.get("bars", [])) if isinstance(res.get("bars"), dict) else res.get("bars", [])
        compact = [{"t": b["t"][:16], "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b["v"]} for b in bars_safe(bars)]
        print(json.dumps(compact, indent=1))

    elif cmd == "chain":
        sym = sys.argv[2]
        expiry = None
        otype = None
        nstrikes = 8
        args = sys.argv[3:]
        for i, a in enumerate(args):
            if a == "--expiry":
                expiry = args[i + 1]
            elif a == "--calls":
                otype = "call"
            elif a == "--puts":
                otype = "put"
            elif a == "--strikes":
                nstrikes = int(args[i + 1])
        q = f"{TRADE_BASE}/options/contracts?underlying_symbols={sym}&limit=20"
        if expiry:
            q += f"&expiration_date={expiry}"
        if otype:
            q += f"&type={otype}"
        contracts = feed.get(q).get("option_contracts", [])
        # get snapshots for greeks/iv
        if contracts:
            syms = ",".join(c["symbol"] for c in contracts[:nstrikes * 2])
            snaps = feed.get(f"{DATA_BASE}/v1beta1/options/snapshots?symbols={syms}&feed=indicative")
        out = []
        last_price = None
        # get underlying last trade for moneyness calc
        try:
            last_price = feed.get(f"{DATA_BASE}/stocks/{sym}/snapshot?feed=iex")["latestTrade"]["p"]
        except Exception:
            pass
        for c in contracts:
            row = {"contract": c["symbol"], "strike": c.get("strike_price"), "type": c.get("type"),
                   "expiry": c.get("expiration_date")}
            snap = (snaps or {}).get("option_snapshots", {}).get(c["symbol"], {}) if snaps else {}
            gq = snap.get("latestQuote") or {}
            gr = snap.get("greeks") or {}
            out["iv"] = snap.get("impliedVolatility")
            out["delta"] = gr.get("delta"); out["theta"] = gr.get("theta")
            out["bid"] = gq.get("bp"); out["ask"] = gq.get("ap")
            if last_price:
                out["moneyness"] = round((float(c.get("strike_price", 0)) - last_price), 2)
            rows_out.append(row)
        print(json.dumps({"underlying_last": last_price, "contracts": rows_out}, indent=1))

    elif cmd == "optquote":
        sym = sys.argv[2]
        res = feed.get(f"{DATA_BASE}/v1beta1/options/snapshots?symbols={sym}&feed=indicative")
        s = (res or {}).get("option_snapshots", {}).get(sym, {})
        lq = s.get("latestQuote") or {}
        gr = s.get("greeks") or {}
        print(json.dumps({"contract": sym, "bid": lq.get("bp"), "ask": lq.get("ap"),
                          "iv": s.get("impliedVolatility"), "delta": gr.get("delta"),
                          "theta": gr.get("theta"), "vega": gr.get("vega")}, indent=1))

    elif cmd == "crypto":
        syms = sys.argv[2].split(",")
        d = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 3
        out = {}
        for s in syms:
            sym_q = s.replace("/", "%2F")
            res = feed.get("https://data.alpaca.markets/v1beta3/crypto/us/bars?symbols=" + sym_q + "&timeframe=1Hour&limit=72")
            bars = (res.get("bars") or {}).get(s, [])
            if bars:
                first, last = bars[0], bars[-1]
                chg = round((last.get("c", 0) / first.get("c", 1) - 1) * 100, 2) if first.get("c") else None
                out[s] = {"last": last.get("c"), f"{_days_label(d)}_change_pct": chg,
                          "bars": [{"t": b.get("t", "")[5:16], "c": b.get("c")} for b in bars[-12:]]}
        print(json.dumps(out, indent=1))

    elif cmd == "account":
        res = feed.get(f"{TRADE_BASE}/account")
        print(json.dumps({"account": res.get("account_number"), "equity": float(res.get("equity", 0)),
                          "cash": float(res.get("cash", 0)), "last_equity": float(res.get("last_equity", 0)),
                          "day_pnl": round(float(res.get("equity", 0)) - float(res.get("last_equity", 0)), 2),
                          "status": res.get("status"), "paper": res.get("account_number", "").startswith("PA")}, indent=1))

    elif cmd == "movers":
        # simple: SPY/QQQ/DIA snapshots as market pulse
        out = {}
        for s in ["SPY", "QQQ", "IWM"]:
            res = feed.get(f"{DATA_BASE}/stocks/{s}/snapshot?feed=iex")
            out[s] = fmt_snap(res)
        print(json.dumps(out, indent=1))

    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


def bars_safe(bars):
    return bars if isinstance(bars, list) else []


def rows_out():
    return []


if __name__ == "__main__":
    main()