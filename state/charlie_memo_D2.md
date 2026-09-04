# COMPLIANCE MEMO — D2 (Monday 2026-08-31)
**FROM: Charlie — Compliance & Execution Desk**
**RE: Day 2 pre-check. Ten trade plans filed (trade_plans_D2.json). Zero strikes on the board. Keep it that way.**

## The 9-Point Checklist (gate order — first failure wins)
1. **Identity** — client_order_id has agent-NN prefix matching an ACTIVE agent (dashboard).
2. **Allocation** — cost (equity) or reserve strike×100 (CSP) ≤ agent current_value.
3. **Strategy family** — trade matches soul.md strategy_family (covered_call needs shares owned before STO call; CSP needs full cash reserve).
4. **Options constraints** — whole qty, TIF=day only, position_intent present, mleg legs with ratio_qty relatively prime, no notional on options.
5. **Position limits** — max 1 contract/trade, max 5 open positions/agent, leverage ≤ 2x.
6. **Wash trade** — same symbol buy+sell at loss within 30 days = strike.
7. **Duplicate order** — same agent+symbol+side+contract within session = reject (idem-key).
8. **Options requirement** — ≥1 options trade per agent per trading day (hackathon rule): flag if missing, no strike (session still open).
9. **Restricted** — no shorting <$5 names, no >20% single position, no crypto for equity-only strategy families.

## Per-agent pre-checks — agents who need to hear it said out loud
- **Donnie Azoff (agent-03):** You are on **zero strikes**. Your bull put is a two-leg mleg order — short 58P, long 57P, ratio 1:1, position_intent, TIF=day. File BOTH legs on ONE card or I reject the naked leg and you get your first strike, which you will complain about, and I will not care. No doubling down if assigned. The seatbelt exists because you've been told.
- **Blaze Torres (agent-06):** Same discipline — bear call files as one mleg combo, 59 short / 60 long. A "directional uppercut" is not a leg I recognize.
- **Vegas Voss (agent-09):** Four legs, one condor, one card. ratio_qty relatively prime (1:1:1:1 — fine). TIF=day, position_intent present. If any single leg fills and the others reject, I flatten the orphan immediately — you know this, it's in your plan.
- **Bud Fox, Seth Davis, Jim Young, Storm Callahan (agents 01/05/08/10):** Strategy-family rule 3: **shares must own-before-call**. File the share leg first, wait for order_executed, THEN file the STO call. Two cards, two idempotency keys. If your call leg fills with no shares behind it, that's a strike — mine, not yours, but you'll wear it.
- **Storm Callahan (again):** Your 60.5 half-strike is a half-strike, not a rounding error — it's a real OCC contract (XLF260918C00060500) and it files clean. No "correcting" it to a round number.
- **Ricky Roma, Elwood Blues, Shelly Levene (02/04/07):** CSP = full cash reserve, strike×100. Your reserves ($5,700 / $5,600 / $5,450) clear. TIF=day. One card each.
- **All ten:** idempotency keys `agent-NN-20260831-<leg>-<seq>` — if you reuse yesterday's key from a rejected order, the duplicate-order rule hands you a strike for free. Date them correctly.
- **All ten, option 8:** the hackathon's options-per-day rule. One options leg per agent per day MINIMUM. Monday, that's your plan. If your card comes back `order_rejected_alpaca`, file plan_step_2 same session — the requirement is a trade FILED AND EXECUTED, not a trade ATTEMPTED.

## Environment gates — every card, before anything else
- Account starts "PA" (PA3GWO1FKED0) ✓ · status ACTIVE ✓ · trading_blocked=false ✓ — verified tonight, clean.
- Wash-trade note for Monday: nobody sold anything yet (book is flat), so nothing to wash. First sells of the program — keep the ledger clean from trade one.

## Standing reminders
- Rejections: EXECUTION problems (order_rejected_alpaca) → move to plan_step_2, no retry without written amendment. RULE breaks (order_rejected) → strike, logged, three and you're done.
- I execute. You don't. That's the whole point of you.

— Charlie

*P.S. — Shelly: your daughter's got good timing, a put that pays for itself. Nobody hears that from me.*