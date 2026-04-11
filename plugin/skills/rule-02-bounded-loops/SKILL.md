---
name: pow10-rule-02-bounded-loops
description: "NASA Power of 10 Rule 2: Give all loops a fixed upper bound (severity: blocker)"
---

# Rule 2: Give all loops a fixed upper bound

**Severity:** blocker

## Rationale

A statically verifiable bound on every loop prevents runaway execution and makes termination trivial to prove. Unbounded loops are incompatible with the Rate Monotonic Analysis used to prove real-time deadlines. The bound should be a compile-time constant wherever possible; when the bound must depend on runtime input, assert it against a fixed maximum.

## Enforcement

**Strategy:** hybrid
**Tools:** clang-tidy, manual-review

Every for/while loop must carry an explicit iteration cap. Prefer: `for (int i = 0; i < N; i++)` where N is a macro or constant. Reject `while (condition)` unless an outer counter enforces a cap. If the loop is intentionally unbounded (e.g. main event loop), tag it with a // pow10: allow rule=2 waiver and document why.

## Citations

- **Holzmann 2006** — Rule 2, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
