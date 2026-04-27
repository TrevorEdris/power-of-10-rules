# Rule 6 — Java

## Forbidden

Mutable `static` fields. Variables declared at method top but used in a single branch. Public fields without `final`.

## Violating example

```java
public class Counter {
    public static int value = 0;

    public static void tick() {
        value++;
    }

    public static int read() {
        return value;
    }
}
```

Mutable public static; shared across classloaders within a JVM; not thread-safe; impossible to test in isolation.

## Remediation

```java
public final class Counter {
    private int value;

    public void tick() {
        value++;
    }

    public int read() {
        return value;
    }
}
```

Ownership explicit. For thread-safe variants, use `AtomicInteger` or synchronize.

## Hard checks

- `Checkstyle`:
  - `VariableDeclarationUsageDistance`
  - `FinalLocalVariable`
- `PMD`:
  - `AvoidUsingVolatile`
  - `MutableStaticState`
- `SpotBugs`:
  - `MS_*` mutable-static checks
