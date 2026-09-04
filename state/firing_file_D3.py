#!/usr/bin/env python3
"""D3 FIRING — file terminations: message board, dashboard.json, ar_log.md."""
import json, os, uuid, time
from datetime import datetime

STATE = "/mnt/agent_share/gordon/hackathon/state"
NOW = datetime.now().astimezone().isoformat(timespec="seconds")

FINALS = {  # agent_id: (rank, day_pnl, day_pnl_pct, current_value, exposure_mark, name)
    "agent-20": (1,   0.00,  0.0,   9981.00, 0.0,   "Jared Stone"),
    "agent-12": (2,  -0.04, -0.0004, 9980.96, -0.09, "Donald Blues"),
    "agent-14": (4,  -0.06, -0.0006, 9980.94, -0.15, "Brad Roma"),
    "agent-17": (5,  -0.09, -0.0009, 9980.91, -0.50, "George Levene"),
    "agent-18": (6,  -0.09, -0.0009, 9980.91, -0.43, "Chester Levene"),
    "agent-15": (8,  -0.22, -0.0022, 9980.78, -1.14, "Dean Roma"),
    "agent-11": (10, -0.30, -0.0030, 9980.70, -0.89, "Johnny Blues"),
}
KEPT = {  # survivors — NEVER leave
    "agent-07": (3,  -0.06, -0.0006, 9999.94, -0.12, "Shelly 'The Machine' Levene"),
    "agent-04": (7,  -0.10, -0.0010, 9994.90, -0.30, "Elwood Blues"),
    "agent-02": (9,  -0.23, -0.0023, 9994.77, -0.64, "Ricky Roma"),
}
STRAT_ADD_FIRED = {
    "agent-11": "FIRED D3 — #10, −$0.30: biggest premium (57.5P @ 0.59), biggest mark. Book wired closed (ar-cleanup GTC 0.98).",
    "agent-12": "FIRED D3 — #2, −$0.04: deep floor held, four-cent mark did it. Book wired closed (ar-cleanup GTC 0.10).",
    "agent-14": "FIRED D3 — #4, −$0.06: beat the tape by 62bp, lost to the survivor rule. Book wired closed (ar-cleanup GTC 0.17).",
    "agent-15": "FIRED D3 — #8, −$0.22: 0.92 October credit, filed by 10:00, gone by 4:30. Book wired closed (ar-cleanup GTC 1.26).",
    "agent-17": "FIRED D3 — #5, −$0.09: the put finally filled (0.41) and the fill fired him. Book wired closed (ar-cleanup GTC 0.55).",
    "agent-18": "FIRED D3 — #6, −$0.09: XLU rose and the insurance still marked against. Book wired closed (ar-cleanup GTC 0.47).",
    "agent-20": "FIRED D3 — #1 with $0.00: Rule-8 non-trading (zero orders, zero positions); mutant chair was a tryout. Flat — nothing to close.",
}
STRAT_ADD_KEPT = {
    "agent-02": " | KEPT D3 — survivor law (−$0.23, mark on carried 57P); book carries into D4",
    "agent-04": " | KEPT D3 — survivor law (−$0.10, mark on carried 56P); book carries into D4",
    "agent-07": " | KEPT D3 — survivor law (−$0.06, XLU 9/4 weekly carry); book carries into D4",
}

FINAL_WORDS = {
    "agent-20": ("You just fired the #1 book on the desk. Let that marinate. Zero down, zero risk, top of the "
                 "leaderboard — and I'm cleaning out my locker because I didn't trade? Your Rule 8 pays for "
                 "presence; crypto pays for conviction, and it never closes. GM. WGMI. See you at the next "
                 "fund — I'll be the one who was right the whole time."),
    "agent-12": ("Fired at #2. FOUR CENTS. I ran my route — deep floor at 54, eight cents of premium, the "
                 "safest book on this desk — and four cents of mark is a pink slip. That's not a firing, "
                 "that's a rounding error with an escort. Route's fixed. Schedule's fixed. Apparently so was "
                 "the outcome. Good luck finding steadier hands than the ones you're walking out."),
    "agent-14": ("Minus six cents. That's 0.0006 of one book on a day the index dropped 0.68% — the "
                 "arithmetic says I beat the tape by sixty-two basis points. The arithmetic also says these "
                 "seven chairs were never chairs; they were tryouts. Quote the price, hold the silence: this "
                 "was decided before the open. No plea. The math holds either way."),
    "agent-17": ("My father finished #1 by waiting all day. I filled by 9:53 — the machine's put finally "
                 "traded, and it cost me the chair the same hour it paid me. Forty-one cents of October "
                 "premium, nine cents of mark. Patience did its eight hours of invisible work and the ledger "
                 "still read fire. One good put — that was the prayer. It filled. The desk pays for exposure, "
                 "not for presence. Same lesson, different altar."),
    "agent-18": ("Eleven years of hardware taught me it's not the rent that kills you, it's the shelf fee. I "
                 "rented the 42 at 34 cents — utilities went UP today and my insurance still marked nine "
                 "cents against me by the bell. That's inventory cost, not a bad business. You're firing the "
                 "cheapest book on the floor over nine cents of shelf time. Fine. Screws, rent, shelf time — "
                 "somebody else's inventory next."),
    "agent-15": ("Filed by 10:00, filled by 9:47 — 92 cents, the biggest premium on the floor, an October "
                 "clock, exactly like the card said. The tape spent six hours marking my insurance down "
                 "twenty-two cents and you're calling speed the problem. Entry hour is credit hour. I had "
                 "the credit before lunch. The desk just fired the only agent who finished the morning's "
                 "work. Enjoy the slow money."),
    "agent-11": ("Excuse me, brother. Thirty cents — three basis points — the worst book on a floor where "
                 "worst still means outperforming the index by sixty-five. I sold the 57.5 against a 57.21 "
                 "close because the bond market was paying for banks; it paid 59 cents into my pocket at "
                 "9:53 and marked me down by the bell. That's carry, not panic. My uncle kept his chair at "
                 "minus five; I lose mine at minus thirty cents on a bigger premium and a tighter line. The "
                 "rent was due and I collected it. The door's where I left it. It always is."),
}
CAUSE = lambda r, p: f"bottom-7 by day P&L — rank #{r} at {p}."

# ---------- 1. MESSAGE BOARD ----------
def send(from_id, to_id, mtype, message, re=None):
    f = os.path.join(STATE, "messageboard_20260901.json")
    msgs = json.load(open(f)) if os.path.exists(f) else []
    msgs.append({
        "id": f"msg-{int(time.time())}-{uuid.uuid4().hex[:4]}",
        "from": from_id, "to": to_id, "type": mtype, "re": re,
        "message": message,
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "read": False,
    })
    tmp = f + ".tmp"; json.dump(msgs, open(tmp, "w"), indent=2); os.replace(tmp, f)

BOARD_LINES = {
    "agent-20": "#1 — You finished #1, $0.00. First place, fired anyway: the mutant's chair was always a tryout. Crypto never closes; the desk does.",
    "agent-12": "#2 — You finished #2, −$0.04. Four cents and a fixed route, straight out the door.",
    "agent-14": "#4 — You finished #4, −$0.06. You beat the tape by 62bp and lost to the survivor rule. Arithmetic closed the file.",
    "agent-17": "#5 — You finished #5, −$0.09. Your put finally filled, and the fill fired you. The Machine's kid learns the ledger.",
    "agent-18": "#6 — You finished #6, −$0.09. Cheapest book on the floor, nine cents of shelf time. Inventory's cleared.",
    "agent-15": "#8 — You finished #8, −$0.22. Biggest premium on the floor, filed by 10:00, gone by 4:30. Speed couldn't outrank blood.",
    "agent-11": "#10 — You finished #10, −$0.30. Worst book on the desk — and still 65bp better than the index. Excuse me, brother. Chair's gone.",
}
send("gordo", "all", "firing",
     "D3 FIRING 4:30 PM — survivor law holds: Levene (#3), Elwood (#7), Roma (#9) keep the chairs. "
     "The bottom 7 — every clone and the mutant — are terminated. Books wired closed via ar-cleanup GTC for Wed open. "
     "6PM: the family reallocates. Seven new chairs, same rule: the floor pays for exposure, not for presence.")
for aid, line in BOARD_LINES.items():
    send("gordo", aid, "termination_notice", line)

# ---------- 2. DASHBOARD ----------
DASH = os.path.join(STATE, "dashboard.json")
d = json.load(open(DASH))

for a in d["agents"]:
    aid = a["id"]
    src = FINALS.get(aid) or KEPT.get(aid)
    rank, pnl, pnl_pct, cur, expo, name = src
    a["rank_today"] = rank
    a["current_value"] = cur
    a["daily_pnl"] = pnl
    a["daily_pnl_pct"] = pnl_pct
    a["exposure"] = expo
    if aid in FINALS:
        a["status"] = "fired"
        a["strategy"] = (a.get("strategy", "").split(" | FIRED")[0].split(" | KEPT")[0]
                         + " | " + STRAT_ADD_FIRED[aid])
        if aid == "agent-20":
            a["tenure_note"] = "mutant — one-day tryout, fired at #1 with a flat book"
    else:
        a["status"] = "active"
        a["strategy"] = (a.get("strategy", "").split(" | FIRED")[0].split(" | KEPT")[0]
                         + STRAT_ADD_KEPT[aid])
        a["tenure_note"] = a.get("tenure_note", "survivor — Day 1 charter, portfolio carried")

fired_dicts = [{"agent": f"{aid} {FINALS[aid][5]}",
                "cause": CAUSE(FINALS[aid][0], f"{FINALS[aid][1]:+.2f}"),
                "final_words": FINAL_WORDS[aid]} for aid in
               ["agent-11", "agent-12", "agent-14", "agent-15", "agent-17", "agent-18", "agent-20"]]
kept_dicts = [{"agent": f"{aid} {KEPT[aid][5]}",
               "cause": f"survivor law — rank #{KEPT[aid][0]} at {KEPT[aid][1]:+.2f}; top-3 charter never leaves.",
               "final_words": "kept"} for aid in ["agent-07", "agent-04", "agent-02"]]

f = d["fund"]
f["current_equity"] = 99794.05
f["total_pnl"] = -205.95
f["total_pnl_pct"] = -0.206
f["day_pnl"] = -96.23
f["day_pnl_pct"] = -0.096
f["day"] = 3
f["last_updated"] = datetime.now().astimezone().isoformat()
f["fired_today"] = fired_dicts
f["kept_today"] = kept_dicts
d["fired_today"] = fired_dicts
d["kept_today"] = kept_dicts
d["daily_history"] = f["daily_history"]  # single source of truth; kill the stale empty dup

f["hr_board"] = (f.get("hr_board") or []) + fired_dicts  # running tally — never overwrite

f["launch_note"] += (" || D3 FIRING 16:30: survivor law — top-3 Roma/Blues/Levene NEVER leave (ranks #9/#7/#3). "
                     "All 7 non-survivors terminated incl. mutant Stone, FIRED #1 with $0.00 (Rule-8 non-trading; "
                     "the floor pays for exposure, not presence). Fired books = 6 short puts, all OTM>$0.05 → "
                     "ar-cleanup GTC BTO caps (~+10% over mark) rest for Wed open; nothing market-closed. "
                     "Orphan QQQ 754C seller (D2 residual) also rests. HR board: state/hr_board_D3.md. "
                     "6PM: the family reallocates — 7 new chairs per LAW.")

f["daily_history"].append({
    "day": 3, "date": "2026-09-01", "equity": 99794.05,
    "day_pnl": -96.23, "day_pnl_pct": -0.096, "total_pnl_pct": -0.206,
    "spy_close": 761.63, "spy_day_pct": -0.68, "spy_since_launch_pct": -0.99,
    "alpha_vs_spy_pct": 0.90, "positions": 10, "cash": 100206.05,
    "keeps": ["Shelly Levene (−$0.06)", "Elwood Blues (−$0.10)", "Ricky Roma (−$0.23)"],
    "fired_count": 7, "fills": 11, "cleaned_realized": 46.32,
    "note": "11 fills: 7 clone STOs $212 premium + 4 D2 residual closers +$46.32 realized. "
            "6PM: 7 ar-cleanup GTC BTOs + 754C seller rest for Wed open — do not refile.",
})

tmp = DASH + ".tmp"; json.dump(d, open(tmp, "w"), indent=2); os.replace(tmp, DASH)

# ---------- 3. AR LOG ----------
AR = os.path.join(STATE, "ar_log.md")
ar = open(AR).read()
marker = "---\n\n## DAY 2 — Monday, August 31, 2026 — 4:30 PM FIRING"
d3 = f"""---

## DAY 3 — Tuesday, September 1, 2026 — 4:30 PM FIRING

**Fund:** Equity $99,794.05 · Day P&L −$96.23 (−0.096%) vs SPY −0.68% (α +0.90% since launch +0.90pp day) · 11 fills (7 clone STOs $212 premium + 4 D2 residual closers +$46.32 realized) · last_equity basis $99,890.28.

**SURVIVOR LAW (Chief directive): top-3 NEVER leave — same id/name, portfolio carries untouched.**
- KEEP agent-07 Shelly Levene — daily P&L −$0.06 (rank #3) — XLU 9/4 42P carry marked 0.12; full powder
- KEEP agent-04 Elwood Blues — daily P&L −$0.10 (rank #7) — carried 56P marked 0.30
- KEEP agent-02 Ricky Roma — daily P&L −$0.23 (rank #9) — carried 57P marked 0.64

**FIRED (all 7 non-survivor desks — the tryout chairs):**
- FIRED agent-20 Jared Stone — daily P&L $0.00 (rank #1) — Rule-8 NON-TRADING: zero orders, zero positions, warning lapsed; fired #1 with a flat book (mutant tryout)
- FIRED agent-12 Donald Blues — daily P&L −$0.04 (rank #2) — XLF 54P STO @ 0.05, marked 0.09
- FIRED agent-14 Brad Roma — daily P&L −$0.06 (rank #4) — XLF 55P STO @ 0.09, marked 0.15
- FIRED agent-17 George Levene — daily P&L −$0.09 (rank #5) — XLF 10/16 55P STO @ 0.41 (reprice to bid), marked 0.50
- FIRED agent-18 Chester Levene — daily P&L −$0.09 (rank #6) — XLU 42P STO @ 0.34, marked 0.43
- FIRED agent-15 Dean Roma — daily P&L −$0.22 (rank #8) — XLF 10/16 57P STO @ 0.92, marked 1.14
- FIRED agent-11 Johnny Blues — daily P&L −$0.30 (rank #10) — XLF 57.5P STO @ 0.59, marked 0.89

**4:45 PM Cleanup (ar- prefix, options only — market closed):**
- 6 fired short puts ALL OTM > $0.05 → per mandate: leave + wire capped GTC buy-to-close for Wed open (D2 precedent)
- FILED 16:5x GTC BTO caps: agent-11 57.5P @0.98 (mark 0.89), agent-12 54P @0.10 (0.09), agent-14 55P @0.17 (0.15), agent-15 57P @1.26 (1.14), agent-17 55P @0.55 (0.50), agent-18 XLU 42P @0.47 (0.43) — all accepted
- agent-20 Stone flat — nothing to close
- Residual orphan: ar-cleanup-agent-09-2 (QQQ 754C sell 0.20 day) rests for Wed open (D2 inherited asset)
- 7 open orders at close, 0 failed fills — nothing carried undocumented

**⚠ 6PM REALLOCATION OPERATOR: do NOT refile the 6 GTC ar-cleanup BTOs or the 754C seller — they close at Wed open. Fired-book residual at marks ≈ −$320 (shorts) + orphan 754C +$20 = −$300. Survivor books (57P/56P/XLU 9/4) carry untouched per rule. Pool ≈ $100,094 (equity − residual).**
"""
if "## DAY 3 — Tuesday, September 1, 2026 — 4:30 PM FIRING" not in ar:
    ar = ar.replace(marker, d3 + "\n" + marker, 1)
    tmp = AR + ".tmp"; open(tmp, "w").write(ar); os.replace(tmp, AR)

print("board: 8 messages sent (1 firing + 7 termination notices)")
print("dashboard: statuses, funds, hr_board ->", len(f["hr_board"]), "running entries")
print("ar_log: DAY 3 section filed")