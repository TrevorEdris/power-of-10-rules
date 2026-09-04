# Rule 9 — Python

Python's analogue: deeply nested `Callable[[...], Callable[[...], ...]]` types crossing module boundaries; closures capturing mutable state; lambdas-of-lambdas in dispatch.

## Forbidden in safety paths

Dispatch via `Callable` parameters supplied by external modules. Curried higher-order functions in safety code. Closures that capture and mutate outer-scope state.

## Allowed

Named callable classes implementing a known protocol. Local closures over read-only data.

## Violating example

```python
def dispatch(handlers: dict[str, Callable[[Event], Result]], event: Event) -> Result:
    return handlers[event.type](event)
```

Callable map is open; reviewer cannot enumerate reachable handlers without grepping callers.

## Remediation

Use a `Protocol` plus an explicit registry confined to the safety package:

```python
from typing import Protocol

class Handler(Protocol):
    def handle(self, event: Event) -> Result: ...

class HeartbeatHandler:
    def handle(self, event: Event) -> Result: ...

class CommandHandler:
    def handle(self, event: Event) -> Result: ...

_HANDLERS: dict[str, Handler] = {
    "heartbeat": HeartbeatHandler(),
    "command":   CommandHandler(),
}

def dispatch(event: Event) -> Result:
    handler = _HANDLERS.get(event.type)
    if handler is None:
        raise ValueError(f"unknown event type: {event.type}")
    return handler.handle(event)
```

Registry private to module; handler types named; static analysis sees the call graph.

## Hard checks

- `mypy --strict` to enforce typed `Handler` protocol
- Manual review for `Callable` parameters crossing module boundaries
- `ruff` `B023` (function-uses-loop-variable for closure capture bugs)
