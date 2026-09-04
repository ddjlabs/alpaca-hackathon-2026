#!/usr/bin/env python3
"""
Test script for the Alpaca WebSocket Bridge.
Verifies:
  1. Dependencies are installed
  2. Environment variables are set
  3. WebSocket connections can be established
  4. Triggers file is valid
  5. Webhook endpoint is reachable

Run: python3 /mnt/agent_share/gordon/hackathon/test_bridge.py
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

def test_dependencies():
    """Check that required Python packages are installed."""
    print("\n=== DEPENDENCY CHECK ===")
    missing = []

    try:
        import websocket
        print(f"  websocket-client: OK (v{getattr(websocket, '__version__', 'unknown')})")
    except ImportError:
        missing.append("websocket-client")
        print("  websocket-client: MISSING")

    try:
        import msgpack
        print(f"  msgpack: OK")
    except ImportError:
        missing.append("msgpack")
        print("  msgpack: MISSING")

    try:
        import requests
        print(f"  requests: OK")
    except ImportError:
        missing.append("requests")
        print("  requests: MISSING")

    if missing:
        print(f"\n  Install missing: pip install {' '.join(missing)}")
        return False
    return True


def test_env_vars():
    """Check that required environment variables are set."""
    print("\n=== ENVIRONMENT VARIABLES ===")
    required = ["HACKATHON_ALPACA_KEY", "HACKATHON_ALPACA_SECRET"]
    optional = ["HERMES_WEBHOOK_URL", "HERMES_WEBHOOK_SECRET"]

    all_good = True
    for var in required:
        val = os.environ.get(var, "")
        if val:
            print(f"  {var}: SET ({val[:4]}...{val[-4:]})")
        else:
            print(f"  {var}: NOT SET ⚠️")
            all_good = False

    for var in optional:
        val = os.environ.get(var, "")
        if val:
            print(f"  {var}: SET")
        else:
            print(f"  {var}: NOT SET (optional)")

    if not all_good:
        print("\n  Set required vars:")
        print('  export HACKATHON_ALPACA_KEY="your-key"')
        print('  export HACKATHON_ALPACA_SECRET="your-secret"')

    return all_good


def test_triggers_file():
    """Check that triggers.json exists and is valid."""
    print("\n=== TRIGGERS FILE ===")
    triggers_path = Path("/mnt/agent_share/gordon/hackathon/state/triggers.json")

    if not triggers_path.exists():
        print(f"  {triggers_path}: NOT FOUND ⚠️")
        print("  Creating default...")
        default = {
            "price_triggers": {},
            "event_triggers": {"order_fill": True}
        }
        triggers_path.parent.mkdir(parents=True, exist_ok=True)
        with open(triggers_path, "w") as f:
            json.dump(default, f, indent=2)
        print(f"  Created default triggers file")
        return True

    try:
        with open(triggers_path, "r") as f:
            data = json.load(f)
        price_count = len(data.get("price_triggers", {}))
        event_count = len(data.get("event_triggers", {}))
        print(f"  File exists: OK")
        print(f"  Price triggers: {price_count} symbols")
        print(f"  Event triggers: {event_count} types")
        if price_count > 0:
            print(f"  Monitored: {list(data['price_triggers'].keys())}")
        return True
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return False


def test_webhook_endpoint():
    """Check if Hermes webhook endpoint is reachable."""
    print("\n=== WEBHOOK ENDPOINT ===")
    url = os.environ.get("HERMES_WEBHOOK_URL", "http://localhost:8644/webhook/alpaca-trade-event")

    # Try health check on the gateway
    health_url = url.rsplit("/", 2)[0] + "/health"
    try:
        resp = requests.get(health_url, timeout=5)
        if resp.status_code == 200:
            print(f"  Gateway health: OK ({health_url})")
        else:
            print(f"  Gateway health: {resp.status_code}")
    except requests.exceptions.RequestException:
        print(f"  Gateway not reachable at {health_url}")
        print("  Start it with: hermes gateway run")
        print("  The bridge will still run — webhooks just won't fire until gateway is up")
        return False

    return True


def test_trading_ws():
    """Test WebSocket connection to Alpaca trading stream."""
    print("\n=== TRADING STREAM CONNECTION TEST ===")

    api_key = os.environ.get("HACKATHON_ALPACA_KEY", "")
    api_secret = os.environ.get("HACKATHON_ALPACA_SECRET", "")

    if not api_key or not api_secret:
        print("  Skipping — no API credentials set")
        return False

    try:
        import websocket
        ws = websocket.create_connection(
            "wss://paper-api.alpaca.markets/stream",
            timeout=10,
        )

        # Auth
        auth_msg = json.dumps({"action": "auth", "key": api_key, "secret": api_secret})
        ws.send(auth_msg)

        result = ws.recv()
        data = json.loads(result)

        if data.get("stream") == "authorization" and data.get("data", {}).get("status") == "authorized":
            print("  Authentication: SUCCESS")
        else:
            print(f"  Authentication: FAILED — {data}")
            ws.close()
            return False

        # Subscribe
        ws.send(json.dumps({"action": "listen", "data": {"streams": ["trade_updates"]}}))
        result = ws.recv()
        data = json.loads(result)

        if data.get("stream") == "listening":
            streams = data.get("data", {}).get("streams", [])
            print(f"  Subscribed to: {streams}")
            print("  Trading stream: OK ✅")
        else:
            print(f"  Subscribe result: {data}")

        ws.close()
        return True

    except Exception as e:
        print(f"  Connection failed: {e}")
        return False


def test_market_data_ws():
    """Test WebSocket connection to Alpaca market data stream."""
    print("\n=== MARKET DATA STREAM CONNECTION TEST ===")

    api_key = os.environ.get("HACKATHON_ALPACA_KEY", "")
    api_secret = os.environ.get("HACKATHON_ALPACA_SECRET", "")

    if not api_key or not api_secret:
        print("  Skipping — no API credentials set")
        return False

    try:
        import websocket
        ws = websocket.create_connection(
            "wss://stream.data.sandbox.alpaca.markets/v1beta1/indicative",
            timeout=10,
        )

        # Auth
        auth_msg = json.dumps({"action": "auth", "key": api_key, "secret": api_secret})
        ws.send(auth_msg)

        # Market data stream returns MsgPack — handle binary
        import msgpack
        result = ws.recv()

        # Try msgpack first (options/market data uses msgpack)
        try:
            data = msgpack.unpackb(result, raw=False)
        except Exception:
            try:
                data = json.loads(result)
            except (json.JSONDecodeError, TypeError):
                data = {}

        if isinstance(data, list):
            data = data[0] if data else {}

        if data.get("T") == "success":
            print(f"  Authentication: SUCCESS — {data.get('msg', '')}")
        else:
            print(f"  Authentication result: {data}")

        # Try subscribing to SPY
        sub_msg = json.dumps({"action": "subscribe", "trades": ["SPY"], "quotes": ["SPY"]})
        ws.send(sub_msg)

        # Wait briefly for confirmation
        time.sleep(2)

        try:
            ws.settimeout(3)
            result = ws.recv()
            print(f"  Subscription response received: {str(result)[:100]}")
            print("  Market data stream: OK ✅")
        except Exception:
            print("  No immediate data (normal if market closed)")
            print("  Market data stream: CONNECTED ✅")

        ws.close()
        return True

    except Exception as e:
        print(f"  Connection failed: {e}")
        return False


def main():
    print("=" * 60)
    print("ALPACA WEBSOCKET BRIDGE — TEST SUITE")
    print("=" * 60)

    results = []

    results.append(("Dependencies", test_dependencies()))
    results.append(("Environment", test_env_vars()))
    results.append(("Triggers file", test_triggers_file()))
    results.append(("Webhook endpoint", test_webhook_endpoint()))
    results.append(("Trading WS", test_trading_ws()))
    results.append(("Market data WS", test_market_data_ws()))

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")

    all_pass = all(p for _, p in results)
    if all_pass:
        print("\n  All tests passed! Bridge is ready to run.")
        print("  Start with: python3 /mnt/agent_share/gordon/hackathon/ws_bridge.py")
    else:
        print("\n  Some tests failed. Fix the issues above before running the bridge.")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())