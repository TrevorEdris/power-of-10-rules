---
name: pow10-rule-01-control-flow
description: "NASA Power of 10 Rule 1: Restrict control flow to simple constructs (severity: blocker)"
---

# Rule 1: Restrict control flow to simple constructs

**Severity:** blocker

## Rationale

Simple control flow is easier to verify by inspection and by static analysis. Goto, setjmp/longjmp, and recursion make call graphs and reachability analyses undecidable or impractical, and they frustrate bounded model checking and coverage analysis. Safety-critical code must use only straight-line execution, conditionals, and bounded iteration.

## Enforcement

**Strategy:** static-analysis
**Tools:** clang-tidy, cppcheck

Forbid goto, setjmp, longjmp, and direct/indirect recursion. Clang-tidy checks: cppcoreguidelines-avoid-goto, misc-no-recursion, cert-err52-cpp. Call graph analysis catches recursion that crosses translation units.

## Citations

- **Holzmann 2006** — Rule 1, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
- **JPL Institutional Coding Standard** — Rule 3 (no recursion), Rule 11 (no goto)
