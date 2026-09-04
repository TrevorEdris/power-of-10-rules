# Rule 9 - Restrict Pointers (C)

**Statement (Holzmann):** At most one level of dereferencing per declaration; pointer dereferences may not be hidden inside macro definitions or typedef declarations; no function pointers.

**Profile (literal):** applies fully; severity **blocker**.

Every extra level of indirection multiplies the aliasing state space a reviewer or static analyzer must track, and a function pointer defeats call-graph construction - the basis for reachability, coverage, and worst-case execution time analysis. Hiding a `*` inside a macro or a `typedef` does not remove the hazard, it just moves the dereference somewhere `grep` and a reviewer's eye won't catch it.

## Checklist

- Reject any declaration with `**` or deeper (except the isolated, documented `main(int, char **)` signature).
- Reject function pointer types, typedefs, and assignments outright.
- Expand every `typedef` and macro definition and check the result for a hidden `*p` or `(*fn)(...)` before approving.
- Replace dispatch tables with a closed `switch` over an enum so the call graph is fully static.
- Flag any macro whose expansion dereferences a pointer argument (`#define AT(p) (*(p))`) as a violation, not a convenience.

## Violation

```c
typedef int (*handler_t)(int);

static handler_t handlers[4];

void dispatch(int type, int val) {
    handlers[type] (val);
}
```

Function pointer table hides the reachable targets; reachability of any specific handler cannot be verified statically.

## Fix

```c
#include <stdio.h>
#include <stdlib.h>

typedef enum { EVT_A, EVT_B, EVT_C } event_type_t;

static void handle_a(int val) { printf("a:%d\n", val); }
static void handle_b(int val) { printf("b:%d\n", val); }

void dispatch(event_type_t type, int val) {
    switch (type) {
        case EVT_A: handle_a(val); break;
        case EVT_B: handle_b(val); break;
        default:
            fprintf(stderr, "dispatch: unknown type %d\n", type);
            abort();
    }
}
```

Call graph is fully static; `default` aborts on an unhandled type instead of hiding it.

## Tooling

- `clang-tidy`: `bugprone-multi-level-implicit-pointer-conversion` - proxy: catches implicit conversions across pointer levels, not a substitute for reading declarations
- `manual review`: expand every macro and typedef by hand and check for `**`, `***`, or function pointer types; no verified clang-tidy or cppcheck check counts declaration-level pointer depth directly

## Strict profile

No strict-mode clang-tidy check targets function-pointer or multi-level-pointer declarations directly, so manual review sign-off stays required on any file containing `**` or a typedef whose underlying type is a function pointer. `cppcheck --enable=all --error-exitcode=1` must also run clean, per the global strict CI gate.
