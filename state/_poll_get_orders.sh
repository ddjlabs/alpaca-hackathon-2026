#!/usr/bin/env bash
source /home/doug/.hermes/profiles/gordon/.env
curl -s -m 10 \
  -H "APCA-API-KEY-ID: $HACKATHON_ALPACA_KEY" \
  -H "APCA-API-SECRET-KEY: $HACKATHON_ALPACA_SECRET" \
  "https://paper-api.alpaca.markets/v2/orders?status=open&limit=50" -o /tmp/_open_orders.json
echo "curl_exit=$?"