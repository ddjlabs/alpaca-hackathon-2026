#!/usr/bin/env python3
"""D3 polish: unify cause strings to D2 style (−$X.XX unicode minus + $), across
every location the dicts appear (fired_today, fund.fired_today, hr_board, fund.hr_board)."""
import json, os

DASH = "/mnt/agent_share/gordon/hackathon/state/dashboard.json"
d = json.load(open(DASH))

NEW_CAUSE = {
    "agent-20": "D3 — fired at rank #1 with $0.00 — Rule-8 non-trading; the mutant's chair was a one-day tryout.",
    "agent-12": "D3 — bottom-7 by day P&L — rank #2 at −$0.04.",
    "agent-14": "D3 — bottom-7 by day P&L — rank #4 at −$0.06.",
    "agent-17": "D3 — bottom-7 by day P&L — rank #5 at −$0.09.",
    "agent-18": "D3 — bottom-7 by day P&L — rank #6 at −$0.09.",
    "agent-15": "D3 — bottom-7 by day P&L — rank #8 at −$0.22.",
    "agent-11": "D3 — bottom-7 by day P&L — rank #10 at −$0.30.",
}

def fix_list(lst):
    n = 0
    for it in lst:
        if isinstance(it, dict):
            for aid, cause in NEW_CAUSE.items():
                if str(it.get("agent", "")).startswith(aid) and it.get("cause") != cause:
                    it["cause"] = cause; n += 1
    return n

total = 0
for key in ("fired_today", "hr_board"):
    total += fix_list(d.get(key, []))
fund = d.get("fund", {})
for key in ("fired_today", "hr_board"):
    total += fix_list(fund.get(key, []))

tmp = DASH + ".tmp"; json.dump(d, open(tmp, "w"), indent=2); os.replace(tmp, DASH)
print("cause strings unified:", total)