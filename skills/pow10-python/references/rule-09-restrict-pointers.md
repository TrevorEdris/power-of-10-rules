# Rule 9 - Restrict Pointers (Python)

**Statement (Holzmann):** No more than one level of pointer dereferencing per declaration, pointer dereferences may not be hidden inside macro definitions or typedef declarations, and no function pointers.

**Profile (adapted):** applies in spirit; severity **advisory**.

Python's dynamism - first-class functions, decorators, duck typing - is core to the language, so a literal ban on callables or dispatch dicts is not workable. The rule narrows to: don't let externally or dynamically supplied callables drive safety- or business-critical branching without a typed contract, and don't let closures silently capture mutable state read later at call time. Most application code is exempt; this tightens for payment, auth, and state-machine logic.

## Checklist
- Define and populate dispatch dicts that drive critical control flow in one module, not from dynamic imports or unvalidated plugin discovery.
- Type public or plugin entry points with a `Protocol` or ABC, not a bare `Callable`, when the call site is safety- or money-critical.
- Avoid closures in critical branching that capture and later mutate an outer-scope variable read at call time.
- Avoid curried or higher-order chains (`f(x)(y)(z)`) in core business logic.
- Run `mypy --strict` on any module defining a `Protocol`-based dispatch registry.

## Violation

```python
def dispatch(handlers: dict, event: str) -> None:
    handlers[event]()  # handlers can come from anywhere, untyped


handlers = {}


def register(name, fn):
    handlers[name] = fn
```

## Fix

```python
from typing import Protocol


class Handler(Protocol):
    def handle(self) -> None:
        pass


class RefundHandler:
    def handle(self) -> None:
        print("refund")

_HANDLERS: dict[str, Handler] = {"refund": RefundHandler()}


def dispatch(event: str) -> None:
    handler = _HANDLERS.get(event)
    if handler is None:
        raise ValueError(f"unknown event: {event}")
    handler.handle()
```

## Tooling
- `mypy --strict`: enforces the `Protocol`-typed dispatch registry instead of a bare `Callable`
- `ruff`: `B023` - flags loop-variable capture in closures, the classic late-binding bug
- `manual review`: dispatch dicts assembled from dynamic imports or plugin discovery outside one owning module

## Strict profile
No `Callable` parameters and no dispatch dicts anywhere in application code, severity **blocker** - the module-boundary and `Protocol`-contract exceptions in the adapted profile no longer apply.
