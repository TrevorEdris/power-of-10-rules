---
name: pow10-rule-10-warnings-as-errors
description: "NASA Power of 10 Rule 10: Compile with all warnings enabled and treat every warning as an error (severity: blocker)"
---

# Rule 10: Compile with all warnings enabled and treat every warning as an error

**Severity:** blocker

## Rationale

Compiler warnings are the cheapest form of static analysis available: they are zero-configuration, run on every build, and catch real defects (use of uninitialized memory, format string mismatches, signed/unsigned comparisons, unreachable code). A safety-critical build must enable the strictest warning flags the compiler offers and treat any warning as a build failure. Code should compile clean with at least two independent static analyzers, each also configured for maximum strictness.

## Enforcement

**Strategy:** compiler-flag
**Tools:** gcc, clang, clang-tidy, cppcheck

Required GCC/Clang flags: -Wall -Wextra -Wpedantic -Werror -Wshadow -Wconversion -Wsign-conversion -Wcast-align -Wstrict-prototypes. CI must block any build that emits warnings. Run at least one additional analyzer (clang-tidy, cppcheck, Coverity, or PVS-Studio) in the CI pipeline.

## Citations

- **Holzmann 2006** — Rule 10, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
