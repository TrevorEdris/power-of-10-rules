# Rule 8 — Python

Python's analogues to the C preprocessor: `eval`, `exec`, `compile`, monkey-patching, dynamic attribute lookup with `getattr(obj, user_input)`.

## Allowed

Decorators (they're plain functions). Type aliases. `dataclass` and `attrs` codegen. Module-level `__all__` declarations.

## Forbidden in safety paths

`eval`/`exec` on any data not produced by a trusted source at this commit. Monkey-patching production modules at runtime. Metaclasses for control flow (acceptable for ORMs at the framework boundary).

## Violating example

```python
def dispatch(action: str, payload: dict) -> Any:
    handler = globals()[f"handle_{action}"]
    return handler(payload)
```

`globals()` lookup is dynamic; safe analyzers cannot enumerate reachable handlers; failure mode is `KeyError` at runtime.

## Remediation

Explicit dispatch table:

```python
def handle_create(payload: dict) -> Result: ...
def handle_update(payload: dict) -> Result: ...
def handle_delete(payload: dict) -> Result: ...

DISPATCH: dict[str, Callable[[dict], Result]] = {
    "create": handle_create,
    "update": handle_update,
    "delete": handle_delete,
}

def dispatch(action: str, payload: dict) -> Result:
    handler = DISPATCH.get(action)
    if handler is None:
        raise ValueError(f"unknown action: {action}")
    return handler(payload)
```

Dispatch table is enumerable; tools see all reachable handlers; unknown action surfaces as a typed error.

## Hard checks

- `bandit`:
  - `B102` (exec)
  - `B307` (eval)
- `ruff`:
  - `S102` (use-of-exec)
  - `S307` (suspicious-eval-usage)
  - `PGH001` (eval/exec)
