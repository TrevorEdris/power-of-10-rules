# Rule 2 — C

## Forbidden

`while (condition)` without an enclosing iteration cap. `for (;;)` outside an annotated main event loop.

## Violating example

```c
void drain_queue(queue_t *q) {
    while (!queue_empty(q)) {
        process(queue_pop(q));
    }
}
```

If a producer outpaces the consumer, this loop never returns.

## Remediation

Add an explicit cap:

```c
#define MAX_DRAIN 256

void drain_queue(queue_t *q) {
    for (int i = 0; i < MAX_DRAIN && !queue_empty(q); i++) {
        process(queue_pop(q));
    }
}
```

`MAX_DRAIN` is a compile-time constant — worst-case execution time is now analyzable.

## Hard checks

- `clang-tidy` check: `bugprone-infinite-loop`
- Manual review for any `while` without a counter or cap
- For intentional `for (;;)` event loops, tag with a Rule 2 waiver comment
