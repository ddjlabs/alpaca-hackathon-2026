import json, urllib.request

env = {}
for line in open('/home/doug/.hermes/profiles/gordon/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

KID, SEC = env.get('HACKATHON_ALPACA_KEY'), env.get('HACKATHON_ALPACA_SECRET')

req = urllib.request.Request('https://paper-api.alpaca.markets/v2/account',
    headers={'APCA-API-KEY-ID': KID, 'APCA-API-SECRET-KEY': SEC})
acct = json.load(urllib.request.urlopen(req, timeout=15))

gate = {'account': acct['account_number'], 'status': acct['status'],
        'trading_blocked': acct['trading_blocked'], 'equity': acct['equity'], 'cash': acct['cash']}
print('GATE:', gate)
assert acct['account_number'] == 'PA3GWO1FKED0' and acct['status'] == 'ACTIVE' and not acct['trading_blocked']

path = '/mnt/agent_share/gordon/hackathon/state/orders_20260902.json'
log = json.load(open(path))
log.append({
    "ts": "2026-09-02T12:45:52-04:00", "action": "poll_1245", "result": "ACTIVE",
    "gate": gate,
    "note": "board empty, 0 cards for charlie, 0 inbound order_requests (10 board msgs today, all pre-logged: ernie 07:02 wire + charlie 09:44/10:48 desk notes); unfilled-watch NOT ARMED (12:45 < 14:30). Teeth roster unchanged if unfilled at 14:30: agents 21/22/23/24 (resting since 09:43) + 25/26 (since 10:48) = one forced reprice to live bid; exempt: agent-27 (filled 09:43), 02/04/07 (survivor carried short puts). No warnings due. 15:45 fallback armed behind reprice. Last fill remains agent-27 BTC tranche 09:43."
})
json.dump(log, open(path, 'w'), indent=1)
print('heartbeat logged, entries:', len(log))