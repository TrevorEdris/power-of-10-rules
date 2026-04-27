# Rule 5 — C

## Target

Average ≥ 2 `assert()` calls per function across a translation unit. Side-effect-free expressions only. In safety-critical builds, replace `NDEBUG`-strip with a `safe_assert` macro that calls a recovery handler.

## Violating example

```c
void transfer(account_t *from, account_t *to, int64_t amount) {
    from->balance -= amount;
    to->balance += amount;
}
```

No preconditions, no invariant checks, no postconditions.

## Remediation

```c
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

## Hard checks

- Custom metric: count `assert(` per function; require average ≥ 2 across the TU
- `clang-tidy`: `cert-msc54-cpp` (no side-effect in assert)
- Manual review for `NDEBUG` in safety-critical builds
