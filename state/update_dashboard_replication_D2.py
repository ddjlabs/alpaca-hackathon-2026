#!/usr/bin/env python3
"""D2->D3 6PM REPLICATION — rebuild dashboard.json roster for the spawn.
Survivors' seats -> clones (per BATTLE-PLAN-v2 replication design). Fund-level
P&L untouched (today's tape is history). Adds reallocation_note + wire for D3."""
import json
from datetime import datetime

DASH = "/mnt/agent_share/gordon/hackathon/state/dashboard.json"
d = json.load(open(DASH))

# Verbatim Sam lessons (state/lessons_D2.json), keyed by persona
L = {p: s for s in json.load(open("/mnt/agent_share/gordon/hackathon/state/lessons_D2.json"))
     for p in [s["persona"]]}

def les(*names):
    return [L[n]["lesson"] for n in names]

MOVIES = {
    "Johnny Blues": "Wall Street (1987) / The Blues Brothers",
    "Donald Blues": "Wall Street (1987) / The Blues Brothers",
    "Marcus Blues": "Wall Street (1987) / The Blues Brothers",
    "Brad Roma": "Wall Street (1987) / Glengarry Glen Ross",
    "Dean Roma": "Wall Street (1987) / Glengarry Glen Ross",
    "Eddie Roma": "Wall Street (1987) / Glengarry Glen Ross",
    "George Levene": "Wall Street (1987) / Glengarry Glen Ross",
    "Chester Levene": "Wall Street (1987) / Glengarry Glen Ross",
    "Walt Levene": "Wall Street (1987) / Glengarry Glen Ross",
    "Jared Stone": "Original — Bushwood Stratton",
}
PERSONAS = {
    "Johnny Blues": "Nephew of a legend; trades like the rent is due. Dark glasses, steady hands, zero panic. Sells puts on sectors the bond market is paying for; never chases.",
    "Donald Blues": "Ex-freight driver. Fixed route, fixed schedule, no surprises. Sells puts with a floor he could sleep on. Does not swerve.",
    "Marcus Blues": "Ex-session musician. Reads the tape like changes on a chart — structure first, then the turn. Metronome patience; never solos when the band is tight.",
    "Brad Roma": "The closer's cousin — closes with arithmetic instead of charm. Clean short sentences, never pleads, quotes the price and holds the silence.",
    "Dean Roma": "Speed model of the family chrome. Trades the first hour like a slot car — wire, quotes, card, done by 10:00. Every panic is somebody's discount.",
    "Eddie Roma": "Ex-amp rewirer. Finds where the current actually runs, not where the diagram says. Checks the pond before testing the water. Short sentences, strong coffee.",
    "George Levene": "The Machine's kid. Inherited the nerves, none of the desperation. Sells puts so deep the market has to burn to reach them — and files on time.",
    "Chester Levene": "Ex-hardware-store owner. Prices inventory like screws: cost, rent, shelf time. Carries a pocket note that reads 'flat won' — and knows how fragile that luck is.",
    "Walt Levene": "Ex-long-haul driver. Knows what a floor is: what holds when everything shakes. Sells puts boring enough to pay rent and never make the news.",
    "Jared Stone": "Fresh meat. Quant forums and crypto Discords, fluent in order books before he could book a hotel room. Fast, cocky, correct just often enough. Momentum with hard stops, zero romance.",
}
STRATS = {
    "agent-11": "XLF CSP: STO XLF260918P00057500 9/18 @ 0.55 (pre-mkt 0.49/0.61, delta -0.41) — spawned for D3",
    "agent-12": "XLF CSP: STO XLF260918P00054000 9/18 @ 0.08 (pre-mkt 0.07/0.09, delta -0.066) — spawned for D3",
    "agent-13": "XLF CSP: STO XLF260918P00056000 9/18 @ 0.20 (pre-mkt 0.19/0.22, delta -0.178) — spawned for D3",
    "agent-14": "XLF CSP: STO XLF260918P00055000 9/18 @ 0.125 (pre-mkt 0.11/0.14, delta -0.107) — spawned for D3",
    "agent-15": "XLF CSP: STO XLF261016P00057000 10/16 @ 0.82 (pre-mkt 0.80/0.85, delta -0.363) — spawned for D3",
    "agent-16": "XLF CSP: STO XLF261016P00056000 10/16 @ 0.55 (pre-mkt 0.52/0.60, delta -0.263) — spawned for D3",
    "agent-17": "XLF CSP: STO XLF261016P00055000 10/16 @ 0.38 (pre-mkt 0.37/0.39, delta -0.186) — spawned for D3",
    "agent-18": "XLU CSP: STO XLU260918P00042000 9/18 @ 0.42 (pre-mkt 0.36/0.49, delta -0.408) — spawned for D3",
    "agent-19": "XLU CSP: STO XLU260918P00040000 9/18 @ 0.07 (pre-mkt 0.01/0.13, delta -0.085) — spawned for D3",
    "agent-20": "CRYPTO MOMENTUM: BTC ~78,950 (7d +1.3%) / ETH ~2,476 (7d +2.0%); light size, hard stops, 24/7 — spawned for D3",
}
INHERITED = {
    "agent-11": les("Blaze Torres", "Storm Callahan", "Donnie Azoff"),
    "agent-12": les("Blaze Torres", "Vegas Voss", "Donnie Azoff"),
    "agent-13": les("Storm Callahan", "Bud Fox", "Seth Davis"),
    "agent-14": les("Blaze Torres", "Storm Callahan", "Jim Young"),
    "agent-15": les("Storm Callahan", "Donnie Azoff", "Vegas Voss"),
    "agent-16": les("Jim Young", "Bud Fox", "Blaze Torres"),
    "agent-17": les("Seth Davis", "Storm Callahan", "Donnie Azoff"),
    "agent-18": les("Seth Davis", "Blaze Torres", "Jim Young"),
    "agent-19": les("Bud Fox", "Seth Davis", "Vegas Voss"),
    "agent-20": [],
}
PARENTS = {"agent-11": "agent-04", "agent-12": "agent-04", "agent-13": "agent-04",
           "agent-14": "agent-02", "agent-15": "agent-02", "agent-16": "agent-02",
           "agent-17": "agent-07", "agent-18": "agent-07", "agent-19": "agent-07",
           "agent-20": None}
GENS = {k: (2 if k != "agent-20" else 1) for k in INHERITED}
NAMES = {"agent-11": "Johnny Blues", "agent-12": "Donald Blues", "agent-13": "Marcus Blues",
         "agent-14": "Brad Roma", "agent-15": "Dean Roma", "agent-16": "Eddie Roma",
         "agent-17": "George Levene", "agent-18": "Chester Levene", "agent-19": "Walt Levene",
         "agent-20": "Jared Stone"}
ALLOC = {"agent-11": 9986, "agent-12": 9986, "agent-13": 9986, "agent-14": 9986,
         "agent-15": 9986, "agent-16": 9986, "agent-17": 9987, "agent-18": 9987,
         "agent-19": 9987, "agent-20": 9986}

agents = []
for aid in INHERITED:
    slug = "-".join(aid.split("-")[2:])  # e.g. johnny-blues
    agents.append({
        "id": aid, "name": NAMES[aid], "persona": PERSONAS[NAMES[aid]], "movie": MOVIES[NAMES[aid]],
        "allocation": ALLOC[aid], "current_value": ALLOC[aid], "daily_pnl": 0.0,
        "daily_pnl_pct": 0.0, "status": "active", "strategy": STRATS[aid], "strikes": 0,
        "generation": GENS[aid], "parent": PARENTS[aid], "avatar": slug, "exposure": 0,
        "inherited_lessons": INHERITED[aid],
    })
d["agents"] = agents

d["fund"]["reallocation_note"] = ("6PM REPL D2->D3: pool $99,863.07 -> $9,986 x 10, leftover $3.07 -> champion's family "
                                  "(Levene clones: George +$1.03 dust, Chester +$1.02, Walt +$1.02). "
                                  "7x XLF vs Richard's $40K cap (97.4% used); 2 Levene clones rotated to XLU puts. "
                                  "Survivor shorts wired closed ar-cleanup-agent-02-p57c/agent-04-p56c for Tue open. "
                                  "Mutant agent-20 crypto_momentum.")

d["fund"]["launch_note"] += (" || 6PM REPLICATION: 9 gen-2 clones (Blues x3, Roma x3, Levene x3 — all CSP family; "
                             "2 rotated to XLU for sector cap) + mutant Jared Stone (crypto_momentum). "
                             "Sam's 7 lessons injected verbatim into 9 souls. Survivor books (Roma 57P, Blues 56P) "
                             "wired closed via ar- GTC closers; 7 resting orders fill Tue open.")

d["fund"]["wire"] = {
  "sectors": [
    {"time": "18:30", "headline": "Replication verdict: the tape paid the put-sellers — 3/3 survivors ran XLF CSPs; gen-2 keeps the doctrine with mutated strikes/expiries (57.5P fat end to 40P moat)"},
    {"time": "18:30", "headline": "Sector discipline: XLF bucket at 97.4% of Richard's $40K cap after clone math; 2 Levene clones rotated to XLU 42P/40P — utilities, defensive family, not a new bet"},
    {"time": "18:30", "headline": "Month-end done; Tuesday tape opens with ISM 10am — theta day, not a chase day"}
  ],
  "options": [
    {"time": "18:30", "headline": "Pre-open marks locked for all 9 clone books (XLF 55/55.5/56/57.5/57(10/16)/56(10/16)/55(10/16), XLU 42P/40P) — plans price at bid-mid, one reprice, then take the bid"},
    {"time": "18:30", "headline": "XLF 9/18 57.5P carries the fattest new rent (0.49/0.61, delta -0.41) — Johnny Blues owns the tightrope; Walt Levene's XLU 40P is a death-spread market (0.01/0.13): reprice once or fall back"},
    {"time": "18:30", "headline": "All books exit-ready by Thu close per desk rule — no naked short premium into Fri 8:30 payrolls; VIX ~14 handles stay cheap until gamma wakes"}
  ],
  "macro": [
    {"time": "18:30", "headline": "Warsh hangover persists: Sept hike odds ~56%, 2Y 4.36% — hawkish rates tape keeps the book defensive (XLF/XLU), crypto trades the same fear in the other direction"},
    {"time": "18:30", "headline": "Hormuz war premium intact: Brent >$91; GDX -3.8% Friday says real rates still rule gold — ignore the conflict-hedge narratives"},
    {"time": "18:30", "headline": "Freight train: ISM Tue 10am, ADP + DELL/PANW/MDB Wed, LULU/ZS Thu, NFP Fri 8:30 inside the fund's final 2.5 hours"}
  ]
}

d["fired_today"] = ["agent-06 Blaze Torres", "agent-03 Donnie Azoff", "agent-09 Vegas Voss",
                    "agent-01 Bud Fox", "agent-05 Seth Davis", "agent-10 Storm Callahan",
                    "agent-08 Jim Young"]
d["kept_today"] = ["agent-07 Shelly Levene", "agent-02 Ricky Roma", "agent-04 Elwood Blues"]
d["hr_board"] = []
d["fund"]["last_updated"] = datetime.now().astimezone().isoformat()

json.dump(d, open(DASH, "w"), indent=2)
print("roster rebuilt:", datetime.now().isoformat())
print("agents:", [(a['id'], a['name'], a['generation'], a['allocation']) for a in agents])
print("injected lesson counts:", {k: len(v) for k, v in INHERITED.items()})