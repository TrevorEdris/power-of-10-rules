# Rule 3 — Go

## Forbidden

After init: `make([]T, n)` with runtime-variable `n`, `append` that grows beyond pre-allocated capacity, `fmt.Sprintf` in hot paths, closure captures that escape to heap, interface boxing in tight loops.

## Violating example

```go
func encode(records []Record) []byte {
    out := []byte{}
    for _, r := range records {
        out = append(out, []byte(fmt.Sprintf("%s,%d\n", r.Name, r.Value))...)
    }
    return out
}
```

`Sprintf` allocates a string per record; `append` grows a slice repeatedly; conversion `[]byte(s)` copies. Three allocations per row.

## Remediation

Pre-allocate once, write into a fixed buffer, use `strconv` and `strings.Builder` directly:

```go
func encode(records []Record, buf *bytes.Buffer) {
    buf.Reset()
    buf.Grow(len(records) * 64)  // estimated upper bound
    for _, r := range records {
        buf.WriteString(r.Name)
        buf.WriteByte(',')
        buf.WriteString(strconv.Itoa(r.Value))
        buf.WriteByte('\n')
    }
}
```

Caller owns the `bytes.Buffer` and reuses it (often via `sync.Pool`). Zero allocations in the hot path after warmup.

## Hard checks

- `go test -benchmem` to verify zero allocations
- `golangci-lint` linters: `prealloc`, `gocritic` `appendCombine`
- `pprof` allocation profile to confirm
- `GODEBUG=gctrace=1` for GC frequency
