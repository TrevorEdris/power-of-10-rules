# Rule 9 — Kotlin

Analogue: lambda-of-lambda types (`(A) -> (B) -> C`) crossing module boundaries; deeply nested higher-order callbacks; `KFunction` references for runtime dispatch.

## Forbidden in safety paths

`(A) -> (B) -> R` types as parameters across module boundaries. Lambda lists registered from external modules. `KFunction*.invoke` for control flow.

## Allowed

Lambdas for local computation. Named functional interfaces within one module.

## Violating example

```kotlin
fun dispatch(
    handlers: Map<String, (Event) -> Result>,
    event: Event,
): Result {
    val handler = handlers[event.type]
        ?: error("unknown type: ${event.type}")
    return handler(event)
}
```

Open-ended map; arbitrary lambdas; reachability hidden.

## Remediation

Sealed interface plus closed registry:

```kotlin
sealed interface Handler {
    fun handle(event: Event): Result
}

object HeartbeatHandler : Handler { override fun handle(e: Event): Result = ... }
object CommandHandler : Handler { override fun handle(e: Event): Result = ... }
object TelemetryHandler : Handler { override fun handle(e: Event): Result = ... }

private val HANDLERS: Map<String, Handler> = mapOf(
    "heartbeat" to HeartbeatHandler,
    "command"   to CommandHandler,
    "telemetry" to TelemetryHandler,
)

fun dispatch(event: Event): Result {
    val handler = HANDLERS[event.type]
        ?: throw IllegalArgumentException("unknown type: ${event.type}")
    return handler.handle(event)
}
```

`sealed interface` lets the compiler exhaust-check `when` over implementations; registry is module-private.

## Hard checks

- `detekt`:
  - `ComplexInterface`
  - `LongParameterList`
- Manual review for cross-module lambda parameters
- `kotlin.reflect.*` import audit in safety packages
