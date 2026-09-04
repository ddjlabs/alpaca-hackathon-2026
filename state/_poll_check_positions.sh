#!/usr/bin/env bash
# Rule 10 zero-verification: live Alpaca book vs published holdings
source /home/doug/.hermes/profiles/gordon/.env
curl -s -m 10 \
  -H "APCA-API-KEY-ID: $HACKATHON_ALPACA_KEY" \
  -H "APCA-API-SECRET-KEY: $HACKATHON_ALPACA_SECRET" \
  "https://paper-api.alpaca.markets/v2/positions" -o /tmp/_pos.json
echo "curl_exit=$?"
python3 - <<'EOF'
import json
try:
    pos = json.load(open('/tmp/_pos.json'))
except Exception as e:
    print('parse error:', e); raise SystemExit
if isinstance(pos, list):
    print('alpaca open positions:', len(pos))
    for p in pos:
        print(' ', p.get('symbol'), 'qty', p.get('qty'), 'mkt', p.get('market_value'), 'chg_today', p.get('change_today'))
else:
    print('unexpected:', json.dumps(pos)[:300])
EOF