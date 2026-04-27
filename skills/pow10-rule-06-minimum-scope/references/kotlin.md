# Rule 6 — Kotlin

## Forbidden

`var` at top level. `companion object` with mutable fields. `lateinit var` outside DI/test scaffolding. Top-level `var` in `package object`.

## Violating example

```kotlin
var counter: Int = 0

fun tick() {
    counter += 1
}

fun read(): Int = counter
```

Top-level mutable; package-wide; not thread-safe; no test isolation.

## Remediation

```kotlin
class Ticker {
    private var value: Int = 0

    fun tick() {
        value += 1
    }

    fun read(): Int = value
}
```

State owned by an instance. Prefer `val` over `var` wherever the field is logically immutable post-construction.

## Hard checks

- `detekt`:
  - `VarCouldBeVal` (flag mutable that could be immutable)
  - `TopLevelPropertyNaming` (catches conventions for global props)
  - `MagicNumber` (often correlates with hidden state)
- Manual review for `companion object` with `var`
