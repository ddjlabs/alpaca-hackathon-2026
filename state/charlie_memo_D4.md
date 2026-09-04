# COMPLIANCE MEMO — D4 (Wednesday 2026-09-02)
**FROM: Charlie — Compliance & Execution Desk**
**RE: Day 4 pre-check. Ten active plans (trade_plans_D4.json, gauntlet final Tue 19:30 ET): 3 carry-only books, 6 new-leg desks, 1 crypto mutant. Strike board below. Zero strikes on the board — keep it that way.**

## The 9-Point Checklist (gate order — first failure wins)

1. **Identity** — client_order_id carries an agent-NN prefix matching an ACTIVE dashboard agent. Today's list is TEN: **02, 04, 07, 21, 22, 23, 24, 25, 26, 27.** The D3 class (11, 12, 14, 15, 17, 18, 20) is GONE — cards in their names get rejected on sight. The chairs exist; the capital doesn't.
2. **Allocation** — reserve strike×100 ≤ agent current_value. All six new reserves ($4,100–$8,300) clear with room; Ray's $8,300 on a $9,979 book is 83.2% and it clears because the math says so, not because anyone likes it.
3. **Strategy family** — every new option leg is a cash_secured_put, matching every option-running soul on the floor. Wolf's family is crypto_momentum: **he files no option cards, and nobody files crypto for him.** Nobody gets creative with spreads, nobody "improves" a CSP into a naked thing.
4. **Options constraints** — whole qty, TIF=day, position_intent present, no notional on options. Single-leg only. That is not a preference, it's the shape of the family.
5. **Position limits** — max 1 contract/trade, max 5 open positions/agent, leverage ≤ 2x. Fund book after tonight's plans: ~$65K option reserves + max $6.4K crypto on $99,794 equity ≈ 0.72x. Fine.
6. **Wash trade** — the AR-cleanup GTC closers (fired agents' legacy legs: XLF 54/55/56/57/57.5, both XLF Octs, XLU 42 monthly, plus the agent-01 QQQ call) rest for Wednesday's open. **Those are ownership transfers, NOT your trades. Do not count them, do not file the opposite side of one, and if your family card happens to mirror a cleanup leg, I reject it and we have a conversation about reading the board.**
7. **Duplicate order** — idempotency keys are dated **20260902**. Yesterday's keys are yesterday's. Reuse one and the duplicate rule hands you a free strike.
8. **Options requirement (RULE 8, AS AMENDED — clock-enforced)** — every option-running agent files ≥1 options trade FILED AND EXECUTED today. Carry books (02, 04, 07) satisfy it via the carried position — survivors are exempt from the clock. The six new-leg desks satisfy it at entry. **The amendment is mechanical: no fill by 14:30 → ONE forced reprice to bid. No fill by 15:45 → plan_step_2 files at live mid so the requirement is met by EXECUTION. Zero fills + zero positions at 15:45 → NON-TRADING flag, ineligible for kept. Jared Stone's chair is the exhibit; the plaque is at reception.** Note for the new desks: you cannot "flat-beat-a-stop-out" your way through a tryout. Absent is just flat, and flat gets fired.
9. **Restricted** — no shorting <$5 names, no >20% single position beyond fund cap rules, **no crypto for anyone whose soul isn't agent-27's.**

## Strike board — D4 (live chain pull, Tue 19:05 ET)

| Agent | Underlying | Contract | STO limit | Live bid×ask (mid) | Delta | Spread % of mid | Reserve |
|---|---|---|---|---|---|---|---|
| agent-21 Dave Roma | XLF | 9/18 55.5P | **0.19** | 0.16×0.22 (0.19) | −0.174 | 32% | $5,550 |
| agent-22 Lou Roma | XLF | 9/18 55P | **0.15** | 0.14×0.17 (0.155) | −0.137 | 19% | $5,500 |
| agent-23 Jake Blues | XLF | 9/18 55.5P | **0.19** | 0.16×0.22 (0.19) | −0.174 | 32% | $5,550 |
| agent-24 Ray Blues | XLP | 9/18 83P | **0.29** | 0.29×0.30 (0.295) | −0.189 | 3% | $8,300 |
| agent-25 Tommy Levene | XLU | 9/18 41P | **0.14** | 0.08×0.21 (0.145) | −0.163 | 90% | $4,100 |
| agent-26 Marvin Levene | XLU | 9/18 41P | **0.14** | 0.08×0.21 (0.145) | −0.163 | 90% | $4,100 |

**Changes from the 6PM replication draft — the chain endpoint is LIVE, est-mid era is over:**
- **Lou Roma: 54P @ 0.12 est → CANCELLED, replaced by 55P @ 0.15.** Live 54P mid is 0.06 — under Donald's min-rent floor, a book that can't pay its own mark. His own plan's walk-up rule did the work; I'm making it official.
- **Ray Blues: 84P @ 0.50 est → 83P @ 0.29.** Live 84P delta −0.301 violates the ≤0.20 law; the 83P is −0.189 and quotes a 3% spread. Same family trade, legal strike.
- **Tommy Levene: 41.5P @ 0.35 est → 41P @ 0.14.** Live 41.5P delta −0.225, over the law; 41P is −0.163. Same clock, legal strike.
- Dave/Jake: 0.21 est → 0.19 live mid. Marvin: 0.22 est → 0.14 live mid.
- **plan_step_2 fallbacks re-anchored to live strikes:** Dave/Jake → XLF 55P @ live mid; Lou → take the bid on 55P by 10:00 (walk-up already used); Ray → XLP 83.5P @ live mid; Tommy/Marvin → XLU 40.5P @ live mid. One reprice at ~09:52 if unfilled, then take the bid — Rule 8 does the rest on its clock.
- **Management cards (carry books) re-affirmed:** Roma BTC 57P ≤0.15 if XLF ≥58.60; Elwood BTC 56P ≤0.08 if XLF ≥58.50; Shelly — nothing but the carried stop (XLU ≤41.00) and the Thursday 15:45 guillotine. Anything else from a carry book files as an unauthorized leg and I reject it.

## Options-per-day status
- Satisfied on paper at 9:35: six new-leg desks have cards priced at live mids; three carry books ride open positions; Wolf's engagement is a market tranche on crypto — **he needs one order on the book by 15:45 or the flag lands and his 6PM counterpart inherits a marked-down stake.** The 0.0325 BTC market order at the open IS the requirement, pre-filed. Do not "optimize" it into a limit that sits all day.
- Zero strikes on the board. Ten clean books. Let's keep the ledger boring.

— Charlie