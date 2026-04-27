---
name: pow10-rule-09-restrict-pointers
description: "NASA Power of 10 Rule 9 — At most one level of dereferencing; no function pointers (analogues for non-C langs). Severity: blocker."
---

# Rule 9 — Restrict Pointers / Indirection

**Severity:** blocker

## Statement

In C: at most one level of dereferencing per declaration. No function pointers.

In other languages: limit indirection — first-class function/lambda passing across module boundaries, multi-level reference chains, and dynamic dispatch all reduce static analyzability the same way.

## Rationale

Each level of indirection multiplies the state space a reviewer or static analyzer must track. Multi-level pointers make aliasing analysis effectively impossible. Function pointers defeat call-graph construction — the foundation of reachability, coverage, and worst-case execution time analysis.

## Universal violation patterns

- C: `**`, `***`, function pointer types
- Open-ended `Map<String, Function<...>>` registries crossing module boundaries
- Lambda-of-lambda types `(A) -> (B) -> R` as cross-module parameters
- Strategy maps populated from outside the safety package
- Reflective dispatch (overlaps with Rule 8)

## Universal remediation pattern

Replace open dispatch with a sealed/closed mechanism: `switch`, sealed interface, enum-keyed map, named callback class. The set of reachable targets becomes enumerable at compile time.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## When indirection is justified

- Hardware interrupt vector tables (C) — isolated, documented
- Plugin systems initialized at startup, fixed thereafter
- Strategy/visitor patterns where the set of dispatch targets is enumerated at compile time

Document with a waiver near the indirection.

## Citations

- Holzmann 2006 — Rule 9
- JPL Institutional Coding Standard — Rule 14 (no function pointers)
