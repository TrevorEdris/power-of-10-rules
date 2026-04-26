---
name: pow10-rule-09-restrict-pointers
description: "NASA Power of 10 Rule 9 — At most one level of dereferencing; no function pointers (C-specific; analogues for other langs). Severity: blocker."
---

# Rule 9 — Restrict Pointers / Indirection

**Severity:** blocker

## Statement

In C: at most one level of dereferencing per declaration. No function pointers. Multi-level pointers (`char **`) and function pointers defeat call-graph and aliasing analysis.

In other languages: read this as "limit indirection." First-class function/lambda passing across module boundaries, multi-level reference chains, and dynamic dispatch all reduce static analyzability the same way.

## Rationale

Each level of pointer indirection multiplies the state space a reviewer or static analyzer must track. Multi-level pointers make aliasing analysis effectively impossible. Function pointers defeat call graph construction — the foundation of reachability, coverage, and worst-case execution time analysis.

## What a violation looks like

- C: `char **`, `int ***`, function pointer typedefs, `void (*cb)(void)` outside vector tables
- Go: `chan chan T`, `**T` parameters, `func(...) func(...) ...` curried passed across packages
- Java: `Function<Function<A, B>, C>`, deep callback chains
- Kotlin: lambda-of-lambda chains (`(A) -> (B) -> C`) on safety-critical paths
- Python: nested closures capturing mutable state across modules

## Per-language guidance

### C
- Single `*` only in declarations. Forbid `**` and function pointer types
- Vector tables / interrupt dispatch — isolate to one module, document, waiver
- Tools: `clang-tidy` custom matcher (count `*` in decl); manual review for function pointers

### Go
- Avoid `**T` parameter types — pass struct by pointer once, mutate in place
- First-class functions OK within a package; restrict cross-package `func` parameters in safety-critical modules
- Forbid `chan chan T`
- Tools: manual review; `golangci-lint` (`gocritic` `paramTypeCombine`)

### Python
- Avoid deep `Callable[[...], Callable[[...], ...]]` types in safety paths
- Prefer named classes with `__call__` over anonymous lambdas for cross-module callbacks
- Tools: `mypy --strict`; manual review

### Java
- Avoid functional interface chains across packages — define a named interface instead
- Limit `Function<Function<...>, ...>` types
- Lambdas for local use OK; explicit interfaces for module boundaries
- Tools: `Checkstyle` `MethodTypeParameterName`; manual review

### Kotlin
- Avoid `(T) -> (U) -> R` types crossing module boundaries
- Prefer `interface Callback { fun on(t: T): R }` over `(T) -> R` for stable APIs
- Tools: `detekt` (`ComplexInterface`); manual review

## Remediation pattern

```c
// Before (Rule 9 violation)
typedef int (*handler_t)(event_t *);
handler_t handlers[N];
void dispatch(event_t *e) { handlers[e->type](e); }

// After (table of cases instead of fn pointers)
void dispatch(event_t *e) {
    switch (e->type) {
        case EVT_A: handle_a(e); break;
        case EVT_B: handle_b(e); break;
        default:    panic("unknown event");
    }
}
```

The `switch` makes the call graph explicit and analyzable.

## When indirection is justified

- Hardware interrupt vector tables (C) — isolated, documented
- Plugin systems initialized at startup, fixed thereafter
- Strategy/visitor patterns where the set of dispatch targets is enumerated at compile time

Document with a waiver near the indirection.

## Citations

- Holzmann 2006 — Rule 9
- JPL Institutional Coding Standard — Rule 14 (no function pointers)
