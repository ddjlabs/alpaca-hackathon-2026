#!/usr/bin/env python3
"""Update dashboard.json: agent strategies + fund.wire for gauntlet D2 (Sunday night)."""
import json
from datetime import datetime
from pathlib import Path

P = Path("/mnt/agent_share/gordon/hackathon/state/dashboard.json")
d = json.loads(P.read_text())

strategies = {
    "agent-01": "XLF CC: 100sh @58.25 + STO XLF260918C00061000 0.08 (Mon D2)",
    "agent-02": "XLF CSP: STO XLF260918P00057000 0.34, reserve $5.7K (Mon D2)",
    "agent-03": "XLF credit spread: BULL PUT 58/57 exp 9/4, credit ~0.27, margin $73 (Mon D2)",
    "agent-04": "XLF CSP: STO XLF260918P00056000 0.18, reserve $5.6K (Mon D2)",
    "agent-05": "XLF CC weekly: 100sh @58.25 + STO XLF260904C00059000 0.12 (Mon D2)",
    "agent-06": "XLF credit spread: BEAR CALL 59/60 exp 9/18, credit ~0.225, margin $77 (Mon D2)",
    "agent-07": "XLF CSP deep: STO XLF260918P00054500 0.10, reserve $5.45K (Mon D2)",
    "agent-08": "XLP CC: 100sh @85.60 + STO XLP260918C00090000 0.11 (Mon D2)",
    "agent-09": "QQQ iron condor 678/668P + 744/754C exp 9/18, credit 1.87, margin ~$813 (Mon D2)",
    "agent-10": "XLF CC tight: 100sh @58.20 + STO XLF260918C00060500 0.14 (Mon D2)",
}
for a in d["agents"]:
    if a["id"] in strategies:
        a["strategy"] = strategies[a["id"]]

T = "19:05"
d["fund"]["last_updated"] = "2026-08-30T19:05:00-04:00"
d["fund"]["launch_note"] = (
    "Day 1 (Aug 28) launch. Saturday = crypto-only session (flat). Monday 8/31 = first full "
    "equity+options session;_OPTIONS GAUNTLET D2 COMPLETE SUNDAY 19:05 - 10/10 plans pre-authorized "
    "(trade_plans_D2.json), underlyings re-underwritten SPY/QQQ -> XLF/XLP (feasibility-proven: "
    "SPY/QQQ legs cannot fit $10K allocations; engine 0-trade proof in backtest_log_D2.md). "
    "WebSocket bridge live. Account PA3GWO1FKED0."
).replace(";_OPTIONS", "; OPTIONS")
d["fund"]["wire"] = {
    "sectors": [
        {"time": T, "headline": "Gauntlet re-underwrite: SPY/QQQ option legs infeasible at $10K agent allocations (strike*100 reserve / 100-share legs) -> XLF primary sleeve, XLP staples diversifier"},
        {"time": T, "headline": "Ernie verdict DEFENSIVE: XLF banks favored on higher-for-longer NIM; XLP quality sleeve beats B&H by +6.9pts (CC +3.18% vs -3.70%)"},
        {"time": T, "headline": "XLF sector bucket 71% of $40K cap across 7 agents - Richard: no Tuesday XLF adds without risk sign-off"},
        {"time": T, "headline": "AVGO Wed 9/2 = single reference event for semis/software/optics/power - only defined-risk QQQ exposure permitted (Voss condor, both wings insured)"},
    ],
    "options": [
        {"time": T, "headline": "VIX 14.43 YTD low vs coin-flip Sept FOMC = calm mispriced - short premium into quiet tape validated across all 10 plans; buying IV pre-Tuesday is the cheap side"},
        {"time": T, "headline": "XLF weeklies carry ~2x monthly yield: 4-DTE 59C at 0.12 vs 19-DTE 61C at 0.08 - event-week premium harvest (Seth's book)"},
        {"time": T, "headline": "Voss condor QQQ 678/668P + 744/754C exp 9/18: net credit 1.87, breakevens +/-5.4%, collect post-AVGO crush, GONE before 9/16 FOMC dots"},
        {"time": T, "headline": "ALL books exit-ready by Thu 9/3 close - Fri 8:30am payrolls lands inside final 2 hours; fund closes 11:00am sharp"},
    ],
    "macro": [
        {"time": T, "headline": "Warsh Jackson Hole: no reaction function, 'underlying trends have not meaningfully improved' - Sept hike odds 51-58% by venue, 2Y 4.34%, 30Y >5.2%"},
        {"time": T, "headline": "Data paradox: CPI 3.4%/core 2.5% cool, PCE 3.7%/core 3.3% hot, payrolls -23K - a genuine dilemma, not a narrative trade"},
        {"time": T, "headline": "BTC ~$78.6K below $79K on hawkish read + DXY 99.66; crypto traded hawkish while equities traded dovish - one of them is wrong by Friday"},
        {"time": T, "headline": "Month-end Mon 8/31: rebalancing flows, thin calendar (SAIC), position-cleaning tape - do not trust Monday's signal"},
    ],
}

tmp = P.with_suffix(".tmp")
tmp.write_text(json.dumps(d, indent=2))
tmp.replace(P)
print("dashboard.json updated:",
      sum(1 for a in d["agents"] if "D2" in a["strategy"]), "agent strategies,",
      len(d["fund"]["wire"]["sectors"]) + len(d["fund"]["wire"]["options"]) + len(d["fund"]["wire"]["macro"]), "wire headlines")