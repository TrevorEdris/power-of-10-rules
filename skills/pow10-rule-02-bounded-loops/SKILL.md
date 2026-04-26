---
name: pow10-rule-02-bounded-loops
description: "NASA Power of 10 Rule 2 — Every loop must have a statically determinable upper bound. Severity: blocker."
---

# Rule 2 — Bounded Loops

**Severity:** blocker

## Statement

Every loop must carry an explicit, statically verifiable upper bound on its iteration count. The bound should be a compile-time constant where possible. When the bound depends on runtime input, assert it against a fixed maximum.

## Rationale

Bounded loops make termination trivial to prove and worst-case execution time analyzable — required for Rate Monotonic Analysis in real-time systems. Unbounded loops are the most common source of runaway behavior in embedded code.

## Universal violation patterns

- `while (condition)` with no enclosing iteration cap
- `for (;;)` loops outside an annotated main event loop
- Recursive descent with no depth limit (also violates Rule 1)
- Stream / sequence chains without `take(N)` cap

## Universal remediation pattern

Wrap any potentially-unbounded loop with an explicit counter capped by a compile-time constant. Combine with cancellation context (timeout, channel close, signal) so the loop exits cleanly when work is done.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## When violation is justified

`main()` event loops sometimes must be infinite. Tag them:

```
// pow10: allow rule=2 until=2099-01-01 owner=fsw-team reason="main event loop, intentional"
```

## Citations

- Holzmann 2006 — Rule 2
