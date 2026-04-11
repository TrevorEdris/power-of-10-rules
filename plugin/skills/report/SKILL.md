---
name: pow10-report
description: Produce a JPL LOC-1..LOC-4 compliance report for the current repo.
---

## What this skill does

Aggregates the results of `pow10 audit` into a JPL-style compliance report:
- LOC-1: critical compliance (blocker rules)
- LOC-2: standard compliance (high-severity rules)
- LOC-3: advisory (medium)
- LOC-4: informational (low)

Folds inline waivers into the counts and flags expired waivers separately.

## How to invoke

```
pow10 report [--format markdown|json]
```

## Status

`pow10 report` lands in **M3**. Stub today.
