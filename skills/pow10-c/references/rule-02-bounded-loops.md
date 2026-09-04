# Rule 2 - Bounded Loops (C)

**Statement (Holzmann):** Every loop must carry an explicit, statically verifiable upper bound on its iteration count.

**Profile (literal):** applies fully; severity **blocker**.

The literal rule requires every loop's bound to be provable by a tool, ideally a compile-time constant. An unbounded `while` or bare `for (;;)` outside an annotated main event loop cannot have its worst-case execution time analyzed, which is disqualifying for real-time and safety-critical C. A runtime-derived bound must still be asserted against a fixed maximum before the loop runs.

## Checklist
- Reject any `while (condition)` with no enclosing iteration cap.
- Reject `for (;;)` unless it is the annotated main event loop.
- Cap recursive descent with an explicit depth limit or replace it with iteration.
- Bound queue/stream drain loops with a compile-time constant, not the producer's pace.
- Verify the bound constant is a `#define` or `enum`, not a value computed at runtime with no ceiling.

## Violation

```c
#include <stdbool.h>

typedef struct queue queue_t;
bool queue_empty(queue_t *q);
void *queue_pop(queue_t *q);
void process(void *item);

void drain_queue(queue_t *q) {
    while (!queue_empty(q)) {
        process(queue_pop(q));
    }
}
```

## Fix

```c
#include <stdbool.h>

typedef struct queue queue_t;
bool queue_empty(queue_t *q);
void *queue_pop(queue_t *q);
void process(void *item);

#define MAX_DRAIN 256

void drain_queue(queue_t *q) {
    for (int i = 0; i < MAX_DRAIN && !queue_empty(q); i++) {
        process(queue_pop(q));
    }
}
```

## Tooling
- `clang-tidy`: `bugprone-infinite-loop` - proxy: flags loops whose condition variables never change; does not catch a loop that terminates but has no provable bound
- `manual review`: every while loop without a counter or cap, and every for(;;) not tagged as the main event loop

## Strict profile
No strict-mode clang-tidy check targets loop bounds directly, so manual review sign-off stays required on every loop lacking a compile-time-constant bound. `cppcheck --enable=all --error-exitcode=1` must also run clean, per the global strict CI gate.
