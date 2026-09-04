# Rule 7 — C

## Forbidden

Bare `foo();` for non-void functions. `(void)foo();` without an adjacent comment justifying ignored return. Mutating state before validating parameters.

## Violating example

```c
int withdraw(account_t *acct, int64_t amount) {
    acct->balance -= amount;
    write_log(acct, amount);
    return 0;
}
```

`acct` not checked for NULL; `amount` not validated; `write_log` return value discarded.

## Remediation

```c
int withdraw(account_t *acct, int64_t amount) {
    if (acct == NULL) return ERR_NULL_ACCT;
    if (amount <= 0) return ERR_BAD_AMOUNT;
    if (acct->balance < amount) return ERR_INSUFFICIENT;

    acct->balance -= amount;

    int rc = write_log(acct, amount);
    if (rc != 0) {
        acct->balance += amount;  /* roll back */
        return rc;
    }
    return 0;
}
```

Parameters validated before mutation. `write_log` return propagated; failure rolls back.

## Hard checks

- `clang-tidy`:
  - `bugprone-unused-return-value`
  - `bugprone-argument-comment`
  - `cert-err33-c` (detect and handle stdlib errors)
- `cppcheck` for unchecked returns
