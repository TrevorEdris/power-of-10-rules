# Rule 2 - Bounded Loops (Go)

**Statement (Holzmann):** Every loop must carry an explicit, statically verifiable upper bound on its iteration count, preferably a compile-time constant; when the bound depends on runtime input, assert it against a fixed maximum.

**Profile (adapted):** applies partially; severity **medium**.

Literal compile-time-constant bounds are unrealistic for HTTP services, CLIs, and pipelines, which legitimately run intentional infinite loops (server accept loops, long-lived consumers). The real value for normal Go code: any loop whose iteration count is driven by external or untrusted input (retries, pagination, queue draining, polling) needs an explicit cap or a cancellation path, so a slow dependency or malformed input cannot hang the process or leak a goroutine forever.

## Checklist
- Give retry loops a fixed max-attempts constant instead of `for {}` around a fallible call.
- Cap loops that consume external input (channels, HTTP pagination, DB cursors) by count or select on `ctx.Done()`/a deadline.
- Confirm long-lived worker/server loops are intentionally infinite and honor cancellation.
- Replace recursive-descent functions standing in for a loop with an explicit depth limit.
- Bound polling with `for i := 0; i < max; i++` or a `time.After`/context timeout, not a bare unbounded read loop.
- Join or bound goroutines spawned in a loop (WaitGroup, worker pool) instead of firing them unbounded per iteration.

## Violation

```go
package main

import (
	"fmt"
	"net/http"
)

func fetch(url string) (*http.Response, error) {
	for {
		resp, err := http.Get(url)
		if err == nil {
			return resp, nil
		}
		fmt.Println("retrying")
	}
}
```

## Fix

```go
package main

import (
	"context"
	"fmt"
	"net/http"
)
func fetch(ctx context.Context, url string) (*http.Response, error) {
	const maxAttempts = 5
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	for i := 0; i < maxAttempts; i++ {
		if resp, err := http.DefaultClient.Do(req); err == nil {
			return resp, nil
		}
	}
	return nil, fmt.Errorf("giving up after %d attempts", maxAttempts)
}
```

## Tooling
- `golangci-lint`: `contextcheck` - proxy: flags functions that lose or fail to propagate a `context.Context`, catching loops that can't be cancelled
- `golangci-lint`: `noctx` - proxy: flags HTTP calls made without a context, a common way retry/polling loops end up uncancellable
- `manual review`: no Go linter directly asserts loop iteration bounds; check retry/poll/pagination loops for an explicit cap or cancellation path by hand

## Strict profile
Literal profile requires every loop, including server/consumer loops, to carry a compile-time-constant bound **[blocker]**; infinite `for {}` is disallowed even for accept loops, which must instead be driven by a bounded outer harness.
