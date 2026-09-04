# Rule 7 — Python

## Forbidden

Discarding `Optional[T]` returns without `is not None` check. Calling `.get()` on a `dict` and treating result as non-None. Bare `try: ... except:` swallowing errors silently. Mutating state before validating inputs.

## Violating example

```python
def withdraw(account, amount):
    account.balance -= amount
    write_log(account, amount)
```

No checks. `write_log` may raise; if so, balance is decremented but not logged.

## Remediation

```python
def withdraw(account: Account, amount: int) -> None:
    if account is None:
        raise ValueError("account is None")
    if amount <= 0:
        raise ValueError(f"amount must be positive: {amount}")
    if account.balance < amount:
        raise InsufficientFundsError(amount, account.balance)

    account.balance -= amount
    try:
        write_log(account, amount)
    except LogError:
        account.balance += amount  # roll back
        raise
```

Validation upfront; explicit rollback on log failure; the exception is re-raised so callers can react.

## Hard checks

- `ruff`:
  - `RET503` (missing-explicit-return)
  - `RUF013` (PEP-484 implicit-optional)
  - `B017` (assert-raises-exception too broad)
- `mypy --strict` to force `Optional` handling at compile time
