# Rule 6 — Go

## Forbidden

Package-level mutable variables. `init()` functions that mutate package state. Loop-scoped vars declared above the loop. (Go ≤ 1.21: loop variable capture; fixed in 1.22.)

## Violating example

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

Package-level mutable; not thread-safe; multiple consumers share one global instance.

## Remediation

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

Ownership explicit; instances independent; testable.

## Hard checks

- `golangci-lint`:
  - `gochecknoglobals` (forbid package-level vars)
  - `gochecknoinits` (forbid `init()` blocks)
  - `exportloopref` / `copyloopvar` (loop-variable capture)
- `staticcheck` `SA1029` (improper context use, related)
