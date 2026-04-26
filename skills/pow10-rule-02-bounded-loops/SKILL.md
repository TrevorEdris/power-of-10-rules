---
name: pow10-rule-02-bounded-loops
description: "NASA Power of 10 Rule 2 — Every loop must have a statically determinable upper bound. Severity: blocker."
---

# Rule 2 — Bounded Loops

**Severity:** blocker

## Statement

Every loop must carry an explicit, statically verifiable upper bound on its iteration count. The bound should be a compile-time constant where possible. When the bound depends on runtime input, assert it against a fixed maximum.

## Rationale

Bounded loops make termination trivial to prove and make worst-case execution time analyzable. Required for Rate Monotonic Analysis in real-time systems. Unbounded loops are the most common source of runaway behavior in embedded code.

## What a violation looks like

- `while (condition)` with no enclosing iteration cap
- `for (;;)` event loops without a defensible justification
- Recursive descent with no depth limit (also violates Rule 1)

## Per-language guidance

### C
- Prefer `for (int i = 0; i < N; i++)` with `N` a `#define` or `static const`
- For `while (queue_nonempty())`, wrap with `for (int i = 0; i < MAX_DRAIN && queue_nonempty(); i++)`
- Tools: `clang-tidy` `bugprone-infinite-loop`; manual review for unbounded `while`

### Go
- Use `for i := 0; i < N; i++` instead of `for { ... }`
- Workers: bound with `for i := 0; i < maxBatch && ctx.Err() == nil; i++`
- Tools: `golangci-lint` (`govet`, `staticcheck` SA4017 for unused conditions); custom `analysis.Analyzer` for unbounded `for`

### Python
- Use `for _ in range(N):` over `while True:`
- Bound `while q:` with `for _ in range(MAX_DRAIN):` + `if not q: break`
- Tools: `ruff` (`PLW0120` else-on-loop, `B007` unused loop var); manual review for unbounded `while`

### Java
- Use indexed `for` loops or `Stream.limit(N)` over `while (true)`
- For event loops, bound with a counter + `if (i++ > MAX) throw new IllegalStateException(...)`
- Tools: `PMD` (`WhileLoopWithLiteralBoolean`, `AvoidBranchingStatementAsLastInLoop`); `SpotBugs` infinite-loop detector

### Kotlin
- Prefer `repeat(N) { ... }` or `(0 until N).forEach { ... }` over `while (true)`
- For collections, prefer `take(N)` over manual iteration
- Tools: `detekt` (`LoopWithTooManyJumpStatements`, `EmptyWhileBlock`); manual review

## Remediation pattern

```go
// Before (Rule 2 violation)
for {
    msg := <-ch
    process(msg)
}

// After
for i := 0; i < maxBatch; i++ {
    select {
    case msg := <-ch:
        process(msg)
    case <-ctx.Done():
        return
    }
}
```

## Intentional infinite loops

`main()` event loops sometimes must be infinite. Tag them:

```c
// pow10: allow rule=2 until=2099-01-01 owner=fsw-team reason="main event loop, intentional"
for (;;) { dispatch(); }
```

## Citations

- Holzmann 2006 — Rule 2
