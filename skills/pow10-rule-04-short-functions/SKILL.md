---
name: pow10-rule-04-short-functions
description: "NASA Power of 10 Rule 4 — Functions ≤60 lines (one printed page). Severity: high."
---

# Rule 4 — Short Functions

**Severity:** high

## Statement

Each function fits on one printed page — hard limit 60 source lines (excluding comments), soft limit 40. Functions exceeding the hard limit must be decomposed or carry a documented waiver.

## Rationale

A function that fits on one page can be reviewed and tested as a unit. Longer functions hide bugs by combining responsibilities. Short functions also make refactoring safer and unit testing tractable.

## Universal violation patterns

- Single function > 60 SLoC
- Cyclomatic complexity > 10
- Multiple distinct responsibilities in one body (parsing + validating + persisting)
- Deep nesting (> 3 levels of `if`/`for`)

## Universal remediation pattern

Extract by responsibility. Each helper takes one phase of the work and returns its output to the caller, which now reads as a sequential pipeline. Each helper is independently testable.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## When violation is justified

Generated code, large `switch` dispatchers (consider table-driven instead), state machines. Document with a waiver:

```
// pow10: allow rule=4 until=YYYY-MM-DD owner=<handle> reason="generated state table"
```

## Citations

- Holzmann 2006 — Rule 4
