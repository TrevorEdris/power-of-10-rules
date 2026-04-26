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

## Universal violation patterns

- Discarded non-void returns (`(void)foo()`, `_, _ = foo()`, bare `foo();`)
- Function entry that mutates state before validating parameters
- Empty `catch` / `except` blocks swallowing errors
- `Optional.get()` / `!!` without prior null check
- Errors crossing module boundaries unwrapped

## Universal remediation pattern

At function entry, validate every parameter against domain constraints and reject (return error or raise) before any side effect. After every fallible call, check the return; on failure, propagate (with wrapping for traceability) and roll back any partial mutation.

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## Documented `(void)` casts

When you genuinely don't care about a return value (best-effort cleanup), state why:

```c
(void)fclose(fp); // best-effort; fp already drained
```

```go
//nolint:errcheck // best-effort; lock already released
_ = file.Close()
```

## Citations

- Holzmann 2006 — Rule 7
- CERT C — ERR33-C
