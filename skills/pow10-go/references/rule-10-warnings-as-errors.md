# Rule 10 — Go

## Required

`go vet ./...` clean. `staticcheck` with `all` checks. `golangci-lint` with: `errcheck`, `gosec`, `govet`, `ineffassign`, `unused`, `misspell`, `gocritic`, `revive`. CI fails on any warning.

## Violating example

```yaml
- run: go build ./...
- run: go test ./...
```

Builds and tests pass; vet/static analysis never runs; warnings invisible.

## Remediation

```yaml
- name: go vet
  run: go vet ./...

- name: staticcheck
  uses: dominikh/staticcheck-action@v1
  with:
    version: "latest"
    install-go: false

- name: golangci-lint
  uses: golangci/golangci-lint-action@v6
  with:
    version: latest
    args: --timeout=5m

- name: gosec
  uses: securego/gosec@master
  with:
    args: ./...

- name: build + test
  run: |
    go build -gcflags="-m=2" ./... 2>build.log || true
    go test -race -count=1 ./...
```

`-gcflags=-m=2` shows escape analysis / inlining — review for hot-path regressions.

## golangci-lint baseline (.golangci.yml)

```yaml
linters:
  enable:
    - errcheck
    - gosec
    - govet
    - ineffassign
    - unused
    - misspell
    - gocritic
    - revive
    - staticcheck
    - gocyclo
    - funlen
    - prealloc
    - errorlint
    - wrapcheck
    - nilerr
issues:
  exclude-use-default: false
  max-issues-per-linter: 0
  max-same-issues: 0
```

## Suppressions

```go
//nolint:errcheck // pow10: allow rule=10 until=2026-12-31 owner=team reason="best-effort cleanup"
_ = file.Close()
```
