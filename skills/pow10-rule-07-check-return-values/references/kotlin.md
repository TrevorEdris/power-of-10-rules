# Rule 7 — Kotlin

## Forbidden

`!!` on nullable returns. Discarding `Result<T>` without `getOrThrow`/`getOrElse`/`fold`. Mutation before `require(...)`/`requireNotNull(...)`.

## Violating example

```kotlin
fun withdraw(account: Account, amount: Long) {
    account.balance -= amount
    writeLog(account, amount)
}
```

No validation; `writeLog` exception leaves state inconsistent.

## Remediation

```kotlin
@Throws(InsufficientFundsException::class)
fun withdraw(account: Account, amount: Long) {
    require(amount > 0) { "amount must be positive: $amount" }
    require(account.balance >= amount) { "insufficient funds" }

    account.balance -= amount
    runCatching {
        writeLog(account, amount)
    }.onFailure {
        account.balance += amount  // roll back
        throw RuntimeException("withdraw: log failed", it)
    }
}
```

Type system enforces `account` non-null; `runCatching` makes the rollback path explicit.

## Hard checks

- `detekt`:
  - `UnusedReturnValue` (forbid discarding return)
  - `UnsafeCallOnNullableType` (catch `!!`)
  - `ExceptionRaisedInUnexpectedLocation`
- Mark return-required functions with `@CheckReturnValue` (if using JSR-305)
- Prefer `Result<T>` over throwing for expected failures
