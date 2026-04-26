---
name: pow10-rule-07-check-return-values
description: "NASA Power of 10 Rule 7 — Check every non-void return value; validate every parameter. Severity: blocker."
---

# Rule 7 — Check Return Values & Validate Parameters

**Severity:** blocker

## Statement

Check the return value of every non-void function. Validate every parameter at function entry, before any state mutation. Callers cannot be trusted, even within the same module.

## Rationale

Ignoring a return value discards error information the callee computed. Unvalidated parameters let bad input propagate into corrupted state. Both checks isolate errors at their source.

## What a violation looks like

- `(void)foo()` without a comment justifying why it's safe to ignore
- Function entry that mutates state before validating parameters
- `errno` checked after the wrong call
- Errors swallowed with empty `catch` / `_ = ...` / `// nolint`

## Per-language guidance

### C
- Forbid bare `foo();` for non-void functions. Allow `(void)foo();` only with adjacent comment
- Validate params at top of function; assert non-null and bounds
- Tools: `clang-tidy` (`bugprone-unused-return-value`, `bugprone-argument-comment`, `cert-err33-c`); `cppcheck`

### Go
- Idiomatic — Go forces multi-return error handling. Forbid `_, _ = foo()` outside test code
- Use `if err != nil { return err }` consistently. No naked `return` after error
- Tools: `golangci-lint` (`errcheck`, `errorlint`, `wrapcheck`, `nilerr`); `staticcheck` SA4006 (unused result)

### Python
- Functions raise on error rather than returning codes — but check returned `Optional` / `Result` types
- For typed returns, run `mypy --strict` to force `Optional` handling
- Validate params with explicit `if not isinstance(...) or x < 0: raise ValueError(...)`
- Tools: `ruff` (`RET503` missing-return, `RUF013` PEP-484 implicit-optional); `mypy`

### Java
- Annotate methods with `@CheckReturnValue` (JSR-305 / Error Prone)
- Validate params with `Objects.requireNonNull` / `Preconditions.checkArgument` at entry
- For `Optional` returns, never call `.get()` without prior `.isPresent()`
- Tools: `Error Prone` `CheckReturnValue`, `NullAway`; `SpotBugs` `RV_RETURN_VALUE_IGNORED`

### Kotlin
- Mark return-required functions with `@CheckReturnValue` or use sealed `Result<T>`
- Use `requireNotNull` for params; nullability is type-system enforced (no `!!`)
- For `Result`, force handling with `.getOrElse {}` / `.fold { } { }`
- Tools: `detekt` (`UnusedReturnValue`, `UnsafeCallOnNullableType` for `!!`)

## Remediation pattern

```go
// Before (Rule 7 violation)
func transfer(from *Account, to *Account, amount int64) {
    from.Withdraw(amount)
    to.Deposit(amount)
}

// After
func transfer(from, to *Account, amount int64) error {
    if from == nil || to == nil {
        return ErrNilAccount
    }
    if amount <= 0 {
        return fmt.Errorf("non-positive amount: %d", amount)
    }
    if err := from.Withdraw(amount); err != nil {
        return fmt.Errorf("withdraw: %w", err)
    }
    if err := to.Deposit(amount); err != nil {
        return fmt.Errorf("deposit: %w", err)
    }
    return nil
}
```

Param validation upfront; both errors checked; wrapped for traceability.

## Documented `(void)` casts

When you genuinely don't care about a return value (best-effort cleanup), explain why:

```c
(void)fclose(fp); // best-effort; fp already drained
```

## Citations

- Holzmann 2006 — Rule 7
- CERT C — ERR33-C
