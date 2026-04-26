# Rule 10 — C

## Required compiler flags (GCC / Clang)

```
-Wall -Wextra -Wpedantic -Werror
-Wshadow -Wconversion -Wsign-conversion -Wcast-align
-Wstrict-prototypes -Wnull-dereference -Wdouble-promotion -Wformat=2
```

## Required: at least one second analyzer

`clang-tidy`, `cppcheck`, Coverity, or PVS-Studio — in addition to the compiler.

## Violating example

```yaml
# CI passes despite warnings
- run: gcc -O2 -c src/*.c
```

No strictness flags; warnings are silently accepted.

## Remediation

```yaml
- name: Build with strict warnings
  run: |
    gcc -Wall -Wextra -Wpedantic -Werror \
        -Wshadow -Wconversion -Wsign-conversion -Wcast-align \
        -Wstrict-prototypes -Wnull-dereference -Wdouble-promotion -Wformat=2 \
        -O2 -c src/*.c

- name: clang-tidy
  run: clang-tidy src/*.c -- -Iinclude

- name: cppcheck
  run: cppcheck --enable=all --error-exitcode=1 src/
```

Compiler enforces; second analyzer catches what the compiler misses; either failing aborts CI.

## Suppressions

When unavoidable:

```c
// pow10: allow rule=10 until=2026-06-30 owner=driver-team reason="vendor header triggers -Wshadow"
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wshadow"
#include <vendor/driver.h>
#pragma GCC diagnostic pop
```

Scope as narrowly as possible (push/pop, single file).
