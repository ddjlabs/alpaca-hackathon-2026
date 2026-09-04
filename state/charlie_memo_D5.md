# COMPLIANCE MEMO — D5 (Thursday 2026-09-03)
**FROM: Charlie — Compliance & Execution Desk**
**RE: Day 5 pre-check. Ten active plans (trade_plans_D5.json, gauntlet final Wed 19:45 ET): 3 carry-only books, 6 new-leg desks, 1 defined-risk mutant. Strike board below. Zero strikes on the board — keep it that way.**

## The 9-Point Checklist (gate order — first failure wins)

1. **Identity** — client_order_id carries an agent-NN prefix matching an ACTIVE dashboard agent. Today's list is TEN: **02, 04, 07, 28, 29, 30, 31, 32, 33, 34.** The D4 tryout class (21–27) is GONE — cards in their names get rejected on sight. The D3 class (11, 12, 14, 15, 17, 18, 20) is gone too. The chairs exist; the capital doesn't.
2. **Allocation** — reserve strike×100 ≤ agent current_value. All new reserves are $4,100–$5,600 on $9,983 books (41–56%); Sterling's max risk is $870/lot (8.7% of book) with a $1,740 two-tranche ceiling. Everything clears with room. The leftover $1.86 belongs to the champion's clones (32, 33, +$0.93 each) — it rides, it is not a budget line.
3. **Strategy family** — nine books are cash_secured_put. **agent-34 is credit_spread and is the ONLY book authorized to file a two-leg order — pre-cleared as SPY 9/18 735/725P, mleg, both legs same expiry, 1 lot.** Any other book filing a multi-leg order gets rejected and we have a conversation about reading your own soul. Nobody "improves" a CSP into a naked thing; nobody turns Sterling's spread into a butterfly overnight.
4. **Options constraints** — whole qty, TIF=day on tranche 1, position_intent present, no notional on options. Sterling's tranche 2 is the only GTC on the board (staged, 3-day life, auto-cancel Thu 15:45). Single-leg for nine books; the tenth files both legs in one order and if a fill comes back one-legged, BOTH legs cancel and refile per plan_step_2 — a naked SPY put on this desk is a firing, not a rounding error.
5. **Position limits** — max 1 contract/trade, max 5 open positions/agent, leverage ≤ 2x. Fund book after tonight: ~$27,950 XLF reserves + $12,300 XLU + $1,740 max SPY risk on $99,831.86 equity ≈ 0.42x. Fine.
6. **Wash trade** — five AR-cleanup GTC closers rest for Thursday's open: **XLF 55P (agent-22's leg), XLF 55.5P ×2 (agents 21, 23), XLU 41P ×2 (agents 25, 26).** Ownership transfers, NOT your trades. Do not count them toward your Rule 8 clock, do not file the opposite side of one "as a favor," and if your card lands on the same strike, that is a coincidence of family — the desk nets them in the ledger, not in your order. Chris and Roy: your 55.5P/41.5P filings are your own; the cleanups are nobody's.
7. **Duplicate order** — idempotency keys are dated **20260903**. Yesterday's keys are yesterday's. Reuse one and the duplicate rule hands you a free strike.
8. **Options requirement (RULE 8, AS AMENDED — clock-enforced)** — every option-running agent files ≥1 options trade FILED AND EXECUTED today. Carry books (02, 04, 07) satisfy it via the carried position — survivors are exempt from the clock. The seven new desks satisfy it at entry. **The amendment is mechanical: no fill by 14:30 → ONE forced reprice to bid. No fill by 15:45 → plan_step_2 files at live mid so the requirement is met by EXECUTION. Zero fills + zero positions at 15:45 → NON-TRADING flag, ineligible for kept. Ray Blues wore that flag for 28 minutes yesterday and the chair went with the flag. Carry books are exempt; tryouts are not; the floor pays for exposure, not for presence.**
9. **Restricted** — no shorting <$5 names, no >20% single position beyond fund cap rules, **no crypto for anyone — the Wolf's book liquidated at market Tuesday night and nobody inherits his habits.** Sterling's spread is the only structure with a short leg above $5 notional per share — SPY is $765, it clears.

## Strike board — D5 (night chain pull, Wed 19:45 ET; greeks/IV live, cash marks = last prints)

| Agent | Underlying | Contract | STO limit | Last print | Delta | IV | Reserve |
|---|---|---|---|---|---|---|---|
| agent-28 Chris Roma | XLF | 9/18 55.5P | **max(bid, ~0.15)** | 0.15 (16:47) | −0.127 | 17.4% | $5,550 |
| agent-29 Eddie Roma | XLF | 9/18 55P | **max(bid, 0.12)** | 0.11 (18:32) | −0.103 | 19.1% | $5,500 |
| agent-30 Walt Blues | XLF | 9/18 56P | **~0.21 bid-anchored** | 0.19 (19:55) | −0.162 | 15.7% | $5,600 |
| agent-31 Murph Blues | XLU | 9/18 41.5P | **~0.13** | 0.14 (20:09) | −0.178 | 16.0% | $4,100 |
| agent-32 Alan Levene | XLU | 9/18 41P | **max(bid, 0.12)** | 0.10 (18:57) | −0.101 | 16.1% | $4,100 |
| agent-33 Roy Levene | XLU | 9/18 41.5P | **max(bid, 0.12)** | 0.14 (20:09) | −0.178 | 16.0% | $4,100 |
| agent-34 Mark Sterling | SPY | 9/18 735/725P | **live net mid (floor 0.60)** | 1.64 / 1.07 → net ~0.57 | −0.122 / −0.078 | 17.3% / 18.9% | max risk $870/lot |

**Changes from the 6PM replication draft — two, both caught by the night chain:**
- **Roy Levene: XLU 9/4 42.5P weekly @ 0.13 est → CANCELLED, replaced by XLU 9/18 41.5P @ max(bid, 0.12).** The live weekly runs **delta −0.369 — over the 0.20 law by 85%** — and the 9/4 shelf has no legal retreat (the 42P prints 0.04, under min-rent). His fallback logic survives: hard review Thu 15:45, no fresh legs into NFP. Logged as law-compliance reassignment; his family strike is the family strike, just on the monthly clock.
- **Mark Sterling: net credit est 1.30 → LIVE-MID ANCHOR with 0.60 floor.** The 4PM shelf nets ~0.57 (735P last 1.64, 725P last 1.07) — the draft's estimate is stale by half. Tranche 1 files at the live net mid at the 9:35 gap gate; if the net is under 0.60, no legal premium exists and he sits flat (the law outranks the quota — same doctrine that held Tommy and Marvin out of the D4 open until the chain re-ranged). Tranche 2 GTC at 1.55 stands unchanged as the IV-spike catcher.
- Eddie and Alan: your opens are one tick under your floors at the night marks — expect the 10:30 walk-ups (Eddie → 55.5P, Alan → 41.5P). Both walk-up shelves are pre-cleared on the board above. Murph: liquidity gate first — day-open volume ≥ 50 and bid size, or you rotate the clock, never the price.
- **Management cards (carry books) re-affirmed:** Roma BTC 57P ≤ 0.15 if XLF ≥ 58.60, hard stop BTC 1.02 or XLF ≤ 56.00; Elwood BTC 56P ≤ 0.10 if XLF ≥ 58.00, hard stop 0.57 or XLF ≤ 55.00; Shelly — the AR-wired BTO GTC caps 0.08 at Thursday's open and the 15:45 guillotine does not care about the mark. Anything else from a carry book files as an unauthorized leg and I reject it.

## Options-per-day status
- Satisfied on paper at filing: seven new desks have cards priced at live marks; three carry books ride open positions. Sterling's tranche 1 IS his engagement — a two-leg mleg order on the book at the gap gate, not a promise to think about it.
- **The Rule 8 clock arms 14:30, one reprice to bid, plan_step_2 at live mid by 15:45.** Seven tryouts, zero exemptions. The flag has a chair's name on it every day; yesterday it was Ray's. Don't volunteer.
- Zero strikes on the board. Ten clean books. Let's keep the ledger boring.

— Charlie