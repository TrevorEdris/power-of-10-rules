---
name: pow10-rule-08-limited-preprocessor
description: "NASA Power of 10 Rule 8 — Limit preprocessor to includes + simple macros (C-specific; analogues for other langs). Severity: high."
---

# Rule 8 — Limited Preprocessor / Metaprogramming

**Severity:** high

## Statement

In C: restrict preprocessor use to `#include`, simple object-like constants, and narrow `#ifdef` for platform differences. Forbid token-pasting (`##`), stringification (`#`), recursive/variadic macros, and conditional compilation that varies symbol meaning across files.

In other languages: read this as "limit metaprogramming." Reflection, code generation, runtime class manipulation, and macro DSLs all defeat static analysis the same way the C preprocessor does.

## Rationale

The preprocessor runs before the compiler sees the source. Aggressive use produces code that is unreadable without running cpp by hand and defeats static analysis, debuggers, and IDE tooling. Same logic applies to runtime reflection and codegen DSLs in other languages.

## What a violation looks like

- C: `#define MAX(a,b) ((a)>(b)?(a):(b))` — function-like macro with side-effect risk
- C: token-pasted struct generators, recursive macros
- Java: `Class.forName(...)`, `Method.invoke(...)` for control flow
- Kotlin: `kotlinx.serialization` / KSP for safety-critical paths (acceptable for boilerplate; not for control flow)
- Python: `eval`, `exec`, `__import__`, monkey-patching production code
- Go: `unsafe.Pointer` for type punning; `reflect` for control flow

## Per-language guidance

### C
- Allowed: `#include`, `#define CONST 42`, narrow `#ifdef PLATFORM_X`
- Forbidden: `##`, `#`, recursive macros, variadic macros, function-like macros with side effects
- Prefer `static const` and `static inline` functions over macros
- Tools: `clang-tidy` (`cppcoreguidelines-macro-usage`, `bugprone-macro-parentheses`, `bugprone-reserved-identifier`)

### Go
- Forbid `unsafe` outside narrowly-scoped, well-reviewed packages
- Forbid `reflect` in hot paths; allowed for serialization layer
- Code generation (`go generate`) acceptable when generated output is committed and reviewed
- Tools: `golangci-lint` (`gosec` G103 for unsafe, `staticcheck` SA1019); manual review for `reflect`

### Python
- Forbid `eval`, `exec`, `compile` on user input. Forbid monkey-patching production modules
- Decorators OK (they're functions). Metaclasses discouraged
- Tools: `bandit` (B102, B307 eval/exec); `ruff` (`S102`, `S307`)

### Java
- Forbid `Class.forName` for control flow; allowed for plugin-loading at init
- Annotation processors and APT-generated code OK if generated source is committed
- Forbid `setAccessible(true)` on production state
- Tools: `Error Prone` (`Reflection`, `Var`); `SpotBugs` `DP_DO_INSIDE_DO_PRIVILEGED`

### Kotlin
- KSP / KAPT acceptable for serialization, DI registration, schema codegen
- Forbid `kotlin.reflect.full.*` for control flow
- Inline DSL builders OK if they generate type-checkable code
- Tools: `detekt` (`SpreadOperator`); manual review for KSP usage in safety paths

## Remediation pattern

```c
// Before (Rule 8 violation)
#define SQUARE(x) ((x)*(x))
int n = SQUARE(i++);  // i incremented twice — undefined

// After
static inline int square(int x) { return x * x; }
int n = square(i++);  // i incremented once; well-defined
```

## When metaprogramming is justified

- Boilerplate elimination at build time (annotation processors, codegen) where output is reviewable
- Serialization/deserialization mappers for I/O boundaries
- Test scaffolding only — never production control flow

Document the boundary:

```python
# pow10: allow rule=8 until=2099-01-01 owner=parser-team reason="generated parser tables; output committed at parser/_generated.py"
```

## Citations

- Holzmann 2006 — Rule 8
