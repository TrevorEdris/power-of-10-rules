---
name: pow10-rule-05-assertion-density
description: "NASA Power of 10 Rule 5 — Average ≥2 runtime assertions per function. Severity: high."
---

# Rule 5 — Assertion Density

**Severity:** high

## Statement

Use a minimum of two runtime assertions per function on average across a translation unit. Assertions must have no side effects and must trigger a defined recovery path (not be stripped) in release builds.

## Rationale

Assertions catch what static analysis cannot: violated preconditions, impossible states, broken invariants. Forcing the author to write ~2 per function makes them think through boundaries explicitly.

## Universal violation patterns

- Function with no preconditions, postconditions, or invariant checks
- Side-effecting assertion expressions (`assert(x++ > 0)`)
- Build configurations that strip assertions in production (`NDEBUG`, `-O` for Python)
- "Assertions" that swallow errors silently instead of triggering recovery

## What counts

- Parameter validation at entry
- State invariant checks before mutation
- Postcondition checks before return
- Loop invariants inside bounded loops

## What does NOT count

Error handling for expected failures (network down, file missing) — that's normal control flow, not an assertion.

## Universal remediation pattern

At function entry: validate every parameter against domain constraints. Before mutation: check state invariants. After mutation: check postconditions. Each assertion is a single boolean expression with a meaningful failure message.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## Citations

- Holzmann 2006 — Rule 5
