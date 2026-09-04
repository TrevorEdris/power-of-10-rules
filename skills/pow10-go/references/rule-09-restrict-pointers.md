# Rule 9 — Go

## Forbidden

`**T` parameter types. `chan chan T`. First-class function parameters crossing safety-package boundaries (e.g., `func(...) func(...) ...` curried across modules). Deep nested closures.

## Allowed

First-class functions within a package (e.g., a `Strategy` field on a struct). Channels of value types.

## Violating example

```go
package safety

type EventHandler func(*Event) error

func Dispatch(handlers map[EventType]EventHandler, e *Event) error {
    h, ok := handlers[e.Type]
    if !ok {
        return fmt.Errorf("dispatch: unknown type %v", e.Type)
    }
    return h(e)
}
```

`EventHandler` parameters cross the package boundary; callers can register arbitrary functions; reachability hidden.

## Remediation

Replace function map with sealed dispatch table:

```go
package safety

type EventType int

const (
    EvtHeartbeat EventType = iota
    EvtCommand
    EvtTelemetry
)

func Dispatch(e *Event) error {
    if e == nil {
        return ErrNilEvent
    }
    switch e.Type {
    case EvtHeartbeat:
        return handleHeartbeat(e)
    case EvtCommand:
        return handleCommand(e)
    case EvtTelemetry:
        return handleTelemetry(e)
    default:
        return fmt.Errorf("dispatch: unknown type %v", e.Type)
    }
}
```

Call graph static; `EventType` enum is closed; new types require code change.

## Hard checks

- `golangci-lint`:
  - `gocritic` `paramTypeCombine` (multi-level pointer types)
- Manual review for cross-package `func` parameters in safety packages
- `go vet -unreachable`
