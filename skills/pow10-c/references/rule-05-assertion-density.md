# Rule 5 - Assertion Density (C)

**Statement (Holzmann):** Use a minimum of two runtime assertions per function on average across a translation unit, each side-effect-free, each with a defined recovery path that is not stripped in release builds.

**Profile (literal):** applies fully; severity **high**.

C has no built-in error-return convention for invariant violations, so `assert()` is the primary tool for catching impossible states before they corrupt memory or propagate. A function with no assertions gives a reviewer no evidence the author considered preconditions, postconditions, or invariants. Side-effecting assert expressions are dangerous because `NDEBUG` silently deletes the behavior they were performing.

## Checklist
- Validate every pointer and numeric parameter against domain constraints at function entry
- Check state invariants immediately before any mutation
- Check postconditions immediately before return
- Write assert expressions with zero side effects (no `++`, no assignment, no function calls with effects)
- Never let a failed assertion fall through to continued execution in a safety-critical build
- Flag any translation unit averaging under 2 asserts per function in review

## Violation

```c
#include <assert.h>
#include <stddef.h>
#include <stdint.h>
typedef struct { int64_t balance; } account_t;

void transfer(account_t *from, account_t *to, int64_t amount) {
    from->balance -= amount;
    to->balance += amount;
}

/* no preconditions, no invariant checks, no postconditions */
```

## Fix

```c
#include <assert.h>
#include <stddef.h>
#include <stdint.h>
typedef struct { int64_t balance; } account_t;

void transfer(account_t *from, account_t *to, int64_t amount) {
    assert(from != NULL);
    assert(to != NULL);
    assert(amount > 0);
    assert(from->balance >= amount);
    assert(from != to);

    from->balance -= amount;
    to->balance += amount;

    assert(from->balance >= 0);
}
```

Six assertions in a 6-line function. Each invariant is named explicitly and fails fast.

## Tooling
- `clang-tidy`: `bugprone-assert-side-effect` - flags assert expressions with side effects
- `manual review`: count `assert(` occurrences per function; require average >= 2 per translation unit; flag `NDEBUG` in safety-critical build configs

## Strict profile
`clang-tidy` promotes `bugprone-assert-side-effect` from warning to error in CI [blocker]. `cppcheck --enable=all --error-exitcode=1` also runs and must pass clean.
