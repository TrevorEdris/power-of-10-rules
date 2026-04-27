---
name: pow10-rule-01-control-flow
description: "NASA Power of 10 Rule 1 — Restrict control flow to simple constructs (no goto, setjmp/longjmp, recursion). Severity: blocker."
---

# Rule 1 — Restrict Control Flow to Simple Constructs

**Severity:** blocker

## Statement

Use only straight-line execution, conditionals, and bounded iteration. Forbid `goto`, `setjmp`/`longjmp`, and recursion (direct or indirect, including mutual recursion across translation units).

## Rationale

Simple control flow is verifiable by inspection and by static analysis. `goto` and non-local jumps make reachability undecidable. Recursion makes call graphs unbounded, which defeats stack-depth analysis, coverage, and bounded model checking.

## Universal violation patterns

- A function that calls itself, directly or indirectly
- Any `goto`, `longjmp`, `setjmp`
- Cleanup chains implemented via non-local jumps
- Tail-call-optimized recursion (still reads as recursion to a reviewer)

## Universal remediation pattern

Replace recursion with explicit iteration over a bounded data structure (work stack, deque, counter). The cap also satisfies Rule 2.

## Per-language guidance

Load the file matching the language under review:

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## When violation is justified

State machines requiring genuine non-local exit (e.g., async-safe signal handlers). Isolate to one well-marked module and tag with a waiver:

```
// pow10: allow rule=1 until=YYYY-MM-DD owner=<handle> reason="..."
```

## Citations

- Holzmann 2006 — Rule 1
- JPL Institutional Coding Standard — Rule 3 (no recursion), Rule 11 (no goto)
