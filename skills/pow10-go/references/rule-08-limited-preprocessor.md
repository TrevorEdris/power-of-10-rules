# Rule 8 - Limited Preprocessor (Go)

**Statement (Holzmann):** The preprocessor is limited to header inclusion and simple macro definitions, forbidding token pasting, variable-argument lists, and recursive macro calls, with conditional compilation kept rare and justified.

**Profile (adapted):** applies in spirit; severity **medium**.

Go has no preprocessor, so the literal rule does not apply. The in-spirit successor targets reflect-based control flow and unsafe type punning: both hide the call graph from static analysis the same way aggressive macros do, and the failure mode shifts from a compile error to a runtime panic. Reflection at serialization or dependency-injection boundaries (encoding/json, ORMs, wire/fx-style wiring) is standard idiomatic Go and is not in scope - only reflect used to dispatch business logic by name or type in place of an interface or switch.

## Checklist
- Reject `reflect.ValueOf(x).MethodByName(...).Call(...)`-style dynamic dispatch in request or business-logic paths; use an interface with a type switch or an explicit dispatch table
- Confine `unsafe.Pointer` usage to a narrowly-scoped, reviewed package; never use it for type punning across package boundaries
- Commit `go generate` output to the repo rather than generating it only at build or CI time
- Allow reflection for JSON/YAML/proto (de)serialization or dependency-injection wiring without flagging it
- Reject monkey-patching of package-level vars or funcs to alter production behavior at runtime

## Violation

```go
package main

import (
	"fmt"
	"reflect"
)

func dispatch(action string, p any) error {
	rv := reflect.ValueOf(p)
	m := rv.MethodByName(action)
	if !m.IsValid() {
		return fmt.Errorf("unknown action %q", action)
	}
	m.Call(nil)
	return nil
}
```

## Fix

```go
package main

import "fmt"

type Handler interface{ Handle() error }

var dispatch = map[string]func(Handler) error{
	"create": Handler.Handle,
}

func run(action string, h Handler) error {
	fn, ok := dispatch[action]
	if !ok {
		return fmt.Errorf("unknown action %q", action)
	}
	return fn(h)
}
```

## Tooling
- `golangci-lint` (`gosec`): audits `unsafe.Pointer` usage - proxy: does not catch reflect-based dispatch
- `manual review`: grep for `MethodByName(` outside serialization/DI packages; no installed linter targets dynamic dispatch-by-name

## Strict profile
No `reflect` or `unsafe` anywhere [high]: any import of `reflect` or use of `unsafe.Pointer`, including in serialization and dependency-injection wiring, is a finding regardless of call site.
