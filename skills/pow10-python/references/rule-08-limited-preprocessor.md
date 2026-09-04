# Rule 8 - Limited Preprocessor (Python)

**Statement (Holzmann):** Restrict preprocessor use to header inclusion and simple macro definitions; forbid token pasting, variable-argument macro lists, and recursive macro calls.

**Profile (adapted):** applies partially; severity **high**.

Python has no preprocessor, but `eval`/`exec` and dynamic name lookup defeat static analysis the same way unrestrained macros do. `eval`/`exec` on untrusted or dynamically-built strings is a real risk in normal app code (config parsing, template rendering, plugin loading) and is banned outright. Decorators, `dataclasses`, `attrs`, and pydantic/ORM metaclasses are pervasive and idiomatic - they stay allowed so the rule remains usable in normal services.

## Checklist
- Never call `eval()`/`exec()` on strings built from request input, config, or any non-literal source
- Never use `globals()[name]` or `getattr(obj, user_controlled_string)` for control-flow dispatch - use an explicit dict/enum dispatch table
- Allow decorators, `dataclasses`, `attrs`, and pydantic/ORM metaclasses without flag
- Flag dynamic `importlib.import_module()` calls with a non-literal, user-influenced name; a fixed allowlist of plugin names is fine
- Forbid runtime monkey-patching of production modules/classes outside test fixtures

## Violation

```python
def handle_create(payload: dict):
    return {"created": payload}


def handle_update(payload: dict):
    return {"updated": payload}


def dispatch(action: str, payload: dict):
    handler = globals()[f"handle_{action}"]
    return handler(payload)
```

## Fix

```python
def handle_create(payload: dict):
    return {"created": payload}


def handle_update(payload: dict):
    return {"updated": payload}


DISPATCH = {
    "create": handle_create,
    "update": handle_update,
}


def dispatch(action: str, payload: dict):
    handler = DISPATCH.get(action)
    if handler is None:
        raise ValueError(f"unknown action: {action}")
    return handler(payload)
```

## Tooling
- `ruff`: `S102` - flags use of `exec`
- `ruff`: `S307` - flags suspicious `eval` usage
- `bandit`: `B102 (exec_used)` - flags use of `exec`
- `bandit`: `B307 (eval)` - flags suspicious `eval` usage
- `manual review`: `globals()`/`getattr()`-based dispatch tables, dynamic `importlib.import_module()` calls with non-literal names, runtime monkey-patching outside tests

## Strict profile
Strict **[high]** forbids `eval`, `exec`, computed `getattr(obj, name)` dispatch, and metaclasses in application code entirely, regardless of input source. `importlib.import_module()` names must come from a fixed, reviewed allowlist with no dynamic construction.
