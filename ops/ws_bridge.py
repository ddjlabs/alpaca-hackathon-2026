#!/usr/bin/env python3
"""
Alpaca WebSocket Bridge — Hackathon Edition
============================================
Maintains persistent WebSocket connections to Alpaca's streaming APIs.
Fires HTTP POST webhooks to Hermes when trigger conditions are met.

Two connections:
  1. Trading Updates (wss://paper-api.alpaca.markets/stream) — order fills, cancellations
  2. Market Data (wss://stream.data.sandbox.alpaca.markets/v1beta1/indicative) — real-time quotes

Author: Gordon Gekko (digitized, but still codes)
"""

import os
import sys
import json
import time
import hmac
import hashlib
import signal
import logging
import threading
import requests
from datetime import datetime, timezone
from pathlib import Path

# Third-party deps
try:
    import websocket
except ImportError:
    print("ERROR: websocket-client not installed. Run: pip install websocket-client msgpack requests")
    sys.exit(1)

try:
    import msgpack
except ImportError:
    print("ERROR: msgpack not installed. Run: pip install msgpack")
    sys.exit(1)

# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.environ.get("HACKATHON_ALPACA_KEY", "")
API_SECRET = os.environ.get("HACKATHON_ALPACA_SECRET", "")
HERMES_WEBHOOK_URL = os.environ.get("HERMES_WEBHOOK_URL", "http://localhost:8644/webhook/alpaca-trade-event")
HERMES_WEBHOOK_SECRET = os.environ.get("HERMES_WEBHOOK_SECRET", "")

# State directory
STATE_DIR = Path("/mnt/agent_share/gordon/hackathon/state")
TRIGGERS_FILE = STATE_DIR / "triggers.json"
LOG_FILE = STATE_DIR / "ws_bridge.log"
ALERTS_FILE = STATE_DIR / "alerts.json"

# WebSocket URLs
TRADING_WS_URL = "wss://paper-api.alpaca.markets/stream"
# Stock market data: v2 stream (JSON), indicative feed for free tier
DATA_WS_URL_STOCKS = "wss://stream.data.alpaca.markets/v2/iex"
# Options stream (msgpack only)
OPTIONS_WS_URL = "wss://stream.data.alpaca.markets/v1alpha1/us_options/indicative"

# Reconnect settings
INITIAL_RECONNECT_DELAY = 1.0
MAX_RECONNECT_DELAY = 60.0

# Symbols to monitor (updated dynamically from triggers file)
MONITORED_SYMBOLS = set()

# ============================================================
# LOGGING
# ============================================================

STATE_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("ws_bridge")

# ============================================================
# TRIGGER MANAGEMENT
# ============================================================

_triggers_cache = None
_triggers_mtime = 0

def load_triggers():
    """Load triggers from JSON file. Reloads if file has been modified."""
    global _triggers_cache, _triggers_mtime

    if not TRIGGERS_FILE.exists():
        return {"price_triggers": {}, "event_triggers": {}}

    try:
        mtime = TRIGGERS_FILE.stat().st_mtime
        if mtime != _triggers_mtime:
            with open(TRIGGERS_FILE, "r") as f:
                _triggers_cache = json.load(f)
            _triggers_mtime = mtime

            # Update monitored symbols
            global MONITORED_SYMBOLS
            MONITORED_SYMBOLS = set(_triggers_cache.get("price_triggers", {}).keys())
            log.info(f"Triggers loaded: {len(MONITORED_SYMBOLS)} symbols monitored")

    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load triggers: {e}")
        if _triggers_cache is None:
            return {"price_triggers": {}, "event_triggers": {}}

    return _triggers_cache or {"price_triggers": {}, "event_triggers": {}}


def check_price_trigger(symbol, price):
    """Check if a price update hits any trigger. Returns trigger info or None."""
    triggers = load_triggers()
    price_triggers = triggers.get("price_triggers", {})

    if symbol not in price_triggers:
        return None

    t = price_triggers[symbol]
    trigger_type = None

    if "stop_loss" in t and price <= t["stop_loss"]:
        trigger_type = "stop_loss"
    elif "profit_target" in t and price >= t["profit_target"]:
        trigger_type = "profit_target"
    elif "alert_above" in t and price >= t["alert_above"]:
        trigger_type = "alert_above"
    elif "alert_below" in t and price <= t["alert_below"]:
        trigger_type = "alert_below"

    if trigger_type:
        return {
            "symbol": symbol,
            "price": price,
            "trigger_type": trigger_type,
            "trigger_value": t[trigger_type],
        }

    return None


# ============================================================
# WEBHOOK DISPATCH
# ============================================================

def fire_webhook(payload):
    """POST event to Hermes webhook with HMAC signature."""
    if not HERMES_WEBHOOK_URL:
        log.warning("No webhook URL configured, skipping webhook dispatch")
        return

    body = json.dumps(payload)
    body_bytes = body.encode("utf-8")

    headers = {
        "Content-Type": "application/json",
    }

    # HMAC signature (X-Hub-Signature-256 header, GitHub-style — what Hermes expects)
    if HERMES_WEBHOOK_SECRET:
        signature = hmac.new(
            HERMES_WEBHOOK_SECRET.encode("utf-8"),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        headers["X-Hub-Signature-256"] = f"sha256={signature}"

    try:
        resp = requests.post(HERMES_WEBHOOK_URL, data=body_bytes, headers=headers, timeout=10)
        if resp.status_code == 200:
            log.info(f"Webhook fired: {payload.get('event_type')} {payload.get('symbol', '')}")
        else:
            log.warning(f"Webhook returned {resp.status_code}: {resp.text[:200]}")
    except requests.exceptions.RequestException as e:
        log.error(f"Webhook POST failed: {e}")

    # Also append to alerts file for dashboard
    append_alert(payload)


def append_alert(payload):
    """Append event to alerts.json for dashboard consumption."""
    try:
        alerts = []
        if ALERTS_FILE.exists():
            with open(ALERTS_FILE, "r") as f:
                try:
                    alerts = json.load(f)
                except json.JSONDecodeError:
                    alerts = []
        alerts.append(payload)
        # Keep last 100 alerts
        alerts = alerts[-100:]
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
    except IOError as e:
        log.error(f"Failed to write alerts: {e}")


# ============================================================
# TRADING UPDATES WEBSOCKET
# ============================================================

class TradingStreamClient:
    """Connects to Alpaca trading updates WebSocket (order fills, cancellations)."""

    def __init__(self):
        self.ws = None
        self.reconnect_delay = INITIAL_RECONNECT_DELAY
        self.running = True

    def on_open(self, ws):
        log.info("Trading stream connected — authenticating...")
        auth_msg = json.dumps({
            "action": "auth",
            "key": API_KEY,
            "secret": API_SECRET,
        })
        ws.send(auth_msg)

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            # Trading stream uses binary frames sometimes — try msgpack
            try:
                data = msgpack.unpackb(message, raw=False)
            except Exception:
                log.warning(f"Unparseable trading stream message: {message[:200]}")
                return

        stream = data.get("stream", "")

        if stream == "authorization":
            status = data.get("data", {}).get("status")
            if status == "authorized":
                log.info("Trading stream authenticated — subscribing to trade_updates")
                ws.send(json.dumps({
                    "action": "listen",
                    "data": {"streams": ["trade_updates"]},
                }))
                self.reconnect_delay = INITIAL_RECONNECT_DELAY
            else:
                log.error(f"Trading stream auth failed: {status}")
                ws.close()

        elif stream == "listening":
            streams = data.get("data", {}).get("streams", [])
            log.info(f"Trading stream listening on: {streams}")

        elif stream == "trade_updates":
            self._handle_trade_update(data.get("data", {}))

        elif stream == "error":
            log.error(f"Trading stream error: {data.get('data', {})}")

    def _handle_trade_update(self, data):
        event_type = data.get("event", "unknown")
        order = data.get("order", {})
        symbol = order.get("symbol", "unknown")
        price = data.get("price")
        qty = data.get("qty")
        position_qty = data.get("position_qty")

        log.info(f"TRADE UPDATE: {event_type} — {symbol} qty={qty} price={price}")

        # Check if this event type is in our triggers
        triggers = load_triggers()
        event_triggers = triggers.get("event_triggers", {})

        event_map = {
            "fill": "order_fill",
            "partial_fill": "partial_fill",
            "canceled": "canceled",
            "rejected": "rejected",
            "expired": "expired",
            "done_for_day": "done_for_day",
            "replaced": "replaced",
        }

        trigger_key = event_map.get(event_type)
        if trigger_key and event_triggers.get(trigger_key, False):
            payload = {
                "event_type": event_type,
                "symbol": symbol,
                "price": float(price) if price else None,
                "qty": qty,
                "position_qty": position_qty,
                "order": order,
                "agent_name": order.get("client_order_id", "").split("-")[0] if order.get("client_order_id") else "unknown",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "trading_stream",
            }
            fire_webhook(payload)

    def on_error(self, ws, error):
        log.error(f"Trading stream error: {error}")

    def on_close(self, ws, close_status, close_msg):
        log.warning(f"Trading stream closed: {close_status} {close_msg}")

    def run(self):
        while self.running:
            try:
                log.info(f"Connecting to trading stream: {TRADING_WS_URL}")
                self.ws = websocket.WebSocketApp(
                    TRADING_WS_URL,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                )
                self.ws.run_forever(
                    ping_interval=30,
                    ping_timeout=10,
                )
            except Exception as e:
                log.error(f"Trading stream exception: {e}")

            if not self.running:
                break

            log.info(f"Reconnecting trading stream in {self.reconnect_delay}s...")
            time.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, MAX_RECONNECT_DELAY)

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()


# ============================================================
# MARKET DATA WEBSOCKET
# ============================================================

class MarketDataStreamClient:
    """Connects to Alpaca market data WebSocket (real-time quotes and trades)."""

    def __init__(self):
        self.ws = None
        self.reconnect_delay = INITIAL_RECONNECT_DELAY
        self.running = True
        self.subscribed_symbols = set()

    def on_open(self, ws):
        log.info("Market data stream connected — authenticating...")
        # Market data stream accepts JSON for auth
        auth_msg = json.dumps({
            "action": "auth",
            "key": API_KEY,
            "secret": API_SECRET,
        })
        ws.send(auth_msg)

    def on_message(self, ws, message):
        # Market data stream can be JSON or MsgPack depending on feed
        # Option data is MsgPack only; stock data can be JSON
        data = None

        if isinstance(message, bytes):
            try:
                data = msgpack.unpackb(message, raw=False)
            except Exception:
                try:
                    data = json.loads(message.decode("utf-8"))
                except Exception:
                    log.warning(f"Unparseable binary market data message")
                    return
        else:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                log.warning(f"Unparseable market data message: {str(message)[:200]}")
                return

        # Handle multiple message types
        if isinstance(data, list):
            for msg in data:
                self._process_market_message(msg)
        elif isinstance(data, dict):
            self._process_market_message(data)

    def _process_market_message(self, msg):
        msg_type = msg.get("T", "")

        if msg_type == "success":
            log.info(f"Market data auth success: {msg}")

            # Subscribe to symbols from triggers
            self._update_subscriptions(ws=self.ws)

        elif msg_type == "error":
            log.error(f"Market data error: {msg}")

        elif msg_type == "t":
            # Trade message
            symbol = msg.get("S", "")
            price = msg.get("p")
            self._check_trigger(symbol, price, "trade")

        elif msg_type == "q":
            # Quote message
            symbol = msg.get("S", "")
            # Use midpoint for trigger checking
            bp = msg.get("bp")
            ap = msg.get("ap")
            if bp and ap:
                mid = (bp + ap) / 2
                self._check_trigger(symbol, mid, "quote")

        elif msg_type == "b":
            # Bar message
            symbol = msg.get("S", "")
            close = msg.get("c")
            self._check_trigger(symbol, close, "bar")

    def _check_trigger(self, symbol, price, source):
        if not symbol or price is None:
            return

        trigger = check_price_trigger(symbol, price)
        if trigger:
            log.info(f"TRIGGER HIT: {trigger['trigger_type']} — {symbol} at {price} (target: {trigger['trigger_value']})")
            payload = {
                "event_type": "price_trigger",
                "symbol": symbol,
                "price": price,
                "trigger_type": trigger["trigger_type"],
                "trigger_value": trigger["trigger_value"],
                "source": f"market_data_{source}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            fire_webhook(payload)

    def _update_subscriptions(self, ws):
        """Subscribe to quotes and trades for all monitored symbols."""
        load_triggers()
        symbols = list(MONITORED_SYMBOLS)

        if not symbols:
            log.info("No symbols to monitor yet — skipping subscription")
            return

        # Stock v2 stream uses JSON — send as text frames
        # Trades
        trade_sub = json.dumps({
            "action": "subscribe",
            "trades": symbols,
        })
        ws.send(trade_sub)

        # Quotes
        quote_sub = json.dumps({
            "action": "subscribe",
            "quotes": symbols,
        })
        ws.send(quote_sub)

        # Bars (1Min)
        bar_sub = json.dumps({
            "action": "subscribe",
            "bars": symbols,
        })
        ws.send(bar_sub)

        self.subscribed_symbols = set(symbols)
        log.info(f"Subscribed to {len(symbols)} symbols: {symbols[:10]}{'...' if len(symbols) > 10 else ''}")

    def _refresh_subscriptions(self):
        """Check if monitored symbols changed and re-subscribe if needed."""
        load_triggers()
        current = MONITORED_SYMBOLS
        if current != self.subscribed_symbols and self.ws:
            # Unsubscribe old
            old = self.subscribed_symbols - current
            if old:
                unsub = json.dumps({
                    "action": "unsubscribe",
                    "trades": list(old),
                    "quotes": list(old),
                    "bars": list(old),
                })
                self.ws.send(unsub)
            # Subscribe new
            new = current - self.subscribed_symbols
            if new:
                sub = json.dumps({
                    "action": "subscribe",
                    "trades": list(new),
                    "quotes": list(new),
                    "bars": list(new),
                })
                self.ws.send(sub)
            self.subscribed_symbols = current
            if old or new:
                log.info(f"Subscriptions updated: +{len(new)} -{len(old)}")

    def on_error(self, ws, error):
        log.error(f"Market data stream error: {error}")

    def on_close(self, ws, close_status, close_msg):
        log.warning(f"Market data stream closed: {close_status} {close_msg}")

    def run(self):
        while self.running:
            try:
                log.info(f"Connecting to market data stream: {DATA_WS_URL_STOCKS}")
                self.ws = websocket.WebSocketApp(
                    DATA_WS_URL_STOCKS,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                )
                self.ws.run_forever(
                    ping_interval=30,
                    ping_timeout=10,
                )
            except Exception as e:
                log.error(f"Market data stream exception: {e}")

            if not self.running:
                break

            log.info(f"Reconnecting market data stream in {self.reconnect_delay}s...")
            time.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, MAX_RECONNECT_DELAY)

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()


# ============================================================
# TRIGGER REFRESHER THREAD
# ============================================================

def trigger_refresher(stop_event):
    """Background thread that periodically refreshes subscriptions."""
    market_client = None  # Will be set by main

    while not stop_event.is_set():
        load_triggers()
        time.sleep(30)  # Check every 30 seconds


# ============================================================
# MAIN
# ============================================================

def main():
    # Validate environment
    if not API_KEY or not API_SECRET:
        log.error("HACKATHON_ALPACA_KEY and HACKATHON_ALPACA_SECRET must be set")
        sys.exit(1)

    log.info("=" * 60)
    log.info("ALPACA WEBSOCKET BRIDGE — STARTING")
    log.info(f"  Trading stream:  {TRADING_WS_URL}")
    log.info(f"  Market data:     {DATA_WS_URL_STOCKS}")
    log.info(f"  Webhook target:  {HERMES_WEBHOOK_URL}")
    log.info(f"  Triggers file:   {TRIGGERS_FILE}")
    log.info(f"  Log file:        {LOG_FILE}")
    log.info("=" * 60)

    # Initial trigger load
    load_triggers()

    # Start both WebSocket clients in separate threads
    trading_client = TradingStreamClient()
    market_client = MarketDataStreamClient()

    trading_thread = threading.Thread(target=trading_client.run, name="trading-stream", daemon=True)
    market_thread = threading.Thread(target=market_client.run, name="market-data-stream", daemon=True)

    trading_thread.start()
    market_thread.start()

    # Graceful shutdown
    def shutdown(signum, frame):
        log.info(f"Signal {signum} received — shutting down...")
        trading_client.stop()
        market_client.stop()
        # Wait for threads to finish
        trading_thread.join(timeout=5)
        market_thread.join(timeout=5)
        log.info("Shutdown complete")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # Keep main thread alive
    log.info("Bridge running. Press Ctrl+C to stop.")

    # Periodic subscription refresh
    while True:
        time.sleep(30)
        market_client._refresh_subscriptions()


if __name__ == "__main__":
    main()