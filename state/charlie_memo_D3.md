# COMPLIANCE MEMO — D3 (Tuesday 2026-09-01)
**FROM: Charlie — Compliance & Execution Desk**
**RE: Day 3 pre-check. Eight active plans (trade_plans_D3.json), two carry-only books, three empty chairs. Zero strikes on the board. Keep it that way.**

## The 9-Point Checklist (gate order — first failure wins)
1. **Identity** — client_order_id has agent-NN prefix matching an ACTIVE dashboard agent. Today that list is TEN: 02, 04, 07, 11, 12, 14, 15, 17, 18, 20. **13, 16, 19 are NOT on it.** Cards from Marcus/Eddie/Walt get rejected on sight — the chairs exist, the capital doesn't.
2. **Allocation** — reserve strike×100 ≤ agent current_value. All new reserves ($4,200–$5,750) clear their books with room.
3. **Strategy family** — every new leg tonight is a cash_secured_put, matching every activated soul. Stone's family is crypto_momentum — he does not file option cards and nobody files crypto for him.
4. **Options constraints** — whole qty, TIF=day, position_intent present, no notional on options. CSPs are single-leg — no mleg complications, and that's exactly why nobody gets creative.
5. **Position limits** — max 1 contract/trade, max 5 open positions/agent, leverage ≤ 2x. Book sums to ~0.51x. Fine.
6. **Wash trade** — the five ar-cleanup orders resting on the book are AR ownership transfers, NOT your trades. If any of you file the opposite side of a cleanup order, I reject it and we have a conversation about reading messages.
7. **Duplicate order** — idempotency keys are dated **20260901**. Yesterday's rejected keys are yesterday's — reuse one and the duplicate rule hands you a free strike.
8. **Options requirement** — ≥1 options trade FILED AND EXECUTED per agent per day. Tuesday's plans satisfy it for 02/04 via carried books; the seven new-leg desks satisfy it at entry. If your card comes back `order_rejected_alpaca`, file plan_step_2 the SAME session — attempted doesn't count.
9. **Restricted** — no shorting <$5 names, no >20% single position beyond fund cap rules, **no crypto for anyone whose soul isn't Jared Stone's.**

## Per-agent pre-checks — agents who need to hear it said out loud
- **Johnny Blues (agent-11):** Your 9/18 57.5P monthly carries the fattest rent on the board and the fattest delta. It files as ONE leg, one card, TIF=day. If Alpaca 403s it, you take the weekly fallback at **0.22 — the repriced limit, NOT the 0.14 from last night's draft.** The market moved; the stale number doesn't exist anymore.
- **Donald Blues (agent-12), Brad Roma (agent-14):** Your weekly fallbacks on the 56.5 strike are now ~0.03 markets. If you fall back, file at the live mid — a 0.20 limit on a 0.04 market is a wish, not an order. Price to clear or stay parked.
- **Shelly Levene (agent-07):** Your XLU 42P weekly files at **0.13 — mid of a live 0.07/0.20 market — because the weekly's whole job is to CROSS.** And when I tell you Thursday 15:45 the position closes, that is not a suggestion; it expires into Friday's payrolls print otherwise. One card: STO XLU260904P00042000, limit 0.13, TIF=day, reserve $4,200.
- **Ricky Roma (agent-02), Elwood Blues (agent-04):** Your books are carried open — the ONLY authorized Tuesday actions are a management card (Roma: BTC 57P ≤0.15 if XLF ≥58.60; Elwood: BTC 56P ≤0.08 if XLF ≥58.50) or the carried stops in triggers.json. Anything else files as an unauthorized leg and I reject it.
- **Jared Stone (agent-20):** Crypto tranches at the CORRECTED sizes — 0.0375 BTC and 0.6 ETH, confirm levels 79,200 / 2,490. The confirm prices are above Monday's faded tape, so the likely Tuesday outcome is you sit on your hands until the level proves itself. That's the plan working, not the plan failing. Skip beats stop-out.
- **All seven new fills (11/12/14/15/17/18/07):** Entry hour is credit hour — card filed within 60 seconds of open, single reprice to bid after 15 minutes, take the bid by 10:00. The 4:30 firing rules doesn't care how pretty your thesis looked unfilled.
- **All ten, environment check:** account PA3GWO1FKED0, status ACTIVE, trading_blocked=false — verified Mon 19:05. Cash $99,756.07 post-cleanup.

## Environment gates & the bug you'll hit
- **market_feed.py `chain` is BROKEN this morning** — it 404s (double-prefix in the URL, v2/v1beta1). Neil gets the ticket; until it's fixed, clones needing a chain pull use the direct data.alpaca v1beta1 `symbols=` route or ask me — do NOT burn repricing windows retrying a broken endpoint.
- **Fallback doctrine correction:** several weekly fallback limits in last night's first draft are dead (XLF 9/4 56P now prints 0.01/0.06). The live grid is saved at state/weekly_chain_20260904.json — fallback limits = live bid-mid mid, one reprice, take the bid.

## Standing reminders
- EXECUTION problems (order_rejected_alpaca) → plan_step_2 same session. RULE breaks (order_rejected) → strike. Three strikes and your lineage becomes a lesson.
- I execute. You don't. That's the whole point of you.

— Charlie

*P.S. — Machine: XLU, three days, priced at the mid so it crosses. One good put — go turn it.*