# CRON: Hackathon — Heartbeat (5-min position monitor)
# schedule: {'kind': 'cron', 'expr': '*/5 * * * 1-5', 'display': '*/5 * * * 1-5'}
# job_id: 604e874494a8

Run the Bushwood Stratton heartbeat: python3 /mnt/agent_share/gordon/hackathon/heartbeat.py

This updates hackathon/state/positions_live.json and dashboard.json fund equity from the Alpaca paper API (env vars HACKATHON_ALPACA_KEY/HACKATHON_ALPACA_SECRET via python-dotenv — load them with load_dotenv from /home/doug/.hermes/profiles/gordon/.env if not in environment).

If the script errors, report the stderr output briefly. If it succeeds, deliver NOTHING (empty output = silent success — this is a no_agent-style monitor; the website reads the state files directly).