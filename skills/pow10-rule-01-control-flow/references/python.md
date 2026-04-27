# Rule 1 — Python

## Forbidden

Direct or indirect recursion. `try`/`except` used as control flow on the normal path. (Python has no `goto`.)

## Violating example

```python
def walk(node, visit):
    if node is None:
        return
    visit(node)
    walk(node.left, visit)
    walk(node.right, visit)
```

Default recursion limit is 1000 frames; deep trees raise `RecursionError`.

## Remediation

Iterate with an explicit bounded deque:

```python
from collections import deque

MAX_NODES = 10_000

def walk(root, visit):
    stack = deque([root])
    for _ in range(MAX_NODES):
        if not stack:
            return
        node = stack.pop()
        if node is None:
            continue
        visit(node)
        stack.append(node.right)
        stack.append(node.left)
    raise RuntimeError(f"walk exceeded {MAX_NODES} nodes")
```

The `range(MAX_NODES)` cap satisfies Rule 2; the explicit raise prevents silent overrun.

## Hard checks

- `ruff` codes: `PLR0911` (too-many-return), `PLW0603` (global-statement)
- `pylint` `R0901` for inheritance depth
- Manual review or custom AST check for recursion (no built-in linter rule)
