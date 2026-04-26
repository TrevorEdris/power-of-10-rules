---
name: pow10-rule-03-no-dynamic-memory
description: "NASA Power of 10 Rule 3 — No dynamic memory allocation after initialization. Severity: blocker."
---

# Rule 3 — No Dynamic Memory After Init

**Severity:** blocker

## Statement

After the initialization phase, no heap allocation. All memory comes from fixed-size pools, the stack, or static buffers. Worst-case memory usage must be analyzable at build time.

## Rationale

Heap allocation is nondeterministic: it can fail, fragment, leak, or be used after free. None of these failure modes are statically rule-out-able. Eliminating post-init allocation makes worst-case memory provable.

## Universal violation patterns

- Heap allocation calls in hot paths (`malloc`, `new`, `make([]T, n)`, `[]`)
- Implicit allocations from string concatenation, autoboxing, lambda capture
- Variable-size buffers grown inside loops
- Container growth without pre-sized capacity

## Universal remediation pattern

Allocate at init time. Reuse buffers (object pools, ring buffers, static arrays). Cap input sizes with assertions so worst-case memory is provable. Mark the init/post-init boundary explicitly.

## Init phase boundary

Tag the end of init explicitly so reviewers and tools know where the no-alloc rule kicks in:

```c
int main(void) {
    init_pools();
    init_drivers();
    // pow10:init-end
    for (;;) { tick(); }
}
```

## Per-language guidance

- C: [references/c.md](references/c.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md) (apply in spirit — CPython allocates constantly)
- Java: [references/java.md](references/java.md)
- Kotlin: [references/kotlin.md](references/kotlin.md)

## Waiver convention

```
// pow10: allow rule=3 until=YYYY-MM-DD owner=<handle> reason="..."
```

## Citations

- Holzmann 2006 — Rule 3
- JPL Institutional Coding Standard — Rule 5
