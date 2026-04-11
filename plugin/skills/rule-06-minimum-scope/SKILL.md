---
name: pow10-rule-06-minimum-scope
description: "NASA Power of 10 Rule 6: Declare data objects at the smallest possible scope (severity: medium)"
---

# Rule 6: Declare data objects at the smallest possible scope

**Severity:** medium

## Rationale

Variables declared at the narrowest scope where they are used make data hiding explicit, simplify debugging, and prevent accidental cross-scope mutation. Globals and file-scope statics should be avoided; when unavoidable, they must be const or guarded by documented access protocols. Narrow scope also helps the compiler optimize register allocation and lifetime analysis.

## Enforcement

**Strategy:** static-analysis
**Tools:** clang-tidy

Clang-tidy check: cppcoreguidelines-avoid-non-const-global-variables. Flag any non-const global or file-scope static. For function-local variables, recommend declaring at point of first use (C99) rather than function top.

## Citations

- **Holzmann 2006** — Rule 6, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
