# Rule 9 - Restrict Pointers (Go)

**Statement (Holzmann):** At most one level of dereferencing per declaration; pointer dereferences may not be hidden inside macro definitions or typedef declarations; no function pointers.

**Profile (adapted):** applies in spirit; severity **medium**.

Raw multi-level pointers (`**T`) are already vanishingly rare in idiomatic Go. The real analog is uncontrolled first-class-function dispatch: registries populated from outside the owning package, or curried handler chains, that make it impossible for a reviewer or the compiler to enumerate what actually runs. Ordinary Go idiom - `http.HandlerFunc`, middleware chains, functional options, local closures - is exempt; this targets safety- and business-critical control flow.

## Checklist
- Flag any exported function or method that takes a `**T` parameter on sight.
- Verify dispatch maps keyed by an enum type and holding `func` values, driving critical logic, are populated only inside their owning package, not appended to from outside or via reflection.
- Prefer a closed enum + `switch` over an open dispatch map for state machines, payment/authz decisions, or other auditable control flow.
- Enable `exhaustive` on switches over closed enums so new values can't silently fall through `default`.
- Flag closures nested more than two levels deep, or that both capture and mutate outer-scope state, in core logic paths.

## Violation

```go
package handlers

var Registry = map[string]func(Order) error{}

func Register(name string, fn func(Order) error) {
    Registry[name] = fn // any package can inject a handler
}

func Process(name string, o Order) error {
    h := Registry[name]
    return h(o)
}
```

## Fix

```go
package handlers

import "fmt"

type OrderState int

const (
    StatePending OrderState = iota
    StateShipped
)

func Process(s OrderState, o Order) error {
    switch s {
    case StatePending:
        return handlePending(o)
    case StateShipped:
        return handleShipped(o)
    }
    return fmt.Errorf("process: unknown state %v", s)
}
```

## Tooling
- `golangci-lint`: `exhaustive` - flags switches over a closed enum that don't cover every value
- `manual review`: cross-package dispatch-map registration and curried cross-module function chains - no verified linter targets this directly

## Strict profile
No function values or dispatch maps anywhere, including `http.HandlerFunc`, middleware chains, and functional options **[blocker]**. Enforce via manual review; no verified linter bans function-typed declarations.
