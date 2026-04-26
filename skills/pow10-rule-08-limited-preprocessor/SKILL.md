---
name: pow10-rule-08-limited-preprocessor
description: "NASA Power of 10 Rule 8 — Limit preprocessor + metaprogramming (no recursive macros, no reflection-for-control-flow). Severity: high."
---

# Rule 8 — Limited Preprocessor / Metaprogramming

**Severity:** high

## Statement

In C: restrict preprocessor use to `#include`, simple object-like constants, and narrow `#ifdef` for platform differences. Forbid token-pasting, stringification, recursive/variadic macros.

In other languages: limit metaprogramming. Reflection, runtime class manipulation, `eval`/`exec`, and macro DSLs all defeat static analysis the same way the C preprocessor does.

## Rationale

The C preprocessor runs before the compiler sees the source. Aggressive use defeats static analysis, debuggers, and IDE tooling. The same logic applies to runtime reflection and codegen DSLs in other languages: they hide the call graph from anyone (human or tool) reading the source.

## Universal violation patterns

- C function-like macros with side-effect risk (`SQUARE(i++)`)
- Token pasting (`##`), stringification (`#`), recursive macros
- Reflection used to dispatch by type at runtime (`reflect.MethodByName`, `Class.forName`, `eval`)
- Runtime class manipulation / monkey-patching production code
- Generated code that is not committed to the repo

## Universal remediation pattern

Replace dynamic dispatch with a static, enumerable mechanism: explicit `switch`/sealed interface/dispatch table. The call graph becomes visible to humans and analyzers; failure mode is a typed error rather than a runtime surprise.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## When metaprogramming is justified

- Boilerplate elimination at build time (annotation processors, codegen) where output is reviewable and committed
- Serialization/deserialization mappers at the I/O boundary
- Test scaffolding only — never production control flow

Document the boundary:

```
# pow10: allow rule=8 until=YYYY-MM-DD owner=<handle> reason="generated parser tables; output committed at parser/_generated.py"
```

## Citations

- Holzmann 2006 — Rule 8
