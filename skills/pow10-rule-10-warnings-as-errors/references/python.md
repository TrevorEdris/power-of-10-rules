# Rule 10 — Python

## Required

`ruff check --select ALL` then explicitly prune false positives. `mypy --strict` clean. `pyright` or `pylint --errors-only` as a second analyzer. `bandit` for security.

## Violating example

```yaml
- run: pytest
```

Tests pass; lint and type-check never run; warnings invisible.

## Remediation

```yaml
- name: ruff
  run: ruff check . --select ALL --output-format=github

- name: mypy
  run: mypy --strict src/

- name: pyright
  uses: jakebailey/pyright-action@v2

- name: bandit
  run: bandit -r src/ -ll  # low severity, low confidence; raises bar gradually

- name: pytest
  run: pytest -W error  # treat Python warnings as errors
```

`pytest -W error` fails the test run on `DeprecationWarning`, `RuntimeWarning`, etc.

## ruff baseline (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "D",        # pydocstyle (project decision)
    "ANN101",   # missing-type-self (deprecated)
    "COM812",   # trailing-comma (formatter conflict)
]

[tool.mypy]
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
```

## Suppressions

```python
result = legacy_call()  # noqa: S603  # pow10: allow rule=10 until=2026-09-30 owner=team reason="vendor SDK requires shell=True"
```
