# Rule 5 - Assertion Density (Go)

**Statement (Holzmann):** Use a minimum of two runtime assertions per function on average across a translation unit, with each assertion side-effect-free and triggering a defined recovery path rather than being stripped in release builds.

**Profile (adapted):** applies in spirit; severity **advisory**.

Go has no `assert`, and the literal "2 checks per function, averaged" metric doesn't translate to idiomatic Go. The hazard survives: unchecked preconditions and invariants let corrupted state propagate silently. Validate inputs and invariants at trust boundaries, and keep Holzmann's distinction between a programmer-error invariant (panic) and an expected-failure condition (return error).

## Checklist
- Validate external/untrusted input (HTTP handler bodies, CLI args, config/env parsing) before use in exported functions
- Panic with a clear message on invariant violations that indicate a programmer bug (nil that should be impossible, self-transfer, corrupted internal state)
- Return an error, never panic, for expected failure conditions (not-found, insufficient funds, network error)
- Never use recover()-and-swallow to hide an invariant violation without logging or re-raising
- Write table-driven tests that exercise both the error-return paths and the panic paths
- Reserve literal per-function assertion counts for complex, high-risk functions (financial, auth, concurrency), not every function

## Violation

```go
package main

func Transfer(from, to *Account, amount int64) {
    from.balance -= amount
    to.balance += amount
}

func main() {}
```

## Fix

```go
package main

func Transfer(from, to *Account, amount int64) error {
    if from == nil || to == nil {
        panic("Transfer: nil account")
    }
    if amount <= 0 {
        return fmt.Errorf("amount must be positive, got %d", amount)
    }
    from.balance -= amount
    to.balance += amount
    return nil
}
```

## Tooling
- `errcheck`: default checks - flags unchecked error return values anywhere in the code, not assertion density itself (Rule 7, adjacent to this rule)
- `go vet`: `./...` - catches suspicious constructs and API misuse, not assertion density itself
- `manual review`: no golangci-lint check counts invariant guards per function; flag functions handling untrusted input with zero validation

## Strict profile
Count >=2 side-effect-free assertion-equivalent guards per function, averaged across the file; route every failed guard to a defined recovery handler instead of compiling it out [high].
