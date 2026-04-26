# Rule 3 — Kotlin

## Forbidden after init

Same as Java, plus: lambda captures that allocate (use `inline fun` for hot-path callbacks), `let`/`also`/`apply` blocks that capture mutable state in tight loops, `Sequence` chains without `take(N)` cap.

## Violating example

```kotlin
fun summarize(samples: List<Sample>): String =
    samples.joinToString(separator = "") { "[${it.id}=${it.value}]" }
```

Each iteration: lambda allocation, string interpolation buffer, intermediate string. `joinToString` builds a fresh `StringBuilder` per call.

## Remediation

Inline function with reused `StringBuilder`:

```kotlin
private const val MAX_SAMPLES = 4096
private val buf = StringBuilder(MAX_SAMPLES * 16)

fun summarize(samples: List<Sample>): String {
    require(samples.size <= MAX_SAMPLES) { "too many samples: ${samples.size}" }
    buf.setLength(0)
    for (s in samples) {
        buf.append('[').append(s.id).append('=').append(s.value).append(']')
    }
    return buf.toString()
}
```

Capacity is reserved at field init; `setLength(0)` reuses; explicit `for` avoids lambda allocation.

## Hard checks

- `detekt`: `SpreadOperator`, `ForEachOnRange`
- JVM allocation profiler (`-XX:+PrintGC`, async-profiler `--alloc`)
- Benchmark with `kotlinx-benchmark` and JMH `+gc`
