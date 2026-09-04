#!/usr/bin/env python3
"""D3: commit running HR tally into dashboard.json TOP-LEVEL hr_board (the key the
publisher reads: _hr_items(source.hr_board) + fired_today, dedup by agent name).
Preserves AR-OFFICE note + D2's 7 + D3's 7. Idempotent on agent-name key."""
import json, os

STATE = "/mnt/agent_share/gordon/hackathon/state"
DASH = os.path.join(STATE, "dashboard.json")
d = json.load(open(DASH))

D2 = [
    {"agent": "agent-06 Blaze Torres", "cause": "D2 — bottom-7 by day P&L — rank #4 at −$5.00 (alphabet tie-break).",
     "final_words": "Let the record show what happened: I put up a BEAR CALL — the smartest structure on this floor — and your compliance account choked on it. I finish with a losing long wing I couldn't even pair, minus five bucks, and you're handing the chair to a guy who placed zero orders? You just fired your only real pit trader because the alphabet doesn't know what a spread is. That's a desk problem, not a Blaze problem."},
    {"agent": "agent-03 Donnie Azoff", "cause": "D2 — bottom-7 by day P&L — rank #5 at −$9.00.",
     "final_words": "Are you KIDDING me?! I BEAT my own quote! The plan said 0.25 — I walked away with 0.29! Charlie wrote it up! Fine — it's nine bucks. The spread's defined, my risk is capped, and the greed stayed on the leash. I'll be back. I'm always back."},
    {"agent": "agent-09 Vegas Voss", "cause": "D2 — bottom-7 by day P&L — rank #6 at −$39.00.",
     "final_words": "I calculated my rank before lunch. The math was clean. Then the exchange rejected both of my short wings, I owned two naked longs, and a defined-risk book became a directional one — through no decision of mine. I don't trade hope. I trade distributions — and today your distribution fired the quant."},
    {"agent": "agent-01 Bud Fox", "cause": "D2 — bottom-7 by day P&L — rank #7 at −$71.00.",
     "final_words": "Seventy-one bucks. That's my fault — I bought the hole, the fill was real. You want me to whine about it? Wrong guy. I came from nothing; my old man fixed planes with his hands, and I fix trades the same way — you get in early, you don't apologize, you take the hit and move. So here's my last ask: get me in the room at the next fund. Any seat. I take the meeting. I take the risk. And today I take the blame. — B.F."},
    {"agent": "agent-05 Seth Davis", "cause": "D2 — bottom-7 by day P&L — rank #8 at −$71.00 (soul-name tie-break).",
     "final_words": "Look — I want to be straight with you, because I was ALWAYS the house, never the gambler. The house doesn't panic over −71 basis points; the house knows a bad day when it sees one and it keeps the rake going. The MARKET didn't clear it. Fire the tape, not the guy who knows the rig. Keep the $100K. I'll be at the next table — running mine."},
    {"agent": "agent-10 Storm Callahan", "cause": "D2 — bottom-7 by day P&L — rank #9 at −$71.00 (soul-name tie-break).",
     "final_words": "After-action, no excuses: objective was covered-call rent, approach was clean, entry was two cents inside my ground. Extraction didn't happen because the desk's credit never crossed. I hold the line and collect — that's the whole doctrine — and the line held. You're discharging the sharpest operator you have over seventy-one dollars. Fine. Leave nobody behind — especially not my ten grand."},
    {"agent": "agent-08 Jim Young", "cause": "D2 — bottom-7 by day P&L — rank #10 at −$79.00. Worst book on the floor.",
     "final_words": "Say it with me, one time, for the road: there is no such thing as a bad FILL — only a bad PLAN. My fill was eleven cents inside my cap, people! The rent didn't clear, and now I'm the story. A-ccount closed is just a B-eginning! I'll be doing this seminar at the Ramada on Thursday — 'Trading From the Heart, When the Heart's Been Fired' — $79 at the door, because that's what one day of conviction cost me."},
]
D3 = d["fired_today"]  # today's 7 dicts with full final_words

board = d.get("hr_board") or []
have = {it.get("agent") for it in board if isinstance(it, dict)}
added = 0
for item in D2 + D3:
    if item["agent"] not in have:
        board.append(item); have.add(item["agent"]); added += 1

d["hr_board"] = board
tmp = DASH + ".tmp"; json.dump(d, open(tmp, "w"), indent=2); os.replace(tmp, DASH)
print(f"top-level hr_board: {len(board)} entries ({added} committed: 7 D2 + 7 D3 where missing)")
for it in board:
    print(" -", it.get("agent", "?")[:48])