# pow10 (Claude Code plugin)

This directory is the bundled Claude Code plugin for the `power-of-10-rules` marketplace.

- `pow10/` — bundled stdlib-only Python runtime package
- `bin/` — shebang wrappers (`pow10`, `pow10-audit`, `pow10-report`, `pow10-list-waivers`)
- `data/` — runtime copies of `core/*.json` (populated by `python3 tools/generate.py`)
- `skills/` — 16 `SKILL.md` folders (populated in M2)
- `agents/` — `pow10-auditor.md` (populated in M8)
- `hooks/hooks.json` — PostToolUse incremental checks (populated in M8)

Do not edit `plugin/skills/`, `plugin/data/`, or `plugin/agents/` by hand — they are regenerated from `core/` by `python3 tools/generate.py` and CI verifies no drift.
