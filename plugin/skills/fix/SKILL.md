---
name: pow10-fix
description: Remediate a single pow10 audit finding with a minimal diff.
---

## What this skill does

Given a specific audit finding (file + line + rule), produce a minimal,
reviewable patch that resolves the violation without introducing new ones.

## How to invoke

```
pow10 fix <file>:<line> --rule <N>
```

## Status

`pow10 fix` runtime lands in **M3**. Current implementation is a stub.
