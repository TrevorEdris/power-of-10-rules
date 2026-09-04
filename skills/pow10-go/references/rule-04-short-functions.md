# Rule 4 - Short Functions (Go)

**Statement (Holzmann):** Each function fits on one printed page - hard limit 60 source lines (excluding comments), soft limit 40.

**Profile (adapted):** applies partially; severity **medium**.

Treat 60 lines / 40 statements as a smell threshold, not a hard gate. What matters for normal Go services is single-responsibility per function and testability, not the literal page-fit rationale. Go's verbose `if err != nil` idiom means naive line counting punishes idiomatic error handling - prefer statement count and cyclomatic/cognitive complexity over raw lines.

## Checklist
- Name the function for one action; split it if the name needs "and".
- Keep it under funlen defaults (~60 lines / ~40 statements), or justify exceeding them (e.g. a table-driven switch).
- Keep gocyclo/gocognit complexity in the linter's default range; extract validate/parse/execute/serialize helpers when a function spans multiple phases.
- Limit nesting to ~3 levels; use early returns instead of nested branches.
- Make each extracted helper unit-testable without mocking the whole call chain.
- Exempt constructors/handlers that are pure dependency wiring with no branching.

## Violation

```go
package main

func Handle(w http.ResponseWriter, r *http.Request) {
	var req Req
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad json", 400)
		return
	}
	if req.Name == "" || len(req.Name) > 100 {
		http.Error(w, "invalid name", 400)
		return
	}
	rec, err := db.Insert(req)
	if err != nil {
		http.Error(w, "db error", 500)
		return
	}
	json.NewEncoder(w).Encode(rec)
}
```

## Fix

```go
package main

func Handle(w http.ResponseWriter, r *http.Request) {
	req, err := decodeReq(r)
	if err != nil { http.Error(w, err.Error(), 400); return }
	rec, err := db.Insert(req)
	if err != nil { http.Error(w, "db error", 500); return }
	json.NewEncoder(w).Encode(rec)
}

func decodeReq(r *http.Request) (Req, error) {
	var req Req
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		return Req{}, errors.New("bad json")
	}
	if req.Name == "" || len(req.Name) > 100 {
		return Req{}, errors.New("invalid name")
	}
	return req, nil
}
```

## Tooling
- `golangci-lint`: `funlen` (lines: 60, statements: 40) - flags functions past the size threshold
- `golangci-lint`: `gocyclo` (min-complexity: 10) - flags high branch-count functions
- `golangci-lint`: `gocognit` - flags functions that are hard to follow, independent of raw size

## Strict profile
Strict profile enforces 60 lines as a hard cap, not a soft target, at severity **[high]**. Any function over 60 lines or 40 statements fails review; no justification exempts it - extract helpers before merge.
