# Rule 7 - Check Return Values & Validate Parameters (Go)

**Statement (Holzmann):** Check the return value of every non-void function. Validate every parameter at function entry, before any state mutation. Callers cannot be trusted, even within the same module.

**Profile (adapted):** applies partially; severity **blocker**.

The "check every return" half applies fully - Go's `err != nil` idiom makes this cheap, and ignoring it is a real, common bug source. The "validate every parameter, callers cannot be trusted" half applies at trust boundaries: exported functions, package-public API, HTTP handlers, and anything crossing a service boundary should validate. Unexported helpers called only from code you also control may rely on caller-established invariants instead of re-validating on every internal call.

## Checklist
- Check or explicitly discard every call returning `error`, `(T, error)`, or `(T, bool)` - no bare `_, _ = f()` outside test doubles.
- Run `errcheck` and `staticcheck` clean in CI; pair with `go vet` to catch the bulk of Rule 7 violations mechanically.
- Wrap errors with `%w` at package or service boundaries so callers can `errors.Is`/`errors.As`.
- Validate arguments (nil pointers, empty strings, out-of-range values) in exported functions and HTTP/gRPC/CLI entry points before mutating state.
- Never use `panic` in library/service code as a substitute for returning an error on an expected failure path.
- Roll back a partial mutation (or use a transaction) when a later step in the same function fails.

## Violation

```go
package main

import "database/sql"

type User struct {
	Name string
}

func SaveUser(db *sql.DB, u *User) {
	db.Exec("INSERT INTO users(name) VALUES(?)", u.Name)
}
```

## Fix

```go
package main

import (
	"database/sql"
	"errors"
	"fmt"
)

type User struct{ Name string }

func SaveUser(db *sql.DB, u *User) error {
	if u == nil {
		return errors.New("save user: nil user")
	}
	if _, err := db.Exec("INSERT INTO users(name) VALUES(?)", u.Name); err != nil {
		return fmt.Errorf("save user: %w", err)
	}
	return nil
}
```

## Tooling
- `golangci-lint`: `errcheck` - forbids ignored non-void returns
- `golangci-lint`: `errorlint` - catches unsafe type-assertion / comparison on wrapped errors
- `golangci-lint`: `wrapcheck` - proxy: flags errors returned unwrapped across package boundaries; noisy on internal-only code, treat as advisory
- `golangci-lint`: `nilerr` - catches returning nil after a non-nil error was observed
- `staticcheck`: `SA4017` - flags discarding the return value of a side-effect-free function call

## Strict profile
Severity unchanged: **blocker**. Literal Holzmann reading extends validation to every parameter of every function, exported or not, with no reliance on caller-established invariants - unexported helpers validate their own inputs too.
