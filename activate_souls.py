#!/usr/bin/env python3
"""
Bushwood Stratton — Soul Activator
Renames completed persona.md files to soul.md in each agent directory.
A soul is only "live" when it's named soul.md — persona.md is the staging copy
(writes to soul.md directly are gated by the Hermes file-guard, so new souls
land as persona.md and get activated here).

Usage:
  python3 activate_souls.py            # activate any ready persona.md files
  python3 activate_souls.py --dry-run  # show what would happen

Validation before activation:
  - file has YAML-ish frontmatter with name + agent_id
  - contains WHY YOU EXIST section
  - contains TERMINATION section
Only valid, complete souls are renamed.
"""

import sys
import re
from pathlib import Path

AGENTS_DIR = Path("/mnt/agent_share/gordon/hackathon/agents")

REQUIRED_SECTIONS = ["WHY YOU EXIST", "TERMINATION", "YOUR PERSONA"]


def validate(content: str) -> tuple[bool, str]:
    if not content.startswith("---"):
        return False, "no frontmatter"
    front = content.split("---", 2)[1] if content.count("---") >= 2 else ""
    if "name:" not in front:
        return False, "frontmatter missing name"
    if "agent_id:" not in front:
        return False, "frontmatter missing agent_id"
    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in content:
            return False, f"missing section: {section}"
    return True, "ok"


def main() -> int:
    dry = "--dry-run" in sys.argv
    activated, skipped = [], []

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        soul = agent_dir / "soul.md"
        persona = agent_dir / "persona.md"

        if soul.exists():
            continue  # already live
        if not persona.exists():
            continue  # nothing to activate

        content = persona.read_text(encoding="utf-8")
        ok, reason = validate(content)
        if not ok:
            skipped.append((agent_dir.name, f"persona.md invalid: {reason}"))
            continue

        if dry:
            activated.append((agent_dir.name, "dry-run: would activate"))
        else:
            persona.rename(soul)
            activated.append((agent_dir.name, "activated"))

    for name, msg in activated:
        print(f"✅ {name}: {msg}")
    for name, msg in skipped:
        print(f"⚠️  {name}: {msg}")

    if not activated and not skipped:
        print("No persona.md files awaiting activation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())