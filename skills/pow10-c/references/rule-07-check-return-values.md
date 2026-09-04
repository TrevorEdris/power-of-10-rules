# Rule 7 - Check Return Values (C)

**Statement (Holzmann):** The return value of non-void functions must be checked by each calling function, and the validity of parameters must be checked inside each function.

**Profile (literal):** applies fully; severity **blocker**.

A discarded return value throws away error information the callee already computed - the caller has no way to know a `malloc`, `write`, or library call failed. An unvalidated parameter lets bad input (NULL, out-of-range, wrong size) propagate into a state mutation before anything checks it. Both failures are common roots of memory corruption and undefined behavior in C, where there is no exception mechanism to force the issue.

## Checklist
- Check every non-void return value; assign it to a named variable and branch on failure.
- Validate every parameter (NULL pointers, ranges, sizes) before the first state mutation in the function body.
- Justify any ignored return with an adjacent comment, not a bare `(void)cast`.
- Roll back partial mutations when a later step in the same function fails.
- Propagate the failure code to the caller instead of swallowing it.

## Violation

```c
typedef struct { long balance; } account_t;
int write_log(account_t *acct, long amount);

int withdraw(account_t *acct, long amount) {
    acct->balance -= amount;
    write_log(acct, amount);
    return 0;
}
```

## Fix

```c
typedef struct { long balance; } account_t;
int write_log(account_t *acct, long amount);

int withdraw(account_t *acct, long amount) {
    if (acct == 0) return 1;
    if (amount <= 0) return 2;
    if (acct->balance < amount) return 3;
    acct->balance -= amount;
    int rc = write_log(acct, amount);
    if (rc != 0) {
        acct->balance += amount;
        return rc;
    }
    return 0;
}
```

## Tooling
- `clang-tidy`: `bugprone-unused-return-value` (aliased as `cert-err33-c`) - flags discarded returns from a fixed list of standard library calls, not from arbitrary application functions
- `cppcheck`: `--enable=all` - proxy: flags unchecked return values and NULL-pointer dereferences it can trace

## Strict profile
CI gates on `clang-tidy` with `bugprone-unused-return-value` and `cppcheck --enable=all --error-exitcode=1` both clean; no `(void)`-cast without an adjacent justification comment.
