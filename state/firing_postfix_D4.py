#!/usr/bin/env python3
"""D4 firing post-fix: mirror fired dicts into TOP-LEVEL hr_board (site reads top-level),
fix daily_history alpha convention (total_pnl_pct - spy_since_launch_pct)."""
import json, os

DASH = "/mnt/agent_share/gordon/hackathon/state/dashboard.json"
d = json.load(open(DASH))
fired = d["fired_today"]
top = d.get("hr_board") or []
have = {e.get("agent") for e in top}
added = 0
for e in fired:
    if e["agent"] not in have:
        top.append(e); added += 1
d["hr_board"] = top

for h in d["fund"]["daily_history"]:
    if h.get("day") == 4 and h.get("spy_close"):
        spy_since = round((h["spy_close"] / 769.12 - 1) * 100, 2)
        h["spy_since_launch_pct"] = spy_since
        h["alpha_vs_spy_pct"] = round(h["total_pnl_pct"] - spy_since, 2)
        print("history day4 fixed: spy_since", spy_since, "alpha", h["alpha_vs_spy_pct"])

tmp = DASH + ".tmp"; json.dump(d, open(tmp, "w"), indent=2); os.replace(tmp, DASH)
print("top-level hr_board:", len(top), "entries (added", added, ")")