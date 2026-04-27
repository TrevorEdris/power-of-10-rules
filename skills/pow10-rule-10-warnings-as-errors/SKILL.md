---
name: pow10-rule-10-warnings-as-errors
description: "NASA Power of 10 Rule 10 — All warnings on; treat warnings as errors; second analyzer in CI. Severity: blocker."
---

# Rule 10 — Warnings As Errors

**Severity:** blocker

## Statement

Compile with the strictest warning flags the toolchain offers. Treat any warning as a build failure. CI must run at least one additional static analyzer beyond the compiler, also configured for maximum strictness.

## Rationale

Compiler warnings are the cheapest static analysis available — zero-config, run on every build, catch real defects (uninitialized memory, format mismatches, sign comparisons, unreachable code). A safety-critical build that tolerates warnings leaves free defects on the table.

## Universal violation patterns

- CI passes with warnings present
- Strictness flags missing (`-Wall -Werror` or equivalent)
- Single linter only — no second independent analyzer
- `// nolint` / `@SuppressWarnings("...")` / `# noqa` without an inline reason
- Lint job runs but does not fail the build

## Universal remediation pattern

Configure the compiler / language toolchain with every available warning enabled and warnings-as-errors. Add a second analyzer (different vendor / different technology) and run it in the same CI job. Forbid any suppression that lacks an inline justification comment.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## Suppressions

When a warning must be suppressed, scope as narrowly as possible (push/pop, single line, single block) and document inline:

```
// pow10: allow rule=10 until=YYYY-MM-DD owner=<handle> reason="..."
```

## Citations

- Holzmann 2006 — Rule 10
