# Rule 5 — Kotlin

## Target

Average ≥ 2 invariant checks per function. Kotlin ships idiomatic guards: `require(...)` for parameters, `check(...)` for state invariants, `requireNotNull(...)` for nullability. None are stripped by build flags.

## Violating example

```kotlin
fun transfer(from: Account, to: Account, amount: Long) {
    from.balance -= amount
    to.balance += amount
}
```

No invariant checks. Negative amounts succeed silently.

## Remediation

```kotlin
fun transfer(from: Account, to: Account, amount: Long) {
    require(amount > 0) { "amount must be positive: $amount" }
    require(from.balance >= amount) { "insufficient funds" }
    check(from !== to) { "self-transfer" }

    from.balance -= amount
    to.balance += amount

    check(from.balance >= 0) { "balance went negative: ${from.balance}" }
}
```

Four guards in a 6-line function. `require` for caller errors, `check` for state invariants — distinct intent encoded in the call.

## Hard checks

- `detekt`:
  - `UseCheckOrError` (prefer `check`/`error` over manual `if … throw`)
  - `UseRequire` (prefer `require` over manual `if … throw IllegalArgumentException`)
  - `UnsafeCallOnNullableType` (catches `!!` use)
- Manual review: count `require`/`check`/`requireNotNull` per function
