#!/usr/bin/env python3
"""Correction pass 2 (Option C staging): align two soul MUTATION limits with live
pre-open marks fetched 18:xx (ops/fetch_contract_quotes_D3.py output).
agent-11: XLF 9/18 57.5P live 0.49/0.61 -> entry limit 0.55 (mid), not 0.40.
agent-19: XLU 9/18 40P live 0.01/0.13 -> entry limit 0.07 (mid), not 0.19.
Each replacement must match EXACTLY ONCE."""
from pathlib import Path

AGENTS_DIR = Path("/mnt/agent_share/gordon/hackathon/agents")

EDITS = {
    "agent-11-johnny-blues": [
        (
            "Mutation: strike\n+1.5 to XLF 57.5P, same 9/18 expiry. Delta ~0.25, roughly 2x the premium, still ~0.4%\nfloor per day of theta. Same family, tighter perimeter, wider margin for error on rank.\nWeekly fallback (if monthly sleeps at entry): XLF 9/4 57.5P limit 0.14.",
            "Mutation: strike\n+1.5 to XLF 57.5P, same 9/18 expiry — pre-open mark 0.49/0.61 (delta −0.41, IV 14%),\nentry limit 0.55 at mid. Same family, tighter perimeter, ~2.4x the father's premium.\nWeekly fallback (if monthly sleeps at entry): XLF 9/4 57.5P limit 0.14.",
        ),
    ],
    "agent-19-walt-levene": [
        (
            "one truck): STO XLU 40P exp 9/18, limit 0.19. XLU 42.22 at the close; strike 5.3% OTM\n(delta ~0.09), premium ≈ 1.9x the father's ceiling. Same moat, different road.",
            "one truck): STO XLU 40P exp 9/18, entry limit 0.07 (live 0.01/0.13 — death-spread\nmarket; reprice once, then take the bid or fall back). XLU 42.22 at the close; strike\n5.3% OTM (delta −0.085, IV 19%). Same moat, different road.",
        ),
    ],
}

for agent_dir, edits in EDITS.items():
    soul = AGENTS_DIR / agent_dir / "soul.md"
    assert soul.exists(), f"missing {soul}"
    content = soul.read_text(encoding="utf-8")
    for old, new in edits:
        n = content.count(old)
        assert n == 1, f"{agent_dir}: expected exactly 1 match, got {n} for: {old[:60]!r}"
        content = content.replace(old, new)
    staged = soul.parent / "persona.md"
    staged.write_text(content, encoding="utf-8")
    final = staged.read_text(encoding="utf-8")
    ok = ("## WHY YOU EXIST" in final and "## TERMINATION" in final
          and "## YOUR PERSONA" in final and "## BLOODLINE" in final)
    assert ok, f"validation failed for {agent_dir}"
    staged.replace(soul)
    print(f"OK {agent_dir}: corrected + reactivated")