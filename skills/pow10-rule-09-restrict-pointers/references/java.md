# Rule 9 — Java

Analogue: deeply nested functional types (`Function<Function<A, B>, C>`); first-class lambda parameters crossing safety-package boundaries; deep callback chains.

## Forbidden in safety paths

`Function<Function<A, B>, C>` and similar curried types as method parameters. Lambdas registered from outside the safety package. Callback chains > 2 levels.

## Allowed

Lambdas for local use. Named functional interfaces (`Comparator`, `Predicate`) within a single package boundary.

## Violating example

```java
public Result dispatch(
    Map<String, Function<Event, Result>> handlers,
    Event event
) {
    Function<Event, Result> handler = handlers.get(event.getType());
    if (handler == null) {
        throw new IllegalArgumentException("unknown type: " + event.getType());
    }
    return handler.apply(event);
}
```

Open-ended handler map; callers can register arbitrary lambdas; reachability hidden.

## Remediation

```java
public interface Handler {
    Result handle(Event event);
}

public final class Dispatcher {
    private static final Map<String, Handler> HANDLERS = Map.of(
        "heartbeat", new HeartbeatHandler(),
        "command",   new CommandHandler(),
        "telemetry", new TelemetryHandler()
    );

    public Result dispatch(Event event) {
        Objects.requireNonNull(event, "event");
        Handler h = HANDLERS.get(event.getType());
        if (h == null) {
            throw new IllegalArgumentException("unknown type: " + event.getType());
        }
        return h.handle(event);
    }
}
```

Registry is `private static final` and confined to the safety package.

## Hard checks

- `Checkstyle`:
  - `MethodTypeParameterName` (catches generic-type sprawl)
  - `IllegalType` for `Function<Function<...>, ...>`
- `Error Prone`:
  - `FunctionalInterfaceClash`
- Manual review for cross-package lambda parameters
