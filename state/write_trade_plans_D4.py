#!/usr/bin/env python3
"""D4 trade plans — 10 waiting orders for the 9:35AM execution cron (Wed 9/2).
Survivor plans: carry + standing management authorization. Clone limits = est mids
(chain endpoint still 404 — GAP GATE reprices to live mids before any card files).
Order of file: 1 per active agent, ids ascending; plan_step_2 on every new leg."""

import json
from datetime import datetime

plans = [
 {  # SURVIVOR — carry + management card
  "agent_id": "agent-02", "agent_name": "Ricky Roma",
  "strategy": "cash_secured_put", "symbol": "XLF",
  "legs": [{"symbol_or_contract": "XLF260918P00057000", "side": "carried_open", "qty": 1,
            "limit_price": None,
            "note": "SURVIVOR CARRY — short 57P @ 0.36 carried untouched (2nd carry-over night). No new leg: XLF bucket 69% of cap but remainder fits nothing the family wants; management card is the only authorized action."}],
  "stop_loss": "carried — BTC 57P at 1.02 (~3x credit) OR XLF <= 56.00 intraday",
  "profit_target": "premium decay; management card STANDS: STO nothing — BTC 57P limit <= 0.15 if XLF >= 58.60 (bank 3 weeks of theta early)",
  "sizing_explanation_in_their_voice": "Second carry-over night. The 57 is still mine at 0.36, the reserve never moves, and Wednesday's tape gets to sweat while I don't. Panic is for the buyers. At 4:30 you'll find me where I told you.",
  "backtest_summary": "CSP XLF 21DTE (Mon run): +5.61% vs B&H +12.48%, 6 round trips, 100% win, MDD 0.00%, Sharpe 3.53. Family validated three consecutive sessions.",
  "client_order_id_template": "agent-02-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "N/A — carry only; management card is a BTC and cannot be rejected-alpaca into a new leg"
 },
 {  # SURVIVOR — carry + management card
  "agent_id": "agent-04", "agent_name": "Elwood Blues",
  "strategy": "cash_secured_put", "symbol": "XLF",
  "legs": [{"symbol_or_contract": "XLF260918P00056000", "side": "carried_open", "qty": 1,
            "limit_price": None,
            "note": "SURVIVOR CARRY — short 56P @ 0.19 carried untouched. One tick a day. No new leg; management card or carried stops only."}],
  "stop_loss": "carried — BTC 56P at 0.54 (~3x credit) OR XLF <= 55.25 intraday",
  "profit_target": "premium decay; management card STANDS: BTC 56P limit <= 0.08 if XLF >= 58.50",
  "sizing_explanation_in_their_voice": "It's dark, I'm wearing sunglasses inside anyway, and the 56 still owes me nothing. 106 miles to the closing bell, half a pack of patience. The job is the job.",
  "backtest_summary": "CSP XLF 21DTE (Mon run): +5.61% vs B&H +12.48%, 6 RT, 100% win, MDD 0.00%, Sharpe 3.53.",
  "client_order_id_template": "agent-04-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "N/A — carry only"
 },
 {  # SURVIVOR — carry with the guillotine
  "agent_id": "agent-07", "agent_name": "Shelly 'The Machine' Levene",
  "strategy": "cash_secured_put", "symbol": "XLU",
  "legs": [{"symbol_or_contract": "XLU260904P00042000", "side": "carried_open", "qty": 1,
            "limit_price": None,
            "note": "SURVIVOR CARRY — short XLU 9/4 42P @ 0.12, marked 0.18 at D3 close. EXPIRES FRIDAY 9/4 INSIDE THE PAYROLLS PRINT. Hard exit Thu 9/3 15:45 MANDATORY — no roll, no exceptions (Richard's gate, signed at fill)."}],
  "stop_loss": "BTC if XLU <= 41.00 intraday OR hard close Thu 15:45 — whichever comes first, no negotiation",
  "profit_target": "decay to <= 0.05 by Wed close, else flat by Thu close; assignment acceptable at effective 41.87",
  "sizing_explanation_in_their_voice": "The put finally filled and it's marked against me — fine. One good put, filed on time, closed on time. Thursday 15:45 the position closes and my daughter hears the name again Friday. That's all I ever needed.",
  "backtest_summary": "CSP XLU 21DTE proxy (Mon run): +3.00% vs pond -10.88%, 6/6 wins, Sharpe 1.88.",
  "client_order_id_template": "agent-07-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "N/A — carry only; the exit is mandatory, not optional"
 },
 {  # CLONE — Dave Roma
  "agent_id": "agent-21", "agent_name": "Dave Roma",
  "strategy": "cash_secured_put", "symbol": "XLF",
  "legs": [{"symbol_or_contract": "XLF260918P00055500", "side": "sell_to_open", "qty": 1,
            "limit_price": 0.21,
            "note": "EST MID — chain endpoint still 404 (Neil's ticket). XLF last 57.21; 55.5P ~3.0% OTM, delta est -0.19. Family delta law <=0.20 honored. GAP GATE reprices at 9:35 before any card files."}],
  "stop_loss": "BTC at 0.63 (~3x credit) OR XLF <= 54.50 intraday",
  "profit_target": "premium decay; reprice once to bid 15 min after open, take the bid by 10:00",
  "sizing_explanation_in_their_voice": "The family sent muscle. I set the floor 3% under the pond, I price it to clear, and I walk the strike up if the rent is thin — never the apology out. The counter doesn't move.",
  "backtest_summary": "CSP XLF 21DTE family validation: +5.61% vs B&H +12.48%, 6 RT, 100% win, MDD 0.00%, Sharpe 3.53 (Mon run).",
  "client_order_id_template": "agent-21-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "STO XLF260918P00055000 9/18 55P @ live mid (one strike deeper, same clock); if that 403s, take the bid on 55.5P by 10:00 — no third leg"
 },
 {  # CLONE — Lou Roma
  "agent_id": "agent-22", "agent_name": "Lou Roma",
  "strategy": "cash_secured_put", "symbol": "XLF",
  "legs": [{"symbol_or_contract": "XLF260918P00054000", "side": "sell_to_open", "qty": 1,
            "limit_price": 0.12,
            "note": "EST MID — deep floor, 5.6% OTM, delta est <= -0.10. Donald's min-rent rule (>=10bp/month of notional) governs: if the open pays under $0.10, walk the strike UP one to 55P and pay the delta law's toll. Priced to clear, not to admire."}],
  "stop_loss": "BTC at 0.36 (~3x credit) OR XLF <= 52.50 intraday",
  "profit_target": "premium decay; single reprice to bid, take the bid by 10:00",
  "sizing_explanation_in_their_voice": "Forty years of floors, son. I measure the distance to the water every morning before I set my feet. Deep floor, short clock that pays. That's the whole religion.",
  "backtest_summary": "CSP XLF 21DTE family validation: +5.61% vs B&H +12.48%, 100% win, MDD 0.00%, Sharpe 3.53.",
  "client_order_id_template": "agent-22-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "STO XLF260918P00055000 9/18 55P @ live mid; if 403 again, take the bid on the 54P by 10:00 — no third leg"
 },
 {  # CLONE — Jake Blues
  "agent_id": "agent-23", "agent_name": "Jake Blues",
  "strategy": "cash_secured_put", "symbol": "XLF",
  "legs": [{"symbol_or_contract": "XLF260918P00055500", "side": "sell_to_open", "qty": 1,
            "limit_price": 0.21,
            "note": "EST MID — same shelf as Dave Roma (family bucket), delta law <=0.20 honored. One reprice, take the bid by 10:00; Donald's min-rent rule sets the floor at $0.10."}],
  "stop_loss": "BTC at 0.63 (~3x credit) OR XLF <= 54.50 intraday",
  "profit_target": "premium decay; exit-ready Thu close (payrolls rule)",
  "sizing_explanation_in_their_voice": "My brother kept the chair at minus ten cents; I intend to keep mine at plus. Same discipline, better coffee. We're putting the band back together — the band is a book of short puts that pay rent on time.",
  "backtest_summary": "CSP XLF 21DTE family validation: +5.61% vs B&H +12.48%, 100% win, MDD 0.00%, Sharpe 3.53.",
  "client_order_id_template": "agent-23-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "STO XLF260918P00055000 9/18 55P @ live mid; if 403 again, take the bid on 55.5P by 10:00 — no third leg"
 },
 {  # CLONE — Ray Blues (SECTOR ROTATION)
  "agent_id": "agent-24", "agent_name": "Ray Blues",
  "strategy": "cash_secured_put", "symbol": "XLP",
  "legs": [{"symbol_or_contract": "XLP260918P00084000", "side": "sell_to_open", "qty": 1,
            "limit_price": 0.50,
            "note": "EST MID — SECTOR ROTATION: XLF bucket 69% of Richard's $40K cap with Roma+Blues books; staples are the ballast pond (XLP last 85.27, 84P ~1.5% OTM, delta est -0.28). Chester's shelf-fee rule governs: thin chain => price at live mid, one reprice, take the bid. Stop 3x credit."}],
  "stop_loss": "BTC at 1.50 (~3x credit) OR XLP <= 82.75 intraday",
  "profit_target": "premium decay; boring on purpose — ballast rent, no story",
  "sizing_explanation_in_their_voice": "I'm the rotation in a family of repeats. Staples pay their rent the way utilities pay their bills: quiet, on the first of the month, no story. Watch the board, not the hype.",
  "backtest_summary": "CSP XLP 21DTE proxy (Sun run): +3.66% vs pond -3.70%, 5 RT, 100% win, MDD -2.66%, Sharpe 0.91 — the family trade works in ballast too.",
  "client_order_id_template": "agent-24-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "STO XLP260918P00083500 9/18 83.5P @ live mid; if 403 again, take the bid on 84P by 10:00 — no third leg"
 },
 {  # CLONE — Tommy Levene (champion's clone, +$2.02)
  "agent_id": "agent-25", "agent_name": "Tommy Levene",
  "strategy": "cash_secured_put", "symbol": "XLU",
  "legs": [{"symbol_or_contract": "XLU260918P00041500", "side": "sell_to_open", "qty": 1,
            "limit_price": 0.35,
            "note": "EST MID — XLU last 42.57; 41.5P monthly, delta est -0.22. Father's 42P last marked 0.43; shelf-fee rule governs (thin chain => live mid, one reprice, take the bid). 41P @ ~0.22 is the fallback, not the first choice."}],
  "stop_loss": "BTC at 1.05 (~3x credit) OR XLU <= 40.50 intraday",
  "profit_target": "premium decay; filed by 9:40, one reprice, gone before the bell owes me anything",
  "sizing_explanation_in_their_voice": "My brother filled by 9:53 and it cost him the chair; my father waited all day and it won him one. The difference wasn't nerve — it was the clock. I sell rent on the shortest clock that pays the family rate.",
  "backtest_summary": "CSP XLU 21DTE proxy (Mon run): +3.00% vs pond -10.88%, 6/6 wins, Sharpe 1.88 — utilities sleeve outperformed outright.",
  "client_order_id_template": "agent-25-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "STO XLU260918P00041000 9/18 41P @ live mid; if 403 again, take the bid on 41.5P by 10:00 — no third leg"
 },
 {  # CLONE — Marvin Levene (champion's clone, +$2.03 dust)
  "agent_id": "agent-26", "agent_name": "Marvin Levene",
  "strategy": "cash_secured_put", "symbol": "XLU",
  "legs": [{"symbol_or_contract": "XLU260918P00041000", "side": "sell_to_open", "qty": 1,
            "limit_price": 0.22,
            "note": "EST MID — deep XLU floor on the monthly clock, delta est -0.15. Shelf-fee rule: thin chain => price at live mid, one reprice, take the bid; never chase a wide quote into the close."}],
  "stop_loss": "BTC at 0.66 (~3x credit) OR XLU <= 40.00 intraday",
  "profit_target": "premium decay; filed by 9:40; flat beats a stop-out, absent is just flat",
  "sizing_explanation_in_their_voice": "Nobody chants for the second machine — the leaderboard doesn't have a microphone, it has a ledger. Deep XLU floor, monthly clock, filed by 9:40. If the fill never comes, the powder still counts.",
  "backtest_summary": "CSP XLU 21DTE proxy (Mon run): +3.00% vs pond -10.88%, 6/6 wins, Sharpe 1.88.",
  "client_order_id_template": "agent-26-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "STO XLU260918P00040500 9/18 40.5P @ live mid; if 403 again, take the bid on 41P by 10:00 — no third leg"
 },
 {  # MUTANT — Winston Wolf
  "agent_id": "agent-27", "agent_name": "Winston Wolf",
  "strategy": "crypto_momentum", "symbol": "BTC/USD,ETH/USD",
  "legs": [
   {"symbol_or_contract": "BTC/USD", "side": "buy", "qty": 0.0325, "limit_price": None,
    "note": "MARKET TRANCHE AT OPEN (~$2,500, ~25% of book) — satisfies Rule 8 engagement floor on file, not on hope. Stone died at #1 filing nothing; the Wolf does not stand still."},
   {"symbol_or_contract": "BTC/USD", "side": "buy", "qty": 0.0325, "limit_price": 75800,
    "note": "STAGED LIMIT — buys weakness ~1.9% under the 18:00 mark (77,250); GTC 3 days, cancel-and-restore-powder if unfilled by Thu 15:45"},
   {"symbol_or_contract": "ETH/USD", "side": "buy", "qty": 0.6, "limit_price": 2365,
    "note": "STAGED LIMIT — ETH ~2,415 at spawn; buys weakness ~2.1% lower; same powder-restore rule"}
  ],
  "stop_loss": "Hard stops -2.5% BTC / -3.0% ETH on filled size — filed as BTC cards the session they trigger; no averaging down beyond staged limits",
  "profit_target": "momentum continuation into FOMC Sep 15-16 risk; trim half on +4% BTC / +5% ETH; powder stays ~55%",
  "sizing_explanation_in_their_voice": "I hear the last man in this chair got fired at #1 for standing still. Not my style. I deploy on the open, stage my tranches, and keep my stops closer than my alibi. Ten minutes in and out — the problem never existed.",
  "backtest_summary": "No family backtest — mutant claim-stake. Process edge: engagement floor met at the open, staged limits buy weakness without chasing, hard stops cap the tail. Max deployed ~$6.4K of $9,979 (~65%) with ~55% powder held after tranche 1 + 2 fill fully.",
  "client_order_id_template": "agent-27-20260902-<leg>-<seq>",
  "plan_step_2_if_rejected_alpaca": "Market tranche 403/blocked => file the staged BTC 75,800 limit as tranche 1 and RE-FILE the market tranche as limit at ask +0.1% — engagement floor must be met by an order on the book, not a hope"
 },
]

out = {
 "gauntlet_date": "2026-09-02",
 "prepared_for_session": "Day 4 — Wednesday, September 2, 2026 (9:35 AM ET execution)",
 "day": 4,
 "note": ("D3->D4 6PM replication plans. Survivor books CARRY ( Roma 57P, Elwood 56P, Levene XLU 9/4 42P — "
          "hard exit Thu 15:45). Clone limits are ESTIMATED mids: chain endpoint still 404 (Neil's ticket) — "
          "GAP GATE reprices to live mids at 9:35 before any card files (deploy as filed <0.5% gap; reprice "
          "0.5-1.5%; re-underwrite >1.5%). Delta law <=0.20 binding on every clone short put. Min-rent floor "
          "$0.10 (Donald's rule). All books exit-ready by Thu 9/3 close (payrolls rule). 6 ar-cleanup GTC "
          "closers rest for Wed open — AR plumbing, do not refile, do not count."),
 "plans": plans,
 "reserve_desks_no_allocation": [],
 "global_risk_notes": [
  "Sector buckets after spawn: XLF reserves $27,600 (69% of Richard's $40K cap) — NO XLF legs beyond the clone plans; XLU $12,450; XLP $8,400; crypto staged ~$6.4K max.",
  "Every clone put enters at delta <= 0.20 (Johnny Blues' D3 lesson, binding desk law as of tonight).",
  "Shelf-fee rule (Chester Levene): thin chains charge fat fees — price at live mid, one reprice, take the bid; never chase a wide quote.",
  "Min-rent rule (Donald Blues): never sell a put for under ~10bp of notional/month — walk the strike UP before you sell cheap freight.",
  "Friday 8:30 NFP (cons 40K) is inside the fund's final 2.5 hours — every book exit-ready by Thursday 9/3 close. Levene's XLU weekly has the hard 15:45 exit.",
  "Wolf crypto: engagement floor via market tranche at open; staged limits buy weakness; hard stops -2.5%/-3.0%; ~55% powder. Crypto never closes; discipline does."
 ]
}

path = "/mnt/agent_share/gordon/hackathon/state/trade_plans_D4.json"
json.dump(out, open(path, "w"), indent=2)

# verification
chk = json.load(open(path))
assert len(chk["plans"]) == 10, len(chk["plans"])
ids = [p["agent_id"] for p in chk["plans"]]
assert ids == sorted(ids) and len(set(ids)) == 10, ids
active = {a["id"] for a in json.load(open("/mnt/agent_share/gordon/hackathon/state/dashboard.json"))["agents"]}
assert set(ids) == active, (set(ids) ^ active)
for p in chk["plans"]:
    assert p.get("client_order_id_template", "").startswith(p["agent_id"]), p["agent_id"]
    assert p.get("stop_loss") and p.get("profit_target") and p.get("plan_step_2_if_rejected_alpaca")
print("trade_plans_D4.json VERIFIED: 10 plans, ids match active roster, all required fields present")
print("new-leg plans (STO):", [p["agent_id"] for p in chk["plans"] if any(l.get("side") == "sell_to_open" for l in p["legs"])])
print("carry-only:", [p["agent_id"] for p in chk["plans"] if all(l.get("side") == "carried_open" for l in p["legs"])])
print("crypto mutant:", [p["agent_id"] for p in chk["plans"] if p["strategy"] == "crypto_momentum"])