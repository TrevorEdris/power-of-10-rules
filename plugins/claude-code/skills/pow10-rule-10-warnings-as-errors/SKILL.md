---
name: pow10-rule-10-warnings-as-errors
description: "NASA Power of 10 Rule 10 — All warnings on; treat warnings as errors; second analyzer in CI. Severity: blocker."
---

# Rule 10 — Warnings As Errors

**Severity:** blocker

## Statement

Compile with the strictest warning flags the toolchain offers. Treat any warning as a build failure. CI must run at least one additional static analyzer beyond the compiler, also configured for maximum strictness.

## Rationale

Compiler warnings are the cheapest static analysis available — zero-config, run on every build, catch real defects (uninitialized memory, format mismatches, sign comparisons, unreachable code). A safety-critical build that tolerates warnings is leaving free defects on the table.

## What a violation looks like

- CI passes with warnings present
- `// nolint` / `#pragma warning(disable: ...)` without justification comment
- Compiler invoked without `-Wall -Werror` (or equivalent)
- Single linter only — no second independent analyzer

## Per-language guidance

### C
- Required GCC/Clang flags: `-Wall -Wextra -Wpedantic -Werror -Wshadow -Wconversion -Wsign-conversion -Wcast-align -Wstrict-prototypes -Wnull-dereference -Wdouble-promotion -Wformat=2`
- Run `clang-tidy` AND `cppcheck` (or Coverity / PVS-Studio) in CI
- Tools: GCC, Clang, clang-tidy, cppcheck, scan-build

### Go
- `go vet ./...` clean; `staticcheck` with `all` checks
- `golangci-lint` with `errcheck`, `gosec`, `govet`, `ineffassign`, `unused`, `misspell`, `gocritic`, `revive`
- CI: `go build -gcflags=-m` for inlining/escape analysis review on hot paths
- Tools: `golangci-lint`, `staticcheck`, `gosec`, `nilaway`

### Python
- `ruff check --select ALL` then prune false positives explicitly
- `mypy --strict` clean
- Second analyzer: `pyright` or `pylint` with `--errors-only` initially, ratcheting up
- Tools: `ruff`, `mypy`, `pyright`, `pylint`, `bandit` (security)

### Java
- `javac -Xlint:all -Werror`
- Run BOTH `Error Prone` (compile-time) AND `SpotBugs` (bytecode) AND `Checkstyle` (style/structure) in CI
- Forbid `@SuppressWarnings` without a `// reason:` comment
- Tools: Error Prone, SpotBugs, PMD, Checkstyle, NullAway

### Kotlin
- `kotlinc -Werror -Xjvm-default=all` and enable opt-in warnings
- `detekt` with `--build-upon-default-config` plus a strict project ruleset
- Pair with `ktlint` for style; `Error Prone` via Kotlin support if mixed-JVM
- Tools: `detekt`, `ktlint`, `Error Prone` (mixed projects)

## Remediation pattern

CI snippet (GitHub Actions, C example):

```yaml
- name: Build with strict warnings
  run: |
    gcc -Wall -Wextra -Wpedantic -Werror -Wshadow -Wconversion \
        -Wsign-conversion -Wcast-align -Wstrict-prototypes \
        -Wnull-dereference -Wdouble-promotion -Wformat=2 \
        -O2 -c src/*.c
- name: clang-tidy
  run: clang-tidy src/*.c -- -Iinclude
- name: cppcheck
  run: cppcheck --enable=all --error-exitcode=1 src/
```

## Suppressions

When you must suppress, document inline:

```c
// pow10: allow rule=10 until=2026-06-30 owner=driver-team reason="vendor header triggers -Wshadow; cannot modify"
#pragma GCC diagnostic ignored "-Wshadow"
#include <vendor/driver.h>
#pragma GCC diagnostic pop
```

Scope the suppression as narrowly as possible (push/pop, single file, single block).

## Citations

- Holzmann 2006 — Rule 10
