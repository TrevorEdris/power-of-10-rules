# Rule 5 — Python

## Target

Average ≥ 2 invariant checks per function. Beware: `assert` is stripped under `python -O`. For safety paths, use explicit `if not cond: raise InvariantError(...)` instead of `assert`.

## Violating example

```python
def transfer(from_account, to_account, amount):
    from_account.balance -= amount
    to_account.balance += amount
```

No types, no preconditions, no invariant checks.

## Remediation

```python
def transfer(from_account: Account, to_account: Account, amount: int) -> None:
    if from_account is None or to_account is None:
        raise InvariantError("transfer: account is None")
    if amount <= 0:
        raise ValueError(f"transfer: amount must be positive, got {amount}")
    if from_account.balance < amount:
        raise InsufficientFunds(amount, from_account.balance)
    if from_account is to_account:
        raise InvariantError("transfer: self-transfer")

    from_account.balance -= amount
    to_account.balance += amount

    if from_account.balance < 0:
        raise InvariantError(f"transfer: balance went negative: {from_account.balance}")
```

Five guards. Programmer errors raise distinct exceptions; expected failures raise domain errors. None can be stripped by `-O`.

## Hard checks

- `ruff`:
  - `B011` (assert-False — use raise instead)
  - `S101` (assert in production for security contexts)
- Manual review: count guard density per function
- `mypy --strict` to enforce typed signatures so callers can't pass `None` silently
