# Rule 4 — Python

## Limits

Soft 50 source lines, hard 60 (Python is denser than C). Cyclomatic complexity ≤ 10. Branches ≤ 12.

## Violating example

```python
def process_request(req: Request) -> Response:
    if req is None:
        raise ValueError("nil request")
    if len(req.body) > MAX_LEN:
        raise ValueError(f"len {len(req.body)} > {MAX_LEN}")
    # ... 15 more validation lines ...
    try:
        parsed = json.loads(req.body)
    except json.JSONDecodeError as e:
        raise ParseError(str(e)) from e
    # ... 15 more parse / transform lines ...
    result = compute(parsed)
    # ... 15 more execute lines ...
    return Response(status=200, body=json.dumps(result))
```

70 lines; mixed concerns; hard to test the parse step in isolation.

## Remediation

```python
def process_request(req: Request) -> Response:
    validate(req)
    parsed = parse(req)
    result = execute(parsed)
    return serialize(result)
```

Each helper has one job; main function reads as a four-step pipeline.

## Hard checks

- `ruff`:
  - `PLR0915` (too-many-statements, default 50)
  - `PLR0912` (too-many-branches, default 12)
  - `C901` (complex, McCabe ≥ 10)
- `radon cc -s -a` for cyclomatic complexity report
