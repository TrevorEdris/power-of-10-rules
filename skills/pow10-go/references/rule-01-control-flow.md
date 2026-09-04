# Rule 1 - Restrict Control Flow to Simple Constructs (Go)

**Statement (Holzmann):** Use only straight-line execution, conditionals, and bounded iteration. Forbid `goto`, `setjmp`/`longjmp`, and recursion (direct or indirect, including mutual recursion across translation units).

**Profile (adapted):** applies partially; severity **medium**.

`goto` is essentially moot in Go - idiomatic code almost never uses it and style convention already discourages it. Recursion is normal and often idiomatic (tree/graph walks, recursive descent parsers, divide-and-conquer); goroutine stacks grow dynamically, so recursion over trusted, internally-bounded data is not a safety-critical concern. The real modern hazard is recursion whose depth is driven by external or attacker-controlled input (nested JSON, request payloads, recursive config includes), which is a stack-exhaustion DoS vector.

## Checklist
- Flag any `goto` used as a substitute for structured error handling.
- Require an explicit, enforced depth cap on any recursive function whose depth depends on external or user-controlled input.
- Accept recursion over trusted, size-bounded internal data without extra guards.
- Reject indirect or mutual recursion across package boundaries without a documented depth limit.
- Verify unbounded growth is checked even though goroutine stacks grow dynamically by default.

## Violation

```go
package main

func depth(v any, d int) int {
	m, ok := v.(map[string]any)
	if !ok || len(m) == 0 {
		return d
	}
	max := d
	for _, val := range m {
		if c := depth(val, d+1); c > max {
			max = c
		}
	}
	return max
}
```

## Fix

```go
package main

import "fmt"

func depth(v any, d int) (int, error) {
	const maxJSONDepth = 64
	if d > maxJSONDepth {
		return 0, fmt.Errorf("nesting exceeds %d", maxJSONDepth)
	}
	m, ok := v.(map[string]any)
	if !ok { return d, nil }
	best := d
	for _, val := range m {
		c, err := depth(val, d+1)
		if err != nil { return 0, err }
		best = max(best, c)
	}
	return best, nil
}
```

## Tooling
- `golangci-lint` (`gocyclo`, `gocognit`, `nestif`): proxy - indirect complexity signal, none detect recursion directly
- `manual review`: confirm any recursive function whose depth is driven by external input carries an explicit, enforced depth cap

## Strict profile
Strict profile bans every recursive function and every `goto` outright, trusted data included, at severity blocker. Convert recursive walks to explicit iteration over a bounded work stack.
