# Rule 2 — Python

## Forbidden

`while True:` without a counter cap. `while cond:` without a bounded outer loop.

## Violating example

```python
def drain(q):
    while q:
        process(q.popleft())
```

If `q` is fed faster than `process` consumes, no termination.

## Remediation

Bound with `range`:

```python
MAX_DRAIN = 256

def drain(q):
    for _ in range(MAX_DRAIN):
        if not q:
            return
        process(q.popleft())
    raise RuntimeError(f"drain exceeded {MAX_DRAIN}")
```

Termination is now provable; cap is a constant.

## Hard checks

- `ruff` codes: `PLW0120` (else-on-loop), `B007` (unused loop var)
- Manual review for `while True` and unbounded `while cond`
