# Rule 2 — Kotlin

## Forbidden

`while (true)` without internal counter. `do { } while (true)`. Sequence operations without `take(N)` cap.

## Violating example

```kotlin
fun consume(channel: ReceiveChannel<Msg>) = runBlocking {
    while (true) {
        val msg = channel.receive()
        process(msg)
    }
}
```

Unbounded; no termination proof.

## Remediation

```kotlin
private const val MAX_BATCH = 256

suspend fun consume(channel: ReceiveChannel<Msg>) {
    repeat(MAX_BATCH) {
        val msg = channel.receiveCatching().getOrNull() ?: return
        process(msg)
    }
}
```

`repeat(MAX_BATCH)` makes the cap explicit; `receiveCatching` returns null on close so the loop exits cleanly.

## Hard checks

- `detekt`: `LoopWithTooManyJumpStatements`, `EmptyWhileBlock`
- Manual review for any `while (true)` or unbounded `while (cond)`
