# Rule 4 — Java

## Limits

Hard 60 source lines per method. Soft 40. Cyclomatic complexity ≤ 10. Java boilerplate (modifiers, exception declarations, imports) eats lines — extract aggressively.

## Violating example

```java
public Response processRequest(Request req) throws ProcessingException {
    if (req == null) throw new IllegalArgumentException("nil request");
    if (req.getBody().length() > MAX_LEN) {
        throw new IllegalArgumentException(
            "len " + req.getBody().length() + " > " + MAX_LEN);
    }
    // ... 15 more validation lines ...
    Parsed parsed;
    try {
        parsed = parser.parse(req.getBody());
    } catch (ParseException e) {
        throw new ProcessingException("parse failed", e);
    }
    // ... 15 more parse / transform lines ...
    Result result = executor.run(parsed);
    // ... 15 more execute lines ...
    return new Response(200, mapper.writeValueAsString(result));
}
```

80+ lines; checked exceptions and verbose conversions inflate the count.

## Remediation

```java
public Response processRequest(Request req) throws ProcessingException {
    validate(req);
    Parsed parsed = parse(req);
    Result result = execute(parsed);
    return serialize(result);
}
```

Each helper is a unit-testable method.

## Hard checks

- `Checkstyle`: `MethodLength` with `max: 60`
- `PMD`: `ExcessiveMethodLength`, `CyclomaticComplexity`
- `Error Prone`: `MethodCanBeStatic` (sometimes a sign of misplaced logic)
