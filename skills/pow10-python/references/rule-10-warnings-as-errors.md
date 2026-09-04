# Rule 10 - Warnings As Errors (Python)

**Statement (Holzmann):** Compile with the strictest warning flags the toolchain offers, and treat any warning as a build failure.

**Profile (adapted):** applies partially; severity **medium**.

The literal "ruff --select ALL, mypy --strict everywhere" stack is heavier than most backend/CLI Python teams run day to day - ALL churns with every ruff release, and mypy --strict on an untyped legacy codebase produces noise with low signal. The adapted profile keeps the spirit - lint and type-check are CI gates, not optional - but scopes the ruleset and allows incremental typing. As an extension beyond Holzmann's compiler-only scope, CI should also run a type checker and a security-focused linter pass.

## Checklist
- Run `ruff check` in CI with a curated, checked-in ruleset and fail the build on any finding
- Run `mypy` in CI at least on new and public-interface code; treat `--strict` as a goal, not a day-one requirement for legacy modules
- Forbid a bare `# noqa`; every suppression names a rule code and a reason
- Run `pytest` with warnings visible (audit `filterwarnings`, do not silently swallow them)
- Enable ruff's flake8-bandit (`S`-prefixed) security rules in CI, not only locally
- Fail CI on lint or type errors; a green test run alone does not satisfy this rule

## Violation

```python
import subprocess


def run(cmd: str) -> None:
    subprocess.run(cmd, shell=True)  # noqa
```

## Fix

```python
import subprocess


def run(cmd: list[str]) -> None:
    # argv is a fixed list built by this function, not user input
    subprocess.run(cmd, shell=False, check=True)  # noqa: S603
```

## Tooling
- `ruff`: `check` with a curated `select` list - fails CI on lint findings
- `ruff`: `S603` - flags a `subprocess` call made without `shell=True`, prompting review that its arguments are trusted
- `ruff`: `S602`/`S604` - flags a `subprocess` call made with `shell=True`, a shell-injection risk
- `mypy`: incremental strict mode via per-module overrides - fails CI on type errors
- `pytest`: `-W error` - promotes Python warnings to test failures
- `manual review`: confirm every `# noqa` names a rule code and a reason, not a bare suppression

## Strict profile
`ruff check` runs the full, uncurated ruleset; `mypy --strict` runs across the whole codebase; `pytest -W error` gates every test run. Severity **blocker**.
