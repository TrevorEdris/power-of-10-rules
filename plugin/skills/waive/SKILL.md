---
name: pow10-waive
description: Author a well-formed inline waiver comment at a specific violation site.
---

## What this skill does

Writes a `pow10: allow` inline comment at a specified file:line with the
correct comment syntax for the file's language. Prompts for:
- `owner` — engineer accepting the waiver
- `until` — expiry date (YYYY-MM-DD)
- `reason` — free-text justification

No statefile — waivers live next to the code they waive.

## How to invoke

```
pow10 waive <file>:<line> --rule <N>
```

## Status

`pow10 waive` lands in **M3**. Stub today.
