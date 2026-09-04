# Rule 4 - Short Functions (Python)

**Statement (Holzmann):** No function should be longer than what can be printed on a single sheet of paper (about 60 lines).

**Profile (adapted):** applies partially; severity **medium**.

Line-count limits matter less than statement and branch counts in Python given dense syntax like comprehensions and context managers. Treat the limits as review smells, not hard CI blockers, unless the team wants stricter enforcement. A function mixing validation, parsing, and execution hides bugs and resists focused unit testing.

## Checklist
- Read the function as a short, named pipeline (validate -> transform -> act), not one body mixing concerns.
- Keep it under ruff's statement default (50) and branch default (12), or document why it exceeds them.
- Keep McCabe complexity reasonable when C901 is enabled; pull deeply nested try/except or comprehensions into helpers.
- Make each helper independently unit-testable and separately importable.
- Limit nesting to about 3 levels; prefer guard clauses over nested `if`.

## Violation

```python
def process_request(req):
    if req is None:
        raise ValueError("nil request")
    if len(req.body) > MAX_LEN:
        raise ValueError("too long")
    try:
        parsed = json.loads(req.body)
    except json.JSONDecodeError as e:
        raise ParseError(str(e)) from e
    result = compute(parsed)
    return Response(status=200, body=json.dumps(result))
```

## Fix

```python
def process_request(req):
    validate(req)
    parsed = parse(req)
    result = compute(parsed)
    return serialize(result)

def validate(req):
    if req is None:
        raise ValueError("nil request")
    if len(req.body) > MAX_LEN:
        raise ValueError("too long")

def parse(req):
    try:
        return json.loads(req.body)
    except json.JSONDecodeError as e:
        raise ParseError(str(e)) from e

def serialize(result):
    return Response(status=200, body=json.dumps(result))
```

## Tooling
- `ruff`: `PLR0915` - too-many-statements, default threshold 50
- `ruff`: `PLR0912` - too-many-branches, default threshold 12
- `ruff`: `C901` - McCabe complexity too high; requires `select = ["C90"]` and `[tool.ruff.lint.mccabe] max-complexity = 10` in pyproject.toml, not enabled by default

## Strict profile
60-line hard limit, severity **high**. Treat PLR0915/PLR0912 as build-blocking with no exceptions mechanism, and enable C901 explicitly with `max-complexity = 10`.
