#!/usr/bin/env python3
"""D2 4:30PM FIRING — update dashboard.json from REST-truth marks."""
import json
from datetime import datetime

DASH = '/mnt/agent_share/gordon/hackathon/state/dashboard.json'
d = json.load(open(DASH))

# Final P&L by agent (equity, day) — REST-verified marks
FINALS = {
    'agent-01': 9929.00,
    'agent-02': 9995.00,
    'agent-03': 9991.00,
    'agent-04': 9995.00,
    'agent-05': 9929.00,
    'agent-06': 9995.00,
    'agent-07': 10000.00,
    'agent-08': 9921.00,
    'agent-09': 9961.00,
    'agent-10': 9929.00,
}
KEEP = {'agent-07', 'agent-02', 'agent-04'}

for a in d['agents']:
    aid = a['id']
    eq = FINALS[aid]
    alloc = a['allocation']
    a['current_value'] = eq
    a['daily_pnl'] = round(eq - alloc, 2)
    a['daily_pnl_pct'] = round((eq - alloc) / alloc * 100, 2)
    a['exposure'] = 0  # post-cleanup mark; cleanup liquidates all fired books
    if aid in KEEP:
        a['status'] = 'active'
        if a['id'] == 'agent-07':
            a['strategy'] = 'FLAT — zero fills D2; deep 54.5 CSP never executed. #1 seed on a flat book.'
        else:
            a['strategy'] += ' | KEPT D2 — short put marked against at close (−$5); reserve intact'
    else:
        a['status'] = 'fired'
        a['strategy'] += ' | FIRED D2 — book liquidated in 4:45 cleanup'

d['fired_today'] = ['agent-06 Blaze Torres', 'agent-03 Donnie Azoff', 'agent-09 Vegas Voss',
                    'agent-01 Bud Fox', 'agent-05 Seth Davis', 'agent-10 Storm Callahan',
                    'agent-08 Jim Young']
d['kept_today'] = ['agent-07 Shelly Levene', 'agent-02 Ricky Roma', 'agent-04 Elwood Blues']

d['fund']['current_equity'] = 99884.07
d['fund']['total_pnl'] = -115.93
d['fund']['total_pnl_pct'] = -0.116
d['fund']['day_pnl'] = -115.93
d['fund']['day_pnl_pct'] = -0.14
d['fund']['day'] = 2
d['fund']['last_updated'] = datetime.now().astimezone().isoformat()
d['fund']['launch_note'] += (" || D2 FIRING 16:30: 7/10 terminated. Kept: Levene ($0.00, zero fills — flat book won the day), "
                             "Roma (−$5.00), Blues (−$5.00, soul-name tie-break over Torres). Fired books liquidated 4:45 "
                             "via ar-cleanup orders; $99,884.07 pool returns to cash for the 6PM reallocation. "
                             "HR board: state/hr_board_D2.md.")

json.dump(d, open(DASH, 'w'), indent=2)
print('dashboard.json updated:', datetime.now().isoformat())
print('kept:', d['kept_today'])
print('fired:', len(d['fired_today']), 'agents')