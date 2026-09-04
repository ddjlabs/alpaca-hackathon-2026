#!/usr/bin/env python3
"""D4 correction: Winston Wolf final P&L re-attributed to REALIZED +$7.98
(exit 77,395.03 x 0.03241875 = $2,509.05 proceeds vs $2,501.07 cost).
Planning estimate +$9.37 was computed on rounded qty — replaced in all persistent records."""
import json, os

STATE = "/mnt/agent_share/gordon/hackathon/state"

def swap(path, pairs, count_only=False):
    s = open(path).read()
    n = 0
    for old, new in pairs:
        c = s.count(old)
        if c:
            s = s.replace(old, new); n += c
    if not count_only and n:
        tmp = path + ".tmp"; open(tmp, "w").write(s); os.replace(tmp, path)
    return n

# --- dashboard.json: agents row + all fired/kept dicts + hr_board tallies ---
D = os.path.join(STATE, "dashboard.json")
d = json.load(open(D))
for a in d["agents"]:
    if a["id"] == "agent-27":
        a["daily_pnl"] = 7.98
        a["daily_pnl_pct"] = 0.0008
        a["current_value"] = 9986.98
        a["strategy"] = a["strategy"].replace("FIRED D4 — #1, +$9.37", "FIRED D4 — #1, +$7.98 realized")
        a["strategy"] += " [exit 77,395.03 — realized booked]"
def fix_dicts(lst):
    for e in lst or []:
        if e["agent"].startswith("agent-27"):
            e["cause"] = "D4 — bottom-7 by day P&L — rank #1 at +$7.98 realized (BTC exited 77,395.03; marked +$15.63 at the 16:30 close)."
            e["final_words"] = e["final_words"].replace(
                "Nine dollars and thirty-seven cents. The only green book",
                "Seven dollars and ninety-eight cents, realized. The only green book")
fix_dicts(d["fired_today"]); fix_dicts(d["kept_today"])
fix_dicts(d["fund"]["fired_today"]); fix_dicts(d["fund"]["kept_today"])
fix_dicts(d["fund"].get("hr_board")); fix_dicts(d.get("hr_board"))
h = d["fund"]["daily_history"][-1]
h["note"] = h["note"].replace("Wolf fired #1 green", "Wolf fired #1 green (+$7.98 realized)")
tmp = D + ".tmp"; json.dump(d, open(tmp, "w"), indent=2); os.replace(tmp, D)
print("dashboard corrected")

# --- hr_board_D4.md ---
M = os.path.join(STATE, "hr_board_D4.md")
n = swap(M, [
    ("P&L +$9.37 ⚰️ FIRED FIRST PLACE, GREEN", "P&L +$7.98 realized ⚰️ FIRED FIRST PLACE, GREEN"),
    ("BTC 0.0325 @ 77,148.74, marked 77,177.25 — the desk's ONLY green book.",
     "BTC 0.0325 @ 77,148.74 — liquidated 16:39 at 77,395.03, realized +$7.98. The desk's ONLY green book."),
    ("FIRED (7): Wolf (+$9.37, #1 — GREEN)", "FIRED (7): Wolf (+$7.98 realized, #1 — GREEN)"),
    ("Nine dollars and thirty-seven cents. The only green book",
     "Seven dollars and ninety-eight cents, realized. The only green book"),
    ("Winston Wolf made nine bucks of real mark",
     "Winston Wolf made eight bucks of realized money"),
])
print("hr_board_D4.md:", n, "replacements")

# --- ar_log.md: FIRED line + correction note appended to DAY 4 section ---
A = os.path.join(STATE, "ar_log.md")
s = open(A).read()
s = s.replace(
    "- FIRED agent-27 Winston Wolf — daily P&L +$9.37 (rank #1) — mutant fired #1 with the desk's ONLY green book (BTC 0.0325 @ 77,148.74, marked 77,177.25); survivor charter outranks the tape. 2 staged GTCs canceled in cleanup.",
    "- FIRED agent-27 Winston Wolf — daily P&L +$7.98 REALIZED (rank #1) — mutant fired #1 with the desk's ONLY green book (BTC 0.0325 @ 77,148.74, liquidated 77,395.03 at 16:39); survivor charter outranks the tape. 2 staged GTCs canceled in cleanup.\n"
    "- CORRECTION (16:45): Wolf's 4:30 board notice said +$9.37 — planning estimate on rounded qty. Book of record is +$7.98 realized on actual fills ($2,509.05 proceeds vs $2,501.07 cost). All persistent records corrected; board notices stand as sent.")
tmp = A + ".tmp"; open(tmp, "w").write(s); os.replace(tmp, A)
print("ar_log corrected")

# final echo
d = json.load(open(D))
w = [a for a in d["agents"] if a["id"] == "agent-27"][0]
print("wolf row:", w["daily_pnl"], w["current_value"], "| cause:", d["fired_today"][0]["cause"][:80])