# Rule 1 — C

## Forbidden

`goto`, `setjmp`, `longjmp`, direct or indirect recursion (including across translation units).

## Violating example

```c
int sum_list(node_t *n) {
    return n ? n->value + sum_list(n->next) : 0;
}
```

`sum_list` calls itself — recursion.

## Remediation

Replace recursion with iteration capped by a constant:

```c
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

The explicit cap also satisfies Rule 2 (bounded loops).

## Hard checks

- `clang-tidy` checks: `cppcoreguidelines-avoid-goto`, `misc-no-recursion`, `cert-err52-cpp`
- `cppcheck` for call-graph recursion
