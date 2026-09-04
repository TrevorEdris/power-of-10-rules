# Rule 7 — Go

## Forbidden

`_, _ = foo()` outside test code. Naked `return` after error path. Unwrapped errors crossing module boundaries. Calling mutation functions before validating parameters.

## Violating example

```go
func Withdraw(acct *Account, amount int64) {
    acct.balance -= amount
    writeLog(acct, amount)
}
```

`acct` not nil-checked; amount not validated; `writeLog` error discarded.

## Remediation

```go
func Withdraw(acct *Account, amount int64) error {
    if acct == nil {
        return ErrNilAccount
    }
    if amount <= 0 {
        return fmt.Errorf("withdraw: non-positive amount: %d", amount)
    }
    if acct.balance < amount {
        return ErrInsufficientFunds
    }

    acct.balance -= amount

    if err := writeLog(acct, amount); err != nil {
        acct.balance += amount  // roll back
        return fmt.Errorf("withdraw: log: %w", err)
    }
    return nil
}
```

`fmt.Errorf("...: %w", err)` wraps for traceability; rollback on log failure.

## Hard checks

- `golangci-lint`:
  - `errcheck` (forbid ignored returns)
  - `errorlint` (catch type-assertion on errors)
  - `wrapcheck` (require wrapping at module boundaries)
  - `nilerr` (catch returning nil after error)
- `staticcheck` `SA4006` (unused result)
