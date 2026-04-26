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

## What a violation looks like

- Mutable module-level state shared across functions
- Variables declared at function top but used only inside one branch
- File-scope `static int counter = 0;` mutated from multiple functions
- Loop variables declared outside the loop

## Per-language guidance

### C
- C99 mid-block declarations: declare at point of first use, not function top
- Forbid non-const globals; file-scope `static` allowed only when truly module-private and documented
- Tools: `clang-tidy` `cppcoreguidelines-avoid-non-const-global-variables`, `readability-isolate-declaration`

### Go
- No package-level mutable state — pass via struct or context
- Declare loop-scoped vars with `:=` inside the loop, not above it
- Beware Go 1.21- loop variable capture (fixed in 1.22)
- Tools: `golangci-lint` (`gochecknoglobals`, `gochecknoinits`, `scopelint`/`exportloopref`)

### Python
- No mutable module-level state. Use class instances or pass explicitly
- Avoid `global` keyword
- Inline `with` blocks scope resources tightly
- Tools: `ruff` (`PLW0603` global-statement, `PLW0602` global-variable-not-assigned)

### Java
- No mutable static fields — make them `final`. For shared mutable state, encapsulate in a single owner class with synchronized access
- Declare locals at point of use, not method top
- Tools: `Checkstyle` `VariableDeclarationUsageDistance`; `PMD` `AvoidUsingVolatile`, `BeanMembersShouldSerialize`; `SpotBugs` `MS_*` static-mutability checks

### Kotlin
- Prefer `val` over `var`. No `companion object` mutable fields
- Use `also`/`apply` to scope side-effects
- Tools: `detekt` (`VarCouldBeVal`, `TopLevelPropertyNaming`, `MagicNumber`)

## Remediation pattern

```python
# Before (Rule 6 violation)
counter = 0  # module-level mutable
def tick():
    global counter
    counter += 1

# After
class Ticker:
    def __init__(self) -> None:
        self._counter = 0
    def tick(self) -> int:
        self._counter += 1
        return self._counter
```

State is now scoped, ownership is explicit, and the class is testable in isolation.

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
