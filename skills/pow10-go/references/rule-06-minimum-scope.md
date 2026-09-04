# Rule 6 - Minimum Scope (Go)

**Statement (Holzmann):** Data objects are declared at the smallest possible level of scope.

**Profile (adapted):** applies partially; severity **medium**.

Ban mutable package-level state that is written to after init - singletons, shared caches, counters - since it hides ownership and creates implicit coupling across callers. Package-level `const` and values set once at process start (config, loggers, compiled regexes) are fine and idiomatic Go. Loop-variable capture is a non-issue on Go 1.22+; it only matters on older toolchains.

## Checklist
- Verify no package-level `var` is written to from more than one call site after init
- Move shared state (caches, pools, counters) into a struct constructed via a constructor, not a package-level singleton
- Confirm `init()` only performs read-only registration (drivers, metrics, flags), never populates mutable state read elsewhere
- Declare locals at first use with `:=`, not hoisted to the top of the function
- On Go < 1.22, verify loop variables captured in closures/goroutines are copied per-iteration or `copyloopvar` is enabled
- Reject `context.Context` used to smuggle values that belong as explicit parameters or struct fields

## Violation

```go
package counter

var value int

func Tick() {
	value++
}

func Read() int {
	return value
}
```

## Fix

```go
package counter

type Ticker struct {
	value int
}

func New() *Ticker {
	return &Ticker{}
}

func (t *Ticker) Tick() {
	t.value++
}

func (t *Ticker) Read() int {
	return t.value
}
```

## Tooling
- `golangci-lint`: `gochecknoglobals` - flags package-level mutable variables
- `golangci-lint`: `gochecknoinits` - flags `init()` functions (advisory, not blocking)
- `golangci-lint`: `copyloopvar` - flags manual loop-variable copies (`x := x`) as unnecessary now that Go 1.22+ scopes loop vars per iteration; does not catch missing copies on older Go
- `manual review`: package-level state written from more than one call site after program init

## Strict profile
No mutable package state at all [medium]: any package-level `var` written after init, including test helpers and generated code, is a finding regardless of call-site count.
