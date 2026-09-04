# Rule 6 - Minimum Scope (Python)

**Statement (Holzmann):** Data is declared in the smallest scope that can contain it, with no mutable globals or file-scope statics unless explicitly marked read-only.

**Profile (adapted):** applies in spirit; severity **medium**.

A literal "no module-level state" ban is unworkable in Python: module-level constants, `logging.getLogger(__name__)`, compiled regexes, and framework singletons (FastAPI `app`, SQLAlchemy `engine`) are standard because they are set once at import time and never mutated. The real hazard this rule guards against is the `global` keyword and any module-level container or counter that functions write to across calls - that produces hidden coupling, cross-test pollution, and thread-unsafety.

## Checklist
- Verify no function uses the `global` statement to mutate a module-level name
- Confirm module-level names are constants, loggers, or singletons assigned once at import time
- Move mutable state (caches, counters, buffers) onto a class instance instead of a module dict or list
- Construct long-lived resources (DB connections, HTTP clients) once and inject them explicitly, not lazily cache them in a bare module global
- Declare locals at first use, not hoisted to the top of the function

## Violation

```python
_cache = {}

def set_item(k, v):
    global _cache
    _cache[k] = v

def get_item(k):
    return _cache.get(k)
```

## Fix

```python
class Cache:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def set_item(self, k: str, v: str) -> None:
        self._store[k] = v

    def get_item(self, k: str) -> str | None:
        return self._store.get(k)
```

## Tooling
- `ruff`: `PLW0603` - flags the `global-statement` that mutates module state
- `ruff`: `PLW0602` - flags `global` declared but never assigned (dead scope leak)
- `ruff`: `PLW0604` - flags `global` used outside a function, at module level
- `pylint`: `W0603` - flags `global-statement` use
- `pylint`: `W0602` - flags `global-variable-not-assigned`
- `manual review`: check that module-level names are assigned exactly once at import time, not reassigned later

## Strict profile
Strict mode **[medium]**: bans all module-level mutable state, even without `global` - no list or dict on an imported module object that any function appends to or mutates after import time.
