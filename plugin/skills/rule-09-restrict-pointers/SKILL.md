---
name: pow10-rule-09-restrict-pointers
description: "NASA Power of 10 Rule 9: Restrict pointer use: no more than one level of dereferencing and no function pointers (severity: blocker)"
---

# Rule 9: Restrict pointer use: no more than one level of dereferencing and no function pointers

**Severity:** blocker

## Rationale

Each level of pointer indirection multiplies the state space a human reviewer or static analyzer must track. Multi-level pointers (`char **`, `int ***`) make aliasing analysis effectively impossible and hide ownership. Function pointers defeat call graph construction entirely, which is the foundation of reachability, coverage, and worst-case execution time analysis. Both patterns must be avoided in safety-critical code.

## Enforcement

**Strategy:** static-analysis
**Tools:** clang-tidy, cppcheck

Flag any declaration containing two or more consecutive `*` characters in its type. Forbid function pointer declarations, typedefs, and assignments. If a pattern genuinely requires indirection (e.g. interrupt vector tables), isolate it to a single well-documented module with a waiver. Clang-tidy: custom matcher required.

## Citations

- **Holzmann 2006** — Rule 9, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
- **JPL Institutional Coding Standard** — Rule 14 (no function pointers)
