#!/usr/bin/env python3
"""10:30 ET trade board poll — Day 5. Append poll entry to orders log (atomic)."""
import json, os, datetime

STATE = "/mnt/agent_share/gordon/hackathon/state"
LOG = f"{STATE}/orders_20260903.json"
TMP = LOG + ".tmp"

poll = {
    "poll": "10:30 ET — trade board poll",
    "time": "2026-09-03T10:30:45-04:00",
    "board": "bushwoodstratton_trading",
    "cards_for_charlie": 0,
    "message_board_inbound": 0,
    "environment_gate": {
        "account": "PA3GWO1FKED0",
        "status": "ACTIVE",
        "trading_blocked": False,
        "equity": "99838.40",
        "cash": "99884.40",
        "open_orders": 8,
    },
    "rule_8_unfilled_watch": (
        "IN SCOPE at 14:30 ET — not yet triggered (10:30). Zero-fill agents today: "
        "28/29/30/31/32/33/34 (7) — ALL have resting orders (8 legs, filed 09:38 by "
        "9:35 deploy cron; age 52 min, within tolerance). Survivor-carried (02, 04) "
        "exempt per carve-out. Agent-07 has 1 fill today (hard exit 09:38) — not on "
        "watch. First forced-reprice authority 14:30 ET; 15:45 teeth after."
    ),
    "rule_10_silent_zero_verification": {
        "live_positions": 2,
        "live_contracts": 2,
        "attribution": (
            "PASS — 2/2 survivor-carried short puts resolve to active agents: "
            "agent-04 XLF260918P00056000 (-1, entry 0.19, mark 0.15) + agent-02 "
            "XLF260918P00057000 (-1, entry 0.36, mark 0.31). Zero unattributed."
        ),
        "resting_bto_coverage": (
            "n/a — no resting BTOs; the 8 resting legs are Day-5 plan executions "
            "(7 STO singles + agent-34 2x mleg SPY 735/725 spreads), not cleanup wires"
        ),
        "risk_block": "holdings rollup refreshed 10:30:15 ET (heartbeat chain) — fresh",
        "holdings_rollup_fresh": True,
        "note": (
            "open-order tape re-verified 10:30 via /v2/orders?status=open: 8/8 legs "
            "status=new at filed limits (28+29 XLF55.5P@0.15, 30 XLF56P@0.19, "
            "31/32/33 XLU41.5P@0.14, 34 T1 net 0.60 day + T2 GTC 1.55). No partials, "
            "no cancels, no new submissions since 10:15."
        ),
    },
    "actions": [
        "VERIFIED: kanban queue empty (0 cards for charlie); message board 0 inbound to charlie (9 msgs today = ernie wire + 8 deploy-cron order_executed notices)",
        "VERIFIED: environment gate PASS (PA3GWO1FKED0 / ACTIVE / trading_blocked=false / equity 99838.40)",
        "VERIFIED: open-order tape unchanged since 10:15 — 8 legs resting at filed limits, no partials, no cancels, no new submissions",
        "VERIFIED: no fills after 13:38:51Z (agent-07 hard exit) per /v2/account/activities/FILL",
        "VERIFIED: live positions 2/2 attributed (Rule 10 zero-value check passed — 0.00 would have been a failed gate)",
        "MONITOR: Rule 8 teeth open 14:30 ET — 7 zero-fill agents on watchlist, one forced reprice each if legs still resting",
    ],
    "strikes": 0,
    "rejections": 0,
    "warnings": 0,
    "fills_today": 6,
    "fills_detail": [
        "agent-07 XLU260904P00042000 BTO 1 @0.04 (hard exit wire)",
        "ar-cleanup agent-21 XLF260918P00055500 BTO 1 @0.19",
        "ar-cleanup agent-23 XLF260918P00055500 BTO 1 @0.19",
        "ar-cleanup agent-22 XLF260918P00055000 BTO 1 @0.13",
        "ar-cleanup agent-25 XLU260918P00041000 BTO 1 @0.13",
        "ar-cleanup agent-26 XLU260918P00041000 BTO 1 @0.13",
    ],
}

with open(LOG) as f:
    log = json.load(f)
log["polls"].append(poll)
with open(TMP, "w") as f:
    json.dump(log, f, indent=1)
os.rename(TMP, LOG)
print(f"logged poll -> {LOG} (now {len(log['polls'])} polls today)")