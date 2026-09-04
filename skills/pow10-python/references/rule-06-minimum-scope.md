# Rule 6 — Python

## Forbidden

Module-level mutable state. `global` keyword. Loop-iterable as a name shared with module-level. Resources opened without `with` block.

## Violating example

```python
counter = 0

def tick() -> None:
    global counter
    counter += 1

def read() -> int:
    return counter
```

Module-level mutable; coupled functions; tests in different files share state.

## Remediation

```python
class Ticker:
    def __init__(self) -> None:
        self._value = 0

    def tick(self) -> None:
        self._value += 1

    def read(self) -> int:
        return self._value
```

Each `Ticker()` instance is independent; ownership explicit at construction.

## Hard checks

- `ruff`:
  - `PLW0603` (global-statement)
  - `PLW0602` (global-variable-not-assigned)
  - `PLW0604` (global-at-module-level)
- `pylint`:
  - `W0603` (global-statement)
  - `W0602` (global-variable-not-assigned)
