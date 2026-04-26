# Rule 5 — Go

## Target

Go has no `assert` — use explicit `if !cond { panic(...) }` for invariants and `if cond { return ErrX }` for expected failures (those are control flow, not assertions). Aim for ≥ 2 invariant guards per non-trivial function.

## Violating example

```go
func Transfer(from, to *Account, amount int64) {
    from.balance -= amount
    to.balance += amount
}
```

No precondition, no postcondition, accepts nil and negative amounts silently.

## Remediation

```go
func Transfer(from, to *Account, amount int64) error {
    if from == nil || to == nil {
        panic("Transfer: nil account")
    }
    if amount <= 0 {
        return fmt.Errorf("Transfer: amount must be positive, got %d", amount)
    }
    if from.balance < amount {
        return ErrInsufficientFunds
    }
    if from == to {
        panic("Transfer: self-transfer")
    }

    from.balance -= amount
    to.balance += amount

    if from.balance < 0 {
        panic(fmt.Sprintf("Transfer: balance went negative: %d", from.balance))
    }
    return nil
}
```

Programmer errors → `panic`. Expected runtime failures → returned errors.

## Hard checks

- `go vet ./...` flags some misuse
- Manual review or custom analyzer for invariant-density per function
- `errcheck` ensures returned errors aren't ignored (Rule 7)
