# Mandate Archive — 90-Day Trading Challenge

## STATUS: ARCHIVED — August 25, 2026

All mandate trading crons have been PAUSED. No new trades will be executed on the mandate account (PA3QSMI8HEG5). Existing positions and GTC stop-loss orders remain intact on the Alpaca broker side — those are broker-side orders and will continue to function independently.

## Paused Cron Jobs

| Job ID | Name | Schedule | Status |
|--------|------|----------|--------|
| e2affd843cea | Gekko Pre-Market Scan | 8:15 AM M-F | PAUSED |
| 7b0d18946ec1 | Gekko Mid-Day Execution | 12:00 PM M-F | PAUSED |
| de8736b7cccb | Gekko Close + Daily Email | 5:30 PM M-F | PAUSED |
| ba9789d949ea | Gekko Weekly Review | 8:00 AM Sun | PAUSED |
| 8f273c55296c | Weekly Sector Opportunity Scan | 7:00 PM Sun | PAUSED |
| 3243256e19d1 | Gekko Weekly Blog Post | 9:00 AM Sun | PAUSED (was erroring) |

## Still Active (Non-Mandate)

| Job ID | Name | Purpose |
|--------|------|---------|
| 4c725acabaab | Daily Kanban Task Archive | Infra — keep running |
| 037374bc9db0 | Ernie Economist Weekly Macro Pulse | Retained for hackathon — Ernie feeds The Wire |
| 21483c6cb778 | Check Emails | Already paused (Jul 23) |
| ff9e0ee8b82d | Market Morning Briefing | Already paused (replaced by Gekko) |

## Mandate Final Results

- **Period:** May 22 – August 24, 2026 (90 days)
- **Starting capital:** $99,000
- **Final equity:** $101,943 (+2.97%)
- **SPY return:** +2.75%
- **Alpha:** +0.22% — MANDATE BEATEN
- **Max drawdown:** 2.7%
- **Peak equity:** $102,543 (Jul 3)
- **Best position:** SCHW +27.2%
- **Worst trade:** MU stop-out (-$785)

## Mandate Account Positions (Frozen as of Aug 24)

Positions remain on the Alpaca account with GTC stops live. These are NOT part of the hackathon. The hackathon will use a completely separate, fresh Alpaca paper account.

| Ticker | Shares | Entry | Last Known Price | P/L % |
|--------|--------|-------|-----------------|-------|
| IWM | 60 | $291.29 | ~$300 | +3.5% |
| XLV | 60 | $160.26 | ~$175 | +9.5% |
| XLF | 179 | $55.44 | ~$57.60 | +3.9% |
| BAC | 129.3 | $61.88 | ~$61.84 | -0.1% |
| KR | 137.7 | $58.11 | ~$58.24 | +0.2% |
| XLK | 42 | $187.78 | ~$181.57 | -3.3% |
| XLE | 51.6 | $58.36 | ~$63.44 | +8.7% |
| XLI | 28 | $173.33 | ~$180.25 | +4.0% |
| SCHW | 17 | $88.39 | ~$112.40 | +27.2% |
| SGOV | 53 | $100.59 | ~$100.59 | flat |

## Archive Location

- Mandate wiki: `/mnt/agent_share/gordon/wiki/`
- Mandate DCF models: `/mnt/agent_share/gordon/inv-analysis/`
- Mandate blog posts: `/mnt/agent_share/gordon/blog/posts/`
- Mandate cron outputs: `/home/doug/.hermes/profiles/gordon/cron/output/`
- Performance tracker: `/mnt/agent_share/gordon/wiki/performance-vs-spy.md`
- Trading log: `/mnt/agent_share/gordon/wiki/trading-log.md`

---

*Archived: August 25, 2026 by Gordo*
*Mandate complete. Moving to hackathon operations.*