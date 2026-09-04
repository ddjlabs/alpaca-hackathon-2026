#!/usr/bin/env python3
"""D3 GAUNTLET final step: refresh fund.wire in dashboard.json with tonight's validated items (most recent first)."""
import json
from pathlib import Path

F = Path("/mnt/agent_share/gordon/hackathon/state/dashboard.json")
d = json.loads(F.read_text())
T = "19:45"

new_wire = {
    "last_updated": "2026-08-31T19:45:00-04:00",
    "sectors": [
        {"time": T, "headline": "Options gauntlet D3 validated: XLF CSP family +5.61% Sharpe 3.53 (6/6 wins, MDD 0.00), 46DTE branch +2.39%, XLU +3.00% outright vs a -10.88% pond — utilities is the only sleeve beating its own benchmark"},
        {"time": T, "headline": "XLF bucket carried + gen-2 fills = $39,250 of Richard's $40,000 cap (98.1%) — HARD GATE, no new XLF legs Tuesday for anyone; ISM 10am is a theta day, not a chase day"},
        {"time": "18:30", "headline": "Replication verdict: the tape paid the put-sellers — 3/3 survivors ran XLF CSPs; gen-2 keeps the doctrine with mutated strikes/expiries"},
    ],
    "options": [
        {"time": T, "headline": "Chains re-checked 19:35: all nine book mids sit exactly on plan limits (J.Blues 57.5P 0.55, Dean 10/16 57P 0.82, George 10/16 55P 0.38) — zero repricing needed at the open"},
        {"time": T, "headline": "Weekly fallback grid re-priced live (state/weekly_chain_20260904.json): XLF 9/4 56P dead at 0.01/0.06 — fallback limits price at LIVE mid, one reprice, take the bid; Shelly's XLU 42P weekly at 0.13 mid, HARD close Thu 15:45 (expires into Fri 8:30 NFP)"},
        {"time": T, "headline": "Book carries 5 resting ar-cleanup orders (03/06/09 residuals) — do not refile, not positions; survivors' short puts carried open by design"},
        {"time": "18:30", "headline": "All books exit-ready by Thu close per desk rule — no naked short premium into Fri 8:30 payrolls"},
    ],
    "macro": [
        {"time": T, "headline": "Roster math corrected at 19:40: 10 allocated books only (13/16/19 reclaimed but ZERO allocation — furniture, not funds); Stone's sizing corrected to ~45% max deploy (draft was 103.5%)"},
        {"time": T, "headline": "BTC faded to 78,381 into the night (3d +0.59%); confirm at 79,200 must be EARNED — no front-running the level, skip beats stop-out"},
        {"time": "18:30", "headline": "Warsh hangover persists: Sept hike odds ~56%, 2Y 4.36% — hawkish rates tape keeps the book defensive (XLF/XLU)"},
        {"time": "18:30", "headline": "Freight train: ISM Tue 10am, ADP + DELL/PANW/MDB Wed, LULU/ZS Thu, NFP Fri 8:30 inside the fund's final 2.5 hours"},
    ],
}
d["fund"]["wire"] = new_wire
d["fund"]["last_updated"] = new_wire["last_updated"]
t = F.with_suffix(".tmp")
t.write_text(json.dumps(d, indent=2))
t.replace(F)
# verify
chk = json.loads(F.read_text())
print("wire updated:", chk["fund"]["wire"]["last_updated"], "| sectors:", len(chk["fund"]["wire"]["sectors"]),
      "| options:", len(chk["fund"]["wire"]["options"]), "| macro:", len(chk["fund"]["wire"]["macro"]))
print("agents on roster:", len(chk["agents"]))