# Rule 6 - Minimum Scope (C)

**Statement (Holzmann):** Data objects are declared at the smallest possible level of scope.

**Profile (literal):** applies fully; severity **medium**.

The literal rule bans mutable globals and mutable file-scope `static` state outright, since either creates implicit coupling between functions, defeats reasoning about ownership, and is not thread-safe. It also requires declarations at point of first use rather than hoisted to the top of a block or function, which was a C89 workaround no longer needed under C99.

## Checklist
- Reject any mutable file-scope `static` or externally-linked global variable
- Verify shared state is encapsulated in a struct passed explicitly to the functions that use it
- Confirm `const`-qualified globals used as read-only configuration are the only exception
- Check that local variables are declared at first use, not hoisted to function or block top
- Confirm no variable is declared at function scope but used in only one branch

## Violation

```c
static int counter = 0;

void tick(void) {
    counter += 1;
}

int read_counter(void) {
    return counter;
}
```

## Fix

```c
#include <assert.h>
#include <stddef.h>
typedef struct {
    int value;
} ticker_t;

void ticker_init(ticker_t *t) {
    assert(t != NULL);
    t->value = 0;
}

void ticker_tick(ticker_t *t) {
    assert(t != NULL);
    t->value += 1;
}

int ticker_read(const ticker_t *t) {
    assert(t != NULL);
    return t->value;
}
```

## Tooling
- `clang-tidy`: `cppcoreguidelines-avoid-non-const-global-variables` - flags mutable global/static variables
- `clang-tidy`: `readability-isolate-declaration` - flags multiple variables declared in one statement, a common cause of over-broad hoisted declarations
- `cppcheck --enable=all` - proxy: general static analysis pass that surfaces non-const global usage

## Strict profile
STRICT mode promotes `cppcoreguidelines-avoid-non-const-global-variables` [medium] to a CI-blocking error, banning any file-scope `static` mutable state with zero exceptions, and requires a clean `cppcheck --enable=all --error-exitcode=1` run.
