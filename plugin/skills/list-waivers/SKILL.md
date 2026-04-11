---
name: pow10-list-waivers
description: Walk the repo and list every active pow10 inline waiver with its expiry.
---

## What this skill does

Scans all source files under the current directory, finds every inline
`pow10: allow` comment, and reports:
- File + line
- Rule number
- Owner handle
- Expiry date (YYYY-MM-DD)
- Days remaining (negative = expired)

Expired waivers are flagged prominently.

## How to invoke

```
pow10 list-waivers [--path <dir>]
```

## Status

`pow10 list-waivers` lands in **M3**. Stub today.
