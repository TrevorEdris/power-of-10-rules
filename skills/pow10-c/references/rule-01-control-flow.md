# Rule 1 - Restrict Control Flow to Simple Constructs (C)

**Statement (Holzmann):** Use only straight-line execution, conditionals, and bounded iteration - forbid `goto`, `setjmp`/`longjmp`, and recursion (direct or indirect, including mutual recursion across translation units).

**Profile (literal):** applies fully; severity **blocker**.

The literal rule bans `goto`, `setjmp`/`longjmp`, and all recursion outright, with no exception for trusted or bounded data. `goto` and non-local jumps make reachability undecidable by inspection; recursion makes the call graph unbounded, defeating stack-depth analysis and bounded model checking. There is no "safe" recursion under this profile - every recursive call, direct or mutual, is a violation regardless of how the depth is bounded at runtime.

## Checklist
- Reject any `goto` statement outright; there is no justified use under the literal profile.
- Reject any `setjmp`/`longjmp` pair, including cleanup-via-non-local-jump patterns.
- Reject any function that calls itself directly.
- Reject indirect or mutual recursion spanning functions or translation units.
- Flag tail-call-shaped recursion the same as any other recursion; it still reads as recursion.
- Require iteration with an explicit, constant upper bound as the replacement.

## Violation

```c
typedef struct node {
    int value;
    struct node *next;
} node_t;

int sum_list(node_t *n) {
    return n ? n->value + sum_list(n->next) : 0;
}
```

`sum_list` calls itself - direct recursion, forbidden regardless of list size.

## Fix

```c
#include <stddef.h>

typedef struct node {
    int value;
    struct node *next;
} node_t;

#define MAX_NODES 1024

int sum_list(node_t *n) {
    int total = 0;
    for (int i = 0; i < MAX_NODES && n != NULL; i++) {
        total += n->value;
        n = n->next;
    }
    return total;
}
```

The explicit `MAX_NODES` cap also satisfies Rule 2 (bounded loops).

## Tooling
- `clang-tidy`: `cppcoreguidelines-avoid-goto` - flags goto usage (permits only forward jumps out of nested loops)
- `clang-tidy`: `misc-no-recursion` - flags direct and indirect recursive calls
- `manual review`: setjmp/longjmp pairs and non-local-jump cleanup chains; no verified clang-tidy check covers these on plain C sources

## Strict profile
CI gates both checks as errors with zero exceptions: `clang-tidy` run with `cppcoreguidelines-avoid-goto` and `misc-no-recursion` enabled and treated as build-breaking, plus manual review of any setjmp.h include.
