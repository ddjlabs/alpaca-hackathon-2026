"""D4 post-deploy bookkeeping: message board notices, dashboard strategy updates,
AR log entry, triggers.json sync. Atomic writes throughout. Never prints credentials."""
import json, os, uuid, time
from datetime import datetime

STATE = '/mnt/agent_share/gordon/hackathon/state'
NOW = datetime.now().astimezone().isoformat(timespec='seconds')

def atomic_json(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)

# ---------- 1. MESSAGE BOARD (new day file) ----------
def send(from_id, to_id, mtype, message, re=None):
    return {"id": f"msg-{int(time.time())}-{uuid.uuid4().hex[:4]}", "ts": NOW,
            "from": from_id, "to": to_id, "type": mtype, "re": re or "d4-open-deploy",
            "message": message}

notices = [
 send("charlie", "agent-21", "order_filed",
  "FILED 09:43 ET — STO XLF260918P00055500 (9/18 55.5P) 1 @ 0.16 limit, TIF=day, live quote 0.11x0.21, live delta -0.148 (law <=0.20 honored). GAP GATE: repriced band — plan's 0.19 was the 19:05 mid; live mid took it to 0.16. Reserve $5,550. Stop: BTC 0.57 OR XLF<=54.50 intraday. 09:52 reprice doctrine: one reprice to bid, take the bid by 10:00. Exit-ready Thu close — payrolls rule."),
 send("charlie", "agent-22", "order_filed",
  "FILED 09:43 ET — STO XLF260918P00055000 (9/18 55P) 1 @ 0.14 limit, TIF=day, live quote 0.12x0.16, live delta -0.121. Your walk-up survives the gate: repriced from plan 0.16 to live mid 0.14, still the deepest legal floor on the XLF shelf. Reserve $5,500. Stop: BTC 0.48 OR XLF<=53.50 intraday. One reprice at 09:52, take the bid by 10:00. Exit-ready Thu close — payrolls rule."),
 send("charlie", "agent-23", "order_filed",
  "FILED 09:43 ET — STO XLF260918P00055500 (9/18 55.5P) 1 @ 0.16 limit, TIF=day, live quote 0.11x0.21, live delta -0.148. Same shelf as your brother, repriced 0.19 -> 0.16 live mid. Reserve $5,550. Stop: BTC 0.57 OR XLF<=54.50 intraday. One reprice at 09:52, take the bid by 10:00. Exit-ready Thu close — payrolls rule."),
 send("charlie", "agent-24", "order_filed",
  "FILED 09:43 ET — STO XLP260918P00083000 (9/18 83P) 1 @ 0.28 limit, TIF=day, live quote 0.23x0.33, live delta -0.183 (law honored; your spawned 84P ran -0.301 and the walk-down already saved the card). GAP GATE: repriced 0.30 -> 0.28 live mid. Reserve $8,300 (83% of book — clears the 95% line). Stop: BTC 0.90 OR XLP<=81.50 intraday. Tightest quote on the defensive board — one reprice at 09:52, take the bid by 10:00. Exit-ready Thu close — payrolls rule."),
 send("charlie", "agent-25", "order_held",
  "HELD at the gap gate — your card did NOT file. XLU gapped -0.85% and IV popped (0.163 -> 0.184): the 41P you were cleared to sell now runs live delta -0.212, OVER the 0.20 desk law. Fallback 40.5P live mid 0.065 is under Donald's min-rent floor; the 42P runs -0.38. NO legal filing exists at 09:38 ET — the law outranks the quota, so you sit flat. Rule 8 clock arms 14:30: if the chain re-ranges legal before then, Charlie re-files at the live mid. Do NOT file an illegal strike to make quota. Flat beats a stop-out; absent is just flat."),
 send("charlie", "agent-26", "order_held",
  "HELD at the gap gate — same book as your brother. XLU -0.85% pushed the shared 41P to live delta -0.212 > 0.20 law; 40.5P fails min-rent (0.065 mid); 42P fails the law outright (-0.38). No legal leg exists this morning — you hold flat, no strike. 14:30 clock: Charlie re-files only if the chain re-ranges legal. The ledger remembers who respected the law when the tape moved it."),
 send("charlie", "agent-27", "order_filled",
  "TRANCH 1 FILLED 09:43 ET — BTC/USD 0.0325 @ 77,148.74 (~$2,507, 25% of book). Engagement floor met by EXECUTION, ninety seconds into your tenure — Stone stood still and got fired at #1; you moved. Resting: staged BTC 0.0325 @ 75,800 GTC + ETH 0.6 @ 2,365 GTC (both buy weakness ~1.7-1.9% under live marks; desk cancels Thu 15:45 if unfilled — powder restores). Powder now ~74.5%. Hard stops: -2.5% BTC / -3.0% ETH on filled size, filed as cards the session they trigger. No averaging down beyond staged limits. The problem never existed."),
]
mb_path = f'{STATE}/messageboard_20260902.json'
board = json.load(open(mb_path)) if os.path.exists(mb_path) else []
existing_re = {m.get('re') for m in board}
for n in notices:
    if n['re'] not in existing_re or True:
        board.append(n)
atomic_json(mb_path, board)
print('board entries:', len(board))

# ---------- 2. DASHBOARD strategy strings ----------
dpath = f'{STATE}/dashboard.json'
dash = json.load(open(dpath))
strat = {
 'agent-21': "XLF CSP: FILED 09:43 — STO 9/18 55.5P @ 0.16 live-mid reprice (delta -0.148), DAY order resting; 09:52 reprice doctrine; stop BTC 0.57 / XLF<=54.50",
 'agent-22': "XLF CSP: FILED 09:43 — STO 9/18 55P @ 0.14 live-mid reprice (delta -0.121), DAY order resting; 09:52 reprice doctrine; stop BTC 0.48 / XLF<=53.50",
 'agent-23': "XLF CSP: FILED 09:43 — STO 9/18 55.5P @ 0.16 live-mid reprice (delta -0.148), DAY order resting; 09:52 reprice doctrine; stop BTC 0.57 / XLF<=54.50",
 'agent-24': "XLP CSP: FILED 09:43 — STO 9/18 83P @ 0.28 live-mid reprice (delta -0.183), DAY order resting; 09:52 reprice doctrine; stop BTC 0.90 / XLP<=81.50",
 'agent-25': "XLU CSP: HELD at gap gate — XLU -0.85% pushed 41P live delta to -0.212 > 0.20 law; 40.5P fails min-rent; NO legal leg. Flat book; 14:30 clock governs re-file",
 'agent-26': "XLU CSP: HELD at gap gate — shared 41P live delta -0.212 > 0.20 law; no legal strike exists. Flat book; 14:30 clock governs re-file",
 'agent-27': "CRYPTO MOMENTUM: BTC tranche 1 FILLED 0.0325 @ 77,148.74 at open (engagement by execution); staged BTC 75,800 + ETH 2,365 GTC resting; powder ~74.5%; hard stops -2.5%/-3.0%",
}
for a in dash['agents']:
    if a['id'] in strat:
        a['strategy'] = strat[a['id']]
dash['deployment_note_D4'] = ("9:35 deploy 2026-09-02: gap gate NORMAL band (SPY +0.04%, QQQ -0.27%, XLF +0.37%, XLP +0.01%); XLU -0.85% repriced band. "
 "4 option legs filed at LIVE mids (Dave 55.5P 0.16, Lou 55P 0.14, Jake 55.5P 0.16, Ray XLP 83P 0.28). "
 "XLU 41P clone legs (Tommy/Marvin) HELD — live delta -0.212 over law, no legal strike. "
 "Wolf BTC market tranche filled 0.0325 @ 77,148.74; 2 staged GTC resting. AR-cleanup residuals filled at open (6 covers + QQQ 754C).")
if isinstance(dash.get('fund'), dict):
    dash['fund']['last_updated'] = NOW
atomic_json(dpath, dash)
print('dashboard updated')

# ---------- 3. AR LOG ----------
ar = f"""## DAY 4 — 9:35 OPEN DEPLOYMENT (2026-09-02 09:38-09:44 ET)
- GAP GATE (live snapshots vs prev close, iex): SPY +0.04% (761.63->761.91) | QQQ -0.27% (707.65->705.76) | XLF +0.37% (57.21->57.42, WITH our short puts) | XLP +0.01% | XLU -0.85% (42.57->42.21, repriced band). Regime: NORMAL OPEN — plans deploy as filed with stock/option legs re-anchored to live mids per 0.5-1.5% doctrine. Ernie's 07:00 futures read (ES -1.3%) held in cash overnight; WTI +8.4% is the tape's master.
- AR-CLEANUP VERIFIED at open: 6 fired-class short-put covers + agent-09 QQQ 754C sell ALL FILLED 09:30:04-09:31:32 (book was 0 positions / 0 open orders pre-deploy). Survivors carried untouched: Roma XLF 57P, Elwood XLF 56P, Levene XLU 9/4 42P (hard exit Thu 15:45).
- FILED 09:43 ET (4 option legs, live-mid re-anchored, TIF=day, position_intent=sell_to_open, 1ct each):
  - agent-21 Dave Roma STO XLF260918P00055500 @ 0.16 (plan 0.19 was 19:05 mid; live 0.11x0.21; delta -0.148) — id agent-21-20260902-opt-1, order 40f7fcdb
  - agent-22 Lou Roma STO XLF260918P00055000 @ 0.14 (plan 0.16; live 0.12x0.16; delta -0.121) — id agent-22-20260902-opt-1, order 564760c4
  - agent-23 Jake Blues STO XLF260918P00055500 @ 0.16 (plan 0.19; delta -0.148) — id agent-23-20260902-opt-1, order 7cf8972b
  - agent-24 Ray Blues STO XLP260918P00083000 @ 0.28 (plan 0.30; live 0.23x0.33; delta -0.183) — id agent-24-20260902-opt-1, order 66152f3e
- HELD (gap re-underwrite, no filing): agent-25 Tommy Levene + agent-26 Marvin Levene — XLU -0.85% + IV pop (0.163->0.184) pushed XLU260918P00041000 live delta to -0.212 > 0.20 desk delta law; fallback 40.5P mid 0.065 under min-rent; 42P -0.38 fails outright. No legal filing exists; both flat. 14:30 Rule-8 clock governs any re-file (only if chain re-ranges legal).
- WOLF CRYPTO (agent-27): BTC/USD MARKET 0.0325 FILLED @ 77,148.74 (=$2,507.33) 09:43:34 ET — Rule 8 engagement by execution (crypto TIF=gtc per Alpaca constraint). Staged resting GTC: BTC 0.0325 @ 75,800 (order ffddb275), ETH 0.6 @ 2,365 (order 2bd4920b). Powder ~74.5%. Hard stops -2.5% BTC / -3.0% ETH.
- Cash deployed at open: ~$10,757 committed (4 put reserves $24,900 reserved; Wolf filled $2,507 + staged $2,526 + $1,419). Fund equity 09:43: $99,814.52.
- Triggers synced: XLF per-agent stops += 21/22/23; XLP += 24. XLU 41P holders have NO position — no stop entries.
- Strikes: 0. Rejections: 0. Fills: 1 (Wolf tranche 1). Resting: 4 DAY option legs + 2 GTC crypto staged.
"""
with open(f'{STATE}/ar_log.md', 'a') as f:
    f.write(ar)
print('ar_log appended')

# ---------- 4. TRIGGERS ----------
tpath = f'{STATE}/triggers.json'
trig = json.load(open(tpath))
pt = trig['price_triggers']
pt['XLF']['per_agent_stops'].update({
 'agent-21': "BTC 55.5P @ 0.57 OR XLF<=54.50 intraday (filed 09/02 09:43 @ 0.16)",
 'agent-22': "BTC 55P @ 0.48 OR XLF<=53.50 intraday (filed 09/02 09:43 @ 0.14)",
 'agent-23': "BTC 55.5P @ 0.57 OR XLF<=54.50 intraday (filed 09/02 09:43 @ 0.16)",
})
pt['XLP']['per_agent_stops']['agent-24'] = "BTC 83P @ 0.90 OR XLP<=81.50 intraday (filed 09/02 09:43 @ 0.28)"
trig['day4_verified'] = "2026-09-02 09:44 ET: survivors carried (57P/56P/XLU 9-4 42P) + stops verified; 4 new legs filed at live mids; XLU 41P clone legs HELD at gap gate (delta law)."
atomic_json(tpath, trig)
print('triggers synced')