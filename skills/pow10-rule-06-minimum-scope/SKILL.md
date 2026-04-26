---
name: pow10-rule-06-minimum-scope
description: "NASA Power of 10 Rule 6 — Declare data at smallest possible scope. Severity: medium."
---

# Rule 6 — Minimum Scope

**Severity:** medium

## Statement

Variables declared at the narrowest scope where they are used. No mutable globals or file-scope statics. When unavoidable, mark them `const` or guard with documented access protocols.

## Rationale

Narrow scope makes data hiding explicit, simplifies debugging, prevents accidental cross-scope mutation, and helps the compiler optimize register allocation. Globals hide ownership and create implicit coupling.

## Universal violation patterns

- Mutable module-level / package-level state shared across functions
- Variables declared at function top but used in only one branch
- File-scope `static`/`var` mutated from multiple functions
- Loop variables declared outside the loop (and Go ≤ 1.21 capture bugs)
- `companion object` / static class fields with `var`

## Universal remediation pattern

Encapsulate state in an instance owned by a single object. Pass dependencies explicitly. Declare locals at the point of first use. Prefer immutable bindings (`const`/`final`/`val`) over mutable.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## When module-level state is justified

- Truly immutable constants (`const`/`final`/`val`)
- Logger handles created at startup
- Singleton service handles initialized in init phase

Mark them clearly:

```go
// Configuration loaded at init; immutable thereafter.
var config = mustLoadConfig()
```

## Citations

- Holzmann 2006 — Rule 6
