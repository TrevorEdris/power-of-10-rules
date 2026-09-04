# Rule 3 - No Dynamic Memory After Init (C)

**Statement (Holzmann):** After the initialization phase, no heap allocation is permitted; all memory comes from fixed-size pools, the stack, or static buffers, so worst-case memory usage is analyzable at build time.

**Profile (literal):** applies fully; severity **blocker**.

Heap allocation is nondeterministic: `malloc` can return NULL under pressure, the heap can fragment over a long-running mission, and use-after-free/double-free become possible once allocation and deallocation are dynamic. None of these failure modes are statically provable. Forbidding allocation past the init boundary makes worst-case memory a fixed, link-time-known number and removes an entire class of runtime failure.

## Checklist
- Tag the end of initialization with a `// pow10:init-end` marker
- Grep for `malloc`, `calloc`, `realloc`, `free`, `alloca` after that marker; treat any hit as a violation
- Replace per-call heap buffers with static or stack arrays sized to the worst-case input
- Add an `assert` (or explicit bounds check) guarding any size that could exceed the static buffer
- Verify no library call used post-init (e.g. `strdup`, `asprintf`) allocates internally

## Violation

```c
#include <stddef.h>
#include <stdlib.h>

void read_packet(char *buf, size_t n);
void process_packet(char *buf, size_t n);

void handle_packet(size_t n) {
    char *buf = malloc(n);
    read_packet(buf, n);
    process_packet(buf, n);
    free(buf);
}
```

## Fix

```c
#include <assert.h>
#include <stddef.h>

void read_packet(char *buf, size_t n);
void process_packet(char *buf, size_t n);

#define BUF_MAX 2048

void handle_packet(size_t n) {
    static char buf[BUF_MAX];
    assert(n <= BUF_MAX);
    read_packet(buf, n);
    process_packet(buf, n);
}
```

## Tooling
- `clang-tidy`: `cppcoreguidelines-no-malloc` - flags heap allocation and deallocation calls (applied to C translation units via this C++-guidelines-named check)
- `cppcheck --enable=all` - flags leaks, double-free, and use-after-free around dynamic allocation
- `manual review` - confirm the `// pow10:init-end` marker is placed correctly and no heap call appears after it

## Strict profile
Zero heap calls anywhere past `// pow10:init-end`; no "only when unbounded or hot" carve-out. CI gates: `clang-tidy` with `cppcoreguidelines-no-malloc` promoted to an error, `cppcheck --enable=all --error-exitcode=1`, and a second analyzer from a different vendor, all run clean.
