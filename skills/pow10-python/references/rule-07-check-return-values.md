# Rule 7 - Check Return Values & Validate Parameters (Python)

**Statement (Holzmann):** The return value of non-void functions must be checked by each calling function, and the validity of parameters must be checked inside each function.

**Profile (adapted):** applies in spirit; severity **high**.

Python has no non-void/void distinction and surfaces most failures via exceptions, not return codes, so a literal reading doesn't map. The intent survives as two habits: never silently swallow an exception, and check results of calls that signal success/failure without raising. Validate inputs at public API boundaries before mutating state; private helpers may trust their sole caller.

## Checklist
- Name every exception an `except` clause handles; never use bare `except:` or `except Exception: pass`.
- Check results that signal success/failure without raising (`subprocess.run().returncode`, `shutil.copy`, boolean-returning I/O helpers) instead of discarding them.
- Narrow `Optional[T]` with `is not None` before use; run `mypy --strict` so unchecked-Optional access fails at type-check time.
- Validate argument types and value constraints at public functions (route handlers, CLI entry points, published library functions) before mutating state.
- Wrap or re-raise exceptions crossing a module/service boundary with context (`raise ServiceError(...) from e`) instead of letting a bare leaf exception propagate.

## Violation

```python
import json


def withdraw(account, amount):
    account.balance -= amount
    write_log(account, amount)


def load_config(path):
    try:
        return json.load(open(path))
    except Exception:
        pass
```

## Fix

```python
def withdraw(account: Account, amount: int) -> None:
    if amount <= 0:
        raise ValueError(f"amount must be positive: {amount}")
    if account.balance < amount:
        raise InsufficientFundsError(amount, account.balance)
    account.balance -= amount
    try:
        write_log(account, amount)
    except LogError:
        account.balance += amount
        raise


def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise ConfigError(path) from e
```

## Tooling
- `ruff`: `RET503` (implicit-return) - flags a function with a return value on some paths but not others
- `ruff`: `RUF013` (implicit-optional) - flags a default of `None` on a parameter not typed `Optional`
- `ruff`: `B017` (assert-raises-exception) - flags `assertRaises(Exception)`, too broad to prove the right error path is checked
- `mypy --strict`: forces `Optional` narrowing before use, catching unchecked-return access
- `manual review`: bare `except:` / `except Exception: pass`, and discarded results of `subprocess.run`, `shutil.copy`, or similar non-raising calls

## Strict profile
Literal profile treats every discarded return and every unvalidated parameter as a blocker, matching Holzmann's wording with no in-spirit carve-out. CI gates: `ruff check` (RET503, RUF013, B017 as errors) and `mypy --strict` both clean, zero bare `except` clauses.
