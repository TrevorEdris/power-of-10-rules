# Rule 5 - Assertion Density (Python)

**Statement (Holzmann):** Use a minimum of two runtime assertions per function on average across a translation unit, each side-effect-free and triggering a defined recovery path rather than being stripped in release builds.

**Profile (adapted):** applies partially; severity **medium**.

The literal "≥2 assertions per function" count doesn't fit Python app code, but the core hazard is real: bare `assert` used for input validation vanishes under `python -O` or certain optimized runs. Enforce the boundary distinction instead - raise explicit exceptions for anything reachable from untrusted input (API payloads, CLI args, env vars), and treat `assert` as an acceptable dev-time sanity check only where being stripped carries no security or correctness risk.

## Checklist
- Never use bare `assert` to validate external/untrusted input (request bodies, query params, CLI args, env vars) reachable in production
- Raise a specific exception type (`ValueError`, a domain exception) with a message identifying the violated invariant, not a bare `assert`
- Reserve `assert` for internal invariants where stripping under `-O` is an acceptable risk
- Prefer typed validation (pydantic/attrs/dataclass + mypy) over ad-hoc guard clauses for structured external input
- Cover the raise path for each validation branch with a test
- Treat ruff `S101` findings on trust-boundary code as must-fix, not style noise

## Violation

```python
def transfer(from_account, to_account, amount):
    assert amount > 0
    from_account.balance -= amount
    to_account.balance += amount
    return from_account.balance
```

## Fix

```python
class InsufficientFunds(Exception):
    def __init__(self, amount: int, balance: int) -> None:
        super().__init__(f"amount {amount} exceeds balance {balance}")


def transfer(from_account, to_account, amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if from_account.balance < amount:
        raise InsufficientFunds(amount, from_account.balance)
    from_account.balance -= amount
    to_account.balance += amount
```

## Tooling
- `ruff`: `S101` (assert used - stripped under `-O`; ruff flags all assert usage, security-sensitive checks especially)
- `ruff`: `B011` (assert-false - use `raise` instead of `assert False`)
- `manual review`: count guard density on complex/high-risk functions (financial, auth, concurrency); typed signatures narrow the surface needing manual guards

## Strict profile
Requires >= 2 side-effect-free runtime checks per function on average, counted mechanically; a stripped `assert` does not count toward the total, so use `if not cond: raise` instead **[high]**.
