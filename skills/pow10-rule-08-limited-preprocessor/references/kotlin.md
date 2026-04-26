# Rule 8 — Kotlin

Kotlin's analogues: `kotlin.reflect.full.*` for control flow, KSP/KAPT codegen, inline DSL builders that produce non-type-checkable code.

## Allowed

KSP / KAPT for serialization (`kotlinx.serialization`), DI registration (Koin/Hilt), schema codegen. Inline DSL builders that resolve to type-checked code.

## Forbidden in safety paths

`KClass<*>.functions` lookup for runtime dispatch. `callBy(...)` for control flow. Reflection-based serialization in safety-critical paths.

## Violating example

```kotlin
fun dispatch(action: String, payload: Map<String, Any>): Any? {
    val cls = this::class
    val fn = cls.memberFunctions.firstOrNull { it.name == "handle${action.capitalize()}" }
        ?: error("unknown action: $action")
    return fn.call(this, payload)
}
```

Reflective lookup; call graph hidden; failure mode is runtime `error`.

## Remediation

Sealed interface plus explicit map:

```kotlin
sealed interface Handler {
    fun handle(payload: Map<String, Any>): Result
}

class CreateHandler : Handler { override fun handle(p: Map<String, Any>): Result = ... }
class UpdateHandler : Handler { override fun handle(p: Map<String, Any>): Result = ... }
class DeleteHandler : Handler { override fun handle(p: Map<String, Any>): Result = ... }

private val handlers: Map<String, Handler> = mapOf(
    "create" to CreateHandler(),
    "update" to UpdateHandler(),
    "delete" to DeleteHandler(),
)

fun dispatch(action: String, payload: Map<String, Any>): Result =
    handlers[action] ?: error("unknown action: $action").let { handlers.getValue(action).handle(payload) }
```

(Cleaner: use `requireNotNull(handlers[action]) { "unknown action: $action" }.handle(payload)`.)

Sealed interface lets the compiler check exhaustive `when`; unknown action surfaces as a typed error.

## Hard checks

- `detekt`:
  - `SpreadOperator`
  - `MagicNumber`
- Manual review for `kotlin.reflect.*` imports in safety packages
- KSP usage: confirm generated code is committed and reviewed
