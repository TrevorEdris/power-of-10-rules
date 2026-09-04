# Rule 4 — Go

## Limits

Hard 60 source lines per function. Soft 40. Cyclomatic complexity ≤ 10. Go's verbose error handling makes 60 a tight target — extract error chains into helpers.

## Violating example

```go
func ProcessRequest(req *Request) (*Response, error) {
    if req == nil { return nil, errors.New("nil request") }
    if req.Len > MaxLen { return nil, fmt.Errorf("len %d > %d", req.Len, MaxLen) }
    // ... 15 more validation lines with error wrapping ...
    parsed, err := Parse(req.Body)
    if err != nil { return nil, fmt.Errorf("parse: %w", err) }
    // ... 15 more parse-related lines ...
    result, err := Execute(parsed)
    if err != nil { return nil, fmt.Errorf("execute: %w", err) }
    // ... 15 more execute-related lines ...
    resp, err := Serialize(result)
    if err != nil { return nil, fmt.Errorf("serialize: %w", err) }
    return resp, nil
}
```

80+ lines, error wrapping bloat, four responsibilities.

## Remediation

```go
func ProcessRequest(req *Request) (*Response, error) {
    if err := validateRequest(req); err != nil {
        return nil, err
    }
    parsed, err := parseRequest(req)
    if err != nil {
        return nil, err
    }
    result, err := executeRequest(parsed)
    if err != nil {
        return nil, err
    }
    return serializeResponse(result)
}
```

Each helper is one responsibility, well under 60 lines, independently testable.

## Hard checks

- `golangci-lint`:
  - `funlen` with `lines: 60`, `statements: 40`
  - `gocyclo` with `min-complexity: 10`
  - `gocognit` for cognitive complexity
