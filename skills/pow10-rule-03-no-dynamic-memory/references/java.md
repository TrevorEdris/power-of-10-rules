# Rule 3 — Java

## Forbidden after init

`new` on hot paths. Autoboxing (`List<Integer>` instead of `int[]`). Unbounded `ArrayList`/`HashMap` growth. Lambda captures that allocate. String concatenation in loops without `StringBuilder`.

## Violating example

```java
String summarize(List<Sample> samples) {
    String result = "";
    for (Sample s : samples) {
        result += "[" + s.id() + "=" + s.value() + "]";
    }
    return result;
}
```

`+=` allocates a new `String` per iteration; `String.format`-style concatenation hidden by the compiler still allocates `StringBuilder` per iteration in older bytecode.

## Remediation

Pre-allocated `StringBuilder` plus primitive accessors:

```java
private static final int MAX_SAMPLES = 4096;
private final StringBuilder buf = new StringBuilder(MAX_SAMPLES * 16);

String summarize(List<Sample> samples) {
    if (samples.size() > MAX_SAMPLES) {
        throw new IllegalArgumentException("too many samples: " + samples.size());
    }
    buf.setLength(0);
    for (Sample s : samples) {
        buf.append('[').append(s.id()).append('=').append(s.value()).append(']');
    }
    return buf.toString();
}
```

Buffer allocated once at field-init; `setLength(0)` reuses it. The bound check enforces capacity.

## Hard checks

- `SpotBugs`: `Bx_BOXING_IMMEDIATELY_UNBOXED`, `SBSC_USE_STRINGBUFFER_CONCATENATION`
- `PMD`: `AvoidInstantiatingObjectsInLoops`, `InefficientStringBuffering`
- JMH benchmarks with `+gc` profiler
