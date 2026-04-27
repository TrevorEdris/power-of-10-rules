# Rule 7 — Java

## Forbidden

Discarding return value of `@CheckReturnValue` methods. Calling `Optional.get()` without prior `isPresent()`. Bare `catch (Exception e) { }`. Mutation before parameter validation.

## Violating example

```java
public void withdraw(Account account, long amount) {
    account.balance -= amount;
    writeLog(account, amount);
}
```

No checks. `writeLog` may throw; balance decremented anyway.

## Remediation

```java
public void withdraw(Account account, long amount) throws InsufficientFundsException {
    Objects.requireNonNull(account, "account");
    if (amount <= 0) {
        throw new IllegalArgumentException("amount must be positive: " + amount);
    }
    if (account.balance < amount) {
        throw new InsufficientFundsException(amount, account.balance);
    }

    account.balance -= amount;
    try {
        writeLog(account, amount);
    } catch (LogException e) {
        account.balance += amount;  // roll back
        throw new RuntimeException("withdraw: log failed", e);
    }
}
```

Preconditions checked, mutation reversible, log failure surfaced with cause.

## Hard checks

- `Error Prone`:
  - `CheckReturnValue` (annotate APIs that must be checked)
  - `NullAway` (force null annotations)
  - `OptionalGetWithoutIsPresent`
- `SpotBugs`:
  - `RV_RETURN_VALUE_IGNORED`
  - `NP_NULL_PARAM_DEREF`
- Optionally: `Preconditions.checkArgument` / `Validate`
