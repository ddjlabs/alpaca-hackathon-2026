# CRON: Hackathon — Hourly Dashboard (per-agent P&L during market hours)
# schedule: {'kind': 'cron', 'expr': '15 9-16 * * 1-5', 'display': '15 9-16 * * 1-5'}
# job_id: 348a47cd27d6

Run the Bushwood hourly dashboard update: python3 /mnt/agent_share/gordon/hackathon/hourly_dashboard.py

This updates dashboard.json with per-agent P&L attribution from Alpaca fills (client_order_id prefixes agent-NN-*) plus fund equity/day P&L — the website leaderboard refreshes hourly from this. Credentials load from env or /home/doug/.hermes/profiles/gordon/.env (script handles both).

On success: deliver NOTHING (empty output = silent success; the state publisher Docker picks up the file changes automatically). On error: report the stderr line briefly.