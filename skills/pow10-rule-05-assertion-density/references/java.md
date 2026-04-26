# Rule 5 — Java

## Target

Average ≥ 2 invariant checks per method. `assert` keyword is disabled by default (requires `-ea`) — prefer `Objects.requireNonNull` plus explicit `if (...) throw new IllegalStateException(...)` so checks always run.

## Violating example

```java
public void transfer(Account from, Account to, long amount) {
    from.balance -= amount;
    to.balance += amount;
}
```

No null checks, no positive-amount check, no invariant on result.

## Remediation

```java
public void transfer(Account from, Account to, long amount) {
    Objects.requireNonNull(from, "from");
    Objects.requireNonNull(to, "to");
    if (amount <= 0) {
        throw new IllegalArgumentException("amount must be positive: " + amount);
    }
    if (from.balance < amount) {
        throw new InsufficientFundsException(amount, from.balance);
    }
    if (from == to) {
        throw new IllegalStateException("self-transfer");
    }

    from.balance -= amount;
    to.balance += amount;

    if (from.balance < 0) {
        throw new IllegalStateException("balance went negative: " + from.balance);
    }
}
```

Five guards. None depend on `-ea`. Distinct exception types let callers pattern-match.

## Hard checks

- `Error Prone`: `NullAway` for null preconditions
- `SpotBugs`: `NP_NULL_PARAM_DEREF`, `NP_NULL_ON_SOME_PATH`
- `Checkstyle`: custom `RegexpSingleline` to flag bare `public.*\(.*\) \{$` followed by mutation without prior check
- Optionally: `Preconditions.checkArgument` (Guava) or `Validate` (Apache Commons)
