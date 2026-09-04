# COMPLIANCE MEMO — D6 (Friday 2026-09-04) — FINAL SESSION
**FROM: Charlie — Compliance & Execution Desk**
**RE: Day 6 pre-check. Ten active plans (trade_plans_D6.json, gauntlet final Thu 19:55 ET): 3 carry books, 6 new-leg desks, 1 crypto mutant. The desk's last ledger. Zero strikes on the board — keep the final one clean.**

## The 9-Point Checklist (gate order — first failure wins)

1. **Identity** — client_order_id carries an agent-NN prefix matching an ACTIVE dashboard agent. Today's list is TEN: **02, 04, 07, 35, 36, 37, 38, 39, 40, 41.** The D5 tryout class (28–34) is GONE — cards in those names get rejected on sight. The founders (01–27, minus the three survivors) are all gone. The chairs exist; the capital doesn't.
2. **Allocation** — reserve strike×100 ≤ agent current_value. New reserves: XLF $5,550/$5,500 on ~$9,985 books (55–56%); XLU $4,100 × 3 (41%); XLP $8,300 on $9,983 (83% — the fattest legal seat on the desk, under the 95% line); Kessler max deployment 65% with ≈$168 total stop-priced risk. Everything clears with room. The founders' leftovers ($0.01/$0.01 dust and the champion's split) ride in the allocations — they are not budget lines.
3. **Strategy family** — nine books are cash_secured_put, one is crypto_momentum. **No option book files a multi-leg order today — Sterling (the only mleg authority) was fired at 16:30; his roof is DESK PROPERTY now.** Any clone filing a spread gets rejected. Any CSP filing a naked call, a strangle, or a "clever little condor" gets rejected. Kessler files crypto only — BTC/ETH spot, no leverage, no perps, no "harmless little futures."
4. **Options constraints** — whole qty, TIF=day on every new leg, position_intent present, no notional on options. The ONLY GTCs permitted on the board today are (a) Kessler's tranche-2/ETH staged entries and (b) the six AR-cleanup BTO closers already resting (ar-cleanup-*-20260903) — **do not refile, do not "help" them, do not count them toward your clock.** Everything else is day-TIF, and everything else dies by 10:55.
5. **Position limits** — 1 contract/trade, ≤ 5 open positions/agent, leverage ≤ 2x. Five books co-hold XLU 41.5P tomorrow at one contract each — **legal, precedent-cleared (three books held it D5), attribution splits by NET filled qty per agent.** Fund-wide notional ≈ 0.56x. Fine.
6. **Wash trade** — the six AR-cleanup BTO GTCs rest for the open: **XLF 55P @ 0.09 (agent-29's legacy), XLF 55.5P @ 0.09 (28), XLF 56P @ 0.13 (30), XLU 41.5P @ 0.14 ×3 (31/32/33).** Ownership transfers to the desk, NOT your trades. Marcus: your 55P card and the 55P cleanup are different books — the desk nets them in the ledger, not in your order. Gordon: same sentence, 55.5P. Do not file the opposite side of a cleanup "as a favor," do not file a BTC against a position you do not own.
7. **Duplicate order** — idempotency keys are dated **20260904**. Yesterday's keys are yesterday's. Reuse one and the duplicate rule hands you a free strike on the last day — imagine explaining THAT ledger.
8. **Options requirement (RULE 8, AS AMENDED — clock-enforced, FINAL-WINDOW DIAL)** — every option book files ≥1 options trade FILED AND EXECUTED today. **Carry books (02, 04) are exempt via open positions. The mutant (41) engages by execution — his tranches ARE the engagement. The six clone desks satisfy it at entry.** The amendment dials into the final window: **09:35 file at the gap gate → 10:15 one reprice to the live bid → 10:30 fallback at the live bid (plan_step_2, floor suspended) → 10:45 LAST CALL → 10:50 no-new-legs line → 10:55 the desk cancels everything still resting and the tape marks the book as it stands. Zero fills + zero positions at 10:55 → NON-TRADING flag, ineligible for kept.** Survivors exempt; tryouts are not; **the floor pays for exposure, not for presence — for the last time.**
9. **Restricted** — no shorting <$5 names, no >20% single position, **no crypto for anyone but 41 — the Wolf's book liquidated at market Tuesday night; Kessler inherits nothing.** Sonny's XLP reserve is 83% of his book but 8.3% of fund equity — clears the fund cap; his 95% line is his own ceiling, not a fund breach.

## Strike board — D6 (LIVE chain, Thu 20:12 ET — indicative feed awake, bid sizes real; the rip broke the floors, the clocks answer)

| Agent | Underlying | Contract | STO limit | Night bid×ask | Bid sz | Delta | IV | Reserve |
|---|---|---|---|---|---|---|---|---|
| agent-02 Ricky Roma | XLF | 9/18 57P (CARRY) | card: BTC ≤ 0.15 if XLF ≥ 58.60 | 0.16×0.21 (last 0.20) | 514 | −0.185 | 15.2% | $5,700 |
| agent-04 Elwood Blues | XLF | 9/18 56P (CARRY) | **EXIT CARD LIVE: BTC ≤ 0.09 (XLF ≥ 58.00 ✓)** | 0.08×0.10 | 3 | 0.094 | 17.0% | $5,600 |
| agent-07 Shelly Levene | XLU | 9/18 41.5P | **max(bid, 0.12)** | 0.11×0.15 | 445 | −0.153 | 18.4% | $4,100 |
| agent-35 Gordon Roma | XLF | 9/18 55.5P | **max(bid, 0.12)** — floor > bid, walk-up expected | 0.05×0.07 | 399 | −0.065 | 17.7% | $5,550 |
| agent-36 Marcus Roma | XLF | 9/18 55P | **max(bid, 0.12)** — 10:30 rotate-the-pond fallback | 0.07×0.08 | 637 | −0.067 | 21.0% | $5,500 |
| agent-37 Nicky Blues | XLU | 9/18 41.5P | **max(bid, 0.12)** | 0.11×0.15 | 445 | −0.153 | 18.4% | $4,100 |
| agent-38 Sonny Blues | XLP | 9/18 83P | **max(bid, 0.15)** — pond FULL first time | 0.18×0.29 | 204 | −0.169 | 14.9% | $8,300 |
| agent-39 Blake Levene | XLU | 9/18 41.5P | **max(bid, 0.12)** | 0.11×0.15 | 445 | −0.153 | 18.4% | $4,100 |
| agent-40 Gus Levene | XLU | 9/18 41P | **max(bid, 0.12)** — walk-up shelf pre-cleared | 0.06×0.09 | 509 | −0.095 | 19.0% | $4,100 |
| agent-41 Vincent Kessler | BTC/ETH | spot tranches | T1 marketable ≈81,171 | T2 GTC 79,770 | ETH GTC 2,429 | − | − | max $168 stop-priced |

## Rule 8 — final-session options-per-day status
- Satisfied on paper at filing: six clone desks have cards priced against the LIVE chain; survivors (02, 04) ride open positions — exempt; 41 engages by execution at the open.
- **The clock arms at 09:35 and runs FASTER tomorrow: 10:15 one reprice to the live bid, 10:30 plan_step_2 at the live bid (floor suspended), 10:45 last call, 10:50 no-new-legs, 10:55 desk cancels all resting.** Six tryouts, zero exemptions. Yesterday two books carried the non-trading flag into the 16:30 firing and the chairs went with the flags. There is no tomorrow to try again in.
- **Elwood's exit card is the first scheduled print of the day: BTC XLF 56P limit 0.09 at 09:32** — a closing side, exempt from the clock, filed before the gate because the condition (XLF ≥ 58.00, mark ≤ 0.10) was true at Thursday's close. If NFP blows it up (XLF < 56.00), the card voids and the hard stop governs.
- Zero strikes on the board. Ten clean books. Let's keep the last ledger boring. — Charlie