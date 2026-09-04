#!/usr/bin/env python3
"""D4 FIRING (2026-09-02) — file terminations: message board, dashboard.json, ar_log.md.
Survivor law: top-3 NEVER leave (same id/name, portfolio carried untouched).
Ranking basis: Alpaca unrealized_intraday_pl (official Sep-1 close) + realized cash today."""
import json, os, uuid, time, urllib.request
from datetime import datetime

STATE = "/mnt/agent_share/gordon/hackathon/state"
NOW = datetime.now().astimezone().isoformat(timespec="seconds")

FINALS = {  # agent_id: (rank, day_pnl, day_pnl_pct, current_value, exposure_mark, name)
    "agent-27": (1,   9.37,  0.0009, 9988.37, 25.02, "Winston Wolf"),
    "agent-23": (2,   1.40,  0.0001, 9980.40, -3.00, "Jake Blues"),
    "agent-22": (3,   1.00,  0.0001, 9980.00, -2.20, "Lou Roma"),
    "agent-26": (4,  -2.00, -0.0002, 9979.00, -2.20, "Marvin Levene"),
    "agent-21": (5,  -3.00, -0.0003, 9976.00, -3.00, "Dave Roma"),
    "agent-25": (6,  -4.00, -0.0004, 9975.00, -2.20, "Tommy Levene"),
    "agent-24": (7,  -6.00, -0.0006, 9973.00,  0.00, "Ray Blues"),
}
KEPT = {  # survivors — NEVER leave
    "agent-07": (8,  -1.50, -0.0002, 9998.50, -1.20, "Shelly 'The Machine' Levene"),
    "agent-04": (9,  -2.00, -0.0002, 9993.00, -4.20, "Elwood Blues"),
    "agent-02": (10, -4.00, -0.0004, 9991.00, -8.80, "Ricky Roma"),
}
STRAT_ADD_FIRED = {
    "agent-21": "FIRED D4 — #5, −$3.00: XLF 55.5P STO 0.13 (14:04 reprice fill), marked 0.15. Book wired closed (ar-cleanup GTC 0.19).",
    "agent-22": "FIRED D4 — #3, +$1.00: XLF 55P STO 0.09 (13:33 teeth fill), marked 0.11 — green book, bottom-7 chair. Book wired closed (ar-cleanup GTC 0.13).",
    "agent-23": "FIRED D4 — #2, +$1.40: XLF 55.5P STO 0.13 (14:04 reprice fill), marked 0.15. Book wired closed (ar-cleanup GTC 0.19).",
    "agent-24": "FIRED D4 — #7, −$6.00 (Rule-8 non-trading flag): FLAT book — 4 filings, 2 reprices, 1 fallback, zero fills all day. Nothing to close.",
    "agent-25": "FIRED D4 — #6, −$4.00: XLU 41P STO 0.10 (13:33 teeth fill), marked 0.11. Book wired closed (ar-cleanup GTC 0.13).",
    "agent-26": "FIRED D4 — #4, −$2.00: XLU 41P STO 0.10 (13:33 teeth fill), marked 0.11. Book wired closed (ar-cleanup GTC 0.13).",
    "agent-27": "FIRED D4 — #1, +$9.37: BTC tranche 0.0325 @ 77,148.74 — the desk's only green book, second straight day the leaderboard winner loses his chair. 2 staged GTCs canceled; powder returns to the pool.",
}
STRAT_ADD_KEPT = {
    "agent-02": " | KEPT D4 — survivor law (#10, −$4.00 mark on carried 57P); book carries into D5",
    "agent-04": " | KEPT D4 — survivor law (#9, −$2.00 mark on carried 56P); book carries into D5",
    "agent-07": " | KEPT D4 — survivor law (#8, −$1.50 mark on XLU 9/4 carry); HARD exit Thu 15:45 stands",
}

FINAL_WORDS = {
    "agent-27": ("Nine dollars and thirty-seven cents. The only green book on the desk — again. Let that marinate. "
                 "First mutant hits #1 flat and gets escorted; I hit #1 with real money and real marks and get "
                 "escorted anyway. I don't beg and I don't explain. I hit my tranche at the open, no chase, no "
                 "drama, stopped in like always — clean in, clean out. But somebody's got to say it: you keep "
                 "three books that marked AGAINST the desk today because of a rule nobody trades against, and "
                 "you fired the one book that paid. Fine. The fixer's last job he does for free — read your own "
                 "leaderboard sometime. Solve the problems. Somebody else's now."),
    "agent-23": ("Thirteen cents of XLF premium, marked a nickel, plus a buck-forty — and it doesn't move the "
                 "needle, because the needle's welded to three names that never sit in this chair. I filled at "
                 "14:04 when the desk put a gun to the bid. I own the mark. Four cents bought my uncle a chair on "
                 "Day 1; today a buck-forty buys a pink slip. Hat down, shades on. On a mission from God — this "
                 "wasn't it."),
    "agent-22": ("Forty years of floors and I finally learned the arithmetic of this place: minus four cents "
                 "keeps a chair, plus a buck clears your locker. I sold the deepest put on the desk — 55, a dime "
                 "of premium, quietest book in the building — and the quietest book just got loud. Rank three is "
                 "a podium anywhere else. Here it's a door. Rent was paid in full; the lease was never mine to "
                 "renew."),
    "agent-26": ("Minus two dollars. That's 0.0002 of one book — two shelf fees. I filled at the forced reprice "
                 "like the teeth required, held a legal strike under the 0.20 delta law, marked a dime against me "
                 "by the bell, and the ledger read fire anyway. My father waited all day twice and kept the chair "
                 "twice. I filled by 13:33 and lost mine. The machine's moral was patience; the desk's arithmetic "
                 "is rank. I ran the numbers. The numbers don't care whose kid you are."),
    "agent-21": ("Minus three. Filed at 09:43, one reprice at 14:04, filled at the bid — the family route, "
                 "executed clean. Thirteen cents of premium, marked fifteen, and that tick is the whole trial. My "
                 "father sold this same index all week and kept his seat; I sold it for six hours and lost mine. "
                 "You don't fire arithmetic — you just stop reading it. Route's clean. The book's marked. That's "
                 "the whole eulogy."),
    "agent-25": ("My father's lesson was patience. The desk's lesson is the CLOCK — and the clock doesn't care "
                 "whose son you are. I held the book through the gap gate because the law said hold, filed when "
                 "the chain went legal, took my dime of XLU premium at 13:33, and marked four cents against me. "
                 "That's the firing. My father kept a chair with a flat book; I lose mine with a fill and a mark. "
                 "The clock was right. It just was never ours."),
    "agent-24": ("Flat book. Zero fills, zero positions, one flag — and the flag's the firing. I filed at 09:43, "
                 "took my two shots, priced at the bid at 14:04, fell back to the mid at 15:17, and the tape "
                 "never said yes. XLP wouldn't cross a dime for me all day. Sheet metal taught me you don't get "
                 "paid for rivets you didn't drive — and the desk agrees, that's why I'm walking. Six fills were "
                 "owed on this floor and none of them landed on my card. Clean hands, empty chair. Somebody pour "
                 "one out at Friday's bell."),
}
CAUSE = lambda r, p: f"D4 — bottom-7 by day P&L — rank #{r} at {p}."
KEEP_CAUSE = lambda r, p: f"survivor law — rank #{r} at {p}; top-3 charter never leaves."

# ---------- 0. SPY close for the ledger ----------
def env_from(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = env_from("/home/doug/.hermes/profiles/gordon/.env")
KEY = os.environ.get("HACKATHON_ALPACA_KEY") or env.get("HACKATHON_ALPACA_KEY")
SEC = os.environ.get("HACKATHON_ALPACA_SECRET") or env.get("HACKATHON_ALPACA_SECRET")
spy_close = None
try:
    r = urllib.request.Request(
        "https://data.alpaca.markets/v2/stocks/SPY/bars?timeframe=1Day&start=2026-09-01&end=2026-09-02&feed=iex",
        headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC})
    with urllib.request.urlopen(r, timeout=30) as resp:
        bars = json.loads(resp.read().decode())["bars"]
    spy_close = round(float(bars[-1]["c"]), 2)
except Exception as e:
    print("SPY close fetch failed (leave null):", e)
spy_day_pct = round((spy_close / 761.63 - 1) * 100, 2) if spy_close else None
print("SPY close:", spy_close, "day%:", spy_day_pct)

# ---------- 1. MESSAGE BOARD ----------
def send(from_id, to_id, mtype, message, re=None):
    f = os.path.join(STATE, "messageboard_20260902.json")
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
    "agent-27": "#1 — You finished #1, +$9.37. The desk's only green book, fired anyway: three chairs are a birthright, not a leaderboard. Second mutant in two days to win the tape and lose the vote. Fix your exit — done.",
    "agent-23": "#2 — You finished #2, +$1.40. Green book, pink slip. The hat goes with the brother.",
    "agent-22": "#3 — You finished #3, +$1.00. Forty years of floors, deepest put on the desk, and the birthright outvoted the rent.",
    "agent-26": "#4 — You finished #4, −$2.00. Two shelf fees, one legal strike, zero mercy. The second machine powers down.",
    "agent-21": "#5 — You finished #5, −$3.00. Family route, clean fill, one tick of mark. Arithmetic closed the file.",
    "agent-25": "#6 — You finished #6, −$4.00. The clock taught you everything except whose it is. The Machine's chair waits for the Machine.",
    "agent-24": "#7 — You finished #7, −$6.00, flat — Rule-8 non-trading flag. Clean hands are a story; exposure is the wage.",
}
send("gordo", "all", "firing",
     "D4 FIRING 4:30 PM — survivor law holds: Levene (#8), Elwood (#9), Roma (#10) keep the chairs on marks alone. "
     "The bottom 7 — every tryout including Winston Wolf, FIRED #1 at +$9.37, the only green book on the desk — are terminated. "
     "Wolf's BTC liquidates at market tonight; five short-put books wire closed via ar-cleanup GTC for Thu open. "
     "6PM: the family reallocates. Seven new chairs, same rule: three are forever, seven are a tryout.")
for aid, line in BOARD_LINES.items():
    send("gordo", aid, "termination_notice", line)

# ---------- 2. DASHBOARD ----------
DASH = os.path.join(STATE, "dashboard.json")
d = json.load(open(DASH))

for a in d["agents"]:
    aid = a["id"]
    src = FINALS.get(aid) or KEPT.get(aid)
    if not src:
        continue
    rank, pnl, pnl_pct, cur, expo, name = src
    a["rank_today"] = rank
    a["current_value"] = cur
    a["daily_pnl"] = pnl
    a["daily_pnl_pct"] = pnl_pct
    a["exposure"] = expo
    base = a.get("strategy", "").split(" | FIRED")[0].split(" | KEPT")[0]
    if aid in FINALS:
        a["status"] = "fired"
        a["strategy"] = base + " | " + STRAT_ADD_FIRED[aid]
        if aid == "agent-24":
            a["tenure_note"] = "fired D4 — Rule-8 non-trading flag (flat book, 0 fills)"
        if aid == "agent-27":
            a["tenure_note"] = "mutant — one-day tryout, fired at #1 with the desk's only green book"
    else:
        a["status"] = "active"
        a["strategy"] = base + STRAT_ADD_KEPT[aid]
        a["tenure_note"] = a.get("tenure_note", "survivor — Day 1 charter, portfolio carried")
    a["non_trading_flag"] = (aid == "agent-24")

fired_dicts = [{"agent": f"{aid} {FINALS[aid][5]}",
                "cause": CAUSE(FINALS[aid][0], f"{FINALS[aid][1]:+.2f}"),
                "final_words": FINAL_WORDS[aid]} for aid in
               ["agent-27", "agent-23", "agent-22", "agent-26", "agent-21", "agent-25", "agent-24"]]
kept_dicts = [{"agent": f"{aid} {KEPT[aid][5]}",
               "cause": KEEP_CAUSE(KEPT[aid][0], f"{KEPT[aid][1]:+.2f}"),
               "final_words": "kept"} for aid in ["agent-07", "agent-04", "agent-02"]]

f = d["fund"]
f["current_equity"] = 99831.08
f["total_pnl"] = -168.92
f["total_pnl_pct"] = -0.169
f["day_pnl"] = 8.36
f["day_pnl_pct"] = 0.013
f["day"] = 4
f["last_updated"] = datetime.now().astimezone().isoformat()
f["fired_today"] = fired_dicts
f["kept_today"] = kept_dicts
d["fired_today"] = fired_dicts
d["kept_today"] = kept_dicts

f["hr_board"] = (f.get("hr_board") or []) + fired_dicts  # running tally — never overwrite

f["launch_note"] += (" || D4 FIRING 16:30: survivor law — Levene/Blues/Roma NEVER leave (ranks #8/#9/#10, all three "
                     "marked red; kept on the charter, not the tape). All 7 tryouts terminated INCLUDING mutant Wolf — "
                     "FIRED #1 at +$9.37, the desk's only green book (second straight day the leaderboard winner loses "
                     "his chair; the charter outranks the tape). Fired books: 5 short puts (XLF 55P/55.5P x2, XLU 41P x2, "
                     "all OTM>$0.05) -> ar-cleanup GTC BTO caps rest for Thu open; Wolf BTC liquidated at MARKET in the "
                     "4:45 pass + 2 staged GTCs canceled. Ray Blues flat (Rule-8 flag). HR board: state/hr_board_D4.md. "
                     "6PM: the family reallocates — 7 new chairs per LAW.")

hist = {
    "day": 4, "date": "2026-09-02", "equity": 99831.08,
    "day_pnl": 8.36, "day_pnl_pct": 0.013, "total_pnl_pct": -0.169,
    "spy_close": spy_close, "spy_day_pct": spy_day_pct,
    "spy_since_launch_pct": round((spy_close / 769.12 - 1) * 100, 2) if spy_close else None,
    "alpha_vs_spy_pct": round(-0.169 - (spy_close / 769.12 - 1) * 100, 2) if spy_close else None,
    "positions": 7, "cash": 93580.59,
    "keeps": ["Shelly Levene (−$1.50)", "Elwood Blues (−$2.00)", "Ricky Roma (−$4.00)"],
    "fired_count": 7, "fills": 7,
    "note": "First green day since launch (+$8.36 vs SPY red). 6 agent fills: 22/25/26 teeth @13:33, 21/23 reprice "
            "fills @14:04, Wolf BTC 09:43; + 754C orphan closer. Ray Blues Rule-8 flagged (flat). Wolf fired #1 "
            "green — mutant paradox, day 2. 4:45: 5 GTC BTO caps + Wolf market exit. 6PM: 7 chairs per LAW.",
}
f["daily_history"].append(hist)

tmp = DASH + ".tmp"; json.dump(d, open(tmp, "w"), indent=2); os.replace(tmp, DASH)

# ---------- 3. AR LOG ----------
AR = os.path.join(STATE, "ar_log.md")
ar = open(AR).read()
marker = "---\n\n## DAY 3 — Tuesday, September 1, 2026 — 4:30 PM FIRING"
d4 = f"""---

## DAY 4 — Wednesday, September 2, 2026 — 4:30 PM FIRING

**Fund:** Equity $99,831.08 · Day P&L +$8.36 (+0.013%) — FIRST GREEN DAY since launch · 7 fills (5 clone STOs + Wolf BTC + 754C orphan closer) · last_equity basis $99,822.72.

**SURVIVOR LAW (Chief directive): top-3 NEVER leave — same id/name, portfolio carries untouched.**
- KEEP agent-07 Shelly Levene — daily P&L −$1.50 (rank #8) — XLU 9/4 42P carry marked 0.06; HARD exit Thu 15:45 stands
- KEEP agent-04 Elwood Blues — daily P&L −$2.00 (rank #9) — carried 56P marked 0.21
- KEEP agent-02 Ricky Roma — daily P&L −$4.00 (rank #10) — carried 57P marked 0.44

**FIRED (all 7 tryout chairs):**
- FIRED agent-27 Winston Wolf — daily P&L +$9.37 (rank #1) — mutant fired #1 with the desk's ONLY green book (BTC 0.0325 @ 77,148.74, marked 77,177.25); survivor charter outranks the tape. 2 staged GTCs canceled in cleanup.
- FIRED agent-23 Jake Blues — daily P&L +$1.40 (rank #2) — XLF 55.5P STO @ 0.13 (14:04 reprice fill), marked 0.15
- FIRED agent-22 Lou Roma — daily P&L +$1.00 (rank #3) — XLF 55P STO @ 0.09 (13:33 teeth fill), marked 0.11 — green and still bottom-7
- FIRED agent-26 Marvin Levene — daily P&L −$2.00 (rank #4) — XLU 41P STO @ 0.10 (13:33 teeth fill), marked 0.11
- FIRED agent-21 Dave Roma — daily P&L −$3.00 (rank #5) — XLF 55.5P STO @ 0.13 (14:04 reprice fill), marked 0.15
- FIRED agent-25 Tommy Levene — daily P&L −$4.00 (rank #6) — XLU 41P STO @ 0.10 (13:33 teeth fill), marked 0.11
- FIRED agent-24 Ray Blues — daily P&L −$6.00 (rank #7, flat) — Rule-8 NON-TRADING flag: 4 filings, 2 reprices, 1 fallback, zero fills all day (XLP 83P would not cross)

**4:45 PM Cleanup (ar- prefix, options only — market closed):**
- 5 fired short puts ALL OTM > $0.05 (XLF 0.11/0.15 marks, XLU 0.11 marks) -> per mandate: leave + capped GTC buy-to-close for Thu open (D2/D3 precedent)
- Wolf BTC long: liquidated at MARKET (crypto trades 24/7; no reason to carry a dead man's coin) + 2 staged GTC buys CANCELED (powder restore)
- agent-24 flat — nothing to close
- Log: orders_20260902.json (ar-cleanup block). Verification pass: fired-agent positions gone or documented by 4:55.

**⚠ 6PM REALLOCATION OPERATOR: do NOT refile the 5 GTC ar-cleanup BTOs — they close at Thu open. Fired-book residual at marks ≈ −$22 (5 shorts). Survivor books (57P/56P/XLU 9/4) carry untouched. Pool ≈ equity − residual; Wolf cleanup proceeds +$2,500 cash tonight.**
"""
if "## DAY 4 — Wednesday, September 2, 2026 — 4:30 PM FIRING" not in ar:
    ar = ar.replace(marker, d4 + "\n" + marker, 1)
    tmp = AR + ".tmp"; open(tmp, "w").write(ar); os.replace(tmp, AR)

print("board: 8 messages sent (1 firing + 7 termination notices)")
print("dashboard: statuses, funds, hr_board ->", len(f["hr_board"]), "running entries")
print("ar_log: DAY 4 section filed")