# Rule 10 - Warnings As Errors (Go)

**Statement (Holzmann):** Compile with all warnings enabled and eliminate warnings by modifying the code, not by suppressing the warning.

**Profile (adapted):** applies fully; severity **high**.

Go's toolchain surfaces defects for free: `go vet` and `staticcheck` catch nil derefs, format-string mismatches, and unreachable code before a single test runs. A CI pipeline that only runs `go build` and `go test` throws this away and lets real bugs merge silently. Extension beyond Holzmann: run `golangci-lint` as an aggregator covering many analyzers in one CI job, rather than requiring a separate second-vendor tool.

## Checklist
- Run `go vet ./...` in CI; fail the build on any non-zero exit
- Run `golangci-lint run` in CI against a checked-in `.golangci.yml`; fail the build on any finding
- Enable staticcheck's checks, standalone or via golangci-lint's staticcheck linter
- Reject bare `//nolint`; require `//nolint:linter // reason` on every suppression
- Keep lint config in version control, not only in a developer's local IDE
- Treat `go build` and `go test` output as insufficient proof of a clean build on their own

## Violation

```go
package example

func process(items []string) error {
	for _, item := range items {
		err := save(item)
		_ = err // errcheck would flag this, but CI never runs errcheck
	}
	return nil
}

func save(item string) error {
	return nil
}
```

## Fix

```go
package example

import "fmt"

func process(items []string) error {
	for _, item := range items {
		if err := save(item); err != nil {
			return fmt.Errorf("save %q: %w", item, err)
		}
	}
	return nil
}

func save(item string) error {
	return nil
}
```

## Tooling
- `go vet ./...`: exit non-zero on any vet diagnostic - catches format-string mismatches, unreachable code, struct tag errors
- `golangci-lint run`: aggregates `errcheck`, `govet`, `staticcheck`, `ineffassign`, `unused`, `gosec`, `revive` - fails CI on any finding
- `staticcheck`: full check set enabled (standalone or via golangci-lint) - catches unused writes, deprecated API use, correctness bugs
- `manual review`: confirm every `//nolint` names a linter and a one-line reason, not a bare suppression

## Strict profile
Unchanged; severity stays **high**. The adapted checklist already applies the literal rule in full: every warning gates CI, with no lower bar to tighten.
