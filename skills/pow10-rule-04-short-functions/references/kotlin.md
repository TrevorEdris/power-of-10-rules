# Rule 4 — Kotlin

## Limits

Hard 60 lines, soft 40. Cyclomatic complexity ≤ 10. Kotlin's expression bodies and scope functions (`apply`, `also`, `let`, `run`) make tight functions easy.

## Violating example

```kotlin
fun processRequest(req: Request): Response {
    require(req.body.isNotEmpty()) { "empty body" }
    require(req.body.length <= MAX_LEN) { "len ${req.body.length} > $MAX_LEN" }
    // ... 15 more validation lines ...
    val parsed = try {
        Json.parseToJsonElement(req.body)
    } catch (e: SerializationException) {
        throw ProcessingException("parse failed", e)
    }
    // ... 15 more parse / transform lines ...
    val result = compute(parsed)
    // ... 15 more execute lines ...
    return Response(200, Json.encodeToString(result))
}
```

70+ lines, four mixed concerns.

## Remediation

```kotlin
fun processRequest(req: Request): Response {
    validate(req)
    val parsed = parse(req)
    val result = execute(parsed)
    return serialize(result)
}
```

Each helper is a single-expression body where possible:

```kotlin
private fun parse(req: Request): JsonElement = runCatching {
    Json.parseToJsonElement(req.body)
}.getOrElse { throw ProcessingException("parse failed", it) }
```

## Hard checks

- `detekt`:
  - `LongMethod` with `threshold: 60`
  - `ComplexMethod` (cyclomatic ≤ 10)
  - `LongParameterList` (≤ 5)
