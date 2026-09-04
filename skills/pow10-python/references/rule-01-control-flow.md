# Rule 1 - Restrict Control Flow to Simple Constructs (Python)

**Statement (Holzmann):** Use only straight-line execution, conditionals, and bounded iteration; forbid `goto`, `setjmp`/`longjmp`, and recursion (direct or indirect, including mutual recursion).

**Profile (adapted):** applies partially; severity **medium**.

Python has no `goto`, so that clause is not applicable. Recursion is common and idiomatic for tree and graph algorithms, and CPython's default recursion limit (1000 frames) turns unbounded recursion into a catchable `RecursionError` rather than memory corruption. The real modern hazard is recursion whose depth is driven by external or untrusted input (nested JSON/YAML, recursive file-tree walks) - that is a stack-exhaustion DoS vector and should be capped.

## Checklist
- Cap the depth of any recursive function that walks user- or network-supplied nesting.
- Raise an explicit, named error when the depth cap is exceeded; do not truncate silently.
- Do not use `sys.setrecursionlimit()` to paper over recursion that should be iterative.
- Accept recursion over trusted, size-bounded internal data structures without extra guards.
- Extension beyond Holzmann's rule 1 (Python-specific, not canonical): avoid `try`/`except` as non-local `goto`-style control flow on the normal, non-error path.

## Violation

```python
def depth(node, d=0):
    # No cap: nesting depth is fully controlled by caller-supplied data.
    if not isinstance(node, dict) or not node:
        return d
    return max(depth(v, d + 1) for v in node.values())
```

## Fix

```python
MAX_DEPTH = 64


def depth(node, d=0):
    if d > MAX_DEPTH:
        raise ValueError(f"nesting exceeds {MAX_DEPTH}")
    if not isinstance(node, dict) or not node:
        return d
    return max(depth(v, d + 1) for v in node.values())
```

## Tooling
- `ruff` `C901`: proxy: mccabe complexity threshold - flags functions with high branching, not recursion itself
- `manual review`: no ruff or pylint rule detects recursion directly; grep for a function calling its own name, or write a small AST check for self-referential `Call` nodes, and confirm a depth cap exists wherever the input is external

## Strict profile
Any recursion, direct or indirect, is a finding **[blocker]** - including over trusted internal data. Convert every recursive function to explicit iteration with a bounded work stack.
