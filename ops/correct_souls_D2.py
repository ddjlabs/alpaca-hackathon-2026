#!/usr/bin/env python3
"""Staged soul corrections for the D2->D3 replication (Option C pattern, same
mechanism as patch_soul_protocol.py): stage corrected copy as persona.md,
validate, rename over soul.md. Each replacement must match EXACTLY ONCE or the
script aborts without touching the soul. Corrections: (1) Levene leftover-rule
allocations, (2) Levene-clone sector rotation to XLU per Richard's 40% XLF cap,
(3) George's long-clock roll."""
from pathlib import Path

AGENTS_DIR = Path("/mnt/agent_share/gordon/hackathon/agents")

EDITS = {
    "agent-17-george-levene": [
        ("allocation: 9986", "allocation: 9987"),
        (
            "Mutation: strike +0.5 to XLF 55P with expiry rolled to 10/16, limit 0.24 at\nmid — deep (4.7% OTM, delta ~0.12) but actually fill-priced, per the family lesson. The\nMachine's patience, repriced to clear.",
            "Mutation: strike +0.5 and expiry ROLLED to XLF 10/16 55P, limit 0.40 at mid —\ndeep (4.7% OTM at entry), less gamma, fill-priced per the family lesson. The\nMachine's patience, repriced to clear.",
        ),
    ],
    "agent-18-chester-levene": [
        ("allocation: 9986", "allocation: 9987"),
        (
            "Mutation: strike +2.0 to XLF 56.5P, same 9/18 expiry, limit 0.30 (mid of\n0.28/0.32) — mid-floor mutation, 2.0x the father's premium ceiling. Patience with a\ndeeper pond than the 57.5's.",
            "Mutation — FAMILY SECTOR ROTATION (same defensive-put doctrine, different\nunderlying): STO XLU 42P exp 9/18, limit 0.36. XLU 42.22; strike 0.5% OTM at entry,\ndelta ~0.25. Mid-floor mutation on the rotated pond.",
        ),
    ],
    "agent-19-walt-levene": [
        ("allocation: 9986", "allocation: 9987"),
        (
            "Mutation: strike −2.0 to XLF 52P, same 9/18 expiry, limit 0.055 — the\ncrash-insurance wing of the family, 9.9% OTM (delta ~0.03). Patience with a wider moat.\nIf the tape says it never fills again, the ledger note rides with you: flat won once.",
            "Mutation — FAMILY SECTOR ROTATION (Richard's 40% XLF cap forces the load off\none truck): STO XLU 40P exp 9/18, limit 0.19. XLU 42.22 at the close; strike 5.3% OTM\n(delta ~0.09), premium ≈ 1.9x the father's ceiling. Same moat, different road.",
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
          and "## YOUR PERSONA" in final and "## BLOODLINE" in final
          and "agent_id:" in final)
    assert ok, f"validation failed for {agent_dir}"
    staged.replace(soul)
    print(f"OK {agent_dir}: {len(edits)} edit(s) staged+activated")