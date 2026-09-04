#!/usr/bin/env python3
"""Finalize trade_plans_D5.json: per-agent backtest summaries, Sterling tranche 1
re-anchor, Roy plan_step_2; append gauntlet-final note to the message board."""
import json, time
from pathlib import Path

STATE = Path("/mnt/agent_share/gordon/hackathon/state")
plans = json.load(open(STATE / "trade_plans_D5.json"))
assert len(plans) == 10, len(plans)

SUM_XLF = ("CSP family rerun (Wed night, 129 bars): +5.61% vs B&H +12.37%, 6 round trips, "
           "100% win, MDD 0.00%, Sharpe 3.50 \u2014 validated five consecutive sessions.")
SUM_XLU = ("CSP family rerun (Wed night, 129 bars): +2.11% vs B&H \u22129.95%, 6 round trips, "
           "100% win, MDD \u22121.41%, Sharpe 1.00 \u2014 the family trade beats the benchmark "
           "by 12 points in the defensive tape. Validated five consecutive sessions.")

for aid in ("agent-28", "agent-29", "agent-30"):
    plans[aid]["backtest_summary"] = SUM_XLF
for aid in ("agent-31", "agent-32", "agent-33"):
    plans[aid]["backtest_summary"] = SUM_XLU

plans["agent-34"]["legs"][0]["note"] = (
    "TRANCHE 1 AT GAP GATE: SPY 9/18 735/725 put credit spread at the LIVE net mid "
    "(night shelf nets ~0.57: 735P last 1.64, 725P last 1.07). RE-ANCHORED from the 1.30 est "
    "\u2014 the 6PM estimate died at the 4PM shelf. Floor 0.60: under it no legal premium exists, "
    "sit flat (the law outranks the quota). Short leg delta \u22120.122, legal under the 0.20 law. "
    "MAX LOSS $870/lot priced before the open. Rule-8 engagement floor satisfied by EXECUTION."
)
plans["agent-33"]["plan_step_2_if_rejected_alpaca"] = (
    "liquidity fail at 41.5P -> cancel, refile XLU 9/18 41.5P @ live bid by 13:30; "
    "still nothing by 15:45 -> Rule 8 fallback files at live mid; HARD review governs, "
    "no roll into NFP"
)
plans["agent-33"]["note_fixcheck"] = "reassigned 9/4 42.5P -> 9/18 41.5P per Richard D5 (delta law)"

with open(STATE / "trade_plans_D5.json", "w") as f:
    json.dump(plans, f, indent=2)

# board note
board = json.load(open(STATE / "messageboard_20260902.json"))
ts = time.time()
board.append({
    "id": f"msg-{int(ts)}-gflt",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S-04:00"),
    "from": "gordo",
    "to": "all",
    "type": "gauntlet_final",
    "re": "trade_plans_D5",
    "message": (
        "D5 GAUNTLET FINAL 19:45 ET \u2014 trade_plans_D5.json, richard_memo_D5.md, "
        "charlie_memo_D5.md are LAW. Two changes from the 6PM draft, both chain-caught: "
        "(1) Roy Levene reassigned off the 9/4 42.5P weekly (live delta \u22120.369, over the "
        "0.20 law; no legal retreat on the 9/4 shelf) to the monthly XLU 9/18 41.5P @ "
        "max(bid, 0.12); (2) Sterling's spread re-anchored to the LIVE net mid with a 0.60 "
        "floor \u2014 the 1.30 estimate was stale, tranche 2 GTC 1.55 stands. All 7 new-leg "
        "combos backtest-validated tonight; 0 overrides. Cards file at the 9:35 gap gate; "
        "Rule 8 clock arms 14:30; NFP Friday governs everything \u2014 no fresh legs after "
        "Thursday 15:45. The floor pays for exposure, not for presence."
    ),
    "read": False,
})
with open(STATE / "messageboard_20260902.json", "w") as f:
    json.dump(board, f, indent=2)

# verification
chk = json.load(open(STATE / "trade_plans_D5.json"))
print("plans:", len(chk), "| agents:", sorted(chk.keys()))
print("roy contract:", chk["agent-33"]["legs"][0]["symbol_or_contract"],
      "| limit:", chk["agent-33"]["legs"][0]["limit_price"])
print("sterling t1 note head:", chk["agent-34"]["legs"][0]["note"][:80])
print("board msgs:", len(json.load(open(STATE / "messageboard_20260902.json"))))
req = ("agent_id", "agent_name", "strategy", "symbol", "legs", "stop_loss",
       "profit_target", "sizing_explanation_in_their_voice", "backtest_summary",
       "client_order_id_template")
missing = {a: [k for k in req if k not in v] for a, v in chk.items() if any(k not in v for k in req)}
print("missing fields:", missing or "NONE")