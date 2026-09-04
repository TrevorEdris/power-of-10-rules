---
name: pow10-go
description: Use when writing, editing, refactoring, or reviewing Go code (.go files, handlers, services, CLIs, goroutines, error handling, PR diffs) and before declaring a Go task done. Applies the NASA Power of 10 safety rules as a 10-item checklist adapted for normal application code; strict literal profile on request. Not general Go idiom advice.
---

# pow10-go

Type: flexible. Adapt each item to the code in front of you; never skip a rule silently.

Announce once per task: `Using pow10-go to check <target> against the Power of 10 (adapted profile).`

## When this applies

- You are writing or editing `.go` files, or reviewing a Go diff.
- Default profile is **adapted**: rules are read for normal application code (services, CLIs, pipelines). Idiomatic Go is not a violation by itself.
- The user asks for "strict" or "literal" Power of 10, or passes `--strict`: use the Strict profile section and announce `(strict profile)`.
- Whole directory, PR, or multi-file diff: dispatch the `pow10-auditor` agent with the scope instead of checking inline. It reads these same references.

## Checklist (adapted profile)

Severity in brackets. Open the linked reference only when its "read when" condition holds.

### Rule 1 - Simple control flow [medium]
- Recursion whose depth follows external input (nested JSON, config includes, request payloads) has an explicit depth cap that returns an error.
- Recursion over trusted, size-bounded internal data is fine. No `goto` outside generated code.
- Read when recursion depth is driven by input you do not control: `references/rule-01-control-flow.md`

### Rule 2 - Bounded loops [medium]
- Retry and polling loops have a max-attempts constant or a `context`/deadline exit. No bare `for {}` around a fallible call.
- Loops draining channels, pagination, or cursors select on `ctx.Done()` or carry a count cap.
- Server and worker main loops are intentionally infinite and honor cancellation.
- Goroutines launched per iteration are bounded (WaitGroup, worker pool, semaphore).
- Read when you write `for {`, a retry, or a loop over external input: `references/rule-02-bounded-loops.md`

### Rule 3 - Bounded allocation [advisory]
- No slice, map, or buffer sized directly from unvalidated input without an upper bound.
- Long-lived caches and queues have a size limit, TTL, or LRU eviction.
- Hot loops identified by profiling reuse buffers or preallocate. Ordinary request code is not flagged.
- Read when allocation size comes from the network or a structure lives for the process lifetime: `references/rule-03-no-dynamic-memory.md`

### Rule 4 - Short functions [medium]
- One responsibility per function. If the name needs "and", split it.
- Under the `funlen` defaults (60 lines, 40 statements) or the reason is stated. Nesting stays under 3 levels via early returns.
- Read when a function crosses 60 lines or mixes parse, validate, and execute: `references/rule-04-short-functions.md`

### Rule 5 - Assertion density [advisory]
- Exported functions and entry points (HTTP, gRPC, CLI, config) validate untrusted input before use.
- Programmer-bug invariants (impossible nil, corrupted state) panic with a clear message. Expected failures return `error`.
- No `recover()` that swallows an invariant violation without logging or re-panicking.
- Read when writing a trust boundary or a `recover()`: `references/rule-05-assertion-density.md`

### Rule 6 - Minimum scope [medium]
- No package-level `var` mutated after init from more than one call site. Shared state lives in a struct passed by injection.
- `init()` only registers (drivers, metrics, flags). It does not populate mutable state consumed elsewhere.
- Locals declared at first use with `:=`. On Go older than 1.22, loop variables captured by goroutines are copied.
- Read when you add a package-level `var`, an `init()`, or a closure inside a loop: `references/rule-06-minimum-scope.md`

### Rule 7 - Check return values [blocker]
- Every `error`, `(T, error)`, or `(T, bool)` result is checked, or discarded with an explicit commented `_ =`.
- Entry points validate arguments (nil, empty, range) and return an error before mutating state.
- Errors crossing a package or service boundary are wrapped with `%w`. No `panic` for expected failures.
- A failing later step rolls back, or the operation is transactional.
- Read when you write `_, _ =`, `_ = f()`, or a function that mutates before it validates: `references/rule-07-check-return-values.md`

### Rule 8 - No metaprogramming in logic paths [medium]
- No `reflect` `MethodByName`/`Call` dispatch in request or business logic. Use interfaces, type switches, or a fixed dispatch map.
- `unsafe` confined to one reviewed package. `go generate` output is committed.
- Reflection inside (de)serialization and dependency wiring is allowed.
- Read when you import `reflect` or `unsafe` outside serialization: `references/rule-08-limited-preprocessor.md`

### Rule 9 - Restricted indirection [medium]
- No exported API takes `**T`.
- Dispatch maps driving critical logic are populated only in their owning package. Prefer a closed enum plus `switch` with `exhaustive` enabled.
- Closures in core paths do not nest beyond two levels or mutate captured state.
- Read when you write a `map[K]func`, a plugin registry, or a `**T`: `references/rule-09-restrict-pointers.md`

### Rule 10 - Warnings as errors [high]
- `go vet ./...` and `golangci-lint run` with a checked-in `.golangci.yml` run in CI and fail the build. `staticcheck` is enabled.
- Every `//nolint` names the linter and a reason.
- Read when touching CI or lint config, or adding a `//nolint`: `references/rule-10-warnings-as-errors.md`

## Reporting while editing

- Fix trivially fixable findings in code you are already changing; mention it in one line.
- Otherwise report one line per finding: `pow10 R7 [blocker] internal/api/order.go:42 - discarded error from tx.Commit - check and return it`.
- Advisory findings never block a task: list them and move on. Blockers stop the task until fixed or the user overrides.
- Do not review code you were not asked to touch. Suggest `/pow10-review <scope>` instead.

## Strict profile

Apply the literal rule at C severity and prefix findings with `[STRICT]`: R1 any recursion or `goto` [blocker]; R2 every loop has a static bound, server loops included [blocker]; R3 no allocation after startup [blocker]; R4 60 lines hard [high]; R5 two runtime checks per function on average [high]; R6 no mutable package state at all [medium]; R7 unchanged [blocker]; R8 no `reflect` or `unsafe` anywhere [high]; R9 no function values or dispatch maps [blocker]; R10 unchanged [high].

## Rationalizations

| Excuse | Reality |
| --- | --- |
| "It is idiomatic Go, so the rule does not apply." | The adapted checklist already allows idiomatic Go. What remains is a real hazard. |
| "This loop can only run a few times." | Then a cap costs one constant and proves it. |
| "That error can never happen here." | Then check it and panic with the reason. Silence hides the day it does. |
| "The auditor will catch it later." | The auditor reads this same list. Catching it now is cheaper. |

## Tooling baseline

`go vet ./...`; `golangci-lint run` with `errcheck`, `govet`, `staticcheck`, `ineffassign`, `unused`, `gosec`, `funlen`, `gocyclo`, `gochecknoglobals`, `copyloopvar`, `exhaustive`; `go test -race ./...`. Config example: `references/rule-10-warnings-as-errors.md`.
