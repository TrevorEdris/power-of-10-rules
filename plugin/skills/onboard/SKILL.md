---
name: pow10-onboard
description: Interactively scaffold .pow10.json, CI wiring, and init-phase markers for a new repo.
---

## What this skill does

Walks the user through adopting pow10 in a new repository:
- Creates `.pow10.json` with detected languages
- Offers to install a CI workflow for `pow10 audit`
- Adds `pow10:init-end` markers to `main()` so Rule 3 knows where the init phase ends
- Lists missing host analyzers with install commands (never auto-installs)
- Offers to copy `cursor/.cursor/rules/*` into the repo (Cursor users)
- Offers to install Codex user-level prompts (Codex CLI users)

## How to invoke

```
pow10 onboard
```

## Status

`pow10 onboard` lands in **M3**. Stub today.
