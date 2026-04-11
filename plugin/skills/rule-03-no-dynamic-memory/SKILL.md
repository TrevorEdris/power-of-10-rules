---
name: pow10-rule-03-no-dynamic-memory
description: "NASA Power of 10 Rule 3: Do not use dynamic memory allocation after initialization (severity: blocker)"
---

# Rule 3: Do not use dynamic memory allocation after initialization

**Severity:** blocker

## Rationale

Heap allocation introduces nondeterministic behavior: allocation can fail unpredictably, memory fragmentation grows over mission lifetime, and use-after-free and leaks are a class of errors that static analysis cannot fully rule out. Once the initialization phase completes, all memory must come from fixed-size pools, stack, or statically allocated buffers. This makes worst-case memory usage analyzable at build time.

## Enforcement

**Strategy:** static-analysis
**Tools:** clang-tidy, cppcheck

Forbid malloc, calloc, realloc, free, and alloca outside explicitly marked init functions. Mark the init phase boundary with a `// pow10:init-end` comment; the audit tool treats any allocation after that marker as a violation. Clang-tidy check: cppcoreguidelines-no-malloc. Recommend fixed-size pool allocators instead.

## Citations

- **Holzmann 2006** — Rule 3, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
- **JPL Institutional Coding Standard** — Rule 5 (no dynamic memory allocation)
