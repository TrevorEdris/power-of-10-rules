# Rule 8 — Java

Java's analogues: reflection (`Class.forName`, `Method.invoke`), bytecode generation, annotation processing.

## Allowed

Annotation processors and APT-generated code (output committed and reviewable). Reflection at startup for plugin discovery. Frameworks (Jackson, Hibernate) at the I/O boundary.

## Forbidden in safety paths

`Class.forName` for control flow. `Method.invoke` for runtime dispatch. `setAccessible(true)` on production state. Bytecode rewriting agents in production builds.

## Violating example

```java
public Object dispatch(String action, Map<String, Object> payload) throws Exception {
    Method m = this.getClass().getMethod("handle" + capitalize(action), Map.class);
    return m.invoke(this, payload);
}
```

Hidden call graph; `NoSuchMethodException` is a runtime surprise; `setAccessible` could expose private state.

## Remediation

Explicit dispatch via interface map:

```java
public interface Handler {
    Result handle(Map<String, Object> payload);
}

private final Map<String, Handler> handlers = Map.of(
    "create", new CreateHandler(),
    "update", new UpdateHandler(),
    "delete", new DeleteHandler()
);

public Result dispatch(String action, Map<String, Object> payload) {
    Handler h = handlers.get(action);
    if (h == null) {
        throw new IllegalArgumentException("unknown action: " + action);
    }
    return h.handle(payload);
}
```

Static call graph; unknown action throws a typed exception.

## Hard checks

- `Error Prone`:
  - `Reflection`
  - `Var`
- `SpotBugs`:
  - `DP_DO_INSIDE_DO_PRIVILEGED`
  - `REFLF_REFLECTION_FORMAT_LITERAL`
- `Checkstyle`: `IllegalImport` blocking `java.lang.reflect.*` from chosen packages
