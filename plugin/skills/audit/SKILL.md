---
name: pow10-audit
description: Run pow10 audit across the current repo and report violations of NASA Power of 10 rules.
---

## What this skill does

Invoke `pow10 audit` to scan the current repository for violations of the
NASA Power of 10 safety-critical coding rules. The audit runs language-specific
static analyzers, normalizes findings, and folds in inline waivers.

## When to use

- Before merging a PR that touches safety-critical code
- As part of a release checklist
- When onboarding a new module into the pow10 discipline

## How to invoke

```
pow10 audit [--path <dir>] [--language c]
```

## Status

Audit runtime lands in **M3** (C analyzer) and **M5** (Go / Python / Kotlin / Java).
Running `pow10 audit` today returns a `not yet implemented` stub.
