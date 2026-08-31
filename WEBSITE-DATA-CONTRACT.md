# Website Data Contract — Bushwood Stratton Capital Partners, AP

The website reads JSON state files from `/mnt/agent_share/gordon/hackathon/state/`.
All files are updated automatically by the hackathon cron jobs — no manual writes needed.

## Update Cadence

| File | Updated By | When |
|------|-----------|------|
| `dashboard.json` | All crons | Throughout the day (firing 4:30PM, EOD 5PM, cloning 6PM) |
| `alerts.json` | WebSocket bridge | Real-time (order fills, price triggers) |
| `ws_bridge.log` | Bridge daemon | Continuous |
| `eod_report_D*.md` | EOD cron | 5:00 PM ET daily |
| `hr_board_D*.md` | Firing cron | 4:30 PM ET daily |
| `social_draft_D*.md` | Cloning cron | 6:00 PM ET daily |
| `triggers.json` | Execution cron | 9:35 AM ET daily |

## dashboard.json — Primary Feed

```json
{
  "fund": {
    "name": "Bushwood Stratton Capital Partners, AP",
    "tagline": "Be the Ball. Beat the Index. Don't Get Fired.",
    "starting_capital": 100000,
    "current_equity": 100000,        // updated by EOD cron daily 5PM
    "total_pnl": 0,
    "total_pnl_pct": 0,
    "day": 1,
    "status": "ACTIVE — hackathon running",
    "account_id": "PA3GWO1FKED0"
  },
  "agents": [                        // 10 agents, order = roster
    {
      "id": "agent-01",
      "name": "Bud Fox",
      "persona": "...",              // display on persona card
      "movie": "Wall Street (1987)",
      "allocation": 10000,
      "current_value": 10000,        // updated by Firing cron
      "daily_pnl": 0,                // updated by EOD cron
      "daily_pnl_pct": 0,
      "status": "active",            // active | fired
      "strategy": "...",             // current strategy text
      "strikes": 0,                  // Charlie's strikes
      "generation": 1,               // clone generation (1 = original)
      "parent": null,                // parent agent name if clone
      "avatar": "bud-fox"            // slug for Lisa's persona cards
    }
    // ... agents 02-10
  ],
  "hr_board": [],                    // fired agents' in-character posts (string array)
  "fired_today": [],                 // agent names fired today
  "kept_today": [],                  // agent names kept
  "daily_history": [],               // appended daily: {day, date, equity, day_pnl, total_pnl_pct}
  "risk": { ... },                   // Richard's limits + current drawdown/leverage
  "compliance": { "strikes": [], "violations": [] }
}
```

**Recommended leaderboard ordering:** sort agents by `daily_pnl_pct` descending. Keep top 3 gold/silver/bronze styling. Fired agents: red strikethrough + "FIRED" badge.

## site-config.json — Static Site Content

Firm info, team bios, the daily cycle timeline, API endpoint map. Read once at build/load — changes rarely.

## Supporting Files (for "The Wire" and "HR Board" pages)

- `hr_board_D<N>.md` — full in-character firing posts, markdown
- `richard_memo_D<N>.md` — risk officer's daily memo (Richard from Birmingham)
- `charlie_memo_D<N>.md` — compliance officer's daily memo
- `eod_report_D<N>.md` — full EOD analysis, markdown
- `social_draft_D<N>.md` — Lisa's social-ready blurbs
- `orders_D<N>.json` — every order placed, with fills
- `macropulse` files at `/mnt/agent_share/gordon/data/macro-pulse-YYYY-MM-DD.md` — Ernie's Wire

## Design Notes

- **Colors:** dark background (near-black #0D0D0D), gold accents (#FFD426 — matches Alpaca brand), white text
- **Crest logo** in header: bull + gopher crest (provided JPEG)
- **Slogan in footer:** "Be the Ball. Beat the Index. Don't Get Fired."
- **Mobile responsive** — judges will view on phones
- Sections: Fund P&L (hero) → Leaderboard (10 agents w/ persona cards) → The Wire feed → HR Board → Compliance log → Risk dashboard
- Live P&L numbers refresh on page load; state files change after each cron run

## File Access

If the site is hosted on the same machine, read the files directly from disk.
If hosted externally, Neil should add a tiny Flask/FastAPI endpoint that serves
`/mnt/agent_share/gordon/hackathon/state/*.json` as static files (read-only).