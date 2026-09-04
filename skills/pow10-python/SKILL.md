---
name: pow10-python
description: Use when writing, editing, refactoring, or reviewing Python code (.py files, services, scripts, CLIs, data pipelines, exception handling, PR diffs) and before declaring a Python task done. Applies the NASA Power of 10 safety rules as a 10-item checklist adapted for normal application code; strict literal profile on request. Not general Python idiom advice.
---

# pow10-python

Type: flexible. Adapt each item to the code in front of you; never skip a rule silently.

Announce once per task: `Using pow10-python to check <target> against the Power of 10 (adapted profile).`

## When this applies

- You are writing or editing `.py` files, or reviewing a Python diff.
- Default profile is **adapted**: rules are read for normal application code (services, scripts, CLIs, pipelines). Idiomatic Python is not a violation by itself.
- The user asks for "strict" or "literal" Power of 10, or passes `--strict`: use the Strict profile section and announce `(strict profile)`.
- Whole directory, PR, or multi-file diff: dispatch the `pow10-auditor` agent with the scope instead of checking inline. It reads these same references.

## Checklist (adapted profile)

Severity in brackets. Open the linked reference only when its "read when" condition holds.

### Rule 1 - Simple control flow [medium]
- No recursion over user- or network-supplied nesting (JSON, YAML, paths) without an explicit depth cap that raises.
- `sys.setrecursionlimit()` is never used to paper over a design that should be iterative.
- `try`/`except` is not used as non-local control flow on the normal path.
- Read when recursion depth is driven by input you do not control: `references/rule-01-control-flow.md`

### Rule 2 - Bounded loops [medium]
- `while True` polling and retry loops have a max-iteration count or wall-clock timeout, and raise or log when it is exceeded.
- Retries use bounded attempts (an explicit counter, or `stop_after_attempt`/`stop_after_delay` in a retry library).
- Loops over external streams (sockets, queues, generators) have an exit: timeout, sentinel, or cancellation event.
- Long-lived worker loops are intentional and check a shutdown event each iteration.
- Read when you write `while True`, a retry, or a loop over external input: `references/rule-02-bounded-loops.md`

### Rule 3 - Bounded allocation [advisory]
- No `bytes`, `list`, or `dict` accumulator grown from unvalidated external input without a size cap.
- Long-lived caches use `functools.lru_cache(maxsize=...)` or an explicit eviction policy, never a bare module-level `dict`.
- Generators are used instead of materializing a large stream into a list.
- Ordinary request, ORM, and script code is not flagged. Claims are backed by `tracemalloc`, not code reading.
- Read when an accumulator grows from external input or a structure lives for the process lifetime: `references/rule-03-no-dynamic-memory.md`

### Rule 4 - Short functions [medium]
- A function reads as a short pipeline (validate, transform, act), not one body mixing concerns.
- Under ruff `PLR0915` (50 statements) and `PLR0912` (12 branches) or the reason is stated. Nesting stays under 3 levels via guard clauses.
- Read when a function crosses 50 statements or mixes parse, validate, and execute: `references/rule-04-short-functions.md`

### Rule 5 - Assertion density [medium]
- Never a bare `assert` to validate external input (request bodies, CLI args, env vars): it is stripped under `-O`. Use `if not cond: raise ...`.
- `assert` is reserved for internal invariants where stripping is acceptable.
- Structured external input goes through typed validation (`dataclass`, pydantic, attrs) checked by `mypy`.
- Guard clauses raise a specific exception with a message naming the violated condition.
- Read when writing a trust boundary or an `assert`: `references/rule-05-assertion-density.md`

### Rule 6 - Minimum scope [medium]
- No `global` statement mutating a module-level name.
- Module-level names are constants, loggers, or singletons assigned once at import and never reassigned.
- Mutable state (caches, counters, buffers) lives on an instance or is passed explicitly.
- Long-lived resources (DB connections, HTTP clients) are constructed once and injected, not cached in an unowned module global.
- Read when you add a module-level mutable, a `global`, or a lazily created resource: `references/rule-06-minimum-scope.md`

### Rule 7 - Check return values [high]
- No bare `except:` or `except Exception: pass`. Every handler names its exceptions and acts or re-raises with `raise ... from e`.
- Status-style returns (`returncode`, `Response.ok`, boolean I/O helpers) are checked, not discarded.
- `Optional` values are narrowed before use; `mypy --strict` passes.
- Route handlers, CLI entry points, and public library functions validate argument types and ranges before mutating state.
- Read when you write an `except`, call `subprocess`, or return `None` on failure: `references/rule-07-check-return-values.md`

### Rule 8 - No metaprogramming in logic paths [high]
- No `eval()`/`exec()` on strings from input, config, or any non-literal source.
- No `globals()[name]` or `getattr(obj, user_string)` for control-flow dispatch. Use an explicit dict or enum table.
- `importlib.import_module()` with a user-influenced name is flagged. A fixed allowlist is not.
- Decorators, dataclasses, attrs, pydantic, and ORM metaclasses are allowed. No monkey-patching of production modules outside tests.
- Read when you write `eval`, `exec`, `getattr` with a computed name, or a dynamic import: `references/rule-08-limited-preprocessor.md`

### Rule 9 - Restricted indirection [advisory]
- Dispatch dicts (`dict[str, Callable]`) driving critical control flow are defined and populated in one module.
- Money- or safety-critical entry points accept a `Protocol` or ABC, not a bare `Callable`.
- Closures used for branching do not capture and later mutate a loop variable (ruff `B023`).
- Curried chains (`f(x)(y)(z)`) stay out of core business logic.
- Read when you write a callable registry, a plugin loader, or a closure in a loop: `references/rule-09-restrict-pointers.md`

### Rule 10 - Warnings as errors [medium]
- `ruff check` runs in CI with a checked-in ruleset and a finding fails the build.
- `mypy` runs in CI on new and public-interface code; `--strict` is the target.
- Every `# noqa` carries a rule code and a reason. Pytest runs with warnings visible.
- Security rules (ruff `S` prefix, or bandit) run in CI, not only locally.
- Read when touching CI or lint config, or adding a `# noqa`: `references/rule-10-warnings-as-errors.md`

## Reporting while editing

- Fix trivially fixable findings in code you are already changing; mention it in one line.
- Otherwise report one line per finding: `pow10 R7 [high] app/ingest.py:88 - bare except swallows OSError - name the exception and re-raise`.
- Advisory findings never block a task: list them and move on. Blockers stop the task until fixed or the user overrides.
- Do not review code you were not asked to touch. Suggest `/pow10-review <scope>` instead.

## Strict profile

Apply the literal rule at C severity and prefix findings with `[STRICT]`: R1 any recursion [blocker]; R2 every loop has a static bound, `while True` included [blocker]; R3 every unbounded container growth and every allocation in a hot loop [blocker]; R4 60 lines hard [high]; R5 two runtime checks per function, `assert` not counted [high]; R6 no mutable module state at all [medium]; R7 unchanged [blocker]; R8 no `eval`, `exec`, computed `getattr`, or metaclass in application code [high]; R9 no `Callable` parameters or dispatch dicts [blocker]; R10 `ruff` broad ruleset, `mypy --strict`, `pytest -W error` [blocker].

## Rationalizations

| Excuse | Reality |
| --- | --- |
| "It is idiomatic Python, so the rule does not apply." | The adapted checklist already allows idiomatic Python. What remains is a real hazard. |
| "`assert` is fine, we never run with `-O`." | Someone will. Validation that can vanish is not validation. |
| "This `except Exception` keeps the service up." | It keeps the bug up too. Name the exception and log the rest. |
| "The auditor will catch it later." | The auditor reads this same list. Catching it now is cheaper. |

## Tooling baseline

`ruff check` with `E`, `F`, `B`, `S`, `PL`, `RET`, `RUF`, `C90` selected; `mypy --strict` on new modules; `pytest -W error::DeprecationWarning`. Config example: `references/rule-10-warnings-as-errors.md`.
