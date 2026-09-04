# Rule 3 - No Dynamic Memory After Init (Go)

**Statement (Holzmann):** After the initialization phase, no heap allocation is permitted; all memory comes from fixed-size pools, the stack, or static buffers so worst-case usage is analyzable at build time.

**Profile (adapted):** applies in spirit; severity **advisory**.

Idiomatic Go allocates constantly through slices, maps, interfaces, and closures, so this rule cannot mean "ban make/new/append." The adapted intent is narrower: no allocation size driven directly by unbounded external input, no needless allocation in profiler-identified hot paths, and no unbounded growth of long-lived caches or queues over the process lifetime.

## Checklist
- Cap any buffer, slice, or map sized directly from unvalidated request or network input with an explicit upper bound
- Reuse buffers or preallocate capacity in hot-path loops the profiler has actually identified, not loops picked by guesswork
- Replace `fmt.Sprintf` or string concatenation in tight per-request or per-record loops with `strings.Builder` or `bytes.Buffer`
- Bound long-lived caches and queues with a size limit, TTL, or LRU policy instead of letting them grow unchecked
- Back any allocation-removal claim with `go test -bench -benchmem` or `pprof`, not code reading alone
- Do not gate ordinary allocation-heavy code (config parsing, CLI flags, request/response handling) behind this rule

## Violation

```go
package main

import (
	"io"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	buf := make([]byte, r.ContentLength) // client controls the size, unbounded
	if _, err := io.ReadFull(r.Body, buf); err != nil {
		http.Error(w, "short body", http.StatusBadRequest)
	}
}
```

## Fix

```go
package main

import (
	"io"
	"net/http"
)

const maxSize = 1 << 20

func handler(w http.ResponseWriter, r *http.Request) {
	n := r.ContentLength
	if n <= 0 || n > maxSize {
		http.Error(w, "invalid size", http.StatusBadRequest)
		return
	}
	buf := make([]byte, n)
	if _, err := io.ReadFull(r.Body, buf); err != nil {
		http.Error(w, "short body", http.StatusBadRequest)
	}
}
```

## Tooling
- `golangci-lint` `prealloc`: flags slices that could be preallocated ahead of a growing loop
- `golangci-lint` `gocritic`: opt-in `appendCombine` check catches combinable append calls that cause extra allocations
- `go test -bench -benchmem`: measures allocations per operation to verify a hot path is zero-alloc
- `go tool pprof`: allocation profile confirms which call sites actually allocate under load
- `manual review`: check that buffer/slice/map sizes derived from external input have an explicit upper bound

## Strict profile
Strict profile applies the literal rule: no allocation after startup **[blocker]**. Every allocation site must move to init-time pools, fixed-size buffers, or the stack; unbounded-input sizing and unbounded cache growth are blockers requiring a documented upper bound.
