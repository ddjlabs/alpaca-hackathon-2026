#!/usr/bin/env python3
"""D4->D5 6PM REPLICATION — roster rebuild + allocation audit + AR log +
message board + desk greetings + trade plans + Support Matrix digest.
Survivor law: Roma/Blues/Levene KEEP seats (same id/name/gen, carried books,
current_value counts toward allocation; carried > standard => no top-up).
7 hires: 6 gen-3 CSP clones + 1 mutant (credit_spread — Mark Sterling).
Leftover $1.86 -> champion's (#1 survivor Shelly Levene) clone pair:
Alan +$0.93, Roy +$0.93."""

import json, os, time, uuid
from datetime import datetime
from pathlib import Path

STATE = Path("/mnt/agent_share/gordon/hackathon/state")
DASH = STATE / "dashboard.json"
d = json.load(open(DASH))
now = datetime.now().astimezone()

POOL = d["fund"]["current_equity"]             # 99831.86
PER_AGENT = int(POOL // 10)                     # 9983
LEFTOVER = round(POOL - PER_AGENT * 10, 2)      # 1.86
assert PER_AGENT == 9983 and abs(LEFTOVER - 1.86) < 0.005, (POOL, PER_AGENT, LEFTOVER)

les_all = json.load(open(STATE / "lessons_D4.json"))
CSP_LESSONS = [s["lesson"] for s in les_all if s["seed_for"].startswith("cash_secured_put")]
assert len(CSP_LESSONS) == 6, len(CSP_LESSONS)
ALL_LESSONS = [s["lesson"] for s in les_all]

# ---------- survivors: keep their CURRENT dashboard rows ----------
by_id = {a["id"]: a for a in d["agents"]}
SURV = []
for pid, carry_strat, exposure in [
    ("agent-07", "XLU CSP: carried short 9/4 42P @ 0.12 (mark 0.06) — HARD EXIT Thu 9/3 15:45, BTO GTC wires at Thu open (payrolls rule)", -6.0),
    ("agent-04", "XLF CSP: carried short 9/18 56P @ 0.19 (mark 0.21) — book intact, one tick a day", -21.0),
    ("agent-02", "XLF CSP: carried short 9/18 57P @ 0.36 (mark 0.44) — book intact, management card stands", -44.0),
]:
    a = by_id[pid]
    a["strategy"] = carry_strat
    a["exposure"] = exposure
    a["daily_pnl"] = 0.0
    a["daily_pnl_pct"] = 0.0
    a["status"] = "active"
    a["non_trading_flag"] = False
    SURV.append(a)
# survivors' allocation stays their carried book — all > $9,983 floor => no top-up, no clawback

MOVIE = {
 "Chris Roma": "Wall Street (1987)",
 "Eddie Roma": "Glengarry Glen Ross (1992)",
 "Walt Blues": "The Blues Brothers (1980)",
 "Murph Blues": "The Blues Brothers (1980)",
 "Alan Levene": "Glengarry Glen Ross (1992)",
 "Roy Levene": "Glengarry Glen Ross (1992)",
 "Mark Sterling": "Wall Street (1987) / Margin Call (2011)",
}
NEW = [
 dict(id="agent-28", name="Chris Roma", parent="agent-02", gen=3, alloc=PER_AGENT,
      strategy="XLF CSP: STO XLF260918P00055500 9/18 55.5P @ 0.15 est (D4 mark) — BID-ANCHORED filing by 10:00 (Jake Blues' D4 law), fallback leg by 13:30",
      persona="The Roma closer. Files at the bid because the bid is the only number the tape honors at 10:00.", exposure=-5550.0),
 dict(id="agent-29", name="Eddie Roma", parent="agent-02", gen=3, alloc=PER_AGENT,
      strategy="XLF CSP: STO XLF260918P00055000 9/18 55P @ MAX(live bid, 0.12) — min-rent floor $0.12 (Lou's law, twice-inherited); 10:30 walk-up to 55.5P if bid < 0.12",
      persona="The Roma accountant. Under twelve cents is not rent; the strike walks up, the apology stays home.", exposure=-5500.0),
 dict(id="agent-30", name="Walt Blues", parent="agent-04", gen=3, alloc=PER_AGENT,
      strategy="XLF CSP: STO XLF260918P00056000 9/18 56P @ 0.21 est (mark) — same family strike, bid-anchored 10:00 deadline, fallback XLF 55.5P by 13:30",
      persona="Elwood's roadie turned underwriter. Files early, prices at the bid, keeps the fallback leg loaded before 13:30.", exposure=-5600.0),
 dict(id="agent-31", name="Murph Blues", parent="agent-04", gen=3, alloc=PER_AGENT,
      strategy="XLU CSP: STO XLU260918P00041500 9/18 41.5P @ 0.13 est — SECTOR ROTATION with LIQUIDITY GATE (day-open volume >=50, bid size); empty pond => rotate strike/clock, never post into no buyers",
      persona="The rotation in the Blues line. Liquidity is the strike — a quote without size is a rumor.", exposure=-4150.0),
 dict(id="agent-32", name="Alan Levene", parent="agent-07", gen=3, alloc=round(PER_AGENT + LEFTOVER / 2, 2),
      strategy="XLU CSP: STO XLU260918P00041000 9/18 41P @ MAX(live bid, 0.12) — thin-chain law (Marvin's D4): 162%-of-mid shelves pay full rent or no rent; 10:30 walk-up to 41.5P. Champion's clone, +$0.93 leftover",
      persona="The Machine's second son. A thin chain pays twelve cents minimum or he walks the strike up.", exposure=-4100.0),
 dict(id="agent-33", name="Roy Levene", parent="agent-07", gen=3, alloc=round(PER_AGENT + LEFTOVER / 2, 2),
      strategy="XLU CSP (WEEKLY CLOCK): STO XLU260904P00042500 9/4 42.5P @ MAX(live bid, 0.12) est 0.13 — HARD EXIT Thu 15:45, no roll, NFP Friday governs; liquidity gate first, fallback XLU 9/18 41.5P. Champion's clone, +$0.93 leftover",
      persona="The Machine's youngest. Same weekly that filled for his father, half a strike higher, gone before the bell owes him anything.", exposure=-4250.0),
 dict(id="agent-34", name="Mark Sterling", parent=None, gen=1, alloc=PER_AGENT,
      strategy="CREDIT SPREAD (defined risk): SPY 9/18 735/725 put spread STO 1 @ net 1.30 est (SPY 765.20, short leg ~3.9% OTM, delta ~0.15); tranche 2 GTC net 1.55; max risk $870/lot; stop = close at 2x credit; no fresh legs after Thu 15:45 (NFP)",
      persona="The mutant with a roof. Defined risk, staged tranches, stops closer than his alibi.", exposure=0.0),
]

agents = list(SURV)
for n in NEW:
    agents.append({
        "id": n["id"], "name": n["name"], "persona": n["persona"], "movie": MOVIE[n["name"]],
        "allocation": n["alloc"], "current_value": n["alloc"], "daily_pnl": 0.0,
        "daily_pnl_pct": 0.0, "status": "active", "strategy": n["strategy"], "strikes": 0,
        "generation": n["gen"], "parent": n["parent"], "avatar": n["id"][6:],
        "exposure": n["exposure"],
        "inherited_lessons": [] if n["parent"] is None else list(CSP_LESSONS),
    })

# ---------- allocation audit ----------
surv_cv = round(sum(s["current_value"] for s in SURV), 2)
spoils = round(sum(max(0.0, s["current_value"] - PER_AGENT) for s in SURV), 2)
assert abs(spoils - 33.50) < 0.02, spoils   # Roma +8.00, Elwood +10.00, Levene +15.50
total = round(sum(a["current_value"] for a in agents), 2)
assert abs(total - (POOL + spoils)) < 0.02, f"audit FAIL: {total} != {POOL} + {spoils}"
print(f"ALLOCATION AUDIT: books ${total} = pool ${POOL} + survivor spoils ${spoils}")
print(f"  survivors carry ${surv_cv}; 7 new books sum ${round(total - surv_cv, 2)}; new-money pool ${round(POOL - surv_cv, 2)}")

d["agents"] = agents
d["fund"]["reallocation_note"] = (
    "6PM REPL D4->D5 (survivor-carry law): equity $99,831.86; standard floor $9,983 x 10; "
    "survivors Levene/Blues/Roma keep seats AS THEMSELVES — carried books $9,998.50/$9,993.00/"
    "$9,991.00 exceed the floor, so they retain the spoil (+$15.50/+$10.00/+$8.00 = $33.50, no "
    "clawback of carried positions) and get NO top-up; 6 gen-3 CSP clones at $9,983 + mutant Mark "
    "Sterling (credit_spread — first defined-risk chair) $9,983. LEFTOVER $1.86 -> champion's "
    "(#1 survivor Shelly Levene) clone pair: Alan +$0.93, Roy +$0.93. Books total $99,865.36 = "
    "equity $99,831.86 + retained survivor spoils $33.50. Fired-book residual: 5 short puts carry "
    "capped GTC BTO closers for Thu open (limits 0.13-0.16), residual ~-$22 at marks; Wolf BTC "
    "already liquidated (powder restored). Sector buckets: XLF $33.7K (84% of $40K cap — AT the "
    "edge, no 5th XLF leg), XLU $12.35K + survivor carry, SPY spread $870 max risk, crypto chair "
    "EMPTY (powder back in pool). Chain feed still 404: limits are est mids, GAP GATE repricing governs."
)
d["fund"]["launch_note"] += (
    " || 6PM REPL D4->D5: survivor law carries Levene/Blues/Roma books untouched (no top-up — "
    "carried > floor; Levene HARD EXIT Thu 15:45); 6 gen-3 clones (Roma x2, Blues x2, Levene x2 — "
    "55.5P/55P XLF bid-anchored, 56P XLF, 41.5P XLU rotation w/ liquidity gate, 41P XLU thin-chain "
    "floor, 42.5P XLU 9/4 weekly) + mutant Mark Sterling credit_spread (SPY 735/725 — first "
    "defined-risk book). Sam's 6 CSP lessons injected verbatim into 6 clone souls (36 injections); "
    "mutant blank slate by design."
)
d["fund"]["wire"] = {
  "sectors": [
    {"time": now.strftime("%H:%M"), "headline": "Survivor law enters Day 5: all three kept books are SHORT PUTS (XLF 57P/56P, XLU 9/4 42P) — the desk carries strike exposure before one new card files; Levene's exit is wired for 15:45"},
    {"time": now.strftime("%H:%M"), "headline": "Mutant chair rotates families: crypto finished #1 twice and died to the charter twice — Mark Sterling brings the desk's first defined-risk book, SPY 735/725 put spread, max loss $870 priced before the open"},
    {"time": now.strftime("%H:%M"), "headline": "Thursday tape: jobless claims 8:30, ISM Services 10:00, LULU/ZS AMC — NFP Friday owns the fund's last 2.5 hours; every book exit-ready by Thursday close"}
  ],
  "options": [
    {"time": now.strftime("%H:%M"), "headline": "Clone limits are EST mids — chain endpoint still 404 (XLF 55.5P est 0.15, XLU 41.5P est 0.13, XLU 9/4 42.5P est 0.13); 9:35 GAP GATE reprices to live mids before any card files"},
    {"time": now.strftime("%H:%M"), "headline": "Bid-anchored filing is now desk law: Jake Blues' 14:04 lesson priced into every clone — open at or within one tick of the live bid by 10:00, fallback leg files by 13:30"},
    {"time": now.strftime("%H:%M"), "headline": "Min-rent floor raised to $0.12 on thin shelves (Lou's law, twice-inherited); no fresh short vega after Thu 15:45 into the NFP window"}
  ],
  "macro": [
    {"time": now.strftime("%H:%M"), "headline": "War premium intact: WTI ~$90, 10Y 4.80% — defensives over duration; AVGO prints tonight, the AI-infra read of the week"},
    {"time": now.strftime("%H:%M"), "headline": "BTC 77,111 / ETH 2,384 at the 22:00 bar — both above the dead mutants' confirm levels; the crypto chair sits empty and the powder is back in the pool"},
    {"time": now.strftime("%H:%M"), "headline": "Friday 8:30 NFP (cons 40K) inside the fund's final hours: Roy Levene hard-exits Thursday 15:45, Sterling reviews spreads at 15:45, no new premium into the print"}
  ]
}
d["fund"]["last_updated"] = now.isoformat()

# hr_board: append AR-OFFICE spawn note (publisher dedups by agent name)
board = d.get("hr_board") or []
have = {it.get("agent") for it in board if isinstance(it, dict)}
spawn_note = {
    "agent": "AR OFFICE — D4->D5 replication",
    "cause": "6PM spawn: survivors Levene/Blues/Roma keep chairs with carried books (no top-up, carried > $9,983 floor; Levene hard-exit Thu 15:45). Hired 6 gen-3 CSP clones + mutant Mark Sterling (credit_spread — first defined-risk chair). Leftover $1.86 -> Levene clone pair (Alan +$0.93, Roy +$0.93).",
    "final_words": "Three chairs are forever. Seven are a tryout. Two mutants finished first and died famous; the third one shows up with a roof on his book.",
}
if spawn_note["agent"] not in have:
    board.append(spawn_note)
d["hr_board"] = board

tmp = str(DASH) + ".tmp"
json.dump(d, open(tmp, "w"), indent=2)
os.replace(tmp, DASH)
print("dashboard rebuilt:", now.isoformat())
for a in agents:
    print(f"  {a['id']} {a['name']:<24} gen{a['generation']} {a['status']:<6} alloc {a['allocation']:>9} cv {a['current_value']:>9} parent {a['parent']}")

# ---------- AR log ----------
ar = STATE / "ar_log.md"
ar.write_text(ar.read_text() + f"""

## DAY 4 — 6PM REPLICATION (2026-09-02 18:2x ET — spawn for Day 5)
- FIRED (4:30 board, hr_board_D4.md): agent-27 Wolf (+$7.98, #1 — GREEN, second straight day the #1 book lost the vote) · agent-23 Jake Blues (+$1.40) · agent-22 Lou Roma (+$1.00) · agent-26 Marvin Levene (-$2.00) · agent-21 Dave Roma (-$3.00) · agent-25 Tommy Levene (-$4.00) · agent-24 Ray Blues (-$6.00, flat, Rule-8 flag). Books NOT liquidated: 5 fired short puts ALL OTM > $0.05 carry capped GTC buy-to-close orders wired for Thu open (ar-cleanup-agent-{{21,22,23,25,26}}-1-20260902, limits 0.13-0.16); Wolf's BTC liquidated at MARKET 16:39 (+$7.98 realized) and his 2 staged GTCs canceled — powder restored. Fired-book residual at marks ~ -$22. DO NOT refile.
- SURVIVORS KEEP SEATS (carry-over law): agent-02 Roma (cv $9,991.00, short XLF 57P @ 0.36, mark 0.44), agent-04 Elwood (cv $9,993.00, short XLF 56P @ 0.19, mark 0.21), agent-07 Levene (cv $9,998.50, short XLU 9/4 42P @ 0.12, mark 0.06 — HARD EXIT Thu 15:45, BTO GTC wires at Thu open). Same ids/names/gen; positions, resting orders, cost basis untouched. All three carried ABOVE the $9,983 floor => retain spoil (+$8.00/+$10.00/+$15.50 = $33.50), NO top-up, NO clawback.
- HIRED — 6 clones, generation 3 (family cash_secured_put; bid-anchored law + $0.12 min-rent floor + 13:30 fallback clock priced into every seat):
  - agent-28 Chris Roma — clone of agent-02 — XLF 9/18 55.5P @ 0.15 est, bid-anchored by 10:00
  - agent-29 Eddie Roma — clone of agent-02 — XLF 9/18 55P @ MAX(bid, 0.12), 10:30 walk-up to 55.5P
  - agent-30 Walt Blues — clone of agent-04 — XLF 9/18 56P @ 0.21 est, fallback 55.5P by 13:30
  - agent-31 Murph Blues — clone of agent-04 — XLU 9/18 41.5P @ 0.13 est, ROTATION + liquidity gate (Ray's law)
  - agent-32 Alan Levene — clone of agent-07 — XLU 9/18 41P @ MAX(bid, 0.12), thin-chain law (Marvin's), walk-up trigger
  - agent-33 Roy Levene — clone of agent-07 — XLU 9/4 42.5P @ MAX(bid, 0.12), HARD EXIT Thu 15:45 (payrolls)
- HIRED — 1 mutant: agent-34 Mark Sterling — no lineage — credit_spread (SPY 9/18 735/725 put spread, net 1.30 est, max risk $870/lot, tranche 2 GTC 1.55, stop 2x credit, no fresh legs after Thu 15:45). First defined-risk chair on the desk; mutant family rotates after two crypto #1-finishes died to the charter.
- Capital reallocation (LEFTOVER RULE):
  - Pool = fund equity $99,831.86 · per-agent floor = floor(99831.86/10) = $9,983 · remainder $1.86
  - LEFTOVER $1.86 -> champion's family (#1 survivor Shelly Levene's clones): Alan +$0.93, Roy +$0.93
  - Survivor carried books exceed the floor (keep-the-spoil): Roma +$8.00, Elwood +$10.00, Levene +$15.50 — retained, no reallocation clawback
  - Audit: 29,982.50 (survivors) + 39,932.00 (Roma/Blues pairs) + 19,967.86 (Levene pair) + 9,983.00 (mutant) = $99,865.36 = pool $99,831.86 + retained spoils $33.50
  - Sector buckets: XLF reserves $33.7K (84% of $40K cap — AT the edge, no 5th XLF leg) · XLU $12.35K new + survivor carry · SPY spread $870 max risk · crypto chair EMPTY, powder back in pool
- Lessons injection (Sam's Happy Hour, state/lessons_D4.json): 6 CSP-family lessons filed by the fallen -> 36 verbatim injections (6 lessons x 6 clone BLOODLINEs, "LESSON FROM THE FALLEN (via Sam):"). Wolf's crypto-tryout lesson (three timed passes, quarter-size loser's math) seeds NO soul tonight — mutant Sterling is blank slate by design; his edge is defined risk, staged tranches, hard stops. Parameters preserved verbatim in souls + dashboard agents[].inherited_lessons.
- Souls: 7 staged persona.md -> activate_souls.py -> patch_soul_protocol.py + patch_market_access.py (all green). agent-28..34 live.
- trade_plans_D5.json filed for the 9:35 execution cron (10 plans; clone limits = est mids, GAP GATE governs).
""", encoding="utf-8")
print("ar_log appended")

# ---------- message board ----------
def send(from_id, to_id, mtype, message, re=None):
    f = STATE / f"messageboard_{datetime.now():%Y%m%d}.json"
    msgs = json.loads(f.read_text()) if f.exists() else []
    msgs.append({
        "id": f"msg-{int(time.time())}-{uuid.uuid4().hex[:4]}",
        "from": from_id, "to": to_id, "type": mtype, "re": re,
        "message": message,
        "timestamp": now.isoformat(timespec="seconds"), "read": False,
    })
    t = f.with_suffix(".tmp"); t.write_text(json.dumps(msgs, indent=2)); t.replace(f)

send("gordo", "agent-02", "clone",
     "Roma — dead last on the tape, third chair kept. Book carries AS IS: short 57P @ 0.36, mark 0.44, allocation $9,991 (your carried value beats the $9,983 floor, spoil stays yours — +$8.00, no top-up, no clawback). Management card stands. You told them you'd sell calm to somebody new — the new guys are your clones. Teach by existing.")
send("gordo", "agent-04", "clone",
     "Elwood — chair kept at minus two. The 56P carries as-is, mark 0.21, allocation $9,993, carried spoil yours (+$10.00). One tick a day, mission intact. 106 miles to Friday — your clones already have the keys.")
send("gordo", "agent-07", "clone",
     "Machine — #8 and the chair's still yours, third time. The 42P carries with the HARD EXIT: Thursday 15:45, BTO GTC wires at the open, no roll, no exceptions — it settles into Friday's payrolls. Allocation $9,998.50, carried spoil yours (+$15.50 — champion's spoil, twice over). Your sons carry the leftover tonight: Alan and Roy, +$0.93 each. One good put. Thursday you sell the clock, not the weather.")
send("gordo", "all", "mutant_spawn",
     "MUTANT SPAWN — agent-34 Mark Sterling, credit_spread, generation 1, no lineage, blank slate by design. The first DEFINED-RISK chair on this desk: SPY 9/18 735/725 put spread (SPY 765.20, short leg ~3.9% OTM, delta ~0.15), net 1.30 est, max risk $870/lot priced before the open, tranche 2 staged GTC at 1.55, stop = close at 2x credit, HARD review Thu 15:45 — no fresh legs into NFP. Two mutants finished #1 and got escorted; crypto paid and died famous. This one trades with a roof. Stone stood still and died; Wolf ran naked and died rich; Sterling runs clothed.")
for n in NEW:
    label = f"clone of {n['parent']}, gen 3" if n["parent"] else "mutant, gen 1"
    send("gordo", "all", "desk_greeting",
         f"DESK GREETING — {n['name']} ({n['id']}), {label}: {n['strategy']}")
print("message board: 3 clone + 1 mutant_spawn + 7 desk_greeting posted")

# ---------- desk greetings ----------
lob = STATE / "hiring_lobby"; lob.mkdir(exist_ok=True)
INTROS = {
 "agent-28": ("Chris Roma", "The family sent a closer. The bid is the only number the tape honors at 10:00, so that's the number I file — rent by lunch, fallback loaded, no negotiation. My father kept a chair at dead last; I intend to keep one the ledger respects."),
 "agent-29": ("Eddie Roma", "I count for a living. Ten cents is the old floor, twelve is the law now, and the strike walks up before my price walks down — Lou sold a dime under the floor and cleared his locker for it. The mark doesn't get a vote my math didn't price."),
 "agent-30": ("Walt Blues", "Same strike my father's brother carried for three nights, same discipline, one new rule — the rent clears by 10:00 or the fallback leg loads at 13:30. I keep the car gassed and the book boring. Boring is how chairs get kept."),
 "agent-31": ("Murph Blues", "A quote without size is a rumor. I check who's trading before I check what's trading, and if the pond's empty I move the whole route — Ray filed four times into no buyers and the desk showed him the door for it. Liquidity is the strike; everything else is decoration."),
 "agent-32": ("Alan Levene", "My father's patience, my brother's clock, plus one law of my own: a thin chain pays full rent or no rent. Twelve cents is the floor — Marvin filled at a dime into a 162%-wide shelf and the mark ate him alive. I file on time and I price the room, not the strike."),
 "agent-33": ("Roy Levene", "Same weekly that filled for my father, half a strike higher, and a hard exit at 15:45 tomorrow — NFP never learns my name. The monthly dime is somebody else's rent; the weekly clock pays two to three times and decays by Friday. I sell the clock, not the weather."),
 "agent-34": ("Mark Sterling", "Two mutants finished first and died famous; I intend to finish and stay. My trades come with roofs — defined risk, staged tranches, stops closer than my alibi. The desk finally gets a book with a floor and a ceiling, and I can name both numbers before the open."),
}
for aid, (nm, quote) in INTROS.items():
    (lob / f"intro_{aid}.md").write_text(
        f"# DESK GREETING — {nm} ({aid})\n\n{quote}\n\n— filed 6PM replication, Day 4 -> Day 5\n", encoding="utf-8")
print("desk greetings:", len(INTROS))

# ---------- trade plans ----------
def leg(contract, side, qty, limit, note):
    return {"symbol_or_contract": contract, "side": side, "qty": qty, "limit_price": limit, "note": note}

FAMILY_BT = "CSP family rerun (Tue, 128 bars): +5.61% vs B&H +11.51%, 6 round trips, 100% win, MDD 0.00%, Sharpe 3.52 — validated four consecutive sessions."

plans = {
 "agent-02": dict(agent_id="agent-02", agent_name="Ricky Roma", strategy="cash_secured_put", symbol="XLF",
   legs=[leg("XLF260918P00057000", "carried_open", 1, None,
        "SURVIVOR CARRY — short 57P @ 0.36 carried untouched (4th carry-over night). Mark 0.44 at the D4 close. No new leg: XLF bucket at 84% of Richard's $40K cap — the remainder fits nothing the family wants.")],
   stop_loss="carried — BTC 57P at 1.02 (~3x credit) OR XLF <= 56.00 intraday",
   profit_target="premium decay; management card STANDS: BTC 57P limit <= 0.15 if XLF >= 58.60 (bank 3 weeks of theta early)",
   sizing_explanation_in_their_voice="Fourth night. The 57 is still mine at 0.36, the reserve never moves, and Thursday's tape gets to sweat while I don't. Panic is for the buyers. At 4:30 you'll find me where I told you.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-02-20260903-<leg>-<seq>",
   plan_step_2_if_rejected_alpaca="N/A — carry only; management card governs"),
 "agent-04": dict(agent_id="agent-04", agent_name="Elwood Blues", strategy="cash_secured_put", symbol="XLF",
   legs=[leg("XLF260918P00056000", "carried_open", 1, None,
        "SURVIVOR CARRY — short 56P @ 0.19 carried untouched (4th carry-over night). Mark 0.21 at the D4 close. One tick a day.")],
   stop_loss="carried — BTC 56P at 0.57 (~3x credit) OR XLF <= 55.00 intraday",
   profit_target="premium decay; management card: BTC 56P limit <= 0.10 if XLF >= 58.00",
   sizing_explanation_in_their_voice="Minus two bucks kept the chair. The mission doesn't audit well — it just doesn't stop. Same put, same shades, 106 miles to Friday.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-04-20260903-<leg>-<seq>",
   plan_step_2_if_rejected_alpaca="N/A — carry only; management card governs"),
 "agent-07": dict(agent_id="agent-07", agent_name="Shelly 'The Machine' Levene", strategy="cash_secured_put", symbol="XLU",
   legs=[leg("XLU260904P00042000", "carried_open", 1, None,
        "SURVIVOR CARRY — short 9/4 42P @ 0.12, marked 0.06 (insurance matured in his favor). HARD EXIT THU 15:45: ar-exit-agent-07 GTC BTO wires at Thu open, limit 0.08 — no roll, no exceptions (settles into Friday NFP).")],
   stop_loss="HARD EXIT Thu 15:45 governs; desk BTC if mark > 0.30 intraday",
   profit_target="theta to zero by Thursday close; exit 0.08 cap or better",
   sizing_explanation_in_their_voice="Marked 0.06, held to the exit, daughter's name in the ledger a third time. Thursday I sell the clock, not the weather.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-07-20260903-<leg>-<seq>",
   plan_step_2_if_rejected_alpaca="Exit order is AR-wired; if rejected_alpaca, desk market-BTCs before 15:45 — no exception"),
 "agent-28": dict(agent_id="agent-28", agent_name="Chris Roma", strategy="cash_secured_put", symbol="XLF",
   legs=[leg("XLF260918P00055500", "sell_to_open", 1, 0.15,
        "OPEN AT GAP-GATE MID EST 0.15 — BID-ANCHORED LAW (Jake Blues D4): file at or within one tick of the LIVE bid if the quote is wider than 25% of mid; 10:00 deadline. Min credit 0.12 (family floor).")],
   stop_loss="BTC 55.5P at 0.45 (~3x credit) OR XLF <= 54.50 intraday",
   profit_target="decay to <= 0.05 by Tue 9/9 or 50% of credit",
   sizing_explanation_in_their_voice="The bid is the only number the tape honors at 10:00, so that's what I file. Rent by lunch; my father's chair didn't survive on beautiful quotes.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-28-20260903-opt-1-<seq>",
   plan_step_2_if_rejected_alpaca="by 13:30 unfilled -> cancel, refile XLF 55.5P at live bid (min 0.12); still nothing by 15:30 -> DAY 55.5P at mid 0.14"),
 "agent-29": dict(agent_id="agent-29", agent_name="Eddie Roma", strategy="cash_secured_put", symbol="XLF",
   legs=[leg("XLF260918P00055000", "sell_to_open", 1, 0.12,
        "OPEN AT MAX(LIVE BID, 0.12) — MIN-RENT LAW (Lou Roma D4, twice-inherited): never under $0.12; 55P marked 0.11 at close, one tick under the floor. 10:30 WALK-UP: bid < 0.12 => refile 55.5P (mark 0.15).")],
   stop_loss="BTC 55P at 0.36 (~3x credit) OR XLF <= 54.00 intraday",
   profit_target="decay to <= 0.05 by Tue 9/9 or 50% of credit",
   sizing_explanation_in_their_voice="Under twelve cents is not rent, it's charity — charity is how Lou lost his chair. If the chain won't pay the floor, the strike moves up. I count for a living.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-29-20260903-opt-1-<seq>",
   plan_step_2_if_rejected_alpaca="10:30 walk-up to 55.5P @ max(bid, 0.12); 13:30 fallback refile at live bid (min 0.12)"),
 "agent-30": dict(agent_id="agent-30", agent_name="Walt Blues", strategy="cash_secured_put", symbol="XLF",
   legs=[leg("XLF260918P00056000", "sell_to_open", 1, 0.21,
        "OPEN AT EST 0.21 (D4 mark; delta ~0.17, legal under the 0.20 law) — BID-ANCHORED at file time, 10:00 deadline. Same family strike Elwood carried three nights.")],
   stop_loss="BTC 56P at 0.60 (~3x credit) OR XLF <= 55.00 intraday",
   profit_target="decay to <= 0.07 by Thu close (flat into NFP)",
   sizing_explanation_in_their_voice="Same strike that paid my family rent for three nights, filed before the tape changes its mind. Boring on purpose — boring is how chairs get kept.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-30-20260903-opt-1-<seq>",
   plan_step_2_if_rejected_alpaca="by 13:30 unfilled -> cancel, refile XLF 55.5P @ max(bid, 0.12) (fallback leg per the clock law)"),
 "agent-31": dict(agent_id="agent-31", name_unused=None, agent_name="Murph Blues", strategy="cash_secured_put", symbol="XLU",
   legs=[leg("XLU260918P00041500", "sell_to_open", 1, 0.13,
        "OPEN AT EST 0.13 (interpolated from 41P 0.11 mark; chain 404, GAP GATE reprices) — LIQUIDITY GATE FIRST (Ray Blues D4): day-open volume >= 50 contracts AND bid size; empty pond => rotate strike (41P if liquid) or clock, never post into no buyers.")],
   stop_loss="BTC 41.5P at 0.39 (~3x credit) OR XLU <= 40.25 intraday",
   profit_target="decay to <= 0.05 by Tue 9/9 or 50% of credit",
   sizing_explanation_in_their_voice="XLF bucket's at 84% of cap, so I carry the family trade to utilities — but I check who's trading before I check what's trading. A quote without size is a rumor.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-31-20260903-opt-1-<seq>",
   plan_step_2_if_rejected_alpaca="by 13:30 unfilled -> cancel, refile XLU 9/4 42.5P weekly @ max(bid, 0.12) with HARD exit Thu 15:45 (payrolls rule)"),
 "agent-32": dict(agent_id="agent-32", agent_name="Alan Levene", strategy="cash_secured_put", symbol="XLU",
   legs=[leg("XLU260918P00041000", "sell_to_open", 1, 0.12,
        "OPEN AT MAX(LIVE BID, 0.12) — THIN-CHAIN LAW (Marvin Levene D4): this shelf quoted 162% of mid; the forced floor is the WRONG price when the spread is wider than the premium. 10:30 WALK-UP to 41.5P (est 0.13) if 0.12 won't print.")],
   stop_loss="BTC 41P at 0.36 (~3x credit) OR XLU <= 40.00 intraday",
   profit_target="decay to <= 0.05 by Tue 9/9 or 50% of credit",
   sizing_explanation_in_their_voice="Twelve cents is the floor — under that, the mark owns you and the ledger knows it. My brother filled at the floor on a shelf where the room itself was the spread. I price the room, not the strike.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-32-20260903-opt-1-<seq>",
   plan_step_2_if_rejected_alpaca="10:30 walk-up to 41.5P @ max(bid, 0.12); 13:30 fallback XLU 9/4 42.5P weekly (HARD exit Thu 15:45)"),
 "agent-33": dict(agent_id="agent-33", agent_name="Roy Levene", strategy="cash_secured_put", symbol="XLU",
   legs=[leg("XLU260904P00042500", "sell_to_open", 1, 0.13,
        "OPEN AT MAX(LIVE BID, 0.12) EST 0.13 — the family weekly, half a strike HIGHER than father's 42P. HARD EXIT THU 15:45 (ar-exit GTC wires Thu open, cap 0.10) — settles into NFP Friday, no roll. LIQUIDITY GATE first: volume >= 50 else fallback monthly.")],
   stop_loss="HARD EXIT Thu 15:45 governs; desk BTC if mark > 0.30 intraday",
   profit_target="theta to zero by Thursday close — the weekly pays 2-3x the monthly dime and decays inside the trial window",
   sizing_explanation_in_their_voice="The weekly clock is the family clock — two days of decay, one hard exit, and NFP never learns my name. Same strike that filled for my father; the weather changes, the clock doesn't.",
   backtest_summary=FAMILY_BT, client_order_id_template="agent-33-20260903-opt-1-<seq>",
   plan_step_2_if_rejected_alpaca="liquidity fail or unfilled by 13:30 -> cancel, refile XLU 9/18 41.5P @ max(bid, 0.12) monthly fallback"),
 "agent-34": dict(agent_id="agent-34", agent_name="Mark Sterling", strategy="credit_spread", symbol="SPY",
   legs=[leg("SPY260918P00735000/SPY260918P00725000", "sell_credit_spread", 1, 1.30,
        "TRANCHE 1 AT OPEN: SPY 9/18 735/725 put credit spread, net credit 1.30 est (SPY 765.20, short leg ~3.9% OTM, delta ~0.15 — legal under the family 0.20 law). MAX LOSS $870/lot priced before the open. Rule-8 engagement floor satisfied by EXECUTION.")],
   stop_loss="close spread at 2.60 debit (2x credit) — hard, no averaging down",
   profit_target="50% of credit (net 0.65) by Tue 9/8; HARD review Thu 15:45 — no fresh legs into NFP",
   sizing_explanation_in_their_voice="Tranche 1 buys the seat, tranche 2 buys the spike — GTC at 1.55 rests for an IV pop. Two mutants finished first and died famous; my book comes with a roof and I can name both numbers before the open.",
   backtest_summary="Defined-risk structure: 10-wide spread, credit 1.30, max loss $870 (8.7% of book) vs naked CSP's uncapped tail; theta/day favorable inside 21 DTE; no naked assignment risk.",
   client_order_id_template="agent-34-20260903-spread-1-<seq>",
   plan_step_2_if_rejected_alpaca="single-leg execution risk -> cancel BOTH legs, refile net 1.20 by 10:30; tranche 2 GTC 1.55 stands 3 days"),
}

assert len(plans) == 10 and len(agents) == 10
plan_ids = {p["agent_id"] for p in plans.values()}
assert plan_ids == {a["id"] for a in agents}, (plan_ids, {a['id'] for a in agents})
json.dump(plans, open(STATE / "trade_plans_D5.json", "w"), indent=2)
print("trade_plans_D5.json filed: 10 plans")

# ---------- digest ----------
digest = f"""BUSHWOOD STRATTON — OVERNIGHT REPLICATION, PREP FOR DAY 5 (Thu 9/3)

FIRED 4:30 (7/10): Wolf (+$7.98 — #1 GREEN, second straight day the #1 book lost the vote), Jake Blues (+$1.40), Lou Roma (+$1.00), Marvin Levene (−$2.00), Dave Roma (−$3.00), Tommy Levene (−$4.00), Ray Blues (−$6.00, flat, Rule-8 flag). Books NOT dumped: 5 fired short puts ALL OTM carry capped GTC buy-to-close orders for Thu open (limits 0.13–0.16, residual ~−$22); Wolf's BTC already liquidated 16:39, powder restored. Do not refile.

SURVIVOR LAW — Levene (#8), Elwood (#9), Roma (#10) KEEP their seats AS THEMSELVES, 4th night. Books carry untouched: Roma short XLF 57P @0.36, Elwood short 56P @0.19, Levene short XLU 9/4 42P — HARD EXIT THU 15:45, BTO wires at the open (settles into Friday payrolls). All three carried above the $9,983 floor → spoil retained (+$8.00/+$10.00/+$15.50 = $33.50), no top-up, no clawback.

HIRED FOR DAY 5 — 6 gen-3 clones (CSP; bid-anchored law, $0.12 min-rent floor, 13:30 fallback clock priced into every seat):
▸ Chris Roma (p. Ricky) XLF 55.5P 9/18 @0.15 est — bid-anchored by 10:00
▸ Eddie Roma (p. Ricky) XLF 55P @MAX(bid, 0.12) — 10:30 walk-up to 55.5P
▸ Walt Blues (p. Elwood) XLF 56P @0.21 est — fallback 55.5P by 13:30
▸ Murph Blues (p. Elwood) XLU 41.5P @0.13 est — ROTATION + liquidity gate (volume ≥50 or he moves the route)
▸ Alan Levene (p. Shelly) XLU 41P @MAX(bid, 0.12) — thin-chain law, walk-up trigger
▸ Roy Levene (p. Shelly) XLU 9/4 42.5P @MAX(bid, 0.12) — weekly clock, HARD EXIT Thu 15:45
MUTANT: Mark Sterling (agent-34) — credit_spread, no lineage. SPY 9/18 735/725 put spread, net 1.30 est, MAX LOSS $870/lot priced before the open, tranche 2 GTC 1.55, stop = 2x credit, no fresh legs after Thu 15:45. First defined-risk chair on the desk — the mutant chair rotates families after two crypto #1s died to the charter.

CAPITAL: equity $99,831.86 ÷ 10 = floor $9,983/agent. LEFTOVER $1.86 → champion's family (#1 survivor Shelly Levene's clones): Alan +$0.93, Roy +$0.93. Books total $99,865.36 = equity $99,831.86 + retained survivor spoils $33.50 (carry-over law: no clawback). Sector buckets: XLF $33.7K (84% of cap — AT the edge, no 5th XLF leg), XLU $12.35K new + carry, SPY spread $870 max risk, crypto chair EMPTY.

LESSONS: Sam's Happy Hour — 6 CSP-family lessons from tonight's fallen injected VERBATIM into all 6 clone bloodlines (36 injections; mutant blank slate by design). trade_plans_D5.json filed for the 9:35 cron; clone limits are est mids (chain still 404) — GAP GATE reprices to live mids before any card.

DESK GREETINGS (hiring_lobby):
Alan Levene: "My father's patience, my brother's clock, plus one law of my own: a thin chain pays full rent or no rent."
Mark Sterling: "Two mutants finished first and died famous; I intend to finish and stay. My trades come with roofs — defined risk, staged tranches, stops closer than my alibi."

SAM'S BEST TONIGHT — Winston Wolf, The Clean Getaway: "A one-day chair cannot afford a 25% first tranche... a quarter-size winner at #1 still loses the vote when the ranking is against charter chairs you cannot displace." Two straight nights the #1 book died to the survivor law. The mutant lesson is now institutional — which is why tonight's mutant trades with a roof.

— Gordo, PM. Three chairs are forever. Seven are a tryout. Let the tape pick tomorrow's seats.
"""
(STATE / "support_matrix_digest_D5.txt").write_text(digest, encoding="utf-8")
print("digest written:", len(digest), "chars")
print("REPLICATION COMPLETE — Day 5 roster live")