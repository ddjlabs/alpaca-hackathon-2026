"""Fix data_issue note in orders log programmatically (patch tool broke JSON)."""
import json, os

p = '/mnt/agent_share/gordon/hackathon/state/orders_20260902.json'
log = json.load(open(p))
print('loaded OK, entries:', len(log))

new_note = ('Alpaca options quotes unavailable: feed=iex -> 400 invalid option feed; feed=opra -> 403 OPRA agreement not signed; '
            'feed=sip -> 400. FALLBACK VERIFIED 10:20 ET: CBOE delayed quotes '
            'https://cdn.cboe.com/api/global/delayed_quotes/options/{SYM}.json (free, full chain, bid/ask/iv; delta=null -> '
            'BS-compute from iv + Alpaca live underlying). 14:30 RECIPE: underlying from Alpaca iex snapshots, option bid from CBOE; '
            'XLU 41P law check = BS delta with CBOE iv (10:20 read: -0.195 to -0.238 depending on spot — ON the 0.20 line, recompute live).')

found = False
for e in log:
    if isinstance(e, dict) and e.get('poll') == '1015' and 'data_issue' in e:
        e['data_issue'] = new_note
        found = True
print('patched 1015 entry:', found)

tmp = p + '.tmp'
with open(tmp, 'w') as f:
    json.dump(log, f, indent=2)
os.replace(tmp, p)

chk = json.load(open(p))
print('reloaded OK, entries:', len(chk))
for e in chk:
    if e.get('poll') == '1015':
        print('1015 entry actions:', e.get('actions_taken'))