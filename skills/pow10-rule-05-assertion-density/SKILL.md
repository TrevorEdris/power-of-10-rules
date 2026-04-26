---
name: pow10-rule-05-assertion-density
description: "NASA Power of 10 Rule 5 — Average ≥2 runtime assertions per function. Severity: high."
---

# Rule 5 — Assertion Density

**Severity:** high

## Statement

Use a minimum of two runtime assertions per function on average across a translation unit. Assertions must have no side effects and must trigger a defined recovery path (not be stripped) in release builds.

## Rationale

Assertions catch what static analysis cannot: violated preconditions, impossible states, broken invariants. Forcing the author to write ~2 per function makes them think through boundaries explicitly. Side-effect-free assertions are safe to compile out for performance experiments — but for safety-critical builds they should remain or invoke a recovery handler.

## What a violation looks like

- Function with no preconditions, postconditions, or invariant checks
- `assert(x++ > 0)` — side-effecting expression inside assert
- `assert(False)` as a marker for unreachable code without a defined handler
- `NDEBUG` defined in safety-critical builds

## Per-language guidance

### C
- Use `assert.h`. For release-build safety, replace `NDEBUG` strip with a `safe_assert` macro that calls a recovery handler
- Validate parameters at function entry; assert invariants before mutating state
- Tools: custom metric (count `assert(` per function); manual review for side-effects

### Go
- Go has no `assert`. Use explicit `if !cond { panic("...") }` or `log.Fatal`
- For test-only invariants use `t.Helper()` + `if got != want { t.Fatalf(...) }`
- Pre-condition style: return early with a sentinel error
- Tools: `go vet` flags some misuse; custom linter for `if` density

### Python
- Use `assert` at module top + parameter checks. Beware: Python strips asserts when run with `-O`. For safety-critical paths, use explicit `if not cond: raise InvariantError(...)` instead
- Tools: `ruff` (`B011` assert-False, `S101` assert-in-prod for security contexts); custom AST count

### Java
- `assert` is disabled by default — must enable with `-ea`. Prefer `Objects.requireNonNull` and explicit `if (...) throw new IllegalStateException(...)`
- Use `Preconditions.checkArgument`/`checkState` (Guava) or `Validate` (Apache Commons) for parameter validation
- Tools: `SpotBugs` (`NP_NULL_PARAM_DEREF`); `Checkstyle` custom check

### Kotlin
- Built-in: `require(...)` for params, `check(...)` for state, `requireNotNull` for nullability
- Idiomatic and not strippable, unlike `assert`
- Tools: `detekt` (`UseCheckOrError`, `UseRequire`)

## Remediation pattern

```kotlin
// Before (Rule 5 violation)
fun transfer(from: Account, to: Account, amount: Long) {
    from.balance -= amount
    to.balance += amount
}

// After
fun transfer(from: Account, to: Account, amount: Long) {
    require(amount > 0) { "amount must be positive: $amount" }
    require(from.balance >= amount) { "insufficient funds" }
    check(from != to) { "self-transfer" }
    from.balance -= amount
    to.balance += amount
    check(from.balance >= 0) { "balance went negative" }
}
```

Four assertions in a 6-line function — densifies invariants without adding logic.

## What counts

- Parameter validation at entry
- State invariant checks before mutation
- Postcondition checks before return
- Loop invariants inside bounded loops

What does NOT count: error handling for expected failures (network down, file missing). That's normal control flow, not an assertion.

## Citations

- Holzmann 2006 — Rule 5
