# Rule 2 — Go

## Forbidden

`for { ... }` without a counter or context cancellation. `for cond { ... }` without a bound on iterations.

## Violating example

```go
func consume(ch <-chan Msg) {
    for {
        msg := <-ch
        process(msg)
    }
}
```

Runs forever; ignores cancellation; not analyzable.

## Remediation

Bound by counter and context:

```go
const maxBatch = 256

func consume(ctx context.Context, ch <-chan Msg) error {
    for i := 0; i < maxBatch; i++ {
        select {
        case msg := <-ch:
            process(msg)
        case <-ctx.Done():
            return ctx.Err()
        }
    }
    return nil
}
```

Caller drives repeated batches; each invocation has a known upper bound.

## Hard checks

- `go vet ./...`
- `staticcheck` SA4017 (unused conditions); `golangci-lint` `govet`
- Custom `analysis.Analyzer` for unbounded `for`
