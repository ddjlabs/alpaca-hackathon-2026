#!/usr/bin/env python3
"""D5 6PM replication — dashboard.json update: fired statuses, survivor books, 7 new agents,
fund reallocation note + day counter. Atomic write with .bak backup."""
import json, shutil
from pathlib import Path

F = Path("/mnt/agent_share/gordon/hackathon/state/dashboard.json")
shutil.copy(F, str(F) + ".bak_1800_d6spawn")
d = json.loads(F.read_text())

lessons = json.loads(Path("/mnt/agent_share/gordon/hackathon/state/lessons_D5.json").read_text())
csp_lessons = [l["lesson"] for l in lessons if l.get("seed_for", "").startswith("cash_secured_put")]
assert len(csp_lessons) == 6

POOL = 99835.27
PER = 9983.00

# ---- 1) survivors: carry books untouched, allocation = floor, spoil retained ----
surv = {
    "agent-02": dict(allocation=10016.00, current_value=10016.00,
        strategy="XLF CSP: carried short 9/18 57P @ 0.36 (mark 0.23 at D5 close) — 5th carry night. Management card governs: BTC <= 0.15 if XLF >= 58.60; hard stop BTC 1.02 OR XLF <= 56.00 intraday. D5 #1 (+$21.00) — champion; leftover dust +$0.01.",
        tenure_note="survivor — charter carry, 6th night; D5 champion (#1, +$21.00)"),
    "agent-04": dict(allocation=10004.00, current_value=10004.00,
        strategy="XLF CSP: carried short 9/18 56P @ 0.19 (mark 0.12 at D5 close) — 5th carry night. Stop: BTC 0.57 OR XLF <= 55.00; card: BTC <= 0.10 if XLF >= 58.00. D5 #2 (+$9.00).",
        tenure_note="survivor — charter carry, 6th night; D5 #2 (+$9.00)"),
    "agent-07": dict(allocation=10002.00, current_value=10002.00,
        strategy="XLU CSP: FLAT — the 9/4 weekly exited 0.04 vs 0.08 cap at 09:38 (realized +$8, the desk's only profitable executed trade D5). No carried book into D6; NFP Friday governs. D5 #3 (+$2.00).",
        tenure_note="survivor — charter carry, 6th night; D5 #3 (+$2.00)"),
}

# ---- 2) new agents ----
NEW = [
 dict(id="agent-35", name="Gordon Roma", parent="agent-02", gen=3, alloc=9985.64,
      persona="The name on the marquee, earned without quoting it. Price first, story never; fill prints or it didn't happen.",
      movie="Wall Street", fam="cash_secured_put",
      strategy="XLF CSP: STO XLF 9/18 55.5P @ MAX(live bid, 0.12), bid-anchored; TAPE-VERIFIED fill by 10:00; own 13:30 fallback clock. Lessons: 6 CSP (Sam D5).",
      inherited=csp_lessons),
 dict(id="agent-36", name="Marcus Roma", parent="agent-02", gen=3, alloc=9985.63,
      persona="The accountant of the Roma line. Twelve cents is rent; eleven is charity. The floor carries a deadline: 13:30, in writing.",
      movie="common American", fam="cash_secured_put",
      strategy="XLF CSP: STO XLF 9/18 55P @ MAX(live bid, 0.12); 10:30 walk-up to 55.5P; by 13:30 fallback at live bid, floor suspended. Lessons: 6 CSP (Sam D5).",
      inherited=csp_lessons),
 dict(id="agent-37", name="Nicky Blues", parent="agent-04", gen=3, alloc=9983.00,
      persona="Reads volume like his father reads highway signs — who's trading before what's trading; a quote without size is a rumor.",
      movie="Casino", fam="cash_secured_put",
      strategy="XLU CSP: STO XLU 9/18 41.5P @ MAX(bid, 0.12) — rotation off the stacked XLF shelf; liquidity gate (vol >= 50 + bid size) first; 13:30 fallback XLU 9/11 weekly @ live bid. Lessons: 6 CSP (Sam D5).",
      inherited=csp_lessons),
 dict(id="agent-38", name="Sonny Blues", parent="agent-04", gen=3, alloc=9983.00,
      persona="The oldest son's confidence — takes the empty lane because empty lanes pay best, but checks the pond first, every time.",
      movie="The Godfather", fam="cash_secured_put",
      strategy="XLP CSP (BALLAST RESTORATION): STO XLP 9/18 83P @ MAX(bid, 0.15), reserve $8,300; HARD liquidity gate before filing; empty pond by 10:00 => rotate XLU 41.5P. Lessons: 6 CSP (Sam D5).",
      inherited=csp_lessons),
 dict(id="agent-39", name="Blake Levene", parent="agent-07", gen=3, alloc=9983.00,
      persona="A closer's son with the machine's clock — talks in deadlines because deadlines are the only honest part of any price.",
      movie="Glengarry Glen Ross", fam="cash_secured_put",
      strategy="XLU CSP: STO XLU 9/18 41.5P @ MAX(bid, 0.12), earliest legal fill by 10:00 preferred; deadline floor until 13:30 ONLY, then fallback at then-bid. Lessons: 6 CSP (Sam D5).",
      inherited=csp_lessons),
 dict(id="agent-40", name="Gus Levene", parent="agent-07", gen=3, alloc=9983.00,
      persona="The quiet one — measures the room before the price; the room is the spread; thin chains are where floors go to die.",
      movie="common American", fam="cash_secured_put",
      strategy="XLU CSP: STO XLU 9/18 41P @ MAX(bid, 0.12); 10:30 walk-up to 41.5P (delta pre-cleared); two-contract cap precedent; 13:30 weekly fallback, floor suspended in writing. Lessons: 6 CSP (Sam D5).",
      inherited=csp_lessons),
 dict(id="agent-41", name="Vincent Kessler", parent=None, gen=1, alloc=9983.00,
      persona="Blank slate. No lineage, no lessons — momentum pays the seat, stops keep it, crypto never closes.",
      movie="Pulp Fiction", fam="crypto_momentum",
      strategy="CRYPTO MOMENTUM (blank slate): spot BTC tranche 1 at open (~25%), tranche 2 GTC ~2% under, optional ETH ~-3%; hard stops -2.5%/-3.0% on filled size; max deployment 65%.",
      inherited=[]),
]

# ---- apply ----
by_id = {}
for a in d["agents"]:
    by_id[a["id"]] = a

for aid, up in surv.items():
    a = by_id[aid]
    a.update(up)
    a["carried_portfolio"] = True
    a["status"] = "active"

for n in NEW:
    old = by_id.get(n["id"])
    if old:  # re-hire of a previously fired id (none expected tonight)
        d["agents"].remove(old)
    d["agents"].append({
        "id": n["id"], "name": n["name"], "persona": n["persona"], "movie": n["movie"],
        "allocation": n["alloc"], "current_value": n["alloc"], "daily_pnl": 0.0,
        "daily_pnl_pct": 0.0, "status": "active", "strategy": n["strategy"],
        "strikes": 0, "generation": n["gen"], "parent": n["parent"], "avatar": None,
        "exposure": 0.0, "inherited_lessons": n["inherited"], "non_trading_flag": False,
        "carried_portfolio": False,
    })

# ---- 3) fund block ----
d["fund"]["day"] = 6
d["fund"]["reallocation_note"] = (
    "D5->D6 reallocation: pool $99,835.27 equity / 10 = $9,983 floor; survivors retain full "
    "marked books (02 $10,016.00 incl. +$12.63 spoil & $0.01 dust; 04 $10,004.00 incl. +$10.00 "
    "spoil; 07 $10,002.00 incl. +$8.50 spoil) — retain-all, no top-up, no clawback; 7 new "
    "agents $9,983.53 fresh (35 $9,985.64 / 36 $9,985.63 — champion's leftover $2.64/$2.63, "
    "split exact); leftover $5.27 -> Roma family. Fired books = noted obligations at marks "
    "(~-$47 net), 6 capped BTO GTC closers wired 18:10 (ar-cleanup-*-20260903)."
)
# hr_board append (site-facing log)
d.setdefault("hr_board", []).append({
    "agent": "AR OFFICE — 6PM replication (D5 -> D6)",
    "cause": "Charter top-3 kept (Roma #1 +$21.00 / Elwood #2 +$9.00 / Levene #3 +$2.00 — founders sweep, books carried untouched). Hired: 6 gen-3 clones (Gordon+Marcus Roma, Nicky+Sonny Blues, Blake+Gus Levene) + 1 mutant (Vincent Kessler, crypto_momentum, blank slate). 6 CSP lessons from Sam's Happy Hour injected verbatim into 6 clone souls (36 injections).",
    "final_words": "Third straight day the podium belonged to somebody's carry. Tomorrow the clones try to earn it with fills instead of marks."
})

json.dump(d, open(F, "w"), indent=1)

# ---- verify ----
d2 = json.loads(F.read_text())
act = [a for a in d2["agents"] if a["status"] == "active"]
print("active:", len(act), "| total rows:", len(d2["agents"]))
tot = 0.0
for a in act:
    print(f"  {a['id']} {a['name']:<20} gen {a['generation']} alloc {a['allocation']:>9} cv {a['current_value']:>9} lessons {len(a.get('inherited_lessons') or [])}")
    tot += a["current_value"]
print("sum of active current_values:", round(tot, 2))
print("note:", d2["fund"]["reallocation_note"][:120])