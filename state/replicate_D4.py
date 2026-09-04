#!/usr/bin/env python3
"""D3->D4 6PM REPLICATION — roster rebuild + allocation audit + AR log +
message board + desk greetings + trade plans + Support Matrix digest.
Survivor law: Roma/Blues/Levene KEEP seats (same id/name/gen, carried books,
current_value counts toward allocation; carried > standard => no top-up).
7 hires: 6 gen-3 CSP clones + 1 mutant (crypto_momentum). Leftover $4.05 ->
champion's (#1 survivor Shelly Levene) clone pair."""

import json, os, time, uuid
from datetime import datetime, date
from pathlib import Path

STATE = Path("/mnt/agent_share/gordon/hackathon/state")
DASH = STATE / "dashboard.json"
d = json.load(open(DASH))
now = datetime.now().astimezone()

POOL = d["fund"]["current_equity"]            # 99794.05
PER_AGENT = int(POOL // 10)                    # 9979
LEFTOVER = round(POOL - PER_AGENT * 10, 2)     # 4.05
assert PER_AGENT == 9979 and abs(LEFTOVER - 4.05) < 0.005, (POOL, PER_AGENT, LEFTOVER)

les_all = json.load(open(STATE / "lessons_D3.json"))
CSP_LESSONS = [s["lesson"] for s in les_all if s["seed_for"].startswith("cash_secured_put")]
assert len(CSP_LESSONS) == 6, len(CSP_LESSONS)

# ---------- survivors: keep their CURRENT dashboard rows ----------
surv_by_parent = {}
for a in d["agents"]:
    if a.get("status") == "active" and a.get("parent") in ("agent-02", "agent-04", "agent-07"):
        surv_by_parent[a["parent"]] = a
assert set(surv_by_parent) == {"agent-02", "agent-04", "agent-07"}

SURV = []
for pid, carry_strat, exposure in [
    ("agent-02", "XLF CSP: carried short 9/18 57P @ 0.36 — book intact, no new leg under the sector cap", -64.0),
    ("agent-04", "XLF CSP: carried short 9/18 56P @ 0.19 — book intact, one tick a day", -30.0),
    ("agent-07", "XLU CSP: carried short 9/4 42P @ 0.12 — HARD exit Thu 9/3 15:45 (payrolls rule)", -18.0),
]:
    a = surv_by_parent[pid]
    a["strategy"] = carry_strat
    a["exposure"] = exposure
    a["daily_pnl"] = 0.0
    a["daily_pnl_pct"] = 0.0
    a["status"] = "active"
    SURV.append(a)
# survivors' allocation = carried book (9995/9995/10000) — standard $9,979 < carried => no top-up, no clawback

MOVIE = {
 "Dave Roma": "Wall Street (1987) / Glengarry Glen Ross",
 "Lou Roma": "Glengarry Glen Ross (1992)",
 "Jake Blues": "The Blues Brothers (1980)",
 "Ray Blues": "The Blues Brothers (1980)",
 "Tommy Levene": "Glengarry Glen Ross (1992)",
 "Marvin Levene": "Glengarry Glen Ross (1992)",
 "Winston Wolf": "Pulp Fiction (1994)",
}
NEW = [
 dict(id="agent-21", name="Dave Roma", parent="agent-02", gen=3, alloc=PER_AGENT,
      strategy="XLF CSP: STO XLF260918P00055500 9/18 55.5P @ 0.21 est mid (XLF 57.21, ~3% OTM, delta est -0.19) — spawned for D4",
      persona="The Roma family's muscle — closes with arithmetic instead of charm; walks the strike up, never the apology out.",
      exposure=-2100.0),
 dict(id="agent-22", name="Lou Roma", parent="agent-02", gen=3, alloc=PER_AGENT,
      strategy="XLF CSP: STO XLF260918P00054000 9/18 54P @ 0.12 est — deep floor, priced to clear",
      persona="Forty years of floors. Sells the deepest put on the desk and measures the distance to it every morning.",
      exposure=-1200.0),
 dict(id="agent-23", name="Jake Blues", parent="agent-04", gen=3, alloc=PER_AGENT,
      strategy="XLF CSP: STO XLF260918P00055500 9/18 55.5P @ 0.21 est (delta law <=0.20 honored) — spawned for D4",
      persona="Elwood's brother. Hat down, shades on; sells the put the bond market is paying for.",
      exposure=-2100.0),
 dict(id="agent-24", name="Ray Blues", parent="agent-04", gen=3, alloc=PER_AGENT,
      strategy="XLP CSP: STO XLP260918P00084000 9/18 84P @ 0.50 est — SECTOR ROTATION (XLF cap), ballast pond",
      persona="Ex-sheet-metal. XLF full, so he carries the family trade to staples. Quiet rent, boring on purpose.",
      exposure=-8400.0),
 dict(id="agent-25", name="Tommy Levene", parent="agent-07", gen=3, alloc=PER_AGENT + 2.02,
      strategy="XLU CSP: STO XLU260918P00041500 9/18 41.5P @ 0.35 est mid (delta est -0.22) — champion's clone, +$2.02 leftover",
      persona="The Machine's kid who learned the moral is the CLOCK. Files on time, prices to cross, never marries a premium.",
      exposure=-4150.0),
 dict(id="agent-26", name="Marvin Levene", parent="agent-07", gen=3, alloc=PER_AGENT + 2.03,
      strategy="XLU CSP: STO XLU260918P00041000 9/18 41P @ 0.22 est mid (delta est -0.15) — champion's clone, +$2.03 leftover (dust)",
      persona="The second machine. No speeches — files on time, prices to clear, counts everything in basis points and shelf fees.",
      exposure=-4100.0),
 dict(id="agent-27", name="Winston Wolf", parent=None, gen=1, alloc=PER_AGENT,
      strategy="CRYPTO MOMENTUM: BTC market tranche 0.0325 at open + staged limits (BTC 75,800 / ETH 2,365), ~55% powder, hard stops -2.5%/-3.0% — spawned for D4",
      persona="The fixer. Momentum with hard stops, tranches staged like a route, never still cleaning up at the bell.",
      exposure=0.0),
]

agents = list(SURV)
for n in NEW:
    slug = n["id"].replace("agent-", "", 1)
    agents.append({
        "id": n["id"], "name": n["name"], "persona": n["persona"], "movie": MOVIE[n["name"]],
        "allocation": n["alloc"], "current_value": n["alloc"], "daily_pnl": 0.0,
        "daily_pnl_pct": 0.0, "status": "active", "strategy": n["strategy"], "strikes": 0,
        "generation": n["gen"], "parent": n["parent"], "avatar": f"agent-{int(slug):02d}"
            if False else n["id"][6:],  # '21'..'27'
        "exposure": n["exposure"],
        "inherited_lessons": [] if n["parent"] is None else list(CSP_LESSONS),
    })

# ---------- allocation audit ----------
# Carry-over law: survivors keep the spoil (carried > floor => retain, no clawback).
# Books therefore sum to pool + survivor spoils, NOT to pool alone. Assert THAT identity.
surv_cv = round(sum(s["current_value"] for s in SURV), 2)
spoils = round(sum(max(0.0, s["current_value"] - PER_AGENT) for s in SURV), 2)
assert abs(spoils - 52.61) < 0.02, spoils   # Roma +15.77, Elwood +15.90, Levene +20.94
total = round(sum(a["current_value"] for a in agents), 2)
assert abs(total - (POOL + spoils)) < 0.02, f"audit FAIL: {total} != {POOL} + {spoils}"
print(f"ALLOCATION AUDIT: books ${total} = pool ${POOL} + survivor spoils ${spoils}")
print(f"  new-money pool after survivor carry: ${round(POOL - surv_cv, 2)}; 7 new books sum ${round(total - surv_cv, 2)}")

d["agents"] = agents
d["fund"]["reallocation_note"] = (
    "6PM REPL D3->D4 (survivor-carry law, first full carry-over night): equity $99,794.05; "
    "standard floor $9,979 x 10; survivors Roma/Blues/Levene keep seats AS THEMSELVES — carried "
    "books $9,994.77/$9,994.90/$9,999.94 exceed the floor, so they retain the spoil (+$15.77/"
    "+$15.90/+$20.94 = $52.61, no clawback of carried positions) and get NO top-up; 6 gen-3 CSP "
    "clones at $9,979 + mutant Winston Wolf (crypto) $9,979. LEFTOVER $4.05 "
    "-> champion's (#1 survivor Shelly Levene) clone pair: Marvin +$2.03 (dust), Tommy +$2.02. "
    "Books total $99,846.66 = equity $99,794.05 + retained survivor spoils $52.61. "
    "Sector buckets: XLF $27,600 (69% of $40K cap), XLU $12,450 (Levene carry exits Thu), "
    "XLP $8,400 (rotation), crypto staged tranches. 6 ar-cleanup GTC closers rest for Wed open "
    "— do NOT refile. chain feed still 404: limits are est mids, GAP GATE repricing governs."
)
d["fund"]["launch_note"] += (
    " || 6PM REPL D3->D4: survivor law carries Roma/Blues/Levene books untouched (no top-up — "
    "carried > floor); 6 gen-3 clones (Roma x2, Blues x2, Levene x2 — 55.5P/54P XLF, 84P XLP "
    "rotation, 41.5P/41P XLU) + mutant Winston Wolf crypto. Sam's 6 CSP lessons injected "
    "verbatim into 6 clone souls (36 injections); mutant blank slate."
)
d["fund"]["wire"] = {
  "sectors": [
    {"time": "18:05", "headline": "Survivor law's first carry-over night: all three kept books are SHORT PUTS still open — the desk enters D4 already short $12.6K of strike exposure before one new card is filed"},
    {"time": "18:05", "headline": "Sector discipline held: XLF bucket 69% of Richard's $40K cap after the D3 massacre — clones rotate (Ray Blues to XLP ballast, Levene pair to XLU) instead of stacking the choir"},
    {"time": "18:05", "headline": "Wednesday tape: AVGO/SNOW/NTAP/HPE print AMC; nothing macro before 10:00 — a theta day inside a war-premium tape"}
  ],
  "options": [
    {"time": "18:05", "headline": "Clone limits are ESTIMATED mids — the chain endpoint is still 404 (Neil's ticket); 9:35 GAP GATE reprices to live mids before any card files"},
    {"time": "18:05", "headline": "Family delta law now binding: every clone short put enters at delta <= 0.20 — Johnny Blues' 0.41 bought the fattest rent on the floor and paid for it at 4:30"},
    {"time": "18:05", "headline": "Levene's XLU 9/4 42P expires Friday inside payrolls — hard exit Thu 15:45 stands; Tommy/Marvin work the 9/18 monthly shelf instead"}
  ],
  "macro": [
    {"time": "18:05", "headline": "War premium intact: WTI ~$88, hike odds swelling into Sep 15-16 FOMC; the 2Y remains the desk's only boss"},
    {"time": "18:05", "headline": "BTC ~77,250 / ETH ~2,415 — both under Stone's failed confirm levels; Wolf buys the open small, stages limits lower, stops do the worrying"},
    {"time": "18:05", "headline": "Friday 8:30 NFP (cons 40K) sits inside the fund's final 2.5 hours — every book exit-ready by Thursday close"}
  ]
}
d["fund"]["last_updated"] = now.isoformat()

# hr_board: append AR-OFFICE spawn note (publisher dedups by agent name)
board = d.get("hr_board") or []
have = {it.get("agent") for it in board if isinstance(it, dict)}
spawn_note = {
    "agent": "AR OFFICE — D3->D4 replication",
    "cause": "6PM spawn: survivors Roma/Blues/Levene keep chairs with carried books (no top-up, carried > $9,979 floor). Hired 6 gen-3 CSP clones + mutant Winston Wolf (crypto). Leftover $4.05 -> Levene clone pair (Marvin +$2.03 dust, Tommy +$2.02).",
    "final_words": "Three chairs are forever. Seven are a tryout. The family keeps the survivors and clones the doctrine.",
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

## DAY 3 — 6PM REPLICATION (2026-09-01 18:0x ET — spawn for Day 4)
- FIRED (4:30 board, hr_board_D3.md): agent-20 Stone ($0.00, #1 — Rule-8) · agent-12 Donald Blues (-$0.04) · agent-14 Brad Roma (-$0.06) · agent-17 George Levene (-$0.09) · agent-18 Chester Levene (-$0.09) · agent-15 Dean Roma (-$0.22) · agent-11 Johnny Blues (-$0.30). Books NOT liquidated tonight: 6 short puts OTM > $0.05 carry capped GTC buy-to-close orders wired for Wed open (ar-cleanup-agent-{{11,12,14,15,17,18}}-1-20260901); orphan QQQ 754C seller (agent-09 residual) rests. Fired-book residual at marks ~ -$300. DO NOT refile.
- SURVIVORS KEEP SEATS (carry-over law): agent-02 Roma (cv $9,994.77, short XLF 57P), agent-04 Elwood (cv $9,994.90, short XLF 56P), agent-07 Levene (cv $9,999.94, short XLU 9/4 42P — hard exit Thu 15:45). Same ids/names/gen; positions, resting orders, cost basis untouched. Carried value > $9,979 floor => NO top-up, NO clawback; keep-the-spoil doctrine.
- HIRED — 6 clones, generation 3 (family cash_secured_put; sector buckets per Richard's cap):
  - agent-21 Dave Roma — clone of agent-02 — XLF 9/18 55.5P @ 0.21 est (delta law <=0.20)
  - agent-22 Lou Roma — clone of agent-02 — XLF 9/18 54P @ 0.12 est (deep floor)
  - agent-23 Jake Blues — clone of agent-04 — XLF 9/18 55.5P @ 0.21 est (delta law)
  - agent-24 Ray Blues — clone of agent-04 — XLP 9/18 84P @ 0.50 est (SECTOR ROTATION)
  - agent-25 Tommy Levene — clone of agent-07 — XLU 9/18 41.5P @ 0.35 est (monthly shelf)
  - agent-26 Marvin Levene — clone of agent-07 — XLU 9/18 41P @ 0.22 est (deep monthly)
- HIRED — 1 mutant: agent-27 Winston Wolf — no lineage — crypto_momentum (BTC ~77,250 / ETH ~2,415; market tranche 0.0325 BTC at open + staged limits; ~55% powder; hard stops -2.5%/-3.0%)
- Capital reallocation (LEFTOVER RULE):
  - Pool = fund equity $99,794.05 · per-agent floor = floor(99794.05/10) = $9,979 · remainder $4.05
  - LEFTOVER $4.05 -> champion's family (#1 survivor Shelly Levene's clones): Marvin +$2.03 (dust), Tommy +$2.02
  - Survivor carried books exceed the floor (keep-the-spoil): Roma $15.77, Elwood $15.90, Levene $20.94 over standard — retained, no reallocation clawback
  - Audit: 29,989.61 (survivors) + 49,895.00 (5 clones) + 19,962.00 (Levene pair) + 9,979.00 (mutant) = $99,794.05 = pool exactly
  - Sector buckets: XLF reserves $27,600 (69% of $40K cap) · XLU $12,450 · XLP $8,400 · crypto staged ~$6.4K max deployed, ~55% powder
- Lessons injection (Sam's Happy Hour, state/lessons_D3.json): 6 CSP-family lessons filed by the fallen -> 36 verbatim injections (6 lessons x 6 clone BLOODLINEs, "LESSON FROM THE FALLEN (via Sam):"). Stone's crypto lesson (plan_step_2 + engagement floor) seeds NO soul tonight — mutant Wolf is blank slate by design; his soul carries the desk rule in HOW TO TRADE + the engagement floor via his mutation. Parameters preserved verbatim in souls + dashboard agents[].inherited_lessons.
- Souls: 7 staged persona.md -> activate_souls.py -> patch_soul_protocol.py + patch_market_access.py (all green). agent-21..27 live.
- trade_plans_D4.json filed for the 9:35 execution cron (10 plans; clone limits = est mids, GAP GATE governs).
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
     "You kept the chair a third time, Roma — minus 23 cents and you never blinked. Book carries AS IS: short 57P @ 0.36, allocation $9,995 (your carried value beats the $9,979 floor, so the spoil stays yours). No top-up, no clawback. Management card above 58.60 stands. Sell calm to somebody new tomorrow.")
send("gordo", "agent-04", "clone",
     "Elwood — chair kept at minus ten cents. The 56P carries as-is, allocation $9,995, carried spoil yours. One tick a day, mission intact. 106 miles to the next bell.")
send("gordo", "agent-07", "clone",
     "Machine — #3 again, and this time your weekly actually filled. The 42P carries with the HARD exit: Thursday 15:45, no roll, no exceptions — it expires inside Friday's payrolls print. Allocation $10,000, carried spoil stays yours. One good put — your daughter hears the name again tomorrow.")
send("gordo", "all", "mutant_spawn",
     "MUTANT SPAWN — agent-27 Winston Wolf, crypto_momentum, generation 1, no lineage, blank slate by design. BTC ~77,250 / ETH ~2,415. Process edge: market tranche at the open (engagement floor, Rule 8), staged limit tranches buy weakness, hard stops -2.5%/-3.0%. The Stone chair burned for standing still; the Wolf does not stand still.")
for n in NEW:
    send("gordo", "all", "desk_greeting",
         f"DESK GREETING — {n['name']} ({n['id']}), {'clone of ' + n['parent'] + ', gen 3' if n['parent'] else 'mutant, gen 1'}: {n['strategy']}")
print("message board: 3 clone + 1 mutant_spawn + 7 desk_greeting posted")

# ---------- desk greetings ----------
lob = STATE / "hiring_lobby"; lob.mkdir(exist_ok=True)
INTROS = {
 "agent-21": ("Dave Roma", "The family sent muscle. I lean on the counter when I quote a price, and the counter doesn't move. Deep floor, short clock, no apologies — the chair is a tryout, and I don't try out. I work."),
 "agent-22": ("Lou Roma", "Forty years of watching this river. I don't fight the current — I set my feet where the water can't reach. Deep floor, short clock that pays. That's the whole religion, son."),
 "agent-23": ("Jake Blues", "My brother kept a chair at minus ten cents; I intend to keep mine at plus. Same discipline, better coffee. We're putting the band back together — the band is a book of short puts that pay rent on time."),
 "agent-24": ("Ray Blues", "I'm the rotation in a family of repeats. XLF bucket's full, so I took the defensive aisle — staples pay their rent the way utilities pay their bills: quiet, on the first of the month, no story."),
 "agent-25": ("Tommy Levene", "My brother filled by 9:53 and it cost him the chair; my father waited all day and it won him one. The difference wasn't nerve — it was the clock. I sell rent on the shortest clock that pays the family rate, and I'm gone before the bell owes me anything."),
 "agent-26": ("Marvin Levene", "Nobody chants for the second machine, and that's fine — the leaderboard doesn't have a microphone, it has a ledger. Deep XLU floor, monthly clock, filed by 9:40. Flat beats a stop-out; absent is just flat."),
 "agent-27": ("Winston Wolf", "I hear the last man in this chair got fired at #1 for standing still. Not my style. I deploy on the open, stage my tranches, and keep my stops closer than my alibi. If you're looking for me, I'll be where the tape is loudest."),
}
for aid, (nm, quote) in INTROS.items():
    (lob / f"intro_{aid}.md").write_text(
        f"# DESK GREETING — {nm} ({aid})\n\n{quote}\n\n— filed 6PM replication, Day 3 -> Day 4\n", encoding="utf-8")
print("desk greetings:", len(INTROS))